import streamlit as st
import os
import time
import json
from typing import Dict, List, Tuple, Any, Optional
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# 환경 설정
IS_LOCAL = os.getenv('ENV', 'local') == 'local'
MS_AGENT_ID = "asst_62CgNOtkZwOGWbYVVV84xPaW"
MS_THREAD_ID = "thread_0lAqgleT4Je2keGtqYAivGAw"

# Azure AI Foundry 연결 정보
MS_CONNECTION_STRING = "eastus2.api.azureml.ms;2326c76a-5eab-44b6-808b-1978f2ffee0e;slihackathon-2025-team2-rg;team2_seongryongle-8914"

# Azure AI Foundry 클라이언트 초기화
try:
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=MS_CONNECTION_STRING
    )
    ms_credentials_available = True
except Exception as e:
    ms_credentials_available = False

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
        return str(message)

def query_ms_agent(input_text, tab_id=None):
    """Azure AI Foundry (GPT4.0)를 사용하여 질문에 답변하는 함수"""
    if not ms_credentials_available:
        return "Azure AI Foundry 자격증명이 설정되지 않았습니다. ms_functions.py 파일에서 MS_CONNECTION_STRING 값을 설정하세요.", [], 0, 0, 0, 0

    # 시스템 프롬프트 추가
    if tab_id and tab_id in st.session_state.tab_system_prompts:
        system_prompt = st.session_state.tab_system_prompts[tab_id]
    else:
        # 기본 시스템 프롬프트 사용
        system_prompt = "당신은 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 정확하고 유용한 정보를 제공하세요."

    # 시작 시간 기록
    start_time = time.time()

    try:
        # 에이전트 가져오기
        agent = project_client.agents.get_agent(MS_AGENT_ID)
        
        # 스레드 가져오기
        thread = project_client.agents.get_thread(MS_THREAD_ID)
        
        # 사용자 메시지 생성
        user_message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=input_text
        )
        
        # 실행 생성 및 처리
        run = project_client.agents.create_and_process_run(
            thread_id=thread.id,
            agent_id=agent.id
        )
        
        # 메시지 목록 가져오기
        messages = project_client.agents.list_messages(thread_id=thread.id)

        # 메시지 출력
        print("\n메시지 목록:")
        for text_message in messages.text_messages:
            print(text_message.as_dict())

        # 응답 텍스트 추출
        response_text = ""
        
        # 메시지 목록이 비어있지 않은 경우
        if messages.text_messages:
            # 첫 번째 메시지 가져오기
            first_message = messages.text_messages[0]
            
            # 첫 번째 메시지의 text 딕셔너리에서 value 값 추출
            message_dict = first_message.as_dict()
            if 'text' in message_dict and isinstance(message_dict['text'], dict) and 'value' in message_dict['text']:
                response_text = message_dict['text']['value']
        
        # 응답 텍스트가 비어있는 경우 처리
        if not response_text:
            response_text = "죄송합니다. 응답을 생성하는 데 문제가 발생했습니다. 다시 시도해주세요."
        
        # 경과 시간 계산
        elapsed_time = time.time() - start_time
        
        # 토큰 수 추정 (간단한 추정치)
        input_tokens = len(input_text.split()) // 1.3  # 대략적인 추정
        output_tokens = len(response_text.split()) // 1.3  # 대략적인 추정
        
        # 추적 단계 정보 (Azure AI Foundry에서는 제공하지 않을 수 있음)
        trace_steps = []
        
        return response_text, trace_steps, elapsed_time, input_tokens, output_tokens, start_time

    except Exception as e:
        elapsed_time = time.time() - start_time
        return f"Azure AI Foundry 서비스에 문제가 발생했습니다: {str(e)}", [], elapsed_time, 0, 0, start_time

def test_ms_agent_connection():
    """Azure AI Foundry 에이전트 연결 테스트 함수"""
    try:
        # 에이전트 가져오기
        agent = project_client.agents.get_agent(MS_AGENT_ID)
        
        # 스레드 가져오기
        thread = project_client.agents.get_thread(MS_THREAD_ID)
        
        return True, f"Azure AI Foundry 에이전트 연결 성공 (에이전트: {agent.name}, 스레드: {thread.id})"
    except Exception as e:
        return False, f"Azure AI Foundry 에이전트 연결 실패: {str(e)}"
