from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.chat import ChatService

router = APIRouter(tags=["Chat"])


def get_chat_service() -> ChatService:
    return chat_service


chat_service = ChatService()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    service: Annotated[ChatService, Depends(get_chat_service)],
):
    result = service.ask(request.question)

    return ChatResponse(**result)