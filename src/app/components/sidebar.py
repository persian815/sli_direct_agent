import streamlit as st
from src.data.personas_roles import PERSONAS
from src.data.services_roles import SERVICES
from src.visualization.visualization import create_knowledge_distribution_graph, create_temperature_distribution_graph
from src.llm import aws_credentials_available, ms_credentials_available
from src.llm.ms_functions import test_ms_agent_connection
from src.utils.utils import get_temperature_color

def render_sidebar():
    """사이드바 UI를 렌더링하는 함수"""
    # 세션 상태 초기화
    if 'function_logs' not in st.session_state:
        st.session_state.function_logs = []
    
    # 최초 로드 시 Azure AI Foundry 선택 및 대화 초기화
    if 'is_first_load' not in st.session_state:
        st.session_state.is_first_load = True
        st.session_state.model = "Azure AI Foundry (GPT-4.0)"
        st.session_state.character = "친절한 금자씨"
        
        # Azure AI Foundry 연결 테스트 및 로그 추가
        success, message = test_ms_agent_connection()
        if success:
            st.session_state.function_logs.append(f"Azure AI Foundry 연결 테스트 성공: {message}")
        else:
            st.session_state.function_logs.append(f"Azure AI Foundry 연결 테스트 실패: {message}")
    
    # 기본 모델 설정
    model = st.session_state.get("model", "Azure AI Foundry (GPT-4.0)")
    
    with st.sidebar:
        st.header("설정")
        
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
        
        # Developer mode toggle
        st.subheader("개발자 모드")
        developer_mode = st.toggle("개발자 모드 활성화", key="developer_mode")
        
        # 개발자 모드가 활성화된 경우에만 모델 선택 영역 표시
        if developer_mode:
           
            # # Model selection
            # st.subheader("모델 선택")
            
            # # 사용 가능한 모델 목록 생성
            # available_models = ["Azure AI Foundry (GPT-4.0)"]  # Azure AI Foundry를 기본으로 추가
            
            # # Ollama 모델 추가
            # available_models.append("Ollama (라마 3.3)")
            
            # # AWS 자격증명이 있는 경우 AWS 모델 추가
            # if aws_credentials_available:
            #     available_models.append("AWS Bedrock (클로드 3.5)")
            
            # model = st.radio(
            #     "LLM 모델 선택",
            #     available_models,
            #     key="model",
            #     index=0  # Azure AI Foundry를 기본값으로 설정
            # )
            
            # Azure AI Foundry 연결 테스트 로그 추가 (모델 변경 시)
            if model == "Azure AI Foundry (GPT-4.0)" and not st.session_state.is_first_load:
                success, message = test_ms_agent_connection()
                if success:
                    st.session_state.function_logs.append(f"Azure AI Foundry 연결 테스트 성공: {message}")
                else:
                    st.session_state.function_logs.append(f"Azure AI Foundry 연결 테스트 실패: {message}")
            
            # Knowledge level statistics
            st.subheader("지식 수준 통계")
            if st.session_state.get('developer_mode', False):
                knowledge_levels = [msg.get('knowledge_level', 0) for msg in st.session_state.messages if 'knowledge_level' in msg]
                if knowledge_levels:
                    fig = create_knowledge_distribution_graph(knowledge_levels)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("아직 지식 수준 데이터가 없습니다.")
            
            # User temperature statistics
            st.subheader("사용자 온도 통계")
            if st.session_state.messages:
                temperatures = [
                    msg.get("temperature", 36.5)
                    for msg in st.session_state.messages
                    if msg["role"] == "user" and "temperature" in msg
                ]
                
                if temperatures:
                    # 온도 분포 그래프 생성
                    fig = create_temperature_distribution_graph(temperatures)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("아직 사용자 온도 데이터가 없습니다.")
            
            # Response quality statistics
            st.subheader("답변 품질 통계")
            if st.session_state.messages:
                quality_scores = [
                    msg.get("quality_score", 0)
                    for msg in st.session_state.messages
                    if msg["role"] == "assistant" and "quality_score" in msg and msg.get("quality_score") is not None
                ]
                if quality_scores:
                    avg_quality = sum(quality_scores) / len(quality_scores)
                    st.markdown(f"평균 답변 품질: {avg_quality:.1f}/100")
                    
                    # 품질 점수 분포 그래프 생성
                    quality_ranges = {}
                    for i in range(0, 101, 20):
                        range_key = f"{i}-{i+19}"
                        quality_ranges[range_key] = sum(1 for score in quality_scores if i <= score < i+20)
                    
                    # 품질 점수 분포 그래프 표시
                    import plotly.graph_objects as go
                    fig = go.Figure(data=[
                        go.Bar(
                            x=list(quality_ranges.keys()),
                            y=list(quality_ranges.values()),
                            marker_color='#4CAF50',
                            opacity=0.7
                        )
                    ])
                    
                    # 그래프 레이아웃 업데이트
                    fig.update_layout(
                        title="Response Quality Distribution",
                        xaxis_title="Quality Score Range",
                        yaxis_title="Count",
                        template="plotly_dark",
                        paper_bgcolor="#1E1E1E",
                        plot_bgcolor="#1E1E1E",
                        font=dict(color="#FFFFFF"),
                        margin=dict(t=30, l=40, r=20, b=40),
                        height=300
                    )
                    
                    # 축 업데이트
                    fig.update_xaxes(
                        gridcolor="#2D2D2D",
                        zerolinecolor="#2D2D2D"
                    )
                    fig.update_yaxes(
                        gridcolor="#2D2D2D",
                        zerolinecolor="#2D2D2D"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("아직 에이전트 품질 통계 데이터가 없습니다.")
            
            # Function logs display
            st.subheader("함수 로그")
            for log in st.session_state.function_logs:
                st.text(log)
        else:
            # 개발자 모드가 비활성화된 경우 기본 모델 사용
            model = "Azure AI Foundry (GPT-4.0)"
            st.session_state.model = model
    
    return model, role, character, developer_mode 