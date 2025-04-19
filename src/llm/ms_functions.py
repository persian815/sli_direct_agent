import streamlit as st
import os
import time
import json
import logging
from typing import Dict, List, Tuple, Any, Optional
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from src.data.services_roles import SERVICES
from src.data.personas_roles import PERSONAS

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 환경 설정
IS_LOCAL = os.getenv('ENV', 'local') == 'local'

# agent 디폴트 (통합 전문가)
MS_AGENT_ID = "asst_qdDOMuZzZCDaBTw4MDEwmlMf"
MS_THREAD_ID = "thread_bKzWFyvSbJOgtfDtXtBpf03x"

# 캐싱을 위한 전역 변수
_cached_agent = None
_thread_cache = {}

def get_cached_agent():
    global _cached_agent
    if _cached_agent is None:
        agent_config = get_agent_config()
        _cached_agent = project_client.agents.get_agent(agent_config["agent_id"])
    return _cached_agent

def get_or_create_thread(session_id):
    if session_id not in _thread_cache:
        _thread_cache[session_id] = project_client.agents.create_thread()
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
    character = st.session_state.get("character", "친절한 금자씨")
    
    # 캐릭터 정보 가져오기
    character_info = PERSONAS.get(character, {})
    
    # 캐릭터에 정의된 agent_id와 thread_id 사용
    agent_id = character_info.get("agent_id", MS_AGENT_ID)  # 기본값으로 통합 전문가 ID 사용
    thread_id = character_info.get("thread_id", MS_THREAD_ID)  # 기본값으로 통합 전문가 스레드 ID 사용
    
    logger.info(f"캐릭터 '{character}'에 대한 에이전트 설정: agent_id={agent_id}, thread_id={thread_id}")
    
    return {
        "agent_id": agent_id,
        "thread_id": thread_id
    }

# Azure AI Foundry 연결 정보
MS_CONNECTION_STRING = "eastus2.api.azureml.ms;2326c76a-5eab-44b6-808b-1978f2ffee0e;slihackathon-2025-team2-rg;team2_seongryongle-8914"

# Azure AI Foundry 클라이언트 초기화
try:
    # API 키를 사용하여 인증
    if os.getenv('AZURE_AI_FOUNDRY_API_KEY'):
        # API 키가 설정된 경우 API 키를 사용
        # from azure.core.credentials import AzureKeyCredential
        #credential = AzureKeyCredential(os.getenv('AZURE_AI_FOUNDRY_API_KEY'))
        credential = os.getenv('AZURE_AI_FOUNDRY_API_KEY')
        logger.info("Azure AI Foundry API 키를 사용하여 인증합니다.")
    else:
        # API 키가 설정되지 않은 경우 관리 ID를 사용
        if IS_LOCAL:
            # 로컬 환경에서는 DefaultAzureCredential 사용
            credential = DefaultAzureCredential()
            logger.info("로컬 환경에서 DefaultAzureCredential을 사용하여 인증합니다.")
        else:
            # Azure 환경에서는 ManagedIdentityCredential 사용
            credential = ManagedIdentityCredential()
            logger.info("Azure 환경에서 ManagedIdentityCredential을 사용하여 인증합니다.")
    
    project_client = AIProjectClient.from_connection_string(
        credential=credential,
        conn_str=MS_CONNECTION_STRING
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

    # 시작 시간 기록
    start_time = time.time()

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
        service_prompt = SERVICES.get(role, {}).get('prompt', '')
        persona_prompt = PERSONAS.get(character, {}).get('prompt', '')
        
        # 프롬프트 간소화
        input_texts = f"{service_prompt} {persona_prompt} 질문: {input_text}"
        logger.debug(f"입력 텍스트 준비 완료")

        # 사용자 메시지 생성
        user_message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=input_texts
        )
        logger.debug(f"사용자 메시지 생성 완료: {user_message.id}")

        # 최소한의 지연만 사용
        time.sleep(0.2)  # 필요한 경우에만 최소한의 지연

        # 실행 생성 및 처리
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        logger.debug(f"실행 생성 및 처리 완료: {run.id}")

        # 메시지 목록 가져오기
        messages = project_client.agents.list_messages(thread_id=thread.id)
        
        # 응답 텍스트 추출
        response_text = ""
        if messages.text_messages:
            first_message = messages.text_messages[0]
            message_dict = first_message.as_dict()
            if 'text' in message_dict and isinstance(message_dict['text'], dict) and 'value' in message_dict['text']:
                response_text = message_dict['text']['value']

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
