import streamlit as st
import os
import time
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.core.credentials import AzureKeyCredential, TokenCredential
from src.data.services_roles import SERVICES
from src.data.personas_roles import PERSONAS
from src.data.users_data import USERS

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 환경 설정
IS_LOCAL = os.getenv('ENV', 'local') == 'local'

# agent 디폴트 (통합 전문가)
MS_AGENT_ID = "asst_YVPGAmrKz41p7l5LlsBhJ661"  # 기본 에이전트 ID
MS_THREAD_ID = "thread_M7udZoEMzmXQJDoHfleNS5ng"  # 기본 스레드 ID

# 캐싱을 위한 전역 변수
_cached_agent = None
_thread_cache = {}

# Azure AI Foundry 연결 정보
AZURE_ENDPOINT = "https://eastus2.api.azureml.ms"
AZURE_SUBSCRIPTION_ID = "2326c76a-5eab-44b6-808b-1978f2ffee0e"
AZURE_RESOURCE_GROUP = "slihackathon-2025-team2-rg"
AZURE_PROJECT_NAME = "team2_seongryongle-8914"

def get_cached_agent():
    global _cached_agent
    if _cached_agent is None:
        try:
            agent_config = get_agent_config()
            _cached_agent = project_client.agents.get_agent(agent_config["agent_id"])
            logger.info(f"에이전트 캐시 생성 완료: {_cached_agent.id}")
        except Exception as e:
            logger.error(f"에이전트 캐시 생성 실패: {str(e)}")
            # 기본 에이전트 사용
            _cached_agent = project_client.agents.get_agent(MS_AGENT_ID)
            logger.info(f"기본 에이전트 사용: {MS_AGENT_ID}")
    return _cached_agent

def get_or_create_thread(session_id):
    if session_id not in _thread_cache:
        try:
            _thread_cache[session_id] = project_client.agents.create_thread()
            logger.info(f"새로운 스레드 생성 완료: {_thread_cache[session_id].id}")
        except Exception as e:
            logger.error(f"스레드 생성 실패: {str(e)}")
            # 기본 스레드 사용
            _thread_cache[session_id] = project_client.agents.get_thread(MS_THREAD_ID)
            logger.info(f"기본 스레드 사용: {MS_THREAD_ID}")
    return _thread_cache[session_id]

# 에이전트 ID와 스레드 ID 가져오기
def get_agent_config(service=None):
    """
    현재 선택된 서비스와 캐릭터에 따라 에이전트 설정을 반환하는 함수
    
    Args:
        service (str, optional): 서비스 이름. 기본값은 None으로, 세션 상태에서 가져옵니다.
    
    Returns:
        dict: agent_id와 thread_id를 포함하는 딕셔너리
    """
    # 서비스가 지정되지 않은 경우 세션 상태에서 가져오기
    if service is None:
        service = st.session_state.get("service", "통합 전문가")
    
    # 현재 선택된 캐릭터 가져오기
    character = st.session_state.get("character", "친절한 미영씨")
    
    # 캐릭터 정보 가져오기
    character_info = PERSONAS.get(character, {})
    
    # 캐릭터에 정의된 agent_id와 thread_id 사용
    agent_id = character_info.get("agent_id", MS_AGENT_ID)  # 기본값으로 통합 전문가 ID 사용
    thread_id = character_info.get("thread_id", MS_THREAD_ID)  # 기본값으로 통합 전문가 스레드 ID 사용
    
    # agent_id가 한글인 경우 기본 에이전트 ID 사용
    if any('\u4e00' <= char <= '\u9fff' for char in agent_id):
        logger.warning(f"한글 에이전트 ID 감지: {agent_id}, 기본 에이전트 ID로 대체")
        agent_id = MS_AGENT_ID
    
    logger.info(f"캐릭터 '{character}'에 대한 에이전트 설정: agent_id={agent_id}, thread_id={thread_id}")
    
    return {
        "agent_id": agent_id,
        "thread_id": thread_id
    }

# Azure AI Foundry 연결 정보
MS_CONNECTION_STRING = "eastus2.api.azureml.ms;2326c76a-5eab-44b6-808b-1978f2ffee0e;slihackathon-2025-team2-rg;team2_seongryongle-8914"

# Azure AI Foundry 클라이언트 초기화
try:
    if os.getenv('AZURE_AI_FOUNDRY_API_KEY'):
        # API 키가 설정된 경우 DefaultAzureCredential 사용
        credential = DefaultAzureCredential()
        logger.info("DefaultAzureCredential을 사용하여 인증합니다.")
    elif IS_LOCAL:
        credential = DefaultAzureCredential()
        logger.info("로컬 환경에서 DefaultAzureCredential을 사용하여 인증합니다.")
    else:
        credential = ManagedIdentityCredential()
        logger.info("Azure 환경에서 ManagedIdentityCredential을 사용하여 인증합니다.")

    project_client = AIProjectClient(
        endpoint=AZURE_ENDPOINT,
        credential=credential,
        subscription_id=AZURE_SUBSCRIPTION_ID,
        resource_group_name=AZURE_RESOURCE_GROUP,
        project_name=AZURE_PROJECT_NAME
    )
    ms_credentials_available = True
    logger.info("Azure AI Foundry 클라이언트 초기화 성공")
except Exception as e:
    ms_credentials_available = False
    logger.error(f"Azure AI Foundry 클라이언트 초기화 실패: {str(e)}")

def extract_text_from_message(message):
    """
    메시지 객체에서 텍스트를 추출하는 함수
    다양한 메시지 구조를 처리할 수 있도록 설계됨
    """
    try:
        # 메시지가 문자열인 경우 바로 반환
        if isinstance(message, str):
            return message
            
        # 메시지 객체를 딕셔너리로 변환 시도
        try:
            message_dict = vars(message)
        except (TypeError, AttributeError):
            # vars() 함수를 사용할 수 없는 경우 (문자열 등)
            return str(message)
            
        # content 키가 있는지 확인
        if 'content' in message_dict:
            content = message_dict['content']
            
            # content가 문자열인 경우
            if isinstance(content, str):
                return content
            
            # content가 리스트인 경우
            if isinstance(content, list):
                for item in content:
                    # 항목이 딕셔너리인 경우
                    if isinstance(item, dict):
                        # text 키가 있는지 확인
                        if 'text' in item:
                            text_obj = item['text']
                            
                            # text가 딕셔너리인 경우 value 키 확인
                            if isinstance(text_obj, dict):
                                if 'value' in text_obj:
                                    return text_obj['value']
                            
                            # text가 문자열인 경우
                            if isinstance(text_obj, str):
                                return text_obj
                        
                        # type이 text이고 text 키가 있는 경우
                        if 'type' in item and item['type'] == 'text' and 'text' in item:
                            text_obj = item['text']
                            if isinstance(text_obj, dict) and 'value' in text_obj:
                                return text_obj['value']
                    
                    # 항목이 문자열인 경우
                    if isinstance(item, str):
                        return item
        
        # text 키가 있는지 확인
        if 'text' in message_dict:
            text_obj = message_dict['text']
            if isinstance(text_obj, dict) and 'value' in text_obj:
                return text_obj['value']
            if isinstance(text_obj, str):
                return text_obj
        
        # 모든 방법이 실패한 경우 메시지 객체를 문자열로 변환
        return str(message)
    except Exception as e:
        logger.error(f"메시지 텍스트 추출 중 오류 발생: {str(e)}")
        return str(message)

def query_ms_agent(input_text, tab_id=None, system_prompt=None):
    """Azure AI Foundry (GPT4.0)를 사용하여 질문에 답변하는 함수"""
    if not ms_credentials_available:
        return "Azure AI Foundry 자격증명이 설정되지 않았습니다.", [], 0, 0, 0, 0

    # 세션 상태 초기화
    if "role" not in st.session_state:
        st.session_state.role = "통합 전문가"
    if "character" not in st.session_state:
        st.session_state.character = "친절한 미영씨"
    # user 세션 상태는 초기화하지 않음 (선택된 사용자 정보 유지)

    # 시작 시간 기록
    start_time = time.time()

    persona_prompt = ""
    try:
        # 캐시된 에이전트 사용
        agent = get_cached_agent()
        logger.info(f"에이전트 가져오기 완료: {agent.id}")

        # 세션별 스레드 재사용
        thread = get_or_create_thread(tab_id or "default")
        logger.debug(f"스레드 준비 완료: {thread.id}")

        # 프롬프트 최적화
        role = st.session_state.role
        character = st.session_state.character
        user = st.session_state.get("user", "User1")  # 기본값으로 User1 사용
        selected_user = st.session_state.get("selected_user", "")
        logger.debug(f"query_ms_agent - 현재 선택된 사용자 ID: {user}")
        logger.debug(f"query_ms_agent - 선택된 사용자 표시명: {selected_user}")
        logger.debug(f"USERS 키 목록: {list(USERS.keys())}")
        if user not in USERS:
            logger.warning(f"user({user})가 USERS에 없습니다. User1로 fallback.")
            user = "User1"
        # 사용자 정보 가져오기
        logger.debug(f"USERS 데이터: {USERS}")
        user_info = USERS.get(user, {}).get('info', {})
        if isinstance(user_info, list):
            user_info = user_info[0] if user_info else {}
        logger.debug(f"사용자 정보: {user_info}")
        
        # 사용자 정보를 간단한 문자열로 변환
        user_data = ""
        if user_info:
            # 기본정보
            basic_info = user_info.get('기본정보', {})
            if basic_info:
                user_data += f"사용자 기본정보:\n"
                user_data += f"- 이름: {basic_info.get('이름', '')}\n"
                user_data += f"- 나이: {basic_info.get('나이', '')}세\n"
                user_data += f"- 성별: {basic_info.get('성별', '')}\n"
                user_data += f"- 직업: {basic_info.get('직업', '')}\n"
                user_data += f"- 가족구성: {basic_info.get('가족구성', '')}\n"
                user_data += f"- 월수입: {basic_info.get('월수입', '')}\n"
                user_data += f"- 월지출: {basic_info.get('월지출', '')}\n"
                user_data += f"- 자산: {basic_info.get('자산', '')}\n"
                user_data += f"- 부채: {basic_info.get('부채', '')}\n"
            
            # 건강검진정보
            health_info = user_info.get('건강검진정보', {})
            if health_info:
                user_data += f"\n건강검진정보:\n"
                user_data += f"- 고혈압: {health_info.get('고혈압', '')}\n"
                user_data += f"- 당뇨: {health_info.get('당뇨', '')}\n"
                user_data += f"- 고지혈증: {health_info.get('고지혈증', '')}\n"
                user_data += f"- 가족력: {health_info.get('가족력', '')}\n"
            
            # 보험가입내역
            insurance_info = user_info.get('보험가입내역', [])
            if isinstance(insurance_info, list) and insurance_info:
                user_data += f"\n보험가입내역:\n"
                for item in insurance_info:
                    상품명 = item.get('상품명', '')
                    보장급부 = item.get('보장급부', '')
                    보장내용 = item.get('보장내용', '')
                    보장금액 = item.get('보장금액(만원)', '')
                    보험료 = item.get('보험료(만원)', '')
                    설명 = item.get('설명', '')
                    user_data += f"- {상품명} / {보장급부} / {보장내용} / 보장금액: {보장금액}만원 / 보험료: {보험료}만원\n  설명: {설명}\n"
            elif isinstance(insurance_info, dict):
                user_data += f"\n보험가입내역:\n"
                user_data += f"- 실손의료보험: {insurance_info.get('실손의료보험', '')}\n"
                user_data += f"- 종합보험: {insurance_info.get('종합보험', '')}\n"
                user_data += f"- 암보험: {insurance_info.get('암보험', '')}\n"
        
        logger.debug(f"구성된 사용자 데이터: {user_data}")
        
        # 메시지 형식 단순화
        input_texts = input_text  # 원본 질문만 사용
        
        # 최종 메시지 구성
        final_message = ""
        if user_data:
            final_message += f"{user_data}\n\n"
        if persona_prompt:
            final_message += f"{persona_prompt}\n\n"
        final_message += f"질문: {input_texts}"
        
        logger.debug(f"입력 텍스트 준비 완료")
        logger.debug(f"캐릭터 프롬프트: {persona_prompt}")
        logger.debug(f"사용자 정보: {user_data}")
        logger.debug(f"최종 메시지: {final_message}")

        try:
            # 사용자 메시지 생성
            user_message = project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=final_message
            )
            logger.debug(f"사용자 메시지 생성 완료: {user_message.id}")

            # 최소한의 지연
            time.sleep(0.2)

            # 실행 생성 및 처리
            run = project_client.agents.create_and_process_run(
                thread_id=thread.id,
                agent_id=agent.id
            )
            logger.debug(f"실행 생성 및 처리 완료: {run.id}")

            # 메시지 목록 가져오기
            messages = project_client.agents.list_messages(thread_id=thread.id)
            logger.debug(f"메시지 목록 가져오기 완료: {len(messages.text_messages) if hasattr(messages, 'text_messages') else 0}개 메시지")
            
            # 응답 텍스트 추출
            response_text = ""
            if messages and hasattr(messages, 'text_messages') and messages.text_messages:
                first_message = messages.text_messages[0]
                logger.debug(f"첫 번째 메시지 타입: {type(first_message)}")
                logger.debug(f"첫 번째 메시지 내용: {first_message}")
                
                if hasattr(first_message, 'as_dict'):
                    message_dict = first_message.as_dict()
                    logger.debug(f"메시지 딕셔너리: {message_dict}")
                    
                    if 'text' in message_dict and isinstance(message_dict['text'], dict) and 'value' in message_dict['text']:
                        response_text = message_dict['text']['value']
                    elif 'text' in message_dict and isinstance(message_dict['text'], str):
                        response_text = message_dict['text']
                    elif 'content' in message_dict and isinstance(message_dict['content'], str):
                        response_text = message_dict['content']
                elif hasattr(first_message, 'content'):
                    response_text = first_message.content
                elif isinstance(first_message, str):
                    response_text = first_message

            if not response_text:
                response_text = "죄송합니다. 응답을 생성하는 데 문제가 발생했습니다."
                logger.warning("응답 텍스트가 비어있습니다.")

            # 경과 시간 계산
            elapsed_time = time.time() - start_time
            
            # 토큰 수 추정
            input_tokens = len(input_text.split()) // 1.3
            output_tokens = len(response_text.split()) // 1.3

            logger.info(f"응답 생성 완료 (경과 시간: {elapsed_time:.2f}초)")
            return response_text, [], elapsed_time, input_tokens, output_tokens, start_time

        except Exception as e:
            logger.error(f"API 호출 중 오류 발생: {str(e)}")
            logger.error(f"오류 상세 정보: {type(e).__name__}")
            elapsed_time = time.time() - start_time
            return f"서비스에 문제가 발생했습니다: {str(e)}", [], elapsed_time, 0, 0, start_time

    except Exception as e:
        logger.error(f"API 호출 중 오류 발생: {str(e)}")
        elapsed_time = time.time() - start_time
        return f"서비스에 문제가 발생했습니다: {str(e)}", [], elapsed_time, 0, 0, start_time

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
