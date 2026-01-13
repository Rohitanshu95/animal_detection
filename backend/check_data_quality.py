"""
Diagnostic script to check remaining non-standard data.
"""
import asyncio
from dotenv import load_dotenv
from database import connect_to_mongo, get_collection, close_mongo_connection
from ai.utils import ODISHA_DISTRICTS

load_dotenv()

async def check_data():
    await connect_to_mongo()
    collection = get_collection()
    
    print("📊 DATA QUALITY REPORT\n")
    
    # 1. Check Animals
    pipeline_animals = [
        {"$unwind": "$extracted_animals"},
        {"$group": {"_id": "$extracted_animals", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 50}
    ]
    animals = await collection.aggregate(pipeline_animals).to_list(None)
    
    print("--- Top Animals (Current State) ---")
    for item in animals:
        name = item["_id"]
        count = item["count"]
        # rudimentary check: does it look "standard"? (Title case, plural usually)
        print(f"{count: <4} {name}")

    print("\n" + "="*30 + "\n")

    # 2. Check Locations
    pipeline_locations = [
        {"$group": {"_id": "$location", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 50}
    ]
    locations = await collection.aggregate(pipeline_locations).to_list(None)
    
    print("--- Top Locations (Current State) ---")
    standard_set = set(ODISHA_DISTRICTS)
    
    non_standard = []
    
    for item in locations:
        name = item["_id"]
        count = item["count"]
        status = "✅" if name in standard_set else "❌"
        print(f"{status} {count: <4} {name}")
        
        if name not in standard_set and name:
            non_standard.append((name, count))
            
    print("\n--- Non-Standard Locations (Potential Misses) ---")
    for name, count in non_standard[:20]:
        print(f"{count}: {name}")
        
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(check_data())
