import streamlit as st
from src.app.config import initialize_app, load_js
from src.app.components import render_sidebar, render_chat_interface
from src.app.components.user_detail import render_user_select, USER_DETAILS
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

    # 1. 사용자 선택
    if 'selected_user' not in st.session_state:
        render_user_select()
        return

    # 2. (이전 상세화면 분기 삭제)
    # 바로 다음 단계로 이동
    model, role, character, _ = render_sidebar()
    # 현재 선택된 캐릭터 정보 표시
    current_character = st.session_state.get("character", "논리적인 테스형")
    character_description = PERSONAS.get(current_character, {}).get("설명", "캐릭터 설명이 없습니다.")
    st.markdown(f'<div class="character-description">{character_description}</div>', unsafe_allow_html=True)
    render_chat_interface(model)
    load_js()
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'character' in st.session_state:
        st.session_state.previous_character = st.session_state.character

if __name__ == "__main__":
    main() 