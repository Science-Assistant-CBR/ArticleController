from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from backend.app.models.base import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    publication_datetime = Column(DateTime, nullable=False)
    url = Column(String, nullable=False)
    text = Column(String, nullable=False)
    source_name = Column(String, nullable=False)
    news_id = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    persons = Column(ARRAY(String), nullable=True)
    title = Column(String, nullable=True)
    topic = Column(String, nullable=True)

    def __repr__(self):
        return f"<News(news_id='{self.news_id}', title='{self.title}')>"
