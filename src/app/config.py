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
        st.session_state.character = "친절한 미영씨"
    if 'persona_info' not in st.session_state:
        from src.data.personas_roles import PERSONAS
        st.session_state.persona_info = {
            "description": PERSONAS.get("친절한 미영씨", {}).get("welcome_message", "안녕하세요! 무엇을 도와드릴까요?")
        }
    
    # Initialize messages in session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'function_logs' not in st.session_state:
        st.session_state.function_logs = []

    if 'is_first_load' not in st.session_state:
        st.session_state.is_first_load = True
    else:
        st.session_state.is_first_load = False 