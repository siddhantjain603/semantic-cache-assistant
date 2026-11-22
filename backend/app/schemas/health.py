from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    application: str
    redis: str
    embedding_model: str