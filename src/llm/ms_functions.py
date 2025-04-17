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

# agent
MS_AGENT_ID = "asst_U5EvVPTcw0kO5XkvENF1k9dF"
MS_THREAD_ID = "thread_lsizSBgblCuAXVZh8UVXLuIR"


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
        return "Azure AI Foundry 자격증명이 설정되지 않았습니다. ms_functions.py 파일에서 MS_CONNECTION_STRING 값을 설정하세요.", [], 0, 0, 0, 0

    # 시스템 프롬프트 추가
    if system_prompt is None:
        if tab_id and tab_id in st.session_state.tab_system_prompts:
            system_prompt = st.session_state.tab_system_prompts[tab_id]
        else:
            # 기본 시스템 프롬프트 사용
            system_prompt = "당신은 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 정확하고 유용한 정보를 제공하세요."

    # 서비스 및 페르소나 프롬프트 추가
    role = st.session_state.role
    character = st.session_state.character
    service_prompt = SERVICES.get(role, {}).get('prompt', '')
    persona_prompt = PERSONAS.get(character, {}).get('prompt', '')
    system_prompt += f"\n\n서비스 프롬프트: {service_prompt}\n페르소나 프롬프트: {persona_prompt}"

    # 시작 시간 기록
    start_time = time.time()

    # 최대 재시도 횟수
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.debug("에이전트 가져오기 시작")
            # 에이전트 가져오기
            agent = project_client.agents.get_agent(MS_AGENT_ID)
            logger.debug(f"에이전트 가져오기 완료: {agent.id}")
            
            # 요청 간 지연 시간 추가 (충돌 방지)
            time.sleep(1)
            
            logger.debug("스레드 생성 시작")
            # 매 요청마다 새로운 스레드 생성
            thread = project_client.agents.create_thread()
            logger.debug(f"스레드 생성 완료: {thread.id}")
            
            # 요청 간 지연 시간 추가 (충돌 방지)
            time.sleep(1)
            
            logger.debug("사용자 메시지 생성 시작")

            # 시스템 프롬프트 추가
            input_texts = f"\n\n다음과 같이 전문분야의 캐릭터로 답변해줘 \n {service_prompt}\n {persona_prompt} \n 사용자 메시지 : {input_text}"

            logger.debug(f"$$$$$input_texts : {input_texts}")

            # 사용자 메시지 생성 - system_prompt 매개변수 제거
            user_message = project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=input_texts
            )
            logger.debug(f"사용자 메시지 생성 완료: {user_message.id}")
            
            # 요청 간 지연 시간 추가 (충돌 방지)
            time.sleep(1)
            
            logger.debug("실행 생성 및 처리 시작")
            # 실행 생성 및 처리
            run = project_client.agents.create_and_process_run(
                thread_id=thread.id,
                agent_id=agent.id
            )
            logger.debug(f"실행 생성 및 처리 완료: {run.id}")
            
            # 요청 간 지연 시간 추가 (충돌 방지)
            time.sleep(2)
            
            logger.debug("메시지 목록 가져오기 시작")
            # 메시지 목록 가져오기
            messages = project_client.agents.list_messages(thread_id=thread.id)
            logger.debug(f"메시지 목록 가져오기 완료: {len(messages.text_messages) if hasattr(messages, 'text_messages') else 0}개 메시지")

            # 메시지 출력
            print("\n메시지 목록:")
            for text_message in messages.text_messages:
                print(text_message.as_dict())

            # 응답 텍스트 추출
            response_text = ""
            
            # 메시지 목록이 비어있지 않은 경우ㅌ
            if messages.text_messages:
                # 첫 번째 메시지 가져오기
                first_message = messages.text_messages[0]
                
                # 첫 번째 메시지의 text 딕셔너리에서 value 값 추출
                message_dict = first_message.as_dict()
                if 'text' in message_dict and isinstance(message_dict['text'], dict) and 'value' in message_dict['text']:
                    response_text = message_dict['text']['value']
                    logger.debug(f"응답 텍스트 추출 완료: {response_text[:50]}...")
            
            # 응답 텍스트가 비어있는 경우 처리
            if not response_text:
                response_text = "죄송합니다. 응답을 생성하는 데 문제가 발생했습니다. 다시 시도해주세요."
                logger.warning("응답 텍스트가 비어있습니다.")
            
            # 경과 시간 계산
            elapsed_time = time.time() - start_time
            
            # 토큰 수 추정 (간단한 추정치)
            input_tokens = len(input_text.split()) // 1.3  # 대략적인 추정
            output_tokens = len(response_text.split()) // 1.3  # 대략적인 추정
            
            # 추적 단계 정보 (Azure AI Foundry에서는 제공하지 않을 수 있음)
            trace_steps = []
            
            logger.info(f"Azure AI Foundry 응답 생성 완료 (경과 시간: {elapsed_time:.2f}초)")
            return response_text, trace_steps, elapsed_time, input_tokens, output_tokens, start_time

        except Exception as e:
            retry_count += 1
            logger.error(f"Azure AI Foundry API 호출 중 오류 발생 (시도 {retry_count}/{max_retries}): {str(e)}")
            
            if retry_count < max_retries:
                # 오류 발생 시 지연 시간 추가 후 재시도
                wait_time = 2 * retry_count
                logger.info(f"{wait_time}초 후 재시도합니다...")
                time.sleep(wait_time)  # 재시도마다 지연 시간 증가
                continue
            else:
                # 최대 재시도 횟수 초과 시 오류 반환
                elapsed_time = time.time() - start_time
                logger.error(f"최대 재시도 횟수 초과. 오류: {str(e)}")
                return f"Azure AI Foundry 서비스에 문제가 발생했습니다: {str(e)}", [], elapsed_time, 0, 0, start_time

def test_ms_agent_connection():
    """Azure AI Foundry 에이전트 연결 테스트 함수"""
    try:
        logger.debug("에이전트 연결 테스트 시작")
        
        # 에이전트 가져오기
        agent = project_client.agents.get_agent(MS_AGENT_ID)
        logger.debug(f"에이전트 가져오기 완료: {agent.id}")
        
        # 요청 간 지연 시간 추가 (충돌 방지)
        time.sleep(1)
        
        # 새로운 스레드 생성
        thread = project_client.agents.create_thread()
        logger.debug(f"스레드 생성 완료: {thread.id}")
        
        logger.info(f"Azure AI Foundry 에이전트 연결 성공 (에이전트: {agent.name}, 스레드: {thread.id})")
        return True, f"Azure AI Foundry 에이전트 연결 성공 (에이전트: {agent.name}, 스레드: {thread.id})"
    except Exception as e:
        logger.error(f"Azure AI Foundry 에이전트 연결 실패: {str(e)}")
        return False, f"Azure AI Foundry 에이전트 연결 실패: {str(e)}"
