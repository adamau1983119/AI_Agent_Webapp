"""快速測試 MongoDB 連接"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure
from dotenv import load_dotenv

load_dotenv()

async def test():
    url = os.getenv("MONGODB_URL")
    print(f"Testing connection with URL: {url[:50]}...")
    
    try:
        client = AsyncIOMotorClient(url, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        print("SUCCESS: Connection successful!")
        client.close()
        return True
    except OperationFailure as e:
        if "authentication failed" in str(e).lower():
            print("ERROR: Authentication failed - check username/password")
        else:
            print(f"ERROR: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test())
    exit(0 if result else 1)

