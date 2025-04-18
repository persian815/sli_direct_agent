import streamlit as st
from src.app.config import initialize_app, load_js
from src.app.components import render_sidebar, render_chat_interface
from src.data.personas_roles import PERSONAS
from src.data.services_roles import SERVICES
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
        
        /* 서비스 표시 스타일 */
        .service-display {
            font-size: 20px;
            font-weight: 600;
            color: #4CAF50;
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 5px;
            background-color: rgba(76, 175, 80, 0.1);
            text-align: center;
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
            .service-display {
                font-size: 18px;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Render sidebar and get selected options
    model, role, character, _ = render_sidebar()

    # 현재 선택된 캐릭터 정보 표시
    current_character = st.session_state.get("character", "논리적인 테스형")
    character_description = PERSONAS.get(current_character, {}).get("설명", "캐릭터 설명이 없습니다.")

    # 캐릭터 정보를 한 줄로 표시
    st.markdown(f'<div class="character-description">{character_description}</div>', unsafe_allow_html=True)

    # Render chat interface
    render_chat_interface(model)

    # Load JavaScript at the end of the page
    load_js()

    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []

    # 캐릭터가 변경되었을 때 개발자 모드 초기화
    if 'character' in st.session_state and 'previous_character' in st.session_state:
        if st.session_state.character != st.session_state.previous_character:
            # 개발자 모드 초기화를 위해 세션 상태에서 제거
            if 'developer_mode' in st.session_state:
                del st.session_state.developer_mode
            
            # 캐릭터 변경 시 role 업데이트
            current_character = st.session_state.character
            character_info = PERSONAS.get(current_character, {})
            st.session_state.role = character_info.get("agent_name", "통합 전문가")
            
            # 캐릭터 변경 시 messages 초기화 및 새로운 웰컴 메시지 추가
            st.session_state.messages = []
            agent_name = current_character
            agent_role = st.session_state.role
            persona_info = character_info
            
            # 역할별 맞춤 환영 메시지 생성
            from src.utils.utils import get_role_specific_message
            role_specific_message = get_role_specific_message(agent_role)

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"""안녕하세요! 저는 {agent_name}이에요. {agent_role}로서 고객님을 만나게 되어 정말 반가워요.\n

{persona_info.get('welcome_message', '').replace('[', '').replace(']', '')}

{role_specific_message} 편하게 말씀해 주세요! 😊""",
                "metrics": {
                    "request_time": 0,
                    "response_time": 0,
                    "input_tokens": 0,
                    "output_tokens": 0
                }
            })
            
            st.session_state.previous_character = current_character

    # 현재 캐릭터를 이전 캐릭터로 저장
    if 'character' in st.session_state:
        st.session_state.previous_character = st.session_state.character

if __name__ == "__main__":
    main() 