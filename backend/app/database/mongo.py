# from motor.motor_asyncio import AsyncIOMotorClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# MONGO_URI = os.getenv("uri")
# MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# client = AsyncIOMotorClient(MONGO_URI)
# mongo_db = client[MONGO_DB_NAME]


from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import logging

load_dotenv()

MONGO_URI = os.getenv("uri")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

client = AsyncIOMotorClient(MONGO_URI)
mongo_db = client[MONGO_DB_NAME]

async def ping_mongo():
    try:
        await client.admin.command("ping")
        logging.info("✅ Successfully connected to MongoDB!")
    except Exception as e:
        logging.error(f"❌ Failed to connect to MongoDB: {e}")
