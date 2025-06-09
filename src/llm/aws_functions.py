import streamlit as st
import boto3
import json
import os
import time
import botocore.eventstream
from typing import Dict, List, Tuple, Any, Optional
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경 설정
IS_LOCAL = os.getenv('ENV', 'local') == 'local'
AWS_REGION = "ap-northeast-2"
SESSION_ID = "default-session"



# AWS 클라이언트 초기화
def initialize_aws_clients():
    """AWS 클라이언트를 초기화하고 자격 증명 상태를 반환합니다."""
    try:
        # AWS 자격 증명 확인
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials is None:
            logger.warning("AWS 자격 증명을 찾을 수 없습니다.")
            return False, None, None
            
        # Bedrock Agent 클라이언트 초기화
        bedrock_agent = boto3.client('bedrock-agent', region_name=AWS_REGION)
        bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=AWS_REGION)
        
        logger.info("AWS 클라이언트 초기화 성공")
        return True, bedrock_agent, bedrock_agent_runtime
        
    except Exception as e:
        logger.error(f"AWS 클라이언트 초기화 실패: {str(e)}")
        return False, None, None

# AWS Bedrock Agent 정보
agents = {
    "Mark3": {
        "id": "OVC8B4DII6",
        "alias": "LNFESZBC1P"
    }
}

def query_bedrock_agent(input_text: str, tab_id: Optional[str] = None) -> Tuple[str, List[str], float, float, float, float]:
    """AWS Bedrock Agent를 사용하여 질문에 답변하는 함수"""
    # AWS 클라이언트 초기화
    aws_available, bedrock_agent, bedrock_agent_runtime = initialize_aws_clients()
    
    if not aws_available:
        return "AWS Bedrock 서비스를 사용하기 위해서는 AWS 자격 증명이 필요합니다.\n\n자격 증명 설정 방법:\n1. AWS CLI 설치\n2. `aws configure` 명령어로 자격 증명 설정\n3. AWS_ACCESS_KEY_ID와 AWS_SECRET_ACCESS_KEY 환경 변수 설정", [], 0, 0, 0, 0

    if tab_id and tab_id in st.session_state.tab_agents:
        agent_info = st.session_state.tab_agents[tab_id]
        agent_id = agent_info["id"]
        agent_alias_id = agent_info["alias"]
    else:
        agent_id = agents["Mark3"]["id"]
        agent_alias_id = agents["Mark3"]["alias"]

    system_prompt = ""
    if tab_id and tab_id in st.session_state.tab_system_prompts:
        system_prompt = st.session_state.tab_system_prompts[tab_id]

    start_time = time.time()
    max_retries = 5
    retry_count = 0
    response_text = ""
    trace_steps = []

    while retry_count < max_retries:
        try:
            if system_prompt:
                input_text = f"시스템 프롬프트: {system_prompt}\n\n사용자 질문: {input_text}"

            logger.info(f"Sending request to Bedrock Agent - Agent ID: {agent_id}, Alias ID: {agent_alias_id}")
            logger.info(f"Input text: {input_text}")

            response = bedrock_agent_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=SESSION_ID,
                inputText=input_text,
                enableTrace=True
            )

            completion_data = response.get("completion", {})
            
            if isinstance(completion_data, botocore.eventstream.EventStream):
                logger.info("Processing EventStream response")
                for event in completion_data:
                    if "trace" in event:
                        trace_data = event["trace"]
                        internal_message = trace_data.get('input', '내부 분석 진행 중...')
                        trace_steps.append({
                            "name": "trace",
                            "status": "success",
                            "input": internal_message,
                            "output": ""
                        })
                        logger.info(f"Trace step: {internal_message}")

                    if "chunk" in event:
                        chunk_bytes = event["chunk"].get("bytes", b"")
                        chunk_text = chunk_bytes.decode("utf-8", errors="replace")
                        response_text += chunk_text
                        logger.info(f"Received chunk: {chunk_text}")

                if response_text:
                    elapsed_time = time.time() - start_time
                    input_tokens = len(input_text.split()) // 1.3
                    output_tokens = len(response_text.split()) // 1.3
                    return response_text.strip(), trace_steps, elapsed_time, input_tokens, output_tokens, start_time
                else:
                    raise ValueError("응답이 비어있습니다.")
            else:
                raise ValueError("Bedrock 응답이 EventStream 형식이 아닙니다.")

        except Exception as e:
            retry_count += 1
            wait_time = 2 ** retry_count
            logger.warning(f"오류 발생: {str(e)}. {retry_count}/{max_retries}회 재시도 중... (대기 {wait_time}초)")
            time.sleep(wait_time)

    logger.error(f"최대 재시도 횟수({max_retries}회)를 초과했습니다.")
    elapsed_time = time.time() - start_time
    return "AWS Bedrock 서비스에 문제가 발생했습니다. 잠시 후 다시 시도해주세요.", [], elapsed_time, 0, 0, start_time

def get_alias_info(agent_id=None, alias_id=None):
    """AWS Bedrock Agent Alias 정보를 가져오는 함수"""
    aws_available, bedrock_agent, _ = initialize_aws_clients()
    
    if not aws_available:
        return None
        
    if agent_id is None:
        agent_id = os.getenv('AGENT_ID')
    if alias_id is None:
        alias_id = os.getenv('AGENT_ALIAS_ID')
    try:
        response = bedrock_agent.get_agent_alias(agentId=agent_id, agentAliasId=alias_id)
        return response["agentAlias"]
    except Exception as e:
        logger.error(f"Alias 정보 조회 실패: {str(e)}")
        return None

def aws_credentials_available() -> bool:
    """AWS 자격 증명이 설정되어 있는지 확인합니다."""
    try:
        # 로컬 환경인 경우 환경 변수에서 자격 증명을 가져옴
        if IS_LOCAL:
            logger.info("로컬 환경에서 AWS 자격 증명 확인")
            session = boto3.Session()
            credentials = session.get_credentials()
            return credentials is not None
        else:
            # 서버 환경인 경우 환경 변수에서 자격 증명을 가져옴
            logger.info("서버 환경에서 AWS 자격 증명 확인")
            # 환경 변수가 설정되어 있는지 확인
            if not all(key in os.environ for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION']):
                logger.error("서버 환경에서 필요한 AWS 환경 변수가 설정되지 않았습니다.")
                return False
            
            # AWS 자격 증명 확인
            session = boto3.Session()
            credentials = session.get_credentials()
            return credentials is not None
    except Exception as e:
        logger.error(f"AWS 자격 증명 확인 중 오류 발생: {str(e)}")
        return False
