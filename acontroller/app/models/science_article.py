from acontroller.app.models.base import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from datetime import datetime



class ScienceArticle(Base):
    __tablename__ = "science_articles"

    id = Column(Integer, primary_key=True, index=True)

    sphere = Column(String, nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    section = Column(String, nullable=True)
    published_date = Column(DateTime, nullable=True)
    authors = Column(PG_ARRAY(String), nullable=True)
    affiliation = Column(String, nullable=True)
    source_name = Column(String, nullable=False)
    annotation = Column(Text, nullable=False)
    policy_conclusions = Column(Text, nullable=False)
    research_motivation = Column(Text, nullable=False)
    contribution = Column(Text, nullable=False)
    research_question = Column(Text, nullable=False)
    data_description = Column(Text, nullable=False)
    model_description = Column(Text, nullable=False)
    results = Column(Text, nullable=False)
    critique = Column(Text, nullable=False)
    relevance_explanation = Column(Text, nullable=False)
    relevance_score = Column(Float, nullable=False)
    full_summary = Column(Text)
    downloads_count = Column(Integer, nullable=True)
    views_count = Column(Integer, nullable=True)
    abstract = Column(Text, nullable=True)
    categories = Column(PG_ARRAY(String), nullable=True)
    parsed_at = Column(DateTime, default=datetime.utcnow, nullable=False)


    def __repr__(self):
        return f"<ScienceArticle(article_id='{self.id}', title='{self.title}')>"
