from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.orm import relationship
from app.models.base import Base


class NewsArticle(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    publication_datetime = Column(DateTime, nullable=False)
    url = Column(String, nullable=False, unique=True)
    text = Column(String, nullable=False)
    source_name = Column(String, nullable=False)
    news_id = Column(String, nullable=False, unique=True)
    tags = Column(PG_ARRAY(String), nullable=True)
    persons = Column(PG_ARRAY(String), nullable=True)
    title = Column(String, nullable=True)
    topic = Column(String, nullable=True)

    def __repr__(self):
        return f"<NewsArticle(news_id='{self.news_id}', title='{self.title}')>"


