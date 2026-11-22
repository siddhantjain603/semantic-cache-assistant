
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.api.routes.health import router as health_router
from backend.app.core.config import get_settings
from backend.app.dependencies.resources import resources


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize shared resources when the application starts.
    resources.initialize()

    yield

    # Release resources when the application shuts down.
    resources.close()


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.include_router(health_router)
