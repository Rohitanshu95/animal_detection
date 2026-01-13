import asyncio
from database import connect_to_mongo, get_collection, close_mongo_connection

async def main():
    await connect_to_mongo()
    collection = get_collection()
    count = await collection.count_documents({})
    print(f"Number of incidents in database: {count}")
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
