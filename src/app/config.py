import streamlit as st
from src.llm import initialize_session_state

def load_css():
    """CSS 파일을 로드하는 함수"""
    with open("static/css/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def load_js():
    """JavaScript 파일을 로드하는 함수"""
    with open("static/js/sidebar.js") as f:
        js_code = f.read()
        st.markdown(f"""
            <script>
                {js_code}
            </script>
        """, unsafe_allow_html=True)

def initialize_app():
    """애플리케이션 초기화 함수"""
    # Page config - 반드시 첫 번째 Streamlit 명령이어야 함
    st.set_page_config(
        page_title="SLI Direct Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load CSS
    load_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Set default values for model, role, and character
    if 'model' not in st.session_state:
        st.session_state.model = "Ollama (라마 3.3)"
    if 'role' not in st.session_state:
        st.session_state.role = "보험 설계사"
    if 'character' not in st.session_state:
        from data.personas_roles import PERSONAS
        st.session_state.character = "은별 나인"
        st.session_state.persona_info = PERSONAS.get("은별 나인", {})
    
    # Initialize tabs in session state
    if 'tabs' not in st.session_state or not st.session_state.tabs:
        from src.app.components.chat import generate_tab_name
        tab_name = generate_tab_name(st.session_state.role, st.session_state.character)
        st.session_state.tabs = [tab_name]
        st.session_state.current_tab = tab_name
    
    # Initialize messages in session state
    if 'messages' not in st.session_state:
        st.session_state.messages = [] 