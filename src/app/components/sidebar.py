"""
사이드바 컴포넌트를 정의하는 모듈입니다.
"""

import streamlit as st
import pandas as pd
import logging
from typing import Dict, List, Optional
import json
import os
from pathlib import Path
from src.data.personas_roles import PERSONAS
from src.data.services_roles import SERVICES
from src.data.users_data import USERS
from src.llm import aws_credentials_available, ms_credentials_available
from src.llm.ms_functions import test_ms_agent_connection, get_agent_config
from src.utils.utils import get_temperature_color, get_chat_history_from_api, get_role_specific_message, evaluate_user_knowledge_level, evaluate_user_temperature
from src.app.components.chat_interface import get_character_icon
from src.visualization.visualization import create_knowledge_distribution_graph, create_temperature_distribution_graph
import time

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def render_sidebar():
    """사이드바를 렌더링합니다."""
    # 세션 상태 초기화
    if 'function_logs' not in st.session_state:
        st.session_state.function_logs = []
    
    # 최초 로드 시 Azure AI Foundry 선택 및 대화 초기화
    if 'is_first_load' not in st.session_state:
        st.session_state.is_first_load = True
        st.session_state.model = "Azure AI Foundry (GPT-4.0)"
        st.session_state.character = "친절한 미영시"
    
    # 기본 모델 설정
    model = st.session_state.get("model", "Azure AI Foundry (GPT-4.0)")
    
    # 서비스 선택 (화면에 표시하지 않음)
    service_options = list(SERVICES.keys())
    default_service_index = 0
    
    # URL 파라미터로 설정된 서비스가 있으면 해당 인덱스로 설정
    if 'service' in st.session_state:
        service_value = st.session_state.service
        if service_value == "1":
            default_service_index = service_options.index("통합 전문가")
        elif service_value == "2":
            default_service_index = service_options.index("질병 전문가")
        elif service_value == "3":
            default_service_index = service_options.index("라이프 전문가")
    
    selected_service = service_options[default_service_index]
    
    # 멀티답변 모드 토글
    st.sidebar.subheader("멀티답변 모드")
    is_multi_mode = st.sidebar.toggle("멀티답변 모드 활성화", key="multi_mode", value=st.session_state.get('multi_mode', False))
    if 'multi_mode' not in st.session_state:
        st.session_state.multi_mode = is_multi_mode
    
    # 개발자 모드 토글
    st.sidebar.subheader("개발자 모드")
    is_developer_mode = st.sidebar.toggle("개발자 모드 활성화", key="developer_mode")
    
    # 더미 모드 토글 (기본값: 활성화)
    st.sidebar.subheader("더미 모드")
    is_dummy_mode = st.sidebar.toggle("더미 모드 활성화", key="dummy_mode", value=st.session_state.get('dummy_mode', True))
    if 'dummy_mode' not in st.session_state:
        st.session_state.dummy_mode = is_dummy_mode
    
    # 개발자 모드가 활성화된 경우에만 사이드바 내용 표시
    if is_developer_mode:
        # 선택된 사용자 정보 표시
        st.sidebar.subheader("선택된 사용자")
        current_user = st.session_state.get("user", "User1")
        user_kor_names = {
            "User1": "사용자 1",
            "User2": "사용자 2",
            "User3": "사용자 3",
            "User4": "사용자 4",
        }
        kor_display = user_kor_names.get(current_user, current_user)
        # 사용자 정보 조회 (영문 id로만!)
        user_info = USERS.get(current_user, {}).get('info', {})
        if isinstance(user_info, list):
            user_info = user_info[0] if user_info else {}
        # 표시
        basic_info = user_info.get('기본정보', {})
        name = basic_info.get('이름', '')
        age = basic_info.get('나이', '')
        display_name = f"{name} ({age}세)" if name and age else kor_display
        st.sidebar.markdown(f"**현재 선택된 사용자**: {display_name}")
        
        st.sidebar.divider()
        
        # 상담원 선택
        current_character = st.session_state.get("character", "친절한 미영시")
        character = st.sidebar.selectbox(
            "상담원 선택",
            list(PERSONAS.keys()),
            index=list(PERSONAS.keys()).index(current_character) if current_character in PERSONAS else 0
        )
        
        # 상담원이 변경된 경우 웰컴 메시지 업데이트
        if character != current_character:
            st.session_state.character = character
            # 웰컴 메시지 업데이트
            welcome_message = PERSONAS.get(character, {}).get("welcome_message", "안녕하세요! 무엇을 도와드릴까요?")
            st.session_state.persona_info = {
                "description": welcome_message
            }
            # 채팅 메시지 초기화
            st.session_state.messages = []
            st.rerun()
        
        # 채팅 히스토리 표시
        st.sidebar.subheader("채팅 히스토리")
        chat_history = get_chat_history_from_api()
        if chat_history:
            df = pd.DataFrame(chat_history)
            if 'id' in df.columns:
                df.set_index('id', inplace=True)
            # 역순으로 정렬하여 최신 메시지가 위에 표시되도록 함
            df = df.sort_index(ascending=False)
            
            # 표시할 컬럼 설정
            display_columns = ['question', 'answer']
            
            # 추가 정보가 있는 경우 컬럼에 추가
            if 'timestamp' in df.columns:
                display_columns.append('timestamp')
            if 'service' in df.columns:
                display_columns.append('service')
            if 'character' in df.columns:
                display_columns.append('character')
            if 'knowledge_level' in df.columns:
                display_columns.append('knowledge_level')
            if 'temperature' in df.columns:
                display_columns.append('temperature')
            if 'quality_score' in df.columns:
                display_columns.append('quality_score')
            
            # 컬럼 이름 한글화
            column_config = {
                'question': '질문',
                'answer': '답변'
            }
            
            if 'timestamp' in display_columns:
                column_config['timestamp'] = '시간'
            if 'service' in display_columns:
                column_config['service'] = '서비스'
            if 'character' in display_columns:
                column_config['character'] = '캐릭터'
            if 'knowledge_level' in display_columns:
                column_config['knowledge_level'] = '지식 레벨'
            if 'temperature' in display_columns:
                column_config['temperature'] = '온도'
            if 'quality_score' in display_columns:
                column_config['quality_score'] = '품질 점수'
            
            # 데이터프레임 표시
            st.sidebar.dataframe(
                df[display_columns],
                column_config=column_config,
                use_container_width=True
            )
        else:
            st.sidebar.info("채팅 히스토리가 없습니다.")
        
        # 통계 그래프 표시
        st.sidebar.subheader("통계")
        chat_history = st.session_state.get("messages", [])
        
        if chat_history:
            # 채팅 히스토리에서 모든 user 질문 추출
            user_questions = []
            for message in chat_history:
                if message.get("role") == "user":
                    user_questions.append(message.get("content"))

            # 지식 레벨 분포
            knowledge_scores = []
            for message in chat_history:
                if message.get("role") == "user" and "knowledge_level" in message:
                    knowledge_scores.append(message["knowledge_level"])
            
            if knowledge_scores:
                beginner = sum(1 for s in knowledge_scores if s < 40)
                intermediate = sum(1 for s in knowledge_scores if 40 <= s < 70)
                advanced = sum(1 for s in knowledge_scores if s >= 70)
                knowledge_levels_data = [beginner, intermediate, advanced]
                knowledge_graph = create_knowledge_distribution_graph(knowledge_levels_data)
                st.sidebar.subheader("지식 레벨 통계")
                st.sidebar.plotly_chart(knowledge_graph, use_container_width=True)

            # 사용자 온도 분포
            temperature_scores = []
            for message in chat_history:
                if message.get("role") == "user" and "temperature" in message:
                    temperature_scores.append(message["temperature"])
            
            if temperature_scores:
                temperature_graph = create_temperature_distribution_graph(temperature_scores)
                st.sidebar.subheader("사용자 온도 통계")
                st.sidebar.plotly_chart(temperature_graph, use_container_width=True)

            # 응답 품질 통계
            quality_scores = []
            for message in chat_history:
                if message.get("role") == "assistant" and "quality_score" in message:
                    quality_scores.append(message["quality_score"])
            
            if quality_scores:
                st.sidebar.subheader("응답 품질 통계")
                quality_df = pd.DataFrame({
                    '응답 품질': quality_scores
                })
                st.sidebar.bar_chart(quality_df)
    else:
        # 개발자 모드가 비활성화된 경우 기본 모델 사용
        model = "Azure AI Foundry (GPT-4.0)"
    
    # 현재 선택된 캐릭터
    current_character = st.session_state.get("character", "논리적인 테스형")
    
    return model, selected_service, current_character, None 

def plot_knowledge_distribution():
    knowledge_data = {}
    for message in st.session_state.chat_history:
        if message.get("role") == "assistant":
            level = message.get("knowledge_level")
            if level is not None:
                try:
                    level = int(level)
                    knowledge_data[level] = knowledge_data.get(level, 0) + 1
                except ValueError:
                    continue
    if not knowledge_data:
        st.warning("지식 레벨 데이터가 없습니다.")
        return
    # ... (이하 동일) 

def generate_response(prompt: str, model: str) -> str:
    # Implementation of generate_response function
    pass 

start_time = time.time()
elapsed_time = 0  # 초기화 추가 