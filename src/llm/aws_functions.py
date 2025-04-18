import streamlit as st
import boto3
import json
import os
import time
import botocore.eventstream
from typing import Dict, List, Tuple, Any, Optional

# 환경 설정
IS_LOCAL = os.getenv('ENV', 'local') == 'local'
AWS_REGION = "ap-northeast-2"
SESSION_ID = "default-session"

# AWS 클라이언트 초기화
aws_credentials_available_flag = False
try:
    bedrock_agent = boto3.client('bedrock-agent', region_name=AWS_REGION)
    bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=AWS_REGION)
    aws_credentials_available_flag = True
except Exception as e:
    print(f"AWS 자격증명 오류: {e}")

# AWS Bedrock Agent 정보
agents = {
    "Mark3": {
        "id": "GKQDRR2FDV",
        "alias": "VE7J4QFSC4"
    }
}

def query_bedrock_agent(input_text, tab_id=None):
    """AWS Bedrock Agent를 사용하여 질문에 답변하는 함수"""
    if not aws_credentials_available_flag:
        return "AWS 자격증명이 설정되지 않았습니다. AWS Bedrock 기능을 사용하려면 자격증명을 설정하세요.", [], 0, 0, 0, 0

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

    try:
        if system_prompt:
            input_text = f"시스템 프롬프트: {system_prompt}\n\n사용자 질문: {input_text}"

        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=SESSION_ID,
            inputText=input_text,
            enableTrace=True
        )

        completion_data = response.get("completion", {})
        trace_steps = []

        if "trace" in response:
            for step in response["trace"]:
                trace_steps.append({
                    "name": step.get("name", ""),
                    "status": step.get("status", ""),
                    "input": step.get("input", {}),
                    "output": step.get("output", {})
                })

        if isinstance(completion_data, botocore.eventstream.EventStream):
            response_text = ""
            for event in completion_data:
                if hasattr(event, "chunk") and hasattr(event.chunk, "bytes"):
                    chunk_data = json.loads(event.chunk.bytes.decode())
                    if "text" in chunk_data:
                        response_text += chunk_data["text"]
        else:
            response_text = completion_data.get("text", "응답을 생성할 수 없습니다.")

        elapsed_time = time.time() - start_time
        input_tokens = len(input_text.split()) // 1.3
        output_tokens = len(response_text.split()) // 1.3

        return response_text, trace_steps, elapsed_time, input_tokens, output_tokens, start_time

    except Exception as e:
        elapsed_time = time.time() - start_time
        return f"AWS Bedrock 서비스에 문제가 발생했습니다: {str(e)}", [], elapsed_time, 0, 0, start_time

def get_alias_info(agent_id=None, alias_id=None):
    """AWS Bedrock Agent Alias 정보를 가져오는 함수"""
    if agent_id is None:
        agent_id = os.getenv('AGENT_ID')
    if alias_id is None:
        alias_id = os.getenv('AGENT_ALIAS_ID')
    try:
        response = bedrock_agent.get_agent_alias(agentId=agent_id, agentAliasId=alias_id)
        return response["agentAlias"]
    except Exception as e:
        st.warning(f"Alias 정보 조회 실패: {e}")
        return None

def aws_credentials_available() -> bool:
    """AWS 자격증명이 사용 가능한지 확인하는 함수"""
    return aws_credentials_available_flag
