
from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.schemas.analytics import AnalyticsResponse
from backend.app.services.analytics import AnalyticsService

router = APIRouter(tags=["Analytics"])


def get_analytics_service() -> AnalyticsService:
    return analytics_service


analytics_service = AnalyticsService()


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics(
    service: Annotated[
        AnalyticsService,
        Depends(get_analytics_service),
    ],
):
    return service.get_analytics()
