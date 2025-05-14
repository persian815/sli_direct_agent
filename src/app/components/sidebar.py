import streamlit as st
import pandas as pd
import logging
from src.data.personas_roles import PERSONAS
from src.data.services_roles import SERVICES
from src.data.users_data import USERS
from src.visualization.visualization import create_knowledge_distribution_graph, create_temperature_distribution_graph
from src.llm import aws_credentials_available, ms_credentials_available
from src.llm.ms_functions import test_ms_agent_connection, get_agent_config
from src.utils.utils import get_temperature_color, get_chat_history_from_api, get_role_specific_message
from src.app.components.chat import get_character_icon

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def render_sidebar():
    """사이드바를 렌더링합니다."""
    # 세션 상태 초기화
    if 'function_logs' not in st.session_state:
        st.session_state.function_logs = []
    
    # 최초 로드 시 Azure AI Foundry 선택 및 대화 초기화
    if 'is_first_load' not in st.session_state:
        st.session_state.is_first_load = True
        st.session_state.model = "Azure AI Foundry (GPT-4.0)"
        st.session_state.character = "친절한 미영시"
    
    # 기본 모델 설정
    model = st.session_state.get("model", "Azure AI Foundry (GPT-4.0)")
    
    # 서비스 선택 (화면에 표시하지 않음)
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
    
    # 서비스 선택 (화면에 표시하지 않음)
    # 서비스 선택 기능은 유지하되 화면에 표시하지 않음
    selected_service = service_options[default_service_index]
    
    # 서비스가 변경되면 세션 상태 업데이트
    if selected_service != st.session_state.get("service", ""):
        st.session_state.service = selected_service
        if 'function_logs' in st.session_state:
            st.session_state.function_logs.append(f"서비스 변경: {selected_service}")
    
    with st.sidebar:
        st.header("설정")
        
        # 개발자 모드 토글
        st.subheader("개발자 모드")
        is_developer_mode = st.toggle("개발자 모드 활성화", key="developer_mode")
        
        if is_developer_mode:
            # 선택된 사용자 정보 표시
            st.subheader("선택된 사용자")
            # 반드시 영문 id만 사용
            current_user = st.session_state.get("selected_user", "User1")
            user_kor_names = {
                "User1": "사용자 1",
                "User2": "사용자 2",
                "User3": "사용자 3",
                "User4": "사용자 4",
            }
            kor_display = user_kor_names.get(current_user, current_user)
            # 사용자 정보 조회 (영문 id로만!)
            user_info = USERS.get(current_user, {})
            if isinstance(user_info, list):
                user_info = user_info[0] if user_info else {}
            # 표시
            basic_info = user_info.get('기본정보', {})
            name = basic_info.get('이름', '')
            age = basic_info.get('나이', '')
            display_name = f"{name} ({age}세)" if name and age else kor_display
            st.markdown(f"**현재 선택된 사용자**: {display_name}")
            
            if user_info:
                # 기본정보
                if basic_info:
                    st.markdown("**기본정보**")
                    st.markdown(f"- 이름: {basic_info.get('이름', '')}")
                    st.markdown(f"- 나이: {basic_info.get('나이', '')}세")
                    st.markdown(f"- 성별: {basic_info.get('성별', '')}")
                    st.markdown(f"- 직업: {basic_info.get('직업', '')}")
                    st.markdown(f"- 가족구성: {basic_info.get('가족구성', '')}")
                    st.markdown(f"- 월수입: {basic_info.get('월수입', '')}")
                    st.markdown(f"- 월지출: {basic_info.get('월지출', '')}")
                    st.markdown(f"- 자산: {basic_info.get('자산', '')}")
                    st.markdown(f"- 부채: {basic_info.get('부채', '')}")
                
                # 건강검진정보
                health_info = user_info.get('건강검진정보', {})
                if health_info:
                    st.markdown("**건강검진정보**")
                    st.markdown(f"- 고혈압: {health_info.get('고혈압', '')}")
                    st.markdown(f"- 당뇨: {health_info.get('당뇨', '')}")
                    st.markdown(f"- 고지혈증: {health_info.get('고지혈증', '')}")
                    st.markdown(f"- 가족력: {health_info.get('가족력', '')}")
                
                # 보험가입내역
                insurance_info = user_info.get('보험가입내역', {})
                if insurance_info:
                    st.markdown("**보험가입내역**")
                    st.markdown(f"- 실손의료보험: {insurance_info.get('실손의료보험', '')}")
                    st.markdown(f"- 종합보험: {insurance_info.get('종합보험', '')}")
                    st.markdown(f"- 암보험: {insurance_info.get('암보험', '')}")
            else:
                st.warning(f"사용자 '{current_user}'의 정보를 찾을 수 없습니다.")
            
            st.divider()
            
            # 에이전트 설정 정보 표시
            st.subheader("에이전트 설정")
            # 현재 선택된 캐릭터의 agent_id와 thread_id를 가져옴
            current_character = st.session_state.get("character", "논리적인 테스형")
            character_info = PERSONAS.get(current_character, {})
            agent_id = character_info.get("agent_id", "")
            thread_id = character_info.get("thread_id", "")
            agent_name = character_info.get("agent_name", "통합 전문가")  # agent_name 가져오기
            
            st.code(f"Agent Name: {agent_name}\nAgent ID: {agent_id}\nThread ID: {thread_id}", language="text")
            
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
                    column_config['knowledge_level'] = '지식 레벨'
                if 'temperature' in display_columns:
                    column_config['temperature'] = '온도'
                if 'quality_score' in display_columns:
                    column_config['quality_score'] = '품질 점수'
                
                # 데이터프레임 표시
                st.dataframe(
                    df[display_columns],
                    column_config=column_config,
                    use_container_width=True
                )
            else:
                st.info("채팅 히스토리가 없습니다.")
            
            # 지식 레벨 통계
            st.subheader("지식 레벨 통계")
            # 기본 지식 레벨 데이터 설정 - List[int] 타입으로 변환
            knowledge_levels_data = [30, 45, 25]  # 초급, 중급, 고급 순서로 값 설정
            knowledge_graph = create_knowledge_distribution_graph(knowledge_levels_data)
            st.plotly_chart(knowledge_graph, use_container_width=True)
            
            # 사용자 온도 통계
            st.subheader("사용자 온도 통계")
            # 기본 온도 데이터 설정 - List[float] 타입으로 변환
            temperature_data = [36.0, 36.5, 37.0, 37.5, 38.0]  # 예시 온도 데이터
            temperature_graph = create_temperature_distribution_graph(temperature_data)
            st.plotly_chart(temperature_graph, use_container_width=True)
            
            # 응답 품질 통계
            st.subheader("응답 품질 통계")
            quality_scores = [0.8, 0.9, 0.7, 0.85, 0.95, 0.75, 0.8, 0.9, 0.85, 0.8]
            quality_df = pd.DataFrame({
                '응답 품질': quality_scores
            })
            st.bar_chart(quality_df)
            
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
    
    # 현재 선택된 캐릭터
    current_character = st.session_state.get("character", "논리적인 테스형")
    
    # 캐릭터 선택 옵션
    character_options = list(PERSONAS.keys())
    
    # 셀렉트박스로 캐릭터 선택
    selected_character = st.selectbox(
        label="캐릭터 선택",
        options=character_options,
        index=character_options.index(current_character) if current_character in character_options else 0,
        key="sidebar_character_select",
        label_visibility="collapsed"
    )
    
    # 선택된 캐릭터가 변경되었으면 세션 상태 업데이트
    if selected_character != current_character:
        # 캐릭터 변경 시 세션 상태 초기화
        st.session_state.character = selected_character
        st.session_state.messages = []  # 대화 내용 초기화
        st.session_state.is_generating = False
        
        # 캐릭터 변경 시 role 업데이트
        current_character = st.session_state.character
        character_info = PERSONAS.get(current_character, {})
        st.session_state.role = character_info.get("agent_name", "통합 전문가")
        
        # 캐릭터 변경 시 아바타 이미지 업데이트
        st.session_state.avatar_image = get_character_icon(current_character)
        
        # 캐릭터 변경 시 messages 초기화 및 새로운 웰컴 메시지 추가
        agent_name = selected_character
        agent_role = st.session_state.role
        
        # 역할별 맞춤 환영 메시지 생성
        role_specific_message = get_role_specific_message(agent_role)

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"""안녕하세요! 저는 {agent_name}이에요. {agent_role}로서 고객님을 만나게 되어 정말 반가워요.\n

{character_info.get('welcome_message', '').replace('[', '').replace(']', '')}

{role_specific_message} 편하게 말씀해 주세요! 😊""",
            "metrics": {
                "request_time": 0,
                "response_time": 0,
                "input_tokens": 0,
                "output_tokens": 0
            }
        })
        
        # 개발자 모드 초기화를 위해 페이지 리로드
        st.rerun()
    
    return model, selected_service, selected_character, None 