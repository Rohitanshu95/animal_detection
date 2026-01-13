"""
MongoDB database connection and configuration
File location: backend/database.py
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "wildlife_smuggling_db")
COLLECTION_NAME = "incidents"

# Global variables
client: AsyncIOMotorClient = None
database = None


async def connect_to_mongo():
    """
    Connect to MongoDB database
    """
    global client, database
    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        database = client[DATABASE_NAME]
        
        # Test connection
        await client.admin.command('ping')
        print(f"Connected to MongoDB: {DATABASE_NAME}")

        # Create indexes for better search performance
        await create_indexes()

    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """
    Close MongoDB connection
    """
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")


async def create_indexes():
    """
    Create database indexes for optimized queries
    """
    global database

    incidents_collection = database[COLLECTION_NAME]

    # Text index for search
    await incidents_collection.create_index([
        ("description", "text"),
        ("location", "text"),
        ("animals", "text"),
        ("source", "text")
    ])

    # Single field indexes
    await incidents_collection.create_index("date")
    await incidents_collection.create_index("status")
    await incidents_collection.create_index("location")
    await incidents_collection.create_index("created_at")

    # Array indexes for filtered fields
    await incidents_collection.create_index("extracted_animals")  # Array index for species filtering
    await incidents_collection.create_index("tags")  # Array index for tag filtering

    # Compound indexes for common filter combinations
    await incidents_collection.create_index([("status", 1), ("created_at", -1)])  # For status + date filtering
    await incidents_collection.create_index([("location", 1), ("created_at", -1)])  # For location-based queries

    print("Created database indexes")


def get_database():
    """
    Get database instance
    """
    return database


def get_collection(collection_name: str = COLLECTION_NAME):
    """
    Get collection instance
    """
    return database[collection_name]


# Synchronous client for non-async operations (e.g., migrations)
def get_sync_client():
    """
    Get synchronous MongoDB client
    """
    return MongoClient(MONGODB_URI)


def get_sync_database():
    """
    Get synchronous database instance
    """
    sync_client = get_sync_client()
    return sync_client[DATABASE_NAME]


async def insert_sample_data():
    """
    Insert sample data for testing
    """
    incidents_collection = database[COLLECTION_NAME]
    
    # Check if collection is empty
    count = await incidents_collection.count_documents({})
    if count > 0:
        print(f"Database already has {count} records")
        return
    
    sample_incidents = [
        {
            "date": "2024-12-15",
            "location": "Mumbai Port, India",
            "animals": "Pangolin scales",
            "quantity": "150 kg",
            "description": "Customs officials seized 150kg of pangolin scales hidden in seafood containers",
            "source": "Wildlife Crime Control Bureau",
            "status": "Investigated",
            "created_at": "2024-12-15T10:30:00",
            "updated_at": "2024-12-15T10:30:00"
        },
        {
            "date": "2024-12-10",
            "location": "Delhi Airport, India",
            "animals": "Star tortoises",
            "quantity": "23 specimens",
            "description": "Passenger caught attempting to smuggle endangered star tortoises in luggage",
            "source": "Airport Customs",
            "status": "Prosecuted",
            "suspects": "1 arrested",
            "created_at": "2024-12-10T14:20:00",
            "updated_at": "2024-12-10T14:20:00"
        },
        {
            "date": "2024-11-28",
            "location": "Chennai, Tamil Nadu",
            "animals": "Red sanders wood",
            "quantity": "500 kg",
            "description": "Illegal transportation of red sanders worth 50 lakhs intercepted",
            "source": "Forest Department",
            "status": "Reported",
            "estimated_value": "₹50,00,000",
            "created_at": "2024-11-28T09:15:00",
            "updated_at": "2024-11-28T09:15:00"
        },
        {
            "date": "2024-11-15",
            "location": "Kolkata Port, West Bengal",
            "animals": "Exotic birds",
            "quantity": "45 birds",
            "description": "Rare exotic birds found in shipping container from Southeast Asia",
            "source": "Customs Department",
            "status": "Investigated",
            "created_at": "2024-11-15T11:45:00",
            "updated_at": "2024-11-15T11:45:00"
        },
        {
            "date": "2024-10-22",
            "location": "Goa Border, India",
            "animals": "Tiger claws and teeth",
            "quantity": "12 pieces",
            "description": "Vehicle stopped at border checkpoint found carrying tiger body parts",
            "source": "Wildlife Protection Society",
            "status": "Prosecuted",
            "suspects": "2 arrested",
            "vehicle_info": "Black SUV, MH-12-XX-1234",
            "created_at": "2024-10-22T16:00:00",
            "updated_at": "2024-10-22T16:00:00"
        }
    ]
    
    result = await incidents_collection.insert_many(sample_incidents)
    print(f"Inserted {len(result.inserted_ids)} sample records")


# Database health check
async def check_database_health():
    """
    Check if database connection is healthy
    """
    try:
        await client.admin.command('ping')
        return True
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False