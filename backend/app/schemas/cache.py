
from pydantic import BaseModel


class CacheEntry(BaseModel):
    id: str
    question: str
    answer: str
    inserted_at: float
    updated_at: float


class CacheEntriesResponse(BaseModel):
    entries: list[CacheEntry]
    total_entries: int
    returned_entries: int
    offset: int
    limit: int
