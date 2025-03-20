from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# TODO:
#  на бэкенде, который отвечает за работу с бд
#  в модель дайджеста надо добавить строковое поле "summary"

# добавил в каждый класс (и example)

class DigestBase(BaseModel):
    """Base schema for digest data"""

    title: Optional[str] = None
    body: str
    start_datetime: datetime
    end_datetime: datetime
    article_ids: Optional[List[str]] = None
    summary: str


class DigestCreate(DigestBase):
    """Schema for creating a new digest"""

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Daily News Digest",
                "body": "Summary of today's news...",
                "start_datetime": "2024-01-01T00:00:00",
                "end_datetime": "2024-01-01T23:59:59",
                "article_ids": ["article1", "article2"],
                "summary": "In short, today's news...",
            }
        }


class DigestUpdate(BaseModel):
    """Schema for updating an existing digest"""

    title: Optional[str] = None
    body: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    article_ids: Optional[List[str]] = None
    summary: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Daily News Digest",
                "body": "Updated summary of today's news...",
                "start_datetime": "2024-01-01T00:00:00",
                "end_datetime": "2024-01-01T23:59:59",
                "article_ids": ["article1", "article2", "article3"],
                "summary": "In short, today's news...",
            }
        }


class DigestResponse(DigestBase):
    """Schema for digest responses"""

    id: int
    s3_url: str

    class Config:
        from_attributes = True  # Allows Pydantic to convert SQLAlchemy models to JSON
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Daily News Digest",
                "body": "Summary of today's news...",
                "start_datetime": "2024-01-01T00:00:00",
                "end_datetime": "2024-01-01T23:59:59",
                "article_ids": ["article1", "article2"],
                "summary": "In short, today's news...",
                "s3_url": "s3://news-assistant-digests/digests/uuid.pdf",
            }
        }


class DigestList(BaseModel):
    """Schema for list of digests"""

    items: List[DigestResponse]
    total: int
    skip: int
    limit: int

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "title": "Daily News Digest 1",
                        "body": "Summary of today's news...",
                        "start_datetime": "2024-01-01T00:00:00",
                        "end_datetime": "2024-01-01T23:59:59",
                        "article_ids": ["article1", "article2"],
                        "summary": "In short, today's news...",
                        "s3_url": "s3://news-assistant-digests/digests/uuid1.pdf",
                    },
                    {
                        "id": 2,
                        "title": "Daily News Digest 2",
                        "body": "Another summary of news...",
                        "start_datetime": "2024-01-02T00:00:00",
                        "end_datetime": "2024-01-02T23:59:59",
                        "article_ids": ["article3", "article4"],
                        "summary": "In short, today's news...",
                        "s3_url": "s3://news-assistant-digests/digests/uuid2.pdf",
                    },
                ],
                "total": 2,
                "skip": 0,
                "limit": 20,
            }
        }
