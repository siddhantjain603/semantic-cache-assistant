from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.api.routes.analytics import router as analytics_router
from backend.app.api.routes.cache import router as cache_router
from backend.app.api.routes.chat import (
    chat_service,
)
from backend.app.api.routes.chat import (
    router as chat_router,
)
from backend.app.api.routes.health import router as health_router
from backend.app.core.config import get_settings
from backend.app.dependencies.resources import resources


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize shared resources.
    resources.initialize()

    # Initialize the semantic cache.
    chat_service.initialize()

    yield

    # Release shared resources.
    resources.close()


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(analytics_router)
app.include_router(cache_router)