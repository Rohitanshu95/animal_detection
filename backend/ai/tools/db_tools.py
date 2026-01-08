"""
Database Query Tools for LangGraph Agent
Tools for querying and analyzing wildlife incident data
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from bson import ObjectId
import re


class DatabaseTools:
    """Tools for querying MongoDB incident database"""
    
    def __init__(self, collection):
        """
        Initialize with MongoDB collection
        
        Args:
            collection: Motor AsyncIOMotorCollection instance
        """
        self.collection = collection
    
    async def search_incidents(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        animals: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search incidents with flexible filtering
        
        Args:
            query: Text search across description, animals, location
            location: Filter by location
            animals: Filter by animal type
            status: Filter by status
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            limit: Maximum results
            
        Returns:
            List of matching incidents
        """
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
        results = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for result in results:
            result["_id"] = str(result["_id"])
        
        return results
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics about incidents
        
        Returns:
            Dictionary with various statistics
        """
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
        
        # Recent incidents
        recent_cursor = self.collection.find().sort("created_at", -1).limit(5)
        recent = await recent_cursor.to_list(length=5)
        for r in recent:
            r["_id"] = str(r["_id"])
        
        return {
            "total_incidents": total,
            "by_status": by_status,
            "top_animals": top_animals,
            "top_locations": top_locations,
            "recent_incidents": recent
        }
    
    async def get_time_series(self, days: int = 30) -> Dict[str, int]:
        """
        Get incident counts by date for time series analysis
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary of {date: count}
        """
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        pipeline = [
            {"$match": {"date": {"$gte": cutoff_date}}},
            {"$group": {"_id": "$date", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        time_series = {doc["_id"]: doc["count"] async for doc in cursor}
        
        return time_series
    
    async def aggregate_by_field(self, field: str, limit: int = 10) -> List[Dict]:
        """
        Aggregate incidents by a specific field
        
        Args:
            field: Field name to aggregate by (e.g., 'animals', 'location', 'status')
            limit: Maximum results
            
        Returns:
            List of {field_value, count} dictionaries
        """
        pipeline = [
            {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = [{"value": doc["_id"], "count": doc["count"]} async for doc in cursor]
        
        return results
    
    async def find_similar_incidents(
        self,
        incident_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Find incidents similar to a given incident
        
        Args:
            incident_id: ID of the reference incident
            limit: Maximum results
            
        Returns:
            List of similar incidents
        """
        # Get reference incident
        ref_incident = await self.collection.find_one({"_id": ObjectId(incident_id)})
        
        if not ref_incident:
            return []
        
        # Find similar based on animals and location
        filter_query = {
            "_id": {"$ne": ObjectId(incident_id)},
            "$or": [
                {"animals": ref_incident.get("animals")},
                {"location": ref_incident.get("location")}
            ]
        }
        
        cursor = self.collection.find(filter_query).limit(limit)
        results = await cursor.to_list(length=limit)
        
        for result in results:
            result["_id"] = str(result["_id"])
        
        return results
    
    async def calculate_trends(self, field: str, period_days: int = 30) -> Dict:
        """
        Calculate trends for a specific field
        
        Args:
            field: Field to analyze trends for
            period_days: Number of days to analyze
            
        Returns:
            Trend analysis results
        """
        cutoff_date = (datetime.utcnow() - timedelta(days=period_days)).strftime('%Y-%m-%d')
        
        # Current period
        current_filter = {"date": {"$gte": cutoff_date}}
        current_pipeline = [
            {"$match": current_filter},
            {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        current_cursor = self.collection.aggregate(current_pipeline)
        current_counts = {doc["_id"]: doc["count"] async for doc in current_cursor}
        
        # Previous period
        prev_cutoff = (datetime.utcnow() - timedelta(days=period_days * 2)).strftime('%Y-%m-%d')
        prev_filter = {
            "date": {
                "$gte": prev_cutoff,
                "$lt": cutoff_date
            }
        }
        prev_pipeline = [
            {"$match": prev_filter},
            {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        prev_cursor = self.collection.aggregate(prev_pipeline)
        prev_counts = {doc["_id"]: doc["count"] async for doc in prev_cursor}
        
        # Calculate changes
        trends = {}
        for key in set(list(current_counts.keys()) + list(prev_counts.keys())):
            current = current_counts.get(key, 0)
            previous = prev_counts.get(key, 0)
            change = current - previous
            change_pct = (change / previous * 100) if previous > 0 else 0
            
            trends[key] = {
                "current": current,
                "previous": previous,
                "change": change,
                "change_percent": round(change_pct, 2)
            }
        
        return trends


# LangChain tool wrappers for LangGraph
def create_langchain_tools(collection):
    """
    Create LangChain-compatible tools from DatabaseTools
    
    Args:
        collection: MongoDB collection
        
    Returns:
        List of LangChain tools
    """
    from langchain.tools import Tool
    
    db_tools = DatabaseTools(collection)
    
    tools = [
        Tool(
            name="search_incidents",
            description="Search wildlife incidents by query, location, animals, status, or date range. Returns matching incidents.",
            func=lambda x: db_tools.search_incidents(**eval(x) if isinstance(x, str) else x),
        ),
        Tool(
            name="get_statistics",
            description="Get overall statistics about incidents including totals, top animals, top locations, and status breakdown.",
            func=lambda x: db_tools.get_statistics(),
        ),
        Tool(
            name="get_time_series",
            description="Get incident counts by date for time series analysis. Useful for trend visualization.",
            func=lambda x: db_tools.get_time_series(days=int(x) if x else 30),
        ),
        Tool(
            name="aggregate_by_field",
            description="Aggregate incidents by a specific field (animals, location, status). Returns top values and counts.",
            func=lambda x: db_tools.aggregate_by_field(**eval(x) if isinstance(x, str) else x),
        ),
        Tool(
            name="calculate_trends",
            description="Calculate trends for a specific field over time. Compares current period to previous period.",
            func=lambda x: db_tools.calculate_trends(**eval(x) if isinstance(x, str) else x),
        ),
    ]
    
    return tools
