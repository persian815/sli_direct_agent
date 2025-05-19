import streamlit as st
import os
import time
import logging
from typing import Dict, Optional, Tuple, List
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from src.data.personas_roles import PERSONAS
from src.data.users_data import USERS

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 환경 설정
IS_LOCAL = os.getenv('ENV', 'local') == 'local'

# Azure AI Foundry 연결 정보
AZURE_ENDPOINT = "https://eastus2.api.azureml.ms"
AZURE_SUBSCRIPTION_ID = "2326c76a-5eab-44b6-808b-1978f2ffee0e"
AZURE_RESOURCE_GROUP = "slihackathon-2025-team2-rg"
AZURE_PROJECT_NAME = "team2_seongryongle-8914"

# 기본 에이전트 설정
DEFAULT_AGENT_ID = "asst_YVPGAmrKz41p7l5LlsBhJ661"
DEFAULT_THREAD_ID = "thread_M7udZoEMzmXQJDoHfleNS5ng"
DEFAULT_ROLE = "통합 전문가"
DEFAULT_CHARACTER = "친절한 미영씨"
DEFAULT_USER = "User1"

# 캐싱을 위한 전역 변수
_cached_agent = None
_thread_cache = {}

def initialize_azure_client() -> Tuple[bool, Optional[AIProjectClient]]:
    """Azure AI Foundry 클라이언트를 초기화합니다."""
    try:
        credential = _get_credential()
        project_client = AIProjectClient(
            endpoint=AZURE_ENDPOINT,
            credential=credential,
            subscription_id=AZURE_SUBSCRIPTION_ID,
            resource_group_name=AZURE_RESOURCE_GROUP,
            project_name=AZURE_PROJECT_NAME
        )
        logger.info("Azure AI Foundry 클라이언트 초기화 성공")
        return True, project_client
    except Exception as e:
        logger.error(f"Azure AI Foundry 클라이언트 초기화 실패: {str(e)}")
        return False, None

def _get_credential():
    """환경에 따른 적절한 인증 방식을 반환합니다."""
    if os.getenv('AZURE_AI_FOUNDRY_API_KEY'):
        logger.info("DefaultAzureCredential을 사용하여 인증합니다.")
        return DefaultAzureCredential()
    elif IS_LOCAL:
        logger.info("로컬 환경에서 DefaultAzureCredential을 사용하여 인증합니다.")
        return DefaultAzureCredential()
    else:
        logger.info("Azure 환경에서 ManagedIdentityCredential을 사용하여 인증합니다.")
        return ManagedIdentityCredential()

def get_cached_agent() -> Optional[AIProjectClient]:
    """캐시된 에이전트를 반환하거나 새로 생성합니다."""
    global _cached_agent
    if _cached_agent is None:
        try:
            agent_config = get_agent_config()
            _cached_agent = project_client.agents.get_agent(agent_config["agent_id"])
            logger.info(f"에이전트 캐시 생성 완료: {_cached_agent.id}")
        except Exception as e:
            logger.error(f"에이전트 캐시 생성 실패: {str(e)}")
            _cached_agent = project_client.agents.get_agent(DEFAULT_AGENT_ID)
            logger.info(f"기본 에이전트 사용: {DEFAULT_AGENT_ID}")
    return _cached_agent

def get_or_create_thread(session_id: str) -> AIProjectClient:
    """세션 ID에 해당하는 스레드를 반환하거나 새로 생성합니다."""
    if session_id not in _thread_cache:
        try:
            _thread_cache[session_id] = project_client.agents.create_thread()
            logger.info(f"새로운 스레드 생성 완료: {_thread_cache[session_id].id}")
        except Exception as e:
            logger.error(f"스레드 생성 실패: {str(e)}")
            _thread_cache[session_id] = project_client.agents.get_thread(DEFAULT_THREAD_ID)
            logger.info(f"기본 스레드 사용: {DEFAULT_THREAD_ID}")
    return _thread_cache[session_id]

def get_agent_config(service: Optional[str] = None) -> Dict[str, str]:
    """현재 선택된 서비스와 캐릭터에 따라 에이전트 설정을 반환합니다."""
    service = service or st.session_state.get("service", DEFAULT_ROLE)
    character = st.session_state.get("character", DEFAULT_CHARACTER)
    character_info = PERSONAS.get(character, {})
    
    agent_id = character_info.get("agent_id", DEFAULT_AGENT_ID)
    thread_id = character_info.get("thread_id", DEFAULT_THREAD_ID)
    
    if any('\u4e00' <= char <= '\u9fff' for char in agent_id):
        logger.warning(f"한글 에이전트 ID 감지: {agent_id}, 기본 에이전트 ID로 대체")
        agent_id = DEFAULT_AGENT_ID
    
    logger.info(f"캐릭터 '{character}'에 대한 에이전트 설정: agent_id={agent_id}, thread_id={thread_id}")
    return {"agent_id": agent_id, "thread_id": thread_id}

def _format_user_info(user_info: Dict) -> str:
    """사용자 정보를 문자열로 포맷팅합니다."""
    if not user_info:
        return ""
        
    user_data = []
    
    # 기본정보
    basic_info = user_info.get('기본정보', {})
    if basic_info:
        user_data.append("사용자 기본정보:")
        for key, value in basic_info.items():
            user_data.append(f"- {key}: {value}")
    
    # 건강검진정보
    health_info = user_info.get('건강검진정보', {})
    if health_info:
        user_data.append("\n건강검진정보:")
        for key, value in health_info.items():
            user_data.append(f"- {key}: {value}")
    
    # 보험가입내역
    insurance_info = user_info.get('보험가입내역', [])
    if isinstance(insurance_info, list) and insurance_info:
        user_data.append("\n보험가입내역:")
        for item in insurance_info:
            user_data.append(
                f"- {item.get('상품명', '')} / {item.get('보장급부', '')} / "
                f"{item.get('보장내용', '')} / 보장금액: {item.get('보장금액(만원)', '')}만원 / "
                f"보험료: {item.get('보험료(만원)', '')}만원\n  설명: {item.get('설명', '')}"
            )
    elif isinstance(insurance_info, dict):
        user_data.append("\n보험가입내역:")
        for key, value in insurance_info.items():
            user_data.append(f"- {key}: {value}")
    
    return "\n".join(user_data)

def _extract_response_text(messages) -> str:
    """메시지 객체에서 응답 텍스트를 추출합니다."""
    if not messages or not hasattr(messages, 'text_messages') or not messages.text_messages:
        return "죄송합니다. 응답을 생성하는 데 문제가 발생했습니다."
        
    first_message = messages.text_messages[0]
    logger.debug(f"첫 번째 메시지 타입: {type(first_message)}")
    logger.debug(f"첫 번째 메시지 내용: {first_message}")
    
    if hasattr(first_message, 'as_dict'):
        message_dict = first_message.as_dict()
        logger.debug(f"메시지 딕셔너리: {message_dict}")
        
        if 'text' in message_dict:
            text_obj = message_dict['text']
            if isinstance(text_obj, dict) and 'value' in text_obj:
                return text_obj['value']
            if isinstance(text_obj, str):
                return text_obj
        if 'content' in message_dict and isinstance(message_dict['content'], str):
            return message_dict['content']
    elif hasattr(first_message, 'content'):
        return first_message.content
    elif isinstance(first_message, str):
        return first_message
        
    return "죄송합니다. 응답을 생성하는 데 문제가 발생했습니다."

def query_ms_agent(input_text: str, tab_id: Optional[str] = None, system_prompt: Optional[str] = None) -> Tuple[str, List, float, float, float, float]:
    """Azure AI Foundry (GPT4.0)를 사용하여 질문에 답변합니다."""
    if not ms_credentials_available:
        return "Azure AI Foundry 자격증명이 설정되지 않았습니다.", [], 0, 0, 0, 0

    # 세션 상태 초기화
    if "role" not in st.session_state:
        st.session_state.role = DEFAULT_ROLE
    if "character" not in st.session_state:
        st.session_state.character = DEFAULT_CHARACTER

    start_time = time.time()

    try:
        # 에이전트와 스레드 준비
        agent = get_cached_agent()
        thread = get_or_create_thread(tab_id or "default")
        
        # 사용자 정보 준비
        user = st.session_state.get("user", DEFAULT_USER)
        if user not in USERS:
            logger.warning(f"user({user})가 USERS에 없습니다. User1로 fallback.")
            user = DEFAULT_USER
            
        user_info = USERS.get(user, {}).get('info', {})
        if isinstance(user_info, list):
            user_info = user_info[0] if user_info else {}
            
        # 메시지 구성
        user_data = _format_user_info(user_info)
        final_message = f"{user_data}\n\n질문: {input_text}" if user_data else f"질문: {input_text}"
        
        # API 호출
        user_message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=final_message
        )
        time.sleep(0.2)
        
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        messages = project_client.agents.list_messages(thread_id=thread.id)
        response_text = _extract_response_text(messages)
        
        # 결과 계산
        elapsed_time = time.time() - start_time
        input_tokens = len(input_text.split()) // 1.3
        output_tokens = len(response_text.split()) // 1.3
        
        logger.info(f"응답 생성 완료 (경과 시간: {elapsed_time:.2f}초)")
        return response_text, [], elapsed_time, input_tokens, output_tokens, start_time

    except Exception as e:
        logger.error(f"API 호출 중 오류 발생: {str(e)}")
        logger.error(f"오류 상세 정보: {type(e).__name__}")
        elapsed_time = time.time() - start_time
        return f"서비스에 문제가 발생했습니다: {str(e)}", [], elapsed_time, 0, 0, start_time

# Azure AI Foundry 클라이언트 초기화
ms_credentials_available, project_client = initialize_azure_client()

def test_ms_agent_connection():
    """Azure AI Foundry 에이전트 연결 테스트 함수"""
    try:
        logger.debug("에이전트 연결 테스트 시작")
        
        # 에이전트 설정 가져오기
        agent_config = get_agent_config()
        agent_id = agent_config["agent_id"]
        logger.debug(f"에이전트 설정 가져오기: {agent_id}")
        
        # 에이전트 가져오기
        agent = project_client.agents.get_agent(agent_id)
        logger.debug(f"에이전트 가져오기 완료: {agent.id}")
        
        # 요청 간 지연 시간 추가 (충돌 방지)
        time.sleep(0.2)
        
        # 새로운 스레드 생성
        thread = project_client.agents.create_thread()
        logger.debug(f"스레드 생성 완료: {thread.id}")
        
        logger.info(f"Azure AI Foundry 에이전트 연결 성공 (에이전트: {agent.name}, 스레드: {thread.id})")
        return True, f"Azure AI Foundry 에이전트 연결 성공 (에이전트: {agent.name}, 스레드: {thread.id})"
    except Exception as e:
        logger.error(f"Azure AI Foundry 에이전트 연결 실패: {str(e)}")
        return False, f"Azure AI Foundry 에이전트 연결 실패: {str(e)}"

def main():
    # 순환참조 방지: 필요한 시점에만 import
    from ..app.components.character_select import render_character_select
    from ..app.components.chat import render_chat_interface

    # 세션 상태 초기화 (필요한 상태만 초기화)
    if "selected_character" not in st.session_state:
        st.session_state.selected_character = None
    
    if "role" not in st.session_state:
        st.session_state.role = "통합 전문가"  # 기본 역할 설정
    
    if "character" not in st.session_state:
        st.session_state.character = "친절한 미영씨"  # 기본 캐릭터 설정

    # user 세션 상태는 초기화하지 않음 (선택된 사용자 정보 유지)

    if st.session_state.selected_character is None:
        render_character_select()
    else:
        render_chat_interface(model="Azure AI Foundry (GPT-4.0)")

if __name__ == "__main__":
    main()
