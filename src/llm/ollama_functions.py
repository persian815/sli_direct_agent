import streamlit as st
import os
import time
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, List, Tuple, Any, Optional

from src.data.personas_roles import PERSONAS
from src.data.services_roles import SERVICES

# 환경 설정
IS_LOCAL = os.getenv('ENV', 'local') == 'local'

# 모델 초기화를 세션 상태에 저장하여 재사용
if 'ollama_model' not in st.session_state:
    st.session_state.ollama_model = None

def get_ollama_model():
    """Ollama 모델을 초기화하고 반환하는 함수"""
    if st.session_state.ollama_model is None:
        if IS_LOCAL:
            st.session_state.ollama_model = ChatOllama(
                model="llama3",
                base_url="http://localhost:11434"
            )
        else:
            st.session_state.ollama_model = ChatOllama(
                model="llama3",
                base_url="http://localhost:11434"  # EC2에서는 localhost 사용
            )
    return st.session_state.ollama_model

def query_ollama_optimized(input_text, tab_id=None):
    """Ollama 모델을 사용하여 질문에 답변하는 함수"""
    llm = get_ollama_model()
    
    # 시스템 프롬프트 추가
    if tab_id and tab_id in st.session_state.tab_system_prompts:
        system_prompt = st.session_state.tab_system_prompts[tab_id]
    else:
        # 기본 시스템 프롬프트 대신 현재 선택된 전문 분야와 캐릭터의 프롬프트 사용
        professional_prompt = SERVICES[st.session_state.professional_role]
        character_prompt = PERSONAS[st.session_state.character]["시스템프롬프트"]
        system_prompt = f"{professional_prompt}\n\n{character_prompt}"
    
    # 시작 시간 기록
    start_time = time.time()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{message}")
    ])
    chain = prompt | llm | StrOutputParser()
    response_text = chain.invoke({"message": input_text})
    
    # 경과 시간 계산
    elapsed_time = time.time() - start_time
    
    # 토큰 수 추정 (간단한 추정치)
    input_tokens = len(input_text.split()) // 1.3  # 대략적인 추정
    output_tokens = len(response_text.split()) // 1.3  # 대략적인 추정
    
    return response_text, elapsed_time, input_tokens, output_tokens, start_time 