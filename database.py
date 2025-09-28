import motor.motor_asyncio
from config import MONGODB_URI, OWNER_ID
from datetime import datetime

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.users = None
        self.admins = None
        self.upscales = None

    async def connect(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        self.db = self.client["upscale_bot_db"]
        self.users = self.db["users"]
        self.admins = self.db["admins"]
        self.upscales = self.db["upscales"]

        # Ensure owner is admin on startup
        await self.set_admin(OWNER_ID)
        await self.add_user(OWNER_ID, None, None, None)

    async def add_user(self, user_id, username, first_name, last_name):
        user = await self.users.find_one({"user_id": user_id})
        if not user:
            await self.users.insert_one({
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "is_admin": False,
                "is_banned": False,
                "upscaled_count": 0,
                "created_at": datetime.utcnow()
            })
        else:
            # Update username and names if changed
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name
                }}
            )

    async def set_admin(self, user_id):
        await self.admins.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
        await self.users.update_one({"user_id": user_id}, {"$set": {"is_admin": True}})

    async def remove_admin(self, user_id):
        await self.admins.delete_one({"user_id": user_id})
        await self.users.update_one({"user_id": user_id}, {"$set": {"is_admin": False}})

    async def is_admin(self, user_id):
        admin = await self.admins.find_one({"user_id": user_id})
        return admin is not None

    async def ban_user(self, user_id):
        await self.users.update_one({"user_id": user_id}, {"$set": {"is_banned": True}})

    async def unban_user(self, user_id):
        await self.users.update_one({"user_id": user_id}, {"$set": {"is_banned": False}})

    async def is_banned(self, user_id):
        user = await self.users.find_one({"user_id": user_id})
        return user and user.get("is_banned", False)

    async def increment_upscale(self, user_id):
        await self.users.update_one({"user_id": user_id}, {"$inc": {"upscaled_count": 1}})
        await self.upscales.insert_one({
            "user_id": user_id,
            "timestamp": datetime.utcnow()
        })

    async def get_user_stats(self, user_id):
        user = await self.users.find_one({"user_id": user_id})
        return user.get("upscaled_count", 0) if user else 0

    async def get_top_upscalers(self, limit=10):
        cursor = self.users.find().sort("upscaled_count", -1).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_total_users(self):
        return await self.users.count_documents({})

    async def get_total_upscales(self):
        return await self.upscales.count_documents({})

    async def get_user_info(self, user_id):
        return await self.users.find_one({"user_id": user_id})

    async def close(self):
        self.client.close()

db = Database()
