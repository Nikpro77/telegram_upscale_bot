import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "your_api_hash")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")

OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))

DEEPAI_API_KEY = os.getenv("DEEPAI_API_KEY", "your_deepai_api_key")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "your_imgbb_api_key")

MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "20"))

PORT = int(os.getenv("PORT", "8443"))

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
