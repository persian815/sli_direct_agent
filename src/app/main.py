import streamlit as st
from src.app.config import initialize_app, load_js
from src.app.components import render_sidebar, render_chat_interface
from src.data.personas_roles import PERSONAS
from src.app.components.chat import get_character_icon

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
        
        .character-image {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin-right: 10px;
            object-fit: cover;
        }
        
        .character-description {
            font-size: 12px;
            color: #E0E0E0;
        }
        
        /* 셀렉트박스 스타일 */
        .stSelectbox {
            margin-bottom: 5px;
        }
        
        /* 모바일 최적화 */
        @media (max-width: 768px) {
            .character-image {
                width: 25px;
                height: 25px;
            }
            .character-description {
                font-size: 10px;
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
        "캐릭터 선택",
        options=character_options,
        index=character_options.index(current_character) if current_character in character_options else 0,
        key="character_select"
    )
    
    # 선택된 캐릭터가 변경되었으면 세션 상태 업데이트
    if selected_character != current_character:
        st.session_state.character = selected_character
    
    # 선택된 캐릭터 정보 표시
    character_icon = get_character_icon(selected_character)
    character_description = PERSONAS.get(selected_character, {}).get("description", "캐릭터 설명이 없습니다.")
    
    # 캐릭터 정보를 한 줄로 표시
    st.markdown(f"""
    <div class="character-info">
        <img src="{character_icon}" class="character-image" alt="{selected_character}">
        <div class="character-description">{character_description}</div>
    </div>
    """, unsafe_allow_html=True)

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