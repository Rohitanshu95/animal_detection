"""
Database Query Tools for LangGraph Agent
Async-native tools with Pydantic validation
"""

from typing import List, Dict, Optional, Any, Type
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool, StructuredTool

class SearchInput(BaseModel):
    query: Optional[str] = Field(None, description="Text search across description, animals, and location")
    location: Optional[str] = Field(None, description="Filter by location name")
    animals: Optional[str] = Field(None, description="Filter by animal species")
    status: Optional[str] = Field(None, description="Filter by status (e.g., 'Reported', 'Investigated')")
    date_from: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format")
    date_to: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    limit: int = Field(10, description="Maximum number of results to return")

class StatisticsInput(BaseModel):
    pass

class TrendsInput(BaseModel):
    field: str = Field(..., description="Field to analyze (e.g., 'animals', 'location', 'status')")
    period_days: int = Field(30, description="Number of days to analyze back from today")

class AggregateInput(BaseModel):
    field: str = Field(..., description="Field to aggregate by (e.g., 'animals', 'location')")
    limit: int = Field(10, description="Number of top results to return")

class DatabaseTools:
    """Tools for querying MongoDB incident database"""
    
    def __init__(self, collection):
        self.collection = collection

    async def search_incidents(self, **kwargs) -> List[Dict]:
        """Search incidents with flexible filtering"""
        query = kwargs.get('query')
        location = kwargs.get('location')
        animals = kwargs.get('animals')
        status = kwargs.get('status')
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        limit = kwargs.get('limit', 10)

        filter_query = {}
        
        # Text search
        if query:
            filter_query["$or"] = [
                {"description": {"$regex": query, "$options": "i"}},
                {"animals": {"$regex": query, "$options": "i"}},
                {"location": {"$regex": query, "$options": "i"}},
            ]
        
        # Specific filters
        if location:
            filter_query["location"] = {"$regex": location, "$options": "i"}
        
        if animals:
            filter_query["animals"] = {"$regex": animals, "$options": "i"}
        
        if status:
            filter_query["status"] = {"$regex": status, "$options": "i"}
        
        # Date range
        if date_from or date_to:
            filter_query["date"] = {}
            if date_from:
                filter_query["date"]["$gte"] = date_from
            if date_to:
                filter_query["date"]["$lte"] = date_to
        
        # Execute query
        cursor = self.collection.find(filter_query).limit(limit).sort("created_at", -1)
        # to_list is a coroutine in Motor
        results = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for result in results:
            result["_id"] = str(result["_id"])
        
        return results

    async def get_statistics(self, **kwargs) -> Dict[str, Any]:
        """Get overall statistics about incidents"""
        # Total count
        total = await self.collection.count_documents({})
        
        # By status
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_cursor = self.collection.aggregate(status_pipeline)
        by_status = {doc["_id"]: doc["count"] async for doc in status_cursor}
        
        # By animal type (top 10)
        animals_pipeline = [
            {"$group": {"_id": "$animals", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        animals_cursor = self.collection.aggregate(animals_pipeline)
        top_animals = [{"animal": doc["_id"], "count": doc["count"]} async for doc in animals_cursor]
        
        # By location (top 10)
        location_pipeline = [
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        location_cursor = self.collection.aggregate(location_pipeline)
        top_locations = [{"location": doc["_id"], "count": doc["count"]} async for doc in location_cursor]
        
        return {
            "total_incidents": total,
            "by_status": by_status,
            "top_animals": top_animals,
            "top_locations": top_locations
        }

    async def calculate_trends(self, field: str, period_days: int = 30) -> Dict:
        """Calculate trends for a specific field"""
        cutoff_date = (datetime.utcnow() - timedelta(days=period_days)).strftime('%Y-%m-%d')
        
        # Current period
        current_filter = {"date": {"$gte": cutoff_date}}
        if field == "animals":
             group_field = "$animals"
        elif field == "location":
             group_field = "$location"
        else:
             group_field = f"${field}"

        current_pipeline = [
            {"$match": current_filter},
            {"$group": {"_id": group_field, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        current_cursor = self.collection.aggregate(current_pipeline)
        current_counts = {doc["_id"]: doc["count"] async for doc in current_cursor}
        
        # Previous period (simple comparison)
        prev_cutoff = (datetime.utcnow() - timedelta(days=period_days * 2)).strftime('%Y-%m-%d')
        prev_filter = {
            "date": {
                "$gte": prev_cutoff,
                "$lt": cutoff_date
            }
        }
        prev_pipeline = [
            {"$match": prev_filter},
            {"$group": {"_id": group_field, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        prev_cursor = self.collection.aggregate(prev_pipeline)
        prev_counts = {doc["_id"]: doc["count"] async for doc in prev_cursor}
        
        trends = {}
        for key in set(list(current_counts.keys()) + list(prev_counts.keys())):
            current = current_counts.get(key, 0)
            previous = prev_counts.get(key, 0)
            change = current - previous
            
            trends[key] = {
                "current": current,
                "previous": previous,
                "change": change
            }
        
        return trends

    async def aggregate_by_field(self, field: str, limit: int = 10) -> List[Dict]:
        """Aggregate incidents by a specific field"""
        pipeline = [
            {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = [{"value": doc["_id"], "count": doc["count"]} async for doc in cursor]
        return results

def create_langchain_tools(collection) -> List[BaseTool]:
    """Create a list of StructuredTools for the agent"""
    db_tools = DatabaseTools(collection)

    return [
        StructuredTool.from_function(
            func=None,
            coroutine=db_tools.search_incidents,
            name="search_incidents",
            description="Search wildlife incidents by query, location, animals, status, or date range.",
            args_schema=SearchInput
        ),
        StructuredTool.from_function(
            func=None,
            coroutine=db_tools.get_statistics,
            name="get_statistics",
            description="Get overall statistics about incidents including totals, top animals, and top locations.",
            args_schema=StatisticsInput
        ),
        StructuredTool.from_function(
            func=None,
            coroutine=db_tools.calculate_trends,
            name="calculate_trends",
            description="Calculate trends for a specific field (animals, location) over time.",
            args_schema=TrendsInput
        ),
        StructuredTool.from_function(
            func=None,
            coroutine=db_tools.aggregate_by_field,
            name="aggregate_by_field",
            description="Aggregate incidents by a specific field to see top values.",
            args_schema=AggregateInput
        )
    ]
