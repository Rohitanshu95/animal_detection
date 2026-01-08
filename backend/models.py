"""
Data models for Wildlife Smuggling Tracker
Defines the schema for incident documents
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class IncidentBase(BaseModel):
    """Base incident model with common fields"""
    date: str = Field(..., description="Date of incident in YYYY-MM-DD format")
    location: str = Field(..., description="Location of incident (city, state, country)")
    animals: str = Field(..., description="Type of animal or wildlife product")
    quantity: Optional[str] = Field(None, description="Quantity seized or reported")
    description: str = Field(..., description="Detailed description of the incident")
    source: str = Field(..., description="Information source or reporting agency")
    status: str = Field(default="Reported", description="Current status of the case")
    
    # Optional fields
    suspects: Optional[str] = Field(None, description="Number of suspects or arrests")
    vehicle_info: Optional[str] = Field(None, description="Vehicle information if applicable")
    estimated_value: Optional[str] = Field(None, description="Estimated value in local currency")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2024-12-15",
                "location": "Mumbai Port, India",
                "animals": "Pangolin scales",
                "quantity": "150 kg",
                "description": "Customs officials seized 150kg of pangolin scales hidden in seafood containers",
                "source": "Wildlife Crime Control Bureau",
                "status": "Investigated",
                "suspects": "3 arrested",
                "estimated_value": "₹50,00,000"
            }
        }


class IncidentCreate(IncidentBase):
    """Model for creating new incidents"""
    pass


class IncidentUpdate(BaseModel):
    """Model for updating incidents - all fields optional"""
    date: Optional[str] = None
    location: Optional[str] = None
    animals: Optional[str] = None
    quantity: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    suspects: Optional[str] = None
    vehicle_info: Optional[str] = None
    estimated_value: Optional[str] = None
    notes: Optional[str] = None


class IncidentInDB(IncidentBase):
    """Model for incident stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # AI-generated fields
    extracted_animals: Optional[List[str]] = Field(None, description="AI-extracted animal species")
    extracted_location: Optional[str] = Field(None, description="AI-standardized location")
    ai_summary: Optional[str] = Field(None, description="AI-generated summary")
    keywords: Optional[List[str]] = Field(None, description="Extracted keywords")
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class IncidentResponse(IncidentBase):
    """Model for API responses"""
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    extracted_animals: Optional[List[str]] = None
    extracted_location: Optional[str] = None
    ai_summary: Optional[str] = None
    keywords: Optional[List[str]] = None
    
    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class SearchQuery(BaseModel):
    """Model for search queries"""
    query: str = Field(..., description="Search query string")
    filters: Optional[dict] = Field(None, description="Additional filters")
    limit: int = Field(default=10, ge=1, le=100, description="Maximum results to return")
    skip: int = Field(default=0, ge=0, description="Number of results to skip")


class BulkUploadResponse(BaseModel):
    """Response model for bulk uploads"""
    success: bool
    total_records: int
    inserted_records: int
    failed_records: int
    errors: Optional[List[str]] = None


class StatisticsResponse(BaseModel):
    """Response model for statistics"""
    total_incidents: int
    by_status: dict
    by_month: dict
    top_locations: List[dict]
    top_animals: List[dict]
    recent_incidents: List[IncidentResponse]