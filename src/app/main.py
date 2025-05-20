import streamlit as st
from src.app.config import initialize_app, load_js
from src.app.components import render_sidebar, render_chat_interface
from src.app.components.user_select import render_user_select
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

    # 1. 사용자 선택 화면
    if 'selected_user' not in st.session_state:
        render_user_select()
        return

    # 2. 채팅 인터페이스
    model, role, character, _ = render_sidebar()
    render_chat_interface(model)
    load_js()

    # 3. 채팅 메시지 초기화
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # 4. 이전 캐릭터 정보 저장
    if 'character' in st.session_state:
        st.session_state.previous_character = st.session_state.character

if __name__ == "__main__":
    main() 