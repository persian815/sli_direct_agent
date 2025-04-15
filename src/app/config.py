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
        page_title="다이렉트 ai FIT",
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
        st.session_state.model = "Azure AI Foundry (GPT-4.0)"
    if 'role' not in st.session_state:
        st.session_state.role = "보험 전문가"
    if 'character' not in st.session_state:
        st.session_state.character = "은별 나인"
    if 'persona_info' not in st.session_state:
        st.session_state.persona_info = {
            "description": "안녕하세요! 저는 삼성생명 다이렉트 FIT AI 서비스의 은별 나인입니다. 고객님의 상황과 니즈에 맞는 최적의 보험 상품을 추천해드리겠습니다."
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
        role_specific_message = ""
        if agent_role == "보험 전문가":
            role_specific_message = "보험 설계와 상품 추천을 도와드릴게요. 어떤 보험이 필요하신가요?"
        elif agent_role == "질병 전문가":
            role_specific_message = "질병에 대한 분석과 관련 보험 상품을 추천해드릴게요. 어떤 건강 고민이 있으신가요?"
        elif agent_role == "라이프스타일 전문가":
            role_specific_message = "고객님의 생활 방식에 맞는 보험을 추천해드릴게요. 평소 어떤 생활을 하시나요?"
        elif agent_role == "자산 전문가":
            role_specific_message = "자산 관리와 투자에 대해 상담해드릴게요. 어떤 자산 계획이 있으신가요?"
        else:
            role_specific_message = "고객님께 딱 맞는 보험 상품을 추천해드릴게요. 어떤 도움이 필요하신가요?"

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