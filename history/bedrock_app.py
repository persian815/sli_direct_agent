import streamlit as st
import boto3
import json
import os
import time
import botocore.eventstream

AWS_REGION = "ap-northeast-2"
SESSION_ID = "default-session"

agents = {
    "AGENT_MK2": {"id": "0FCAZOFQJV", "alias": "NVPYE1IE3H", "description": "기본 고객 지원 및 문의 처리"},
    "AGENT_MK3": {"id": "GKQDRR2FDV", "alias": "VE7J4QFSC4", "description": "고급 분석 및 보험 추천 제공"}, 
}

bedrock_agent_runtime = boto3.client(
    service_name="bedrock-agent-runtime",
    region_name=AWS_REGION,
)

bedrock_agent = boto3.client(
    service_name="bedrock-agent",
    region_name=AWS_REGION,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if 'AGENT_ID' not in st.session_state:
    st.session_state['AGENT_ID'] = agents["AGENT_MK2"]["id"]
    st.session_state['AGENT_ALIAS_ID'] = agents["AGENT_MK2"]["alias"]


def get_alias_info(agent_id, alias_id):
    try:
        response = bedrock_agent.get_agent_alias(agentId=agent_id, agentAliasId=alias_id)
        return response["agentAlias"]
    except Exception as e:
        st.warning(f"Alias 정보 조회 실패: {e}")
        return None


def query_bedrock_agent(input_text):
    max_retries = 5
    retry_count = 0
    response_text = ""

    trace_placeholder = st.sidebar.empty()
    trace_steps = "**🔍 내부 추적 과정:**\n"

    start_time = time.time()
    with st.status("🚀 Bedrock 에이전트 시작 중...") as status:
        while retry_count < max_retries:
            try:
                status.update(label="🔍 사용자 입력 분석 중...")

                response = bedrock_agent_runtime.invoke_agent(
                    agentId=st.session_state['AGENT_ID'],
                    agentAliasId=st.session_state['AGENT_ALIAS_ID'],
                    sessionId=SESSION_ID,
                    inputText=input_text
                )

                status.update(label="📡 Bedrock 에이전트 응답 대기 중...")

                completion_data = response["completion"]

                if isinstance(completion_data, botocore.eventstream.EventStream):
                    for event in completion_data:
                        updated = False
                        if "trace" in event:
                            trace_data = event["trace"]
                            internal_message = trace_data.get('input', '내부 분석 진행 중...')
                            trace_steps += f"🔍 {internal_message}\n"
                            updated = True

                        if "chunk" in event:
                            chunk_bytes = event["chunk"].get("bytes", b"")
                            chunk_text = chunk_bytes.decode("utf-8", errors="replace")
                            response_text += chunk_text
                            trace_steps += f"💬 {chunk_text}\n"
                            updated = True

                        if updated:
                            trace_placeholder.markdown(trace_steps)

                    status.update(label="✅ 최종 답변 완료!", state="complete")
                else:
                    raise ValueError("❗ Bedrock 응답이 EventStream 형식이 아닙니다.")

                elapsed_time = time.time() - start_time
                return response_text, trace_steps, elapsed_time

            except Exception as e:
                retry_count += 1
                wait_time = 2 ** retry_count
                st.warning(f"오류 발생: {e}. {retry_count}/{max_retries}회 재시도 중... (대기 {wait_time}초)")
                time.sleep(wait_time)

    elapsed_time = time.time() - start_time
    return "AWS Bedrock 서비스에 문제가 발생했습니다. 잠시 후 다시 시도해주세요.", trace_steps, elapsed_time


st.title("AWS Bedrock AI Agent Chatbot")

with st.sidebar:
    selected_agent = st.selectbox("에이전트를 선택하세요", list(agents.keys()))
    apply_button = st.button("적용")

    st.markdown("---")
    st.subheader("🔎 선택된 에이전트 정보")

    if apply_button:
        st.session_state['AGENT_ID'] = agents[selected_agent]["id"]
        st.session_state['AGENT_ALIAS_ID'] = agents[selected_agent]["alias"]
        st.success("✅ 에이전트 정보가 성공적으로 업데이트되었습니다!")

    current_agent = [k for k, v in agents.items() if v["id"] == st.session_state['AGENT_ID']][0]
    agent_info = agents[current_agent]

    st.markdown(f"**에이전트 이름:** `{current_agent}`")
    st.markdown(f"**설명:** {agent_info['description']}")
    st.markdown(f"**AGENT_ID:** `{agent_info['id']}`")
    st.markdown(f"**AGENT_ALIAS_ID:** `{agent_info['alias']}`")

    alias_details = get_alias_info(agent_info['id'], agent_info['alias'])
    if alias_details:
        st.markdown(f"**Alias 이름:** {alias_details.get('agentAliasName', 'N/A')}")
        st.markdown(f"**생성 날짜:** {alias_details.get('createdAt', 'N/A')}")
        st.markdown(f"**마지막 업데이트:** {alias_details.get('updatedAt', 'N/A')}")

    st.markdown(f"**AWS 리전:** `{AWS_REGION}`")
    st.markdown(f"**세션 ID:** `{SESSION_ID}`")

st.subheader(f"{current_agent} 채팅 창")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("질문을 입력하세요:"):
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("답변 생성 중..."):
        response, trace_log, elapsed_time = query_bedrock_agent(user_input)

        st.chat_message("assistant").markdown(f"{response}\n\n⏱️ **답변 소요 시간:** {elapsed_time:.2f}초")
        st.session_state.messages.append({"role": "assistant", "content": response})

        with st.expander("🔍 AI의 내부 추적 과정 보기"):
            st.markdown(trace_log)  
                                                                   