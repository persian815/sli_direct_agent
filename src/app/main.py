import streamlit as st
from src.app.config import initialize_app, load_js
from src.app.components import render_sidebar, render_chat_interface
from src.data.personas_roles import PERSONAS
import json

import logging
# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Page config - 반드시 첫 번째 Streamlit 명령이어야 함
st.set_page_config(
    page_title="ai FIT",
    page_icon="static/image/logo.ico",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # Initialize the application
    initialize_app()

    # URL 파라미터 처리
    query_params = st.query_params
    
    # 에이전트 설정 파라미터 처리
    if 'agent' in query_params:
        agent_param = query_params['agent']
        # 단순 문자열 파라미터 처리
        st.session_state.service = agent_param
        logger.info("############# main() service : {}".format(st.session_state.service))

        if 'function_logs' in st.session_state:
            st.session_state.function_logs.append(f"URL 파라미터로 서비스 설정: {agent_param}")
    
    # 캐릭터 선택 UI 스타일
    st.markdown("""
    <style>
        /* 캐릭터 선택 UI 스타일 */
        .character-info {
            display: flex;
            align-items: center;
            margin-top: 5px;
            margin-bottom: 5px;
            padding: 5px;
            border-radius: 5px;
            background-color: rgba(255, 255, 255, 0.05);
        }
        
        .character-description {
            font-size: 18px;
            font-weight: 500;
            color: #E0E0E0;
            margin-left: 10px;
            line-height: 1.5;
        }
        
        /* 셀렉트박스 스타일 */
        .stSelectbox {
            margin-bottom: 5px;
        }
        
        /* 모바일 최적화 */
        @media (max-width: 768px) {
            .character-description {
                font-size: 16px;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 현재 선택된 캐릭터
    current_character = st.session_state.get("character", "논리적인 테스형")
    
    # 캐릭터 선택 옵션
    character_options = list(PERSONAS.keys())
    
    # 셀렉트박스로 캐릭터 선택
    selected_character = st.selectbox(
        label="캐릭터 선택",
        options=character_options,
        index=character_options.index(current_character) if current_character in character_options else 0,
        key="character_select",
        label_visibility="collapsed"
    )
    
    # 선택된 캐릭터가 변경되었으면 세션 상태 업데이트 및 대화 초기화
    if selected_character != current_character:
        st.session_state.character = selected_character
        # 대화 내용 초기화
        if 'messages' in st.session_state:
            st.session_state.messages = []
        if 'is_generating' in st.session_state:
            st.session_state.is_generating = False
        # 웰컴 메시지 추가
        if 'messages' in st.session_state:
            welcome_message = PERSONAS.get(selected_character, {}).get("welcome_message", "안녕하세요! 무엇을 도와드릴까요?")
            st.session_state.messages.append({"role": "assistant", "content": welcome_message})
        # 화면 갱신
        st.rerun()
    
    # 선택된 캐릭터 정보 표시
    character_description = PERSONAS.get(selected_character, {}).get("설명", "캐릭터 설명이 없습니다.")
    
    # 캐릭터 정보를 한 줄로 표시
    st.markdown(f'<div class="character-description">{character_description}</div>', unsafe_allow_html=True)

    # Render sidebar and get selected options
    model, role, character, _ = render_sidebar()

    # Render chat interface
    render_chat_interface(model)

    # Load JavaScript at the end of the page
    load_js()

    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []

if __name__ == "__main__":
    main() 