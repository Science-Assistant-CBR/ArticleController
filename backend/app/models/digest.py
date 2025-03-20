from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from app.models.base import Base


class Digest(Base):
    __tablename__ = "digests"

    id = Column(Integer, primary_key=True)
    start_datetime = Column(DateTime, nullable=False, index=True)
    end_datetime = Column(DateTime, nullable=False, index=True)
    s3_url = Column(String, nullable=False)
    article_ids = Column(ARRAY(String), nullable=True)
    title = Column(String, nullable=True)
    body = Column(String, nullable=False)

    def __repr__(self):
        return f"<Digest({self.start_datetime} - {self.end_datetime}) {self.title}>"
