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

    # Title area with character selection
    # 캐릭터 선택 UI
    st.markdown("""
    <style>
        /* 캐릭터 선택 UI 스타일 */
        .character-selector {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 5px;
            margin-bottom: 5px;
        }
        .character-option {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-right: 10px;
            padding: 5px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .character-option:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        .character-option.selected {
            background-color: rgba(255, 255, 255, 0.2);
            border: 2px solid #4CAF50;
        }
        .character-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            margin-bottom: 2px;
        }
        .character-name {
            font-size: 12px;
            text-align: center;
        }
        
        /* 컬럼 스타일 */
        .stColumns {
            margin-top: 0;
            margin-bottom: 0;
            padding-top: 0;
            padding-bottom: 0;
        }
        
        /* 이미지 스타일 */
        .stImage {
            margin-top: 0;
            margin-bottom: 0;
            padding-top: 0;
            padding-bottom: 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 현재 선택된 캐릭터
    current_character = st.session_state.get("character", "논리적인 테스형")
    
    # 캐릭터 선택 옵션
    character_options = list(PERSONAS.keys())
    
    # 캐릭터 선택 UI
    st.markdown('<div class="character-selector">', unsafe_allow_html=True)
    
    # 캐릭터 버튼 생성
    cols = st.columns(len(character_options))
    for i, character_name in enumerate(character_options):
        with cols[i]:
            # 캐릭터 아이콘 경로
            icon_path = get_character_icon(character_name)
            
            # 선택된 캐릭터 여부
            is_selected = character_name == current_character
            
            # 캐릭터 버튼
            if st.button(
                character_name,
                key=f"char_{i}",
                use_container_width=True,
                help=f"{character_name} 선택"
            ):
                st.session_state.character = character_name
                st.rerun()
            
            # 캐릭터 아이콘 표시
            st.image(icon_path, width=40)
            
            # 선택된 캐릭터 표시
            if is_selected:
                st.markdown(f"<div class='character-name' style='color: #4CAF50; font-weight: bold;'>{character_name}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='character-name'>{character_name}</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

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