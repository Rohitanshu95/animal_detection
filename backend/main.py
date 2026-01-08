"""
FastAPI backend for Wildlife Smuggling Tracker
Main application entry point
"""

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import pandas as pd
import io

from models import (
    IncidentCreate, IncidentUpdate, IncidentResponse,
    SearchQuery, BulkUploadResponse, StatisticsResponse
)
from database import (
    connect_to_mongo, close_mongo_connection, 
    get_collection, insert_sample_data, check_database_health
)
from ai.extractor import extract_entities_from_text
from ai.summarizer import generate_summary

# Initialize FastAPI app
app = FastAPI(
    title="Wildlife Smuggling Tracker API",
    description="API for tracking and analyzing wildlife smuggling incidents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await connect_to_mongo()
    # Optionally insert sample data
    # await insert_sample_data()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_mongo_connection()


# Health Check Endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "healthy",
        "service": "Wildlife Smuggling Tracker API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check including database"""
    db_healthy = await check_database_health()
    
    return {
        "api": "healthy",
        "database": "healthy" if db_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# CRUD Endpoints

@app.post("/incidents", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED, tags=["Incidents"])
async def create_incident(incident: IncidentCreate, use_ai: bool = Query(True, description="Use AI to extract entities")):
    """
    Create a new incident
    
    - **use_ai**: If True, AI will extract animals, locations, and generate summary
    """
    collection = get_collection()
    
    # Convert to dict
    incident_dict = incident.dict()
    incident_dict["created_at"] = datetime.utcnow()
    incident_dict["updated_at"] = datetime.utcnow()
    
    # AI Enhancement (if enabled)
    if use_ai:
        try:
            # Extract entities from description
            entities = await extract_entities_from_text(incident.description)
            incident_dict["extracted_animals"] = entities.get("animals", [])
            incident_dict["extracted_location"] = entities.get("location")
            incident_dict["keywords"] = entities.get("keywords", [])
            
            # Generate AI summary
            summary = await generate_summary(incident.description)
            incident_dict["ai_summary"] = summary
            
        except Exception as e:
            print(f"⚠️ AI processing failed: {e}")
            # Continue without AI features
    
    # Insert into database
    result = await collection.insert_one(incident_dict)
    
    # Fetch and return created incident
    created_incident = await collection.find_one({"_id": result.inserted_id})
    created_incident["_id"] = str(created_incident["_id"])
    
    return created_incident


@app.get("/incidents", response_model=List[IncidentResponse], tags=["Incidents"])
async def get_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    location: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """
    Get all incidents with optional filters
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **status**: Filter by status (Reported, Investigated, Prosecuted, Closed)
    - **location**: Filter by location (partial match)
    - **date_from**: Filter incidents from this date (YYYY-MM-DD)
    - **date_to**: Filter incidents until this date (YYYY-MM-DD)
    """
    collection = get_collection()
    
    # Build query
    query = {}
    if status:
        query["status"] = status
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if date_from or date_to:
        query["date"] = {}
        if date_from:
            query["date"]["$gte"] = date_from
        if date_to:
            query["date"]["$lte"] = date_to
    
    # Execute query
    cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
    incidents = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for incident in incidents:
        incident["_id"] = str(incident["_id"])
    
    return incidents


@app.get("/incidents/{incident_id}", response_model=IncidentResponse, tags=["Incidents"])
async def get_incident(incident_id: str):
    """Get a specific incident by ID"""
    collection = get_collection()
    
    try:
        incident = await collection.find_one({"_id": ObjectId(incident_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid incident ID format")
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    incident["_id"] = str(incident["_id"])
    return incident


@app.put("/incidents/{incident_id}", response_model=IncidentResponse, tags=["Incidents"])
async def update_incident(incident_id: str, incident_update: IncidentUpdate):
    """Update an existing incident"""
    collection = get_collection()
    
    # Get only non-None fields
    update_data = {k: v for k, v in incident_update.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data["updated_at"] = datetime.utcnow()
    
    try:
        result = await collection.find_one_and_update(
            {"_id": ObjectId(incident_id)},
            {"$set": update_data},
            return_document=True
        )
    except:
        raise HTTPException(status_code=400, detail="Invalid incident ID format")
    
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    result["_id"] = str(result["_id"])
    return result


@app.delete("/incidents/{incident_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Incidents"])
async def delete_incident(incident_id: str):
    """Delete an incident"""
    collection = get_collection()
    
    try:
        result = await collection.delete_one({"_id": ObjectId(incident_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid incident ID format")
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return None


# Search Endpoint

@app.post("/incidents/search", response_model=List[IncidentResponse], tags=["Search"])
async def search_incidents(search_query: SearchQuery):
    """
    Search incidents using text search
    
    Searches across description, location, animals, and source fields
    """
    collection = get_collection()
    
    # Text search query
    query = {"$text": {"$search": search_query.query}}
    
    # Add additional filters if provided
    if search_query.filters:
        query.update(search_query.filters)
    
    # Execute search
    cursor = collection.find(query).skip(search_query.skip).limit(search_query.limit)
    incidents = await cursor.to_list(length=search_query.limit)
    
    # Convert ObjectId to string
    for incident in incidents:
        incident["_id"] = str(incident["_id"])
    
    return incidents


# Statistics Endpoint

@app.get("/statistics", response_model=StatisticsResponse, tags=["Analytics"])
async def get_statistics():
    """
    Get overall statistics and analytics
    """
    collection = get_collection()
    
    # Total incidents
    total = await collection.count_documents({})
    
    # By status
    status_pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    status_result = await collection.aggregate(status_pipeline).to_list(None)
    by_status = {item["_id"]: item["count"] for item in status_result}
    
    # By month
    month_pipeline = [
        {"$group": {
            "_id": {"$substr": ["$date", 0, 7]},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": -1}},
        {"$limit": 12}
    ]
    month_result = await collection.aggregate(month_pipeline).to_list(None)
    by_month = {item["_id"]: item["count"] for item in month_result}
    
    # Top locations
    location_pipeline = [
        {"$group": {"_id": "$location", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    location_result = await collection.aggregate(location_pipeline).to_list(None)
    top_locations = [{"location": item["_id"], "count": item["count"]} for item in location_result]
    
    # Top animals
    animals_pipeline = [
        {"$group": {"_id": "$animals", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    animals_result = await collection.aggregate(animals_pipeline).to_list(None)
    top_animals = [{"animal": item["_id"], "count": item["count"]} for item in animals_result]
    
    # Recent incidents
    recent_cursor = collection.find().sort("created_at", -1).limit(5)
    recent_incidents = await recent_cursor.to_list(length=5)
    for incident in recent_incidents:
        incident["_id"] = str(incident["_id"])
    
    return {
        "total_incidents": total,
        "by_status": by_status,
        "by_month": by_month,
        "top_locations": top_locations,
        "top_animals": top_animals,
        "recent_incidents": recent_incidents
    }


# Bulk Upload Endpoint

@app.post("/incidents/bulk-upload", response_model=BulkUploadResponse, tags=["Bulk Operations"])
async def bulk_upload(file: UploadFile = File(...), use_ai: bool = Query(False)):
    """
    Bulk upload incidents from Excel/CSV file
    
    - **file**: Excel (.xlsx) or CSV file
    - **use_ai**: If True, AI will process each incident (slower but adds AI features)
    """
    collection = get_collection()
    
    # Read file
    contents = await file.read()
    
    try:
        # Try reading as Excel
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(contents))
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="File must be .xlsx or .csv")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    
    # Validate required columns
    required_columns = ['date', 'location', 'animals', 'description', 'source']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing_columns)}"
        )
    
    # Prepare records
    incidents = df.to_dict('records')
    inserted_count = 0
    failed_count = 0
    errors = []
    
    for idx, incident in enumerate(incidents):
        try:
            incident["created_at"] = datetime.utcnow()
            incident["updated_at"] = datetime.utcnow()
            
            # Set default status if not provided
            if 'status' not in incident or pd.isna(incident['status']):
                incident['status'] = 'Reported'
            
            # AI processing if enabled
            if use_ai and 'description' in incident:
                try:
                    entities = await extract_entities_from_text(str(incident['description']))
                    incident["extracted_animals"] = entities.get("animals", [])
                    incident["extracted_location"] = entities.get("location")
                    incident["keywords"] = entities.get("keywords", [])
                    
                    summary = await generate_summary(str(incident['description']))
                    incident["ai_summary"] = summary
                except:
                    pass  # Continue without AI features
            
            # Insert
            await collection.insert_one(incident)
            inserted_count += 1
            
        except Exception as e:
            failed_count += 1
            errors.append(f"Row {idx + 1}: {str(e)}")
    
    return {
        "success": True,
        "total_records": len(incidents),
        "inserted_records": inserted_count,
        "failed_records": failed_count,
        "errors": errors if errors else None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)