from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ScienceArticleFilter(BaseModel):
    skip: int = Field(default=0, ge=0, description="Number of records to skip for pagination")
    limit: int = Field(default=20, gt=0, le=100, description="Maximum number of records to return")
    title: Optional[str] = Field(default=None, description="Filter by article title (partial match)")
    sphere: Optional[str] = Field(default=None, description="sphere - analysis or science")
    source_name: Optional[str] = Field(default=None, description="Filter by source name")
    start_date: Optional[datetime] = Field(default=None, description="Start of publication date range")
    end_date: Optional[datetime] = Field(default=None, description="End of publication date range")
    section: Optional[str] = Field(default=None, description="Filter by article section")
    categories: Optional[List[str]] = Field(default=None, description="List of categories to filter")
    order_by: Optional[str] = Field(default="publication_datetime", description="Sort field: 'publication_datetime' or 'id'")
    id: Optional[int] = Field(default=None, description="Get a particular one by article ID")
    class Config:
        schema_extra = {
            "example": {
                "title": "AI in Education",
                "sphere": "analysis",
                "source_name": "Nature",
                "start_date": "2024-12-01T00:00:00",
                "end_date": "2025-04-10T23:59:59",
                "section": "Technology",
                "categories": ["AI", "Education"],
                "order_by": "publication_datetime"
            }
        }