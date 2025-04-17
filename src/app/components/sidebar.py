import streamlit as st
from src.data.personas_roles import PERSONAS
from src.data.services_roles import SERVICES
from src.visualization.visualization import create_knowledge_distribution_graph, create_temperature_distribution_graph
from src.llm import aws_credentials_available, ms_credentials_available
from src.llm.ms_functions import test_ms_agent_connection
from src.utils.utils import get_temperature_color, get_chat_history_from_api
import pandas as pd

def render_sidebar():
    """사이드바를 렌더링합니다."""
    # 세션 상태 초기화
    if 'function_logs' not in st.session_state:
        st.session_state.function_logs = []
    
    # 최초 로드 시 Azure AI Foundry 선택 및 대화 초기화
    if 'is_first_load' not in st.session_state:
        st.session_state.is_first_load = True
        st.session_state.model = "Azure AI Foundry (GPT-4.0)"
        st.session_state.character = "친절한 금자씨"
    
    # 기본 모델 설정
    model = st.session_state.get("model", "Azure AI Foundry (GPT-4.0)")
    
    with st.sidebar:
        st.header("설정")
        
        # 서비스 선택
        st.subheader("서비스 선택")
        service_options = list(SERVICES.keys())
        default_service_index = 0
        
        # URL 파라미터로 설정된 서비스가 있으면 해당 인덱스로 설정
        if 'service' in st.session_state:
            service_value = st.session_state.service
            if service_value == "1":
                default_service_index = service_options.index("통합 전문가")
            elif service_value == "2":
                default_service_index = service_options.index("질병 전문가")
            elif service_value == "3":
                default_service_index = service_options.index("라이프 전문가")
        
        selected_service = st.selectbox(
            "서비스 선택",
            options=service_options,
            index=default_service_index,
            key="service_select"
        )
        
        # 서비스가 변경되면 세션 상태 업데이트
        if selected_service != st.session_state.get("service", ""):
            st.session_state.service = selected_service
            if 'function_logs' in st.session_state:
                st.session_state.function_logs.append(f"서비스 변경: {selected_service}")
        
        # 개발자 모드 토글
        st.subheader("개발자 모드")
        is_developer_mode = st.toggle("개발자 모드 활성화", key="developer_mode")
        
        if is_developer_mode:
            # 채팅 히스토리
            st.subheader("채팅 히스토리")
            chat_history = get_chat_history_from_api()
            if chat_history:
                df = pd.DataFrame(chat_history)
                if 'id' in df.columns:
                    df.set_index('id', inplace=True)
                # 역순으로 정렬하여 최신 메시지가 위에 표시되도록 함
                df = df.sort_index(ascending=False)
                
                # 표시할 컬럼 설정
                display_columns = ['question', 'answer']
                
                # 추가 정보가 있는 경우 컬럼에 추가
                if 'timestamp' in df.columns:
                    display_columns.append('timestamp')
                if 'service' in df.columns:
                    display_columns.append('service')
                if 'character' in df.columns:
                    display_columns.append('character')
                if 'knowledge_level' in df.columns:
                    display_columns.append('knowledge_level')
                if 'temperature' in df.columns:
                    display_columns.append('temperature')
                if 'quality_score' in df.columns:
                    display_columns.append('quality_score')
                
                # 컬럼 이름 한글화
                column_config = {
                    'question': '질문',
                    'answer': '답변'
                }
                
                if 'timestamp' in display_columns:
                    column_config['timestamp'] = '시간'
                if 'service' in display_columns:
                    column_config['service'] = '서비스'
                if 'character' in display_columns:
                    column_config['character'] = '캐릭터'
                if 'knowledge_level' in display_columns:
                    column_config['knowledge_level'] = '지식 수준'
                if 'temperature' in display_columns:
                    column_config['temperature'] = '온도'
                if 'quality_score' in display_columns:
                    column_config['quality_score'] = '품질 점수'
                
                # 번호 컬럼 추가
                df['번호'] = range(1, len(df) + 1)
                display_columns.insert(0, '번호')
                column_config['번호'] = '번호'
                
                st.dataframe(
                    df[display_columns],
                    column_config=column_config,
                    hide_index=True
                )
            else:
                st.info("현재 채팅 히스토리가 없습니다.")
                
            # 지식 레벨 통계
            st.subheader("지식 레벨 통계")
            knowledge_levels = {
                "초급": 30,
                "중급": 45,
                "고급": 25
            }
            st.bar_chart(knowledge_levels)
            
            # 사용자 온도 통계
            st.subheader("사용자 온도 통계")
            temperature_stats = {
                "낮음": 20,
                "보통": 50,
                "높음": 30
            }
            st.bar_chart(temperature_stats)
            
            # 응답 품질 통계
            st.subheader("응답 품질 통계")
            quality_stats = {
                "불만족": 10,
                "보통": 40,
                "만족": 50
            }
            st.bar_chart(quality_stats)
            
            # 함수 로그
            st.subheader("함수 로그")
            function_logs = [
                {"timestamp": "2024-03-20 10:00:00", "function": "get_chat_history", "status": "success"},
                {"timestamp": "2024-03-20 10:01:00", "function": "process_message", "status": "success"},
                {"timestamp": "2024-03-20 10:02:00", "function": "generate_response", "status": "error"}
            ]
            st.dataframe(function_logs)
        else:
            # 개발자 모드가 비활성화된 경우 기본 모델 사용
            model = "Azure AI Foundry (GPT-4.0)"
            st.session_state.model = model
    
    # 현재 선택된 캐릭터 반환
    character = st.session_state.get("character", "친절한 금자씨")
    
    return model, selected_service, character, is_developer_mode 