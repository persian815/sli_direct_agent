import os
import streamlit as st
from src.llm import initialize_session_state

def load_css():
    """CSS 파일을 로드하는 함수"""
    css_file = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'css', 'style.css')
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def load_js():
    """JavaScript 파일을 로드하는 함수"""
    js_file = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'js', 'sidebar.js')
    if os.path.exists(js_file):
        with open(js_file) as f:
            st.markdown(f'<script>{f.read()}</script>', unsafe_allow_html=True)

def initialize_app():
    """애플리케이션 초기화 함수"""
    # Load CSS
    load_css()
    
    # Load JavaScript
    load_js()
    
    # Initialize session state
    initialize_session_state()
    
    # Set default values for model, role, and character
    if 'model' not in st.session_state:
        st.session_state.model = "Azure AI Foundry (GPT-4.0)"
    if 'role' not in st.session_state:
        st.session_state.role = "통합 전문가"
    if 'character' not in st.session_state:
        st.session_state.character = "친절한 금자씨"
    if 'persona_info' not in st.session_state:
        from src.data.personas_roles import PERSONAS
        welcome_message = PERSONAS.get("친절한 금자씨", {}).get("welcome_message", "안녕하세요! 무엇을 도와드릴까요?")
        st.session_state.persona_info = {
            "description": welcome_message
        }
    
    # Initialize tabs in session state
    if 'tabs' not in st.session_state or not st.session_state.tabs:
        from src.app.components.chat import generate_tab_name
        tab_name = generate_tab_name(st.session_state.role, st.session_state.character)
        st.session_state.tabs = [tab_name]
        st.session_state.current_tab = tab_name
    
    # Initialize messages in session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        # 초기 환영 메시지 추가
        agent_name = st.session_state.character
        agent_role = st.session_state.role
        persona_info = st.session_state.persona_info
        
        # 역할별 맞춤 환영 메시지 생성
        from src.utils.utils import get_role_specific_message
        role_specific_message = get_role_specific_message(agent_role)

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"""안녕하세요! 저는 {agent_name}이에요. {agent_role}로서 고객님을 만나게 되어 정말 반가워요.

{persona_info.get('description', '').replace('[', '').replace(']', '')}

{role_specific_message} 편하게 말씀해 주세요! 😊""",
            "metrics": {
                "request_time": 0,
                "response_time": 0,
                "input_tokens": 0,
                "output_tokens": 0
            }
        })

    if 'function_logs' not in st.session_state:
        st.session_state.function_logs = []

    if 'is_first_load' not in st.session_state:
        st.session_state.is_first_load = True
    else:
        st.session_state.is_first_load = False 