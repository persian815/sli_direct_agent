import streamlit as st
from data.personas_roles import PERSONAS
from data.services_roles import SERVICES
from src.visualization.visualization import create_knowledge_distribution_graph
from src.llm import aws_credentials_available, ms_credentials_available
from src.llm.ms_functions import test_ms_agent_connection

def render_sidebar():
    """사이드바 UI를 렌더링하는 함수"""
    # 세션 상태 초기화
    if 'function_logs' not in st.session_state:
        st.session_state.function_logs = []
    
    # 최초 로드 시 Azure AI Foundry 선택 및 대화 초기화
    if 'is_first_load' not in st.session_state:
        st.session_state.is_first_load = True
        st.session_state.model = "Azure AI Foundry (GPT-4.0)"
        
        # Azure AI Foundry 연결 테스트 및 로그 추가
        success, message = test_ms_agent_connection()
        if success:
            st.session_state.function_logs.append(f"Azure AI Foundry 연결 테스트 성공: {message}")
        else:
            st.session_state.function_logs.append(f"Azure AI Foundry 연결 테스트 실패: {message}")
    
    with st.sidebar:
        st.header("설정")
        
        # Model selection
        st.subheader("모델 선택")
        
        # 사용 가능한 모델 목록 생성
        available_models = ["Azure AI Foundry (GPT-4.0)"]  # Azure AI Foundry를 기본으로 추가
        
        # Ollama 모델 추가
        available_models.append("Ollama (라마 3.3)")
        
        # AWS 자격증명이 있는 경우 AWS 모델 추가
        if aws_credentials_available:
            available_models.append("AWS Bedrock (클로드 3.5)")
        
        model = st.radio(
            "LLM 모델 선택",
            available_models,
            key="model",
            index=0  # Azure AI Foundry를 기본값으로 설정
        )
        
        # Azure AI Foundry 연결 테스트 로그 추가 (모델 변경 시)
        if model == "Azure AI Foundry (GPT-4.0)" and not st.session_state.is_first_load:
            success, message = test_ms_agent_connection()
            if success:
                st.session_state.function_logs.append(f"Azure AI Foundry 연결 테스트 성공: {message}")
            else:
                st.session_state.function_logs.append(f"Azure AI Foundry 연결 테스트 실패: {message}")
        
        # Service selection
        st.subheader("서비스")
        role = st.selectbox(
            "서비스 선택",
            list(SERVICES.keys()),
            key="role"
        )
        
        # Character selection
        st.subheader("캐릭터")
        def update_persona_info():
            st.session_state.persona_info = PERSONAS.get(st.session_state.character, {})
            # 함수 로그 추가
            st.session_state.function_logs.append(f"페르소나 정보 업데이트: {st.session_state.character}")
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
        if 'developer_mode' not in st.session_state:
            st.session_state.developer_mode = False
            
        developer_mode = st.toggle("개발자 모드 활성화", value=st.session_state.developer_mode)
        st.session_state.developer_mode = developer_mode
        
        if developer_mode:
            st.markdown("### 함수 로그")
            if not st.session_state.function_logs:
                st.info("아직 함수 로그가 없습니다. 앱을 사용하면 로그가 여기에 표시됩니다.")
            else:
                for log in st.session_state.function_logs:
                    st.code(log, language="python")
                
                # 로그 초기화 버튼
                if st.button("로그 초기화"):
                    st.session_state.function_logs = []
                    st.rerun()
    
    return model, role, character, persona_info 