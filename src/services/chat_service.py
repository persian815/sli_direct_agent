"""
채팅 관련 기능을 처리하는 모듈입니다.
"""

import logging
from typing import Dict, List, Optional, Union

from src.data.dummy_data import DAILY_CONVERSATIONS, USER_RECOMMENDED_QUESTIONS

logger = logging.getLogger(__name__)

def get_recommended_questions(user_id: str) -> Dict[str, Dict[str, Union[str, Dict[str, str]]]]:
    """
    사용자별 추천 질문을 반환합니다.
    
    Args:
        user_id (str): 사용자 ID
        
    Returns:
        Dict[str, Dict[str, Union[str, Dict[str, str]]]]: 추천 질문 데이터
    """
    if user_id in USER_RECOMMENDED_QUESTIONS:
        return USER_RECOMMENDED_QUESTIONS[user_id]
    return USER_RECOMMENDED_QUESTIONS["곰철수"]  # 기본값으로 곰철수의 데이터 사용

def get_daily_conversation() -> Dict[str, Dict[str, str]]:
    """
    일상 대화 더미 데이터를 반환합니다.
    
    Returns:
        Dict[str, Dict[str, str]]: 일상 대화 더미 데이터
    """
    return DAILY_CONVERSATIONS

def is_recommended_question(user_id: str, question: str) -> Optional[str]:
    """
    질문이 추천 질문인지 확인하고, 추천 질문인 경우 해당 질문 ID를 반환합니다.
    
    Args:
        user_id (str): 사용자 ID
        question (str): 질문 텍스트
        
    Returns:
        Optional[str]: 추천 질문 ID (추천 질문이 아닌 경우 None)
    """
    recommended_questions = get_recommended_questions(user_id)
    for question_id, question_data in recommended_questions.items():
        if question_data["question"] == question:
            return question_id
    return None

def get_recommended_question_answers(user_id: str, question_id: str, platform: str) -> Optional[str]:
    """
    추천 질문에 대한 답변을 반환합니다.
    
    Args:
        user_id (str): 사용자 ID
        question_id (str): 질문 ID
        platform (str): 플랫폼 (ms, aws, sds)
        
    Returns:
        Optional[str]: 답변 텍스트
    """
    recommended_questions = get_recommended_questions(user_id)
    if question_id in recommended_questions:
        question_data = recommended_questions[question_id]
        if platform in question_data["answers"]:
            return question_data["answers"][platform]
    return None

def get_recommended_question_text(user_id: str, question_id: str) -> Optional[str]:
    """
    추천 질문 텍스트를 반환합니다.
    
    Args:
        user_id (str): 사용자 ID
        question_id (str): 질문 ID
        
    Returns:
        Optional[str]: 질문 텍스트
    """
    recommended_questions = get_recommended_questions(user_id)
    if question_id in recommended_questions:
        return recommended_questions[question_id]["question"]
    return None 