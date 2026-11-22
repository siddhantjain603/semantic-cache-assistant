
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.app.api.routes.chat import chat_service
from backend.app.schemas.cache import CacheEntriesResponse
from backend.app.services.semantic_cache import SemanticCacheService

router = APIRouter(tags=["Cache"])


def get_semantic_cache_service() -> SemanticCacheService:
    return chat_service.semantic_cache


@router.get("/cache", response_model=CacheEntriesResponse)
def get_cache_entries(
    service: Annotated[
        SemanticCacheService,
        Depends(get_semantic_cache_service),
    ],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    result = service.get_entries(offset=offset, limit=limit)
    return CacheEntriesResponse(**result)
