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

@Client.on_message(filters.command("
