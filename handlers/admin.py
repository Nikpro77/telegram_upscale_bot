from pyrogram import Client, filters
from pyrogram.types import Message
from database import db
from config import OWNER_ID

def owner_only(func):
    async def wrapper(client: Client, message: Message):
        if message.from_user.id != OWNER_ID:
            await message.reply_text("🚫 Only the owner can use this command.")
            return
        await func(client, message)
    return wrapper

def admin_or_owner(func):
    async def wrapper(client: Client, message: Message):
        user_id = message.from_user.id
        if user_id == OWNER_ID or await db.is_admin(user_id):
            await func(client, message)
        else:
            await message.reply_text("🚫 You need to be an admin or owner to use this command.")
    return wrapper

@Client.on_message(filters.command("addadmin") & filters.private)
@owner_only
async def add_admin(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /addadmin <user_id>")
        return
    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply_text("Invalid user ID.")
        return
    await db.set_admin(user_id)
    await message.reply_text(f"✅ User {user_id} added as admin.")

@Client.on_message(filters.command("removeadmin") & filters.private)
@owner_only
async def remove_admin(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /removeadmin <user_id>")
        return
    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply_text("Invalid user ID.")
        return
    await db.remove_admin(user_id)
    await message.reply_text(f"✅ User {user_id} removed from admins.")

@Client.on_message(filters.command("ban") & filters.private)
@admin_or_owner
async def ban_user(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /ban <user_id>")
        return
    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply_text("Invalid user ID.")
        return
    await db.ban_user(user_id)
    await message.reply_text(f"🚫 User {user_id} has been banned.")

@Client.on_message(filters.command("unban") & filters.private)
@admin_or_owner
async def unban_user(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /unban <user_id>")
        return
    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply_text("Invalid user ID.")
        return
    await db.unban_user(user_id)
    await message.reply_text(f"✅ User {user_id} has been unbanned.")

@Client.on_message(filters.command("userinfo") & filters.private)
@admin_or_owner
async def user_info(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /userinfo <user_id>")
        return
    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply_text("Invalid user ID.")
        return
    info = await db.get_user_info(user_id)
    if not info:
        await message.reply_text("User  not found.")
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

@Client.on_message(filters.command("totalusers") & filters.private)
@admin_or_owner
async def total_users(client: Client, message: Message):
    total = await db.get_total_users()
    await message.reply_text(f"👥 Total registered users: {total}")

@Client.on_message(filters.command("checkuser") & filters.private)
@admin_or_owner
async def check_user(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /checkuser <user_id>")
        return
    try:
        user_id = int(message.command[1])
    except ValueError:
        await message.reply_text("Invalid user ID.")
        return
    info = await db.get_user_info(user_id)
    if not info:
        await message.reply_text("User  not found.")
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

@Client.on_message(filters.command("broadcast") & filters.private)
@owner_only
async def broadcast(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /broadcast <message>")
        return
    text = message.text.split(None, 1)[1]
    total = await db.get_total_users()
    await message.reply_text(f"📢 Broadcasting to {total} users...")
    async for user in db.users.find({}, {"user_id": 1}):
        user_id = user["user_id"]
        try:
            await client.send_message(user_id, text)
        except Exception:
            pass
    await message.reply_text("✅ Broadcast completed.")

@Client.on_message(filters.command("fbroadcast") & filters.private)
@owner_only
async def forward_broadcast(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to forward it.")
        return
    total = await db.get_total_users()
    await message.reply_text(f"📢 Forwarding message to {total} users...")
    async for user in db.users.find({}, {"user_id": 1}):
        user_id = user["user_id"]
        try:
            await client.forward_messages(user_id, message.chat.id, message.reply_to_message.message_id)
        except Exception:
            pass
    await message.reply_text("✅ Forward broadcast completed.")
