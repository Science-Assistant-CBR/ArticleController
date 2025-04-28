from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NewsArticleFilter(BaseModel):
    title: Optional[str] = Field(
        default=None, description="Filter by article title (partial match)"
    )
    source_name: Optional[str] = Field(
        default=None, description="Filter by source name"
    )
    start_date: Optional[datetime] = Field(
        default=None, description="Start of publication date range"
    )
    end_date: Optional[datetime] = Field(
        default=None, description="End of publication date range"
    )
    section: Optional[str] = Field(
        default=None, description="Filter by article section"
    )
    categories: Optional[List[str]] = Field(
        default=None, description="List of categories to filter"
    )
    order_by: Optional[str] = Field(
        default="publication_datetime",
        description="Sort field: 'publication_datetime' or 'id'",
    )
    limit: Optional[int] = Field(default=10, description="Limit the number of items")

    class Config:
        schema_extra = {
            "example": {
                "title": "научный центр",
                "source_name": "РИА Новости",
                "start_date": "2025-01-01T00:00:00Z",
                "end_date": "2025-04-12T23:59:59Z",
                "section": "Общество",
                "categories": ["наука", "образование"],
                "order_by": "publication_datetime",
                "limit": 10,
            }
        }

