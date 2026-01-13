"""
Script to normalize existing animal data in the database.
This unifies fragmented animal names (e.g. "Turtle", "Sea Turtle" -> "Turtles")
to ensure accurate filter counts.
"""

import asyncio
import os
from dotenv import load_dotenv
from database import connect_to_mongo, get_collection, close_mongo_connection
from ai.utils import normalize_animal_name, normalize_location_name

# Load environment variables
load_dotenv()

async def normalize_incidents():
    print("🚀 Starting data normalization (Animals + Regions)...")
    
    # Connect
    await connect_to_mongo()
    collection = get_collection()
    
    # Fetch all incidents
    incidents = await collection.find({}).to_list(None)
    print(f"📦 Found {len(incidents)} incidents to process.")
    
    updated_count = 0
    
    for incident in incidents:
        needs_update = False
        updates = {}
        
        # 1. Normalize 'extracted_animals' list
        extracted = incident.get("extracted_animals", [])
        if extracted:
            new_extracted = []
            seen = set()
            for animal in extracted:
                norm = normalize_animal_name(animal)
                if norm not in seen:
                    new_extracted.append(norm)
                    seen.add(norm)
            
            # Check if changed
            if sorted(extracted) != sorted(new_extracted):
                updates["extracted_animals"] = new_extracted
                needs_update = True
        
        # 2. Normalize 'animals' field (string)
        main_animal = incident.get("animals", "")
        if main_animal:
            norm_main = normalize_animal_name(main_animal)
            if norm_main != main_animal:
                updates["animals"] = norm_main
                needs_update = True
        
        # 3. Normalize 'location' field
        location = incident.get("location", "")
        if location:
            norm_loc = normalize_location_name(location)
            if norm_loc != location:
                updates["location"] = norm_loc
                needs_update = True
                # print(f"   📍 Location {location} -> {norm_loc}")
                
        # Apply update
        if needs_update:
            await collection.update_one(
                {"_id": incident["_id"]},
                {"$set": updates}
            )
            updated_count += 1
            if updated_count % 10 == 0:
                print(f"   ✅ Updated {updated_count} records...")
    
    print(f"\n🎉 Normalization Complete!")
    print(f"📊 Total updated: {updated_count}/{len(incidents)}")
    
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(normalize_incidents())
