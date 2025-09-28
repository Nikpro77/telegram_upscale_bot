from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.api_clients import upscale_image, upload_image_to_imgbb
from utils.helpers import save_file_to_temp, cleanup_file
from database import db
from utils.rate_limiter import RateLimiter
from utils.queue_manager import queue_manager
from config import MAX_REQUESTS_PER_MINUTE

import io

rate_limiter = RateLimiter(MAX_REQUESTS_PER_MINUTE)

QUALITY_OPTIONS = {
    "standard": "Standard",
    # Extend with more qualities if API supports
}

@Client.on_message(filters.command(["upscale", "up"]) & filters.reply & filters.private)
async def handle_upscale(client: Client, message: Message):
    user = message.from_user
    if await db.is_banned(user.id):
        await message.reply_text("🚫 You are banned from using this bot.")
        return

    if not rate_limiter.is_allowed(user.id):
        await message.reply_text("⏳ Rate limit exceeded. Please wait before sending more requests.")
        return

    replied = message.reply_to_message
    if not replied or not (replied.photo or replied.document):
        await message.reply_text("⚠️ Please reply to an image to upscale.")
        return

    # Ask user for quality selection
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=v, callback_data=f"quality_{k}")] for k,v in QUALITY_OPTIONS.items()]
    )
    await message.reply_text("Select upscale quality:", reply_markup=keyboard)

    # Save context for callback
    client.set_parse_mode("markdown")
    client.data = getattr(client, "data", {})
    client.data[user.id] = {"message": message, "replied": replied}

@Client.on_callback_query(filters.regex(r"quality_(.+)"))
async def quality_callback(client: Client, callback_query):
    user_id = callback_query.from_user.id
    quality = callback_query.data.split("_", 1)[1]

    if user_id not in getattr(client, "data", {}):
        await callback_query.answer("Session expired. Please try again.", show_alert=True)
        return

    context = client.data.pop(user_id)
    message = context["message"]
    replied = context["replied"]

    await callback_query.answer(f"Selected quality: {QUALITY_OPTIONS.get(quality, quality)}")

    # Download image bytes
    file = replied.photo or replied.document
    file_bytes = await client.download_media(file, in_memory=True)

    # Define processing coroutine
    async def process():
        try:
            await message.reply_text("🔄 Processing your image for upscaling... This may take some time.")
            upscaled_bytes = await upscale_image(file_bytes, quality=quality)
            temp_path = await save_file_to_temp(upscaled_bytes, suffix=".jpg")

            await db.add_user(user_id, message.from_user.username, message.from_user.first_name, message.from_user.last_name)
            await db.increment_upscale(user_id)

            await message.reply_document(temp_path, caption="✅ Here is your upscaled image.")
            cleanup_file(temp_path)
        except Exception as e:
            await message.reply_text(f"❌ Upscaling failed: {e}")

    # Add to queue
    added = await queue_manager.add_task(user_id, process)
    if not added:
        await message.reply_text("⚠️ You already have an image being processed. Please wait.")

@Client.on_message(filters.command(["imgurl", "url"]) & (filters.reply | filters.private))
async def handle_imgurl(client: Client, message: Message):
    user = message.from_user
    if await db.is_banned(user.id):
        await message.reply_text("🚫 You are banned from using this bot.")
        return

    if not rate_limiter.is_allowed(user.id):
        await message.reply_text("⏳ Rate limit exceeded. Please wait before sending more requests.")
        return

    replied = message.reply_to_message
    target_msg = replied if replied else message

    if not (target_msg.photo or target_msg.document):
        await message.reply_text("⚠️ Please send or reply to an image to upload.")
        return

    file = target_msg.photo or target_msg.document
    file_bytes = await client.download_media(file, in_memory=True)

    await message.reply_text("🔄 Uploading your image...")

    try:
        url = await upload_image_to_imgbb(file_bytes)
    except Exception as e:
        await message.reply_text(f"❌ Image upload failed: {e}")
        return

    await db.add_user(user.id, user.username, user.first_name, user.last_name)

    await message.reply_text(f"🌐 Your image URL:\n{url}")
