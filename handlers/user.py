from pyrogram import Client, filters
from pyrogram.types import Message
from database import db

@Client.on_message(filters.command(["mystats"]) & filters.private)
async def mystats(client: Client, message: Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.first_name, user.last_name)
    count = await db.get_user_stats(user.id)
    await message.reply_text(f"📊 You have upscaled {count} images.")

@Client.on_message(filters.command(["myinfo"]) & filters.private)
async def myinfo(client: Client, message: Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.first_name, user.last_name)
    info = await db.get_user_info(user.id)
    if not info:
        await message.reply_text("No info found.")
        return
    user_id = info.get("user_id")
    username = info.get("username")
    first_name = info.get("first_name")
    last_name = info.get("last_name")
    is_admin = info.get("is_admin")
    is_banned = info.get("is_banned")
    upscaled_count = info.get("upscaled_count")
    text = (
        f"👤 User Info:\n"
        f"ID: {user_id}\n"
        f"Username: @{username if username else 'N/A'}\n"
        f"Name: {first_name} {last_name if last_name else ''}\n"
        f"Admin: {'Yes' if is_admin else 'No'}\n"
        f"Banned: {'Yes' if is_banned else 'No'}\n"
        f"Upscaled Images: {upscaled_count}"
    )
    await message.reply_text(text)

@Client.on_message(filters.command(["leaderboard", "top"]) & filters.private)
async def leaderboard(client: Client, message: Message):
    top_users = await db.get_top_upscalers()
    if not top_users:
        await message.reply_text("No upscaling data available yet.")
        return
    text = "🏆 Top 10 Upscalers 🏆\n\n"
    for i, user in enumerate(top_users, 1):
        uname = f"@{user.get('username')}" if user.get('username') else f"User  {user.get('user_id')}"
        count = user.get("upscaled_count", 0)
        text += f"{i}. {uname} — {count} images\n"
    await message.reply_text(text)
