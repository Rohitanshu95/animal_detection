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

from dotenv import load_dotenv
load_dotenv()

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
from ai.filter_utils import clean_extracted_animals
from tag_assigner import assign_tags_to_incident

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
    await insert_sample_data()


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
            raw_animals = entities.get("animals", [])
            incident_dict["extracted_animals"] = clean_extracted_animals(raw_animals)
            incident_dict["extracted_location"] = entities.get("location")
            incident_dict["keywords"] = entities.get("keywords", [])
            
            # Auto-populate animals field if missing
            if not incident_dict.get("animals") and entities.get("animals"):
                # Take the first extracted animal/product as the main category
                incident_dict["animals"] = entities["animals"][0]
            
            # Generate AI summary
            summary = await generate_summary(incident.description)
            incident_dict["ai_summary"] = summary
            
        except Exception as e:
            print(f"⚠️ AI processing failed: {e}")
            # Continue without AI features
            
    # Default 'animals' if still missing
    if not incident_dict.get("animals"):
        incident_dict["animals"] = "Unknown"

    # Auto-assign tags based on incident content
    assigned_tags = assign_tags_to_incident(incident_dict)
    if assigned_tags:
        incident_dict["tags"] = assigned_tags

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
    query: Optional[str] = None,
    status: Optional[List[str]] = Query(None),
    species: Optional[List[str]] = Query(None),
    location: Optional[List[str]] = Query(None),
    tags: Optional[List[str]] = Query(None),
    year: Optional[str] = None,
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """
    Get all incidents with optional filters and sorting
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **query**: Text search query
    - **status**: Filter by status (List)
    - **species**: Filter by species (List)
    - **location**: Filter by location (List, partial match supported)
    - **sort_order**: Sort by created_at
    """
    collection = get_collection()
    
    # Build query conditions
    conditions = []
    
    # Text Search (Global)
    if query:
        search_regex = {"$regex": query, "$options": "i"}
        conditions.append({
            "$or": [
                {"description": search_regex},
                {"location": search_regex},
                {"animals": search_regex},
                {"extracted_animals": search_regex},
                {"source": search_regex}
            ]
        })

    # Filters
    if status:
        conditions.append({"status": {"$in": status}})

    if species:
        # Normalize species to title case for exact matching on extracted_animals array
        normalized_species = [s.strip().title() for s in species]
        conditions.append({"extracted_animals": {"$in": normalized_species}})

    if location:
        # Support partial matching with case-insensitive regex
        conditions.append({
            "$or": [{"location": {"$regex": loc, "$options": "i"}} for loc in location]
        })
    if tags:
        conditions.append({"tags": {"$in": tags}})

    if year:
        # Use proper date range queries for year filtering
        start_date = f"{year}-01-01"
        end_date = f"{int(year) + 1}-01-01"
        conditions.append({"date": {"$gte": start_date, "$lt": end_date}})

    if date_from or date_to:
        date_query = {}
        if date_from:
            date_query["$gte"] = date_from
        if date_to:
            date_query["$lte"] = date_to
        conditions.append({"date": date_query})
    
    # Combine conditions
    mongo_query = {"$and": conditions} if conditions else {}
    
    # Determine sort direction
    direction = -1 if sort_order == "desc" else 1

    # Execute query
    cursor = collection.find(mongo_query).skip(skip).limit(limit).sort("created_at", direction)
    incidents = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for incident in incidents:
        incident["_id"] = str(incident["_id"])
    
    return incidents



@app.get("/incidents/filters", tags=["Incidents"])
async def get_incident_filters():
    """Get dynamic filter options and counts"""
    collection = get_collection()
    
    pipeline = [
        {
            "$facet": {
                "status_counts": [
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ],
                "location_counts": [
                    {"$group": {"_id": "$location", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 50}
                ],
                "species_counts": [
                    {"$unwind": {"path": "$extracted_animals", "preserveNullAndEmptyArrays": True}},
                    {"$group": {"_id": "$extracted_animals", "count": {"$sum": 1}}},
                    {"$match": {"_id": {"$ne": None}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 50}
                ],
                "tags_counts": [
                    {"$unwind": {"path": "$tags", "preserveNullAndEmptyArrays": True}},
                    {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
                    {"$match": {"_id": {"$ne": None}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 50}
                ],
                "year_counts": [
                    {
                        "$project": {
                            "year": {"$substr": ["$date", 0, 4]}
                        }
                    },
                    {"$group": {"_id": "$year", "count": {"$sum": 1}}},
                    {"$sort": {"_id": -1}}
                ]
            }
        }
    ]
    
    # Predefined tags for wildlife incidents
    predefined_tags = [
        "Animal Hunting", "Animal Killing", "Poaching", "Animal Smuggling",
        "Illegal Wildlife Trade", "Animal Capture", "Animal Injury/Cruelty",
        "Seizure of Animal Products", "Illegal Weapon Usage", "Forest Law Violation",
        "Arrest/Legal Action", "Rescue and Rehabilitation"
    ]

    try:
        result = await collection.aggregate(pipeline).to_list(length=1)
        stats = result[0] if result else {}

        # Get actual tag counts from database
        actual_tags = {item["_id"]: item["count"] for item in stats.get("tags_counts", [])}

        # Merge predefined tags with actual counts (use 0 for predefined tags not in database)
        tags_stats = {}
        for tag in predefined_tags:
            tags_stats[tag] = actual_tags.get(tag, 0)

        return {
            "status": {item["_id"]: item["count"] for item in stats.get("status_counts", [])},
            "location": {item["_id"]: item["count"] for item in stats.get("location_counts", [])},
            "species": {item["_id"]: item["count"] for item in stats.get("species_counts", [])},
            "tags": tags_stats,
            "years": {item["_id"]: item["count"] for item in stats.get("year_counts", [])}
        }
    except Exception as e:
        print(f"Filter aggregation error: {e}")
        return {"status": {}, "location": {}, "species": {}, "tags": {}, "years": {}}


@app.get("/incidents/filters/dynamic", tags=["Incidents"])
async def get_dynamic_incident_filters(
    status: Optional[List[str]] = Query(None),
    species: Optional[List[str]] = Query(None),
    location: Optional[List[str]] = Query(None),
    tags: Optional[List[str]] = Query(None),
    year: Optional[str] = None
):
    """Get dynamic filter options and counts based on current filter selections"""
    collection = get_collection()

    # Build match conditions from current filters
    match_conditions = []

    if status:
        match_conditions.append({"status": {"$in": status}})

    if species:
        normalized_species = [s.strip().title() for s in species]
        match_conditions.append({"extracted_animals": {"$in": normalized_species}})

    if location:
        match_conditions.append({
            "$or": [{"location": {"$regex": loc, "$options": "i"}} for loc in location]
        })

    if tags:
        match_conditions.append({"tags": {"$in": tags}})

    if year:
        start_date = f"{year}-01-01"
        end_date = f"{int(year) + 1}-01-01"
        match_conditions.append({"date": {"$gte": start_date, "$lt": end_date}})

    # Base match stage
    match_stage = {"$match": {"$and": match_conditions}} if match_conditions else {}

    pipeline = [
        match_stage,
        {
            "$facet": {
                "status_counts": [
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 50}
                ],
                "location_counts": [
                    {"$group": {"_id": "$location", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 50}
                ],
                "species_counts": [
                    {"$unwind": {"path": "$extracted_animals", "preserveNullAndEmptyArrays": True}},
                    {"$group": {"_id": "$extracted_animals", "count": {"$sum": 1}}},
                    {"$match": {"_id": {"$ne": None}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 50}
                ],
                "tags_counts": [
                    {"$unwind": {"path": "$tags", "preserveNullAndEmptyArrays": True}},
                    {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
                    {"$match": {"_id": {"$ne": None}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 50}
                ],
                "year_counts": [
                    {
                        "$project": {
                            "year": {"$substr": ["$date", 0, 4]}
                        }
                    },
                    {"$group": {"_id": "$year", "count": {"$sum": 1}}},
                    {"$sort": {"_id": -1}}
                ]
            }
        }
    ]

    # Predefined tags for wildlife incidents
    predefined_tags = [
        "Animal Hunting", "Animal Killing", "Poaching", "Animal Smuggling",
        "Illegal Wildlife Trade", "Animal Capture", "Animal Injury/Cruelty",
        "Seizure of Animal Products", "Illegal Weapon Usage", "Forest Law Violation",
        "Arrest/Legal Action", "Rescue and Rehabilitation"
    ]

    try:
        result = await collection.aggregate(pipeline).to_list(length=1)
        stats = result[0] if result else {}

        # Get actual tag counts from database
        actual_tags = {item["_id"]: item["count"] for item in stats.get("tags_counts", [])}

        # Merge predefined tags with actual counts
        tags_stats = {}
        for tag in predefined_tags:
            tags_stats[tag] = actual_tags.get(tag, 0)

        return {
            "status": {item["_id"]: item["count"] for item in stats.get("status_counts", [])},
            "location": {item["_id"]: item["count"] for item in stats.get("location_counts", [])},
            "species": {item["_id"]: item["count"] for item in stats.get("species_counts", [])},
            "tags": tags_stats,
            "years": {item["_id"]: item["count"] for item in stats.get("year_counts", [])}
        }
    except Exception as e:
        print(f"Dynamic filter aggregation error: {e}")
        return {"status": {}, "location": {}, "species": {}, "tags": {}, "years": {}}


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
async def get_statistics(
    location: Optional[str] = None,
    species: Optional[str] = None,
    division: Optional[str] = None,
    year: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """
    Get overall statistics and analytics with optional filters

    - **location**: Filter by location (partial match)
    - **species**: Filter by species (partial match)
    - **division**: Filter by division (partial match)
    - **year**: Filter by year (YYYY format)
    - **date_from**: Filter incidents from this date (YYYY-MM-DD)
    - **date_to**: Filter incidents to this date (YYYY-MM-DD)
    """
    collection = get_collection()

    # Build base query for filtering
    base_query = {}
    conditions = []

    if location:
        conditions.append({"location": {"$regex": location, "$options": "i"}})

    if division:
        conditions.append({"location": {"$regex": division, "$options": "i"}})

    if species:
        conditions.append({
            "$or": [
                {"animals": {"$regex": species, "$options": "i"}},
                {"extracted_animals": {"$regex": species, "$options": "i"}}
            ]
        })

    if year:
        # Use proper date range queries for year filtering
        start_date = f"{year}-01-01"
        end_date = f"{int(year) + 1}-01-01"
        conditions.append({"date": {"$gte": start_date, "$lt": end_date}})

    if date_from or date_to:
        date_query = {}
        if date_from:
            date_query["$gte"] = date_from
        if date_to:
            date_query["$lte"] = date_to
        conditions.append({"date": date_query})

    if conditions:
        base_query = {"$and": conditions}

    # Total incidents (filtered)
    total = await collection.count_documents(base_query)

    # By status (filtered)
    status_pipeline = [
        {"$match": base_query},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    status_result = await collection.aggregate(status_pipeline).to_list(None)
    by_status = {item["_id"]: item["count"] for item in status_result}

    # By month (filtered)
    month_pipeline = [
        {"$match": base_query},
        {"$group": {
            "_id": {"$substr": ["$date", 0, 7]},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": -1}},
        {"$limit": 12}
    ]
    month_result = await collection.aggregate(month_pipeline).to_list(None)
    by_month = {item["_id"]: item["count"] for item in month_result}

    # Top locations (filtered)
    location_pipeline = [
        {"$match": base_query},
        {"$group": {"_id": "$location", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    location_result = await collection.aggregate(location_pipeline).to_list(None)
    top_locations = [{"location": item["_id"], "count": item["count"]} for item in location_result]

    # Top animals (filtered)
    animals_pipeline = [
        {"$match": base_query},
        {"$group": {"_id": "$animals", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    animals_result = await collection.aggregate(animals_pipeline).to_list(None)
    top_animals = [{"animal": item["_id"], "count": item["count"]} for item in animals_result]

    # Recent incidents (filtered)
    recent_cursor = collection.find(base_query).sort("created_at", -1).limit(5)
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
    required_columns = ['date', 'location', 'description', 'source']
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
                    raw_animals = entities.get("animals", [])
                    incident["extracted_animals"] = clean_extracted_animals(raw_animals)
                    incident["extracted_location"] = entities.get("location")
                    incident["keywords"] = entities.get("keywords", [])
                    
                    # Auto-populate animals if missing
                    if ('animals' not in incident or pd.isna(incident['animals'])) and entities.get("animals"):
                         incident["animals"] = entities["animals"][0]
                    
                    summary = await generate_summary(str(incident['description']))
                    incident["ai_summary"] = summary
                except:
                    pass  # Continue without AI features
            
            # Default 'animals' if still missing or NaN
            if 'animals' not in incident or pd.isna(incident['animals']):
                incident['animals'] = "Unknown"

            # Auto-assign tags based on incident content
            assigned_tags = assign_tags_to_incident(incident)
            if assigned_tags:
                incident["tags"] = assigned_tags

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


@app.post("/incidents/batch", response_model=BulkUploadResponse, tags=["Bulk Operations"])
async def batch_create_incidents(incidents: List[IncidentCreate]):
    """
    Batch create incidents from JSON list
    """
    collection = get_collection()
    inserted_count = 0
    failed_count = 0
    errors = []
    
    for idx, incident_data in enumerate(incidents):
        try:
            incident_dict = incident_data.dict()
            incident_dict["created_at"] = datetime.utcnow()
            incident_dict["updated_at"] = datetime.utcnow()
            
            # Populate extracted_animals for filters
            if incident_dict.get("animals"):
                raw_animals = [a.strip() for a in incident_dict["animals"].split(",") if a.strip()]
                incident_dict["extracted_animals"] = clean_extracted_animals(raw_animals)

            # Auto-assign tags based on incident content
            assigned_tags = assign_tags_to_incident(incident_dict)
            if assigned_tags:
                incident_dict["tags"] = assigned_tags

            # Insert
            await collection.insert_one(incident_dict)
            inserted_count += 1
            
        except Exception as e:
            failed_count += 1
            errors.append(f"Item {idx + 1}: {str(e)}")
            
    return {
        "success": True,
        "total_records": len(incidents),
        "inserted_records": inserted_count,
        "failed_records": failed_count,
        "errors": errors if errors else None
    }




@app.post("/excel/parse", tags=["Excel Upload"])
async def parse_excel(file: UploadFile = File(...)):
    """
    Parse Excel file and extract incidents
    """
    try:
        from ai.excel_agent import parse_excel_file, validate_incidents
        
        # Read file content
        content = await file.read()
        
        # Parse Excel
        result = parse_excel_file(content)
        
        if result['success']:
            # Validate incidents
            incidents = validate_incidents(result['incidents'])
            result['incidents'] = incidents
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel parsing failed: {str(e)}")


@app.post("/excel/enrich", tags=["Excel Upload"])
async def enrich_incidents(data: dict):
    """
    Enrich incidents with AI-extracted information
    """
    try:
        from ai.enrichment_agent import enrich_multiple_incidents
        
        incidents = data.get('incidents', [])
        
        if not incidents:
            raise HTTPException(status_code=400, detail="No incidents provided")
        
        # Enrich with AI
        enriched = enrich_multiple_incidents(incidents)

        # Clean extracted_animals for enriched incidents
        for incident in enriched:
            if "extracted_animals" in incident:
                incident["extracted_animals"] = clean_extracted_animals(incident["extracted_animals"])

        # Auto-assign tags to enriched incidents
        for incident in enriched:
            assigned_tags = assign_tags_to_incident(incident)
            if assigned_tags:
                incident["tags"] = assigned_tags

        return {
            "success": True,
            "incidents": enriched,
            "count": len(enriched)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")


# Assistant Endpoints
@app.post("/assistant/chat", tags=["Assistant"])
async def assistant_chat(data: dict):
    """
    Chat with AI assistant
    
    Expected input:
    {
        "message": "User question",
        "chat_history": [{"role": "user", "content": "..."}, ...]
    }
    """
    try:
        from ai.assistant_agent import create_assistant
        
        message = data.get('message')
        chat_history = data.get('chat_history', [])
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get database collection
        collection = get_collection()
        
        # Create assistant
        assistant = create_assistant(collection)
        
        # Get response (awaiting the async chat method)
        response = await assistant.chat(message, chat_history)
        # print(response)
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Assistant error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)