"""
FastAPI 애플리케이션의 메인 모듈입니다.
"""

import logging
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.services.chat_service import (
    get_daily_conversation,
    get_recommended_question_answers,
    get_recommended_question_text,
    is_recommended_question,
)
from src.config import settings
from src.utils.logger import setup_logger

# 로거 설정
setup_logger()
logger = logging.getLogger(__name__)

app = FastAPI(title="SLI Direct Agent API")

class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    user_id: str
    question: str
    platform: str = "ms"  # 기본값은 ms

class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    answer: str
    is_recommended: bool = False
    recommended_question_id: Optional[str] = None

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    채팅 요청을 처리합니다.
    
    Args:
        request (ChatRequest): 채팅 요청 데이터
        
    Returns:
        ChatResponse: 채팅 응답 데이터
    """
    logger.info(f"Sending chat log to API - Question: {request.question}")
    
    # 추천 질문인지 확인
    recommended_question_id = is_recommended_question(request.user_id, request.question)
    if recommended_question_id:
        answer = get_recommended_question_answers(
            request.user_id, recommended_question_id, request.platform
        )
        if answer:
            return ChatResponse(
                answer=answer,
                is_recommended=True,
                recommended_question_id=recommended_question_id
            )
    
    # 일반 질문 처리
    daily_conversations = get_daily_conversation()
    for category, data in daily_conversations.items():
        if any(pattern in request.question for pattern in data["patterns"]):
            if request.platform in data["answers"]:
                return ChatResponse(answer=data["answers"][request.platform])
    
    # 기본 응답
    return ChatResponse(answer="죄송합니다. 그 질문에 대해서는 답변하기 어렵네요. 다른 질문을 해주시겠어요?") 