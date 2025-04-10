import streamlit as st
from data.personas_roles import PERSONAS
from data.professional_roles import PROFESSIONAL_ROLES
from src.visualization.visualization import create_knowledge_distribution_graph
from src.llm import aws_credentials_available, ms_credentials_available
from src.llm.ms_functions import test_ms_agent_connection

def render_sidebar():
    """사이드바 UI를 렌더링하는 함수"""
    with st.sidebar:
        st.header("설정")
        
        # Model selection
        st.subheader("모델 선택")
        
        # 사용 가능한 모델 목록 생성
        available_models = ["Ollama (라마 3.3)"]
        
        # AWS 자격증명이 있는 경우 AWS 모델 추가
        if aws_credentials_available:
            available_models.append("AWS Bedrock (클로드 3.5)")
        
        # MS Azure 자격증명이 있는 경우 MS 모델 추가
        if ms_credentials_available:
            available_models.append("Azure AI Foundry (GPT-3.5)")
        
        model = st.radio(
            "LLM 모델 선택",
            available_models,
            key="model"
        )
        
        # Azure AI Foundry 연결 테스트
        if model == "Azure AI Foundry (GPT-3.5)":
            if st.button("Azure AI Foundry 연결 테스트"):
                success, message = test_ms_agent_connection()
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        # Professional role selection
        st.subheader("전문 역할")
        role = st.selectbox(
            "전문 역할 선택",
            list(PROFESSIONAL_ROLES.keys()),
            key="role"
        )
        
        # Character selection
        st.subheader("캐릭터")
        def update_persona_info():
            st.session_state.persona_info = PERSONAS.get(st.session_state.character, {})
        character = st.selectbox(
            "캐릭터 선택",
            list(PERSONAS.keys()),
            key="character",
            on_change=update_persona_info
        )
        
        # Display selected persona information
        st.subheader("선택된 페르소나")
        persona_info = PERSONAS.get(character, {})
        if persona_info:
            st.markdown(f"**설명:** {persona_info.get('설명', 'N/A')}")
        else:
            st.warning("페르소나 정보를 가져오는데 실패했습니다.")
        
        # Knowledge level statistics
        st.subheader("지식 수준 통계")
        if st.session_state.messages:
            knowledge_levels = [
                msg.get("knowledge_level", 0)
                for msg in st.session_state.messages
                if msg["role"] == "user" and "knowledge_level" in msg
            ]
            if knowledge_levels:
                avg_level = sum(knowledge_levels) / len(knowledge_levels)
                st.markdown(f"평균 지식 수준: {avg_level:.1f}/10")
                st.plotly_chart(
                    create_knowledge_distribution_graph(knowledge_levels),
                    use_container_width=True
                )
        
        # Developer mode
        st.subheader("개발자 모드")
        st.session_state.developer_mode = st.toggle("개발자 모드 활성화", value=False)
        if st.session_state.developer_mode:
            st.markdown("### 함수 로그")
            for log in st.session_state.function_logs:
                st.code(log, language="python")
    
    return model, role, character, persona_info 