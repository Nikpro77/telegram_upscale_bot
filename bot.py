import asyncio
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN
from database import db
from handlers import admin, user, image, misc  # Import handlers to register handlers
from utils.queue_manager import queue_manager
async def main():
    await db.connect()
    app = Client(
        "upscale_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
    )
    # Start queue worker
    asyncio.create_task(queue_manager.worker())
    await app.start()
    print("Bot started.")
    # Idle to keep bot running
    await app.idle()
    await app.stop()
    await db.close()
if __name__ == "__main__":
    asyncio.run(main())
