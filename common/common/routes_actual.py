from pydantic import BaseModel
from typing import List

class ActualItem(BaseModel):
    id: int
    title: str
    body: str

class ActualList(BaseModel):
    items: List[ActualItem]
    total: int
    skip: int
    limit: int
