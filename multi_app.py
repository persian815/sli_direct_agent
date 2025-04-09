import streamlit as st
import boto3
import json
import os
import time
import botocore.eventstream
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

AWS_REGION = "ap-northeast-2"
SESSION_ID = "default-session"

agents = {
    "AGENT_MK2": {"id": "0FCAZOFQJV", "alias": "NVPYE1IE3H", "description": "기본 고객 지원 및 문의 처리"},
    "AGENT_MK3": {"id": "GKQDRR2FDV", "alias": "VE7J4QFSC4", "description": "고급 분석 및 보험 추천 제공"}, 
}

bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=AWS_REGION)
bedrock_agent = boto3.client("bedrock-agent", region_name=AWS_REGION)

if "messages" not in st.session_state:
    st.session_state.messages = []

if 'AGENT_ID' not in st.session_state:
    st.session_state['AGENT_ID'] = agents["AGENT_MK3"]["id"]
    st.session_state['AGENT_ALIAS_ID'] = agents["AGENT_MK3"]["alias"]


def get_alias_info(agent_id, alias_id):
    try:
        response = bedrock_agent.get_agent_alias(agentId=agent_id, agentAliasId=alias_id)
        return response["agentAlias"]
    except Exception as e:
        st.warning(f"Alias 정보 조회 실패: {e}")
        return None


def query_bedrock_agent(input_text):
    response_text = ""
    response = bedrock_agent_runtime.invoke_agent(
        agentId=st.session_state['AGENT_ID'],
        agentAliasId=st.session_state['AGENT_ALIAS_ID'],
        sessionId=SESSION_ID,
        inputText=input_text
    )
    completion_data = response["completion"]
    for event in completion_data:
        if "chunk" in event:
            chunk_bytes = event["chunk"].get("bytes", b"")
            chunk_text = chunk_bytes.decode("utf-8", errors="replace")
            response_text += chunk_text
    return response_text


def query_ollama(input_text):
    #llm = ChatOllama(model="llama3.2:latest")

    llm = ChatOllama(
    model="llama3",
    base_url="http://localhost:11434"  # EC2 퍼블릭 IP 입력
    )

    prompt = ChatPromptTemplate.from_template("{message}")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"message": input_text})


st.title("🌟 멀티 LLM 지원 Chatbot 🌟")

with st.sidebar:
    st.header("⚙️ 설정")

    model_option = st.selectbox("LLM 모델 선택", ["AWS Bedrock", "Local Ollama"])

    if model_option == "Bedrock cloud 3.5":
        selected_agent = st.selectbox("에이전트 선택", list(agents.keys()))
        if st.button("적용"):
            st.session_state['AGENT_ID'] = agents[selected_agent]["id"]
            st.session_state['AGENT_ALIAS_ID'] = agents[selected_agent]["alias"]
            st.success("✅ Bedrock cloud 3.5 에이전트 적용 완료")

        current_agent = [k for k, v in agents.items() if v["id"] == st.session_state['AGENT_ID']][0]
        agent_info = agents[current_agent]

        st.markdown(f"**선택된 에이전트:** `{current_agent}`")
        st.markdown(f"**설명:** {agent_info['description']}")

    elif model_option == "Ollama llama 3.2":
        st.markdown("**Ollama llama 3.2 모델**: `llama3.2:latest`")

st.subheader(f"{model_option} 채팅 창")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("질문을 입력하세요:"):
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("답변 생성 중..."):
        if model_option == "AWS Bedrock":
            response = query_bedrock_agent(user_input)
        else:
            response = query_ollama(user_input)

        st.chat_message("assistant").markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
