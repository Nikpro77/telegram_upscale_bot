from pyrogram import Client, filters
from pyrogram.types import Message
from database import db

@Client.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.first_name, user.last_name)
    text = (
        "👋 Welcome to the Image Upscale Bot!\n\n"
        "Reply to any image with /upscale or /up to enhance it.\n"
        "Use /imgurl or /url to upload images and get direct URLs.\n\n"
        "Use /help to see all commands."
    )
    await message.reply_text(text)

@Client.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    text = (
        "📚 *Available Commands:*\n\n"
        "/upscale or /up - Reply to an image to upscale it\n"
        "/imgurl or /url - Upload image and get direct URL\n"
        "/mystats - Your upscaling stats\n"
        "/myinfo - Your user info\n"
        "/leaderboard or /top - Top 10 upscalers\n\n"
        "👮‍♂️ *Admin Commands:*\n"
        "/addadmin <user_id> - Add admin (Owner only)\n"
        "/removeadmin <user_id> - Remove admin (Owner only)\n"
        "/ban <user_id> - Ban user\n"
        "/unban <user_id> - Unban user\n"
        "/userinfo <user_id> - Get user info\n"
        "/totalusers - Total users\n"
        "/checkuser <user_id> - Check user details\n"
        "/broadcast <message> - Broadcast message (Owner only)\n"
        "/fbroadcast - Forward broadcast (Owner only, reply to message)\n"
        "/botstats - Bot statistics\n"
    )
    await message.reply_text(text, parse_mode="markdown")

@Client.on_message(filters.command("botstats") & filters.private)
async def botstats(client: Client, message: Message):
    total_users = await db.get_total_users()
    total_upscales = await db.get_total_upscales()
    top_users = await db.get_top_upscalers(3)
    text = (
        f"🤖 *Bot Statistics:*\n"
        f"Total Users: {total_users}\n"
        f"Total Upscaled Images: {total_upscales}\n"
        f"Top Upscalers:\n"
    )
    for i, user in enumerate(top_users, 1):
        uname = f"@{user.get('username')}" if user.get('username') else f"User  {user.get('user_id')}"
        text += f"{i}. {uname} — {user.get('upscaled_count', 0)} images\n"
    await message.reply_text(text, parse_mode="markdown")
