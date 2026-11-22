
from typing import Annotated

import redis
from fastapi import APIRouter, Depends

from backend.app.dependencies.resources import ApplicationResources, resources
from backend.app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


def get_resources() -> ApplicationResources:
    return resources


@router.get("/health", response_model=HealthResponse)
def health_check(
    app_resources: Annotated[
        ApplicationResources, Depends(get_resources)
    ],
):
    redis_status = "connected"
    embedding_status = "loaded"

    try:
        app_resources.redis_client.ping()
    except redis.exceptions.RedisError:
        redis_status = "unavailable"

    if app_resources.embedding_model is None:
        embedding_status = "not loaded"

    overall_status = (
        "healthy"
        if redis_status == "connected" and embedding_status == "loaded"
        else "degraded"
    )

    return HealthResponse(
        status=overall_status,
        application=app_resources.settings.APP_NAME,
        redis=redis_status,
        embedding_model=embedding_status,
    )
