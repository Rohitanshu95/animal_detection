"""
Check coverage of standard districts
"""
import asyncio
from dotenv import load_dotenv
from database import connect_to_mongo, get_collection, close_mongo_connection
from ai.utils import ODISHA_DISTRICTS

load_dotenv()

async def check_coverage():
    await connect_to_mongo()
    collection = get_collection()
    
    total = await collection.count_documents({})
    
    # Count how many match the standard list
    pipeline = [
        {"$match": {"location": {"$in": ODISHA_DISTRICTS}}},
        {"$count": "valid_count"}
    ]
    result = await collection.aggregate(pipeline).to_list(None)
    valid_count = result[0]["valid_count"] if result else 0
    
    print(f"Total Incidents: {total}")
    print(f"Valid District Locations: {valid_count}")
    print(f"Coverage: {valid_count / total * 100:.1f}%")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(check_coverage())
