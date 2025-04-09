import streamlit as st
import boto3
import json
import os
import time
import botocore.eventstream
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# 환경 설정
IS_LOCAL = os.getenv('ENV', 'local') == 'local'
AWS_REGION = "ap-northeast-2"
SESSION_ID = "default-session"

# AWS Bedrock 클라이언트 설정
if IS_LOCAL:
    # 로컬 환경에서는 AWS 자격증명 필요
    bedrock_agent_runtime = boto3.client(
        service_name="bedrock-agent-runtime",
        region_name=AWS_REGION,
    )
    bedrock_agent = boto3.client(
        service_name="bedrock-agent",
        region_name=AWS_REGION,
    )
else:
    # 서버 환경에서는 EC2 IAM 역할 사용
    bedrock_agent_runtime = boto3.client(
        service_name="bedrock-agent-runtime",
        region_name=AWS_REGION,
    )
    bedrock_agent = boto3.client(
        service_name="bedrock-agent",
        region_name=AWS_REGION,
    )

agents = {
    "Mark2": {"id": "0FCAZOFQJV", "alias": "NVPYE1IE3H", "description": "설문형 에이전트"},
    "Mark3": {"id": "GKQDRR2FDV", "alias": "VE7J4QFSC4", "description": "대화형 에이전트"}, 
}

if "messages" not in st.session_state:
    st.session_state.messages = {}

if 'AGENT_ID' not in st.session_state:
    st.session_state['AGENT_ID'] = agents["Mark3"]["id"]
    st.session_state['AGENT_ALIAS_ID'] = agents["Mark3"]["alias"]

# 탭 관리를 위한 세션 상태 초기화
if 'active_tabs' not in st.session_state:
    st.session_state.active_tabs = set()

# 탭별 모델 정보 저장
if 'tab_models' not in st.session_state:
    st.session_state.tab_models = {}

# 현재 활성화된 탭 인덱스 저장
if 'active_tab_index' not in st.session_state:
    st.session_state.active_tab_index = 0

# 페이지 첫 접속 시 자동으로 기본 모델로 새 채팅 시작
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # 기본 모델 설정 (AWS Bedrock Cloud 3.5)
    default_model = "AWS Bedrock Cloud 3.5"
    # 기본 에이전트 설정 (Mark3)
    st.session_state['AGENT_ID'] = agents["Mark3"]["id"]
    st.session_state['AGENT_ALIAS_ID'] = agents["Mark3"]["alias"]
    
    # 새 탭 생성
    tab_id = f"{default_model}_0"
    st.session_state.active_tabs.add(tab_id)
    st.session_state.messages[tab_id] = []
    st.session_state.tab_models[tab_id] = default_model
    st.session_state.active_tab_index = 0

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
    if IS_LOCAL:
        # 로컬 환경에서는 localhost 사용
        llm = ChatOllama(
            model="llama3",
            base_url="http://localhost:11434"
        )
    else:
        # 서버 환경에서는 EC2 퍼블릭 IP 사용
        llm = ChatOllama(
            model="llama3",
            base_url="http://localhost:11434"  # EC2에서는 localhost 사용
        )

    prompt = ChatPromptTemplate.from_template("{message}")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"message": input_text})

# 모델 초기화를 세션 상태에 저장하여 재사용
if 'ollama_model' not in st.session_state:
    st.session_state.ollama_model = None

def get_ollama_model():
    if st.session_state.ollama_model is None:
        if IS_LOCAL:
            st.session_state.ollama_model = ChatOllama(
                model="llama3",
                base_url="http://localhost:11434"
            )
        else:
            st.session_state.ollama_model = ChatOllama(
                model="llama3",
                base_url="http://localhost:11434"  # EC2에서는 localhost 사용
            )
    return st.session_state.ollama_model

def query_ollama_optimized(input_text):
    llm = get_ollama_model()
    prompt = ChatPromptTemplate.from_template("{message}")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"message": input_text})

st.title("🌟 멀티 LLM 지원  🌟")

# 채팅 입력 영역을 하단에 고정하기 위한 CSS 추가
st.markdown("""
<style>
    /* 채팅 입력 영역 고정 */
    div[data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background-color: #f0f2f6 !important;
        padding: 10px !important;
        z-index: 1000 !important;
        border-top: 1px solid #e0e0e0 !important;
    }
    
    /* 채팅 메시지 영역에 하단 여백 추가 */
    div[data-testid="stChatMessageContainer"] {
        margin-bottom: 100px !important;
    }
    
    /* 사이드바가 열려있을 때 채팅 입력 영역 조정 */
    @media (min-width: 768px) {
        div[data-testid="stChatInput"] {
            width: calc(100% - 300px) !important;
            margin-left: 300px !important;
        }
    }
    
    /* 탭 컨테이너에 하단 여백 추가 */
    .stTabs [data-baseweb="tab-list"] {
        margin-bottom: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    # 환경 표시 아이콘 추가
    if IS_LOCAL:
        st.markdown("### 🖥️ 로컬 환경")
        st.markdown("*AWS 자격증명 필요*")
    else:
        st.markdown("### ☁️ 서버 환경")
        st.markdown("*EC2 IAM 역할 사용 중*")
    
    st.markdown("---")
    st.header("⚙️ 설정")

    model_option = st.selectbox("LLM 모델 선택", ["AWS Bedrock Cloud 3.5", "Local Ollama llama 3.2"])
    
    # AWS Bedrock 선택 시에만 에이전트 정보 표시
    if model_option == "AWS Bedrock Cloud 3.5":
        st.markdown("**에이전트 정보**")
        current_agent = [k for k, v in agents.items() if v["id"] == st.session_state['AGENT_ID']][0]
        agent_info = agents[current_agent]
        
        st.markdown(f"**현재 에이전트:** `{current_agent}`")
        st.markdown(f"**설명:** {agent_info['description']}")
        
        # 에이전트 변경 버튼
        if current_agent == "Mark2":
            button_text = "Mark3 에이전트로 변경"
        else:
            button_text = "Mark2 에이전트로 변경"
            
        if st.button(button_text):
            if current_agent == "Mark2":
                st.session_state['AGENT_ID'] = agents["Mark3"]["id"]
                st.session_state['AGENT_ALIAS_ID'] = agents["Mark3"]["alias"]
                st.success("✅ Mark3 에이전트로 변경되었습니다")
            else:
                st.session_state['AGENT_ID'] = agents["Mark2"]["id"]
                st.session_state['AGENT_ALIAS_ID'] = agents["Mark2"]["alias"]
                st.success("✅ Mark2 에이전트로 변경되었습니다")
            st.rerun()
    
    elif model_option == "Local Ollama llama 3.2":
        st.markdown("**Ollama llama 3.2 모델**: `llama3.2:latest`")
    
    st.markdown("---")
    # 새 탭 생성 버튼 (모델 선택 영역 아래로 이동)
    if st.button("새 채팅 시작", type="primary"):
        with st.spinner("채팅 탭 생성 중..."):
            tab_id = f"{model_option}_{len(st.session_state.active_tabs)}"
            st.session_state.active_tabs.add(tab_id)
            if tab_id not in st.session_state.messages:
                st.session_state.messages[tab_id] = []
            # 탭 생성 시 모델 정보 저장
            st.session_state.tab_models[tab_id] = model_option
            st.rerun()

# 메인 화면에 탭 표시
if st.session_state.active_tabs:
    # 탭 목록 생성
    tab_titles = [f"Chat {i+1}" for i in range(len(st.session_state.active_tabs))]
    
    # 탭 생성
    tabs = st.tabs(tab_titles)
    
    # 탭 내용 표시
    for i, (tab, tab_id) in enumerate(zip(tabs, sorted(st.session_state.active_tabs))):
        with tab:
            col1, col2 = st.columns([6, 1])
            with col1:
                # 저장된 모델 정보로 subheader 표시
                st.subheader(f"{st.session_state.tab_models[tab_id]} Agent")
            with col2:
                if st.button("채팅 종료", key=f"close_{tab_id}"):
                    st.session_state.active_tabs.remove(tab_id)
                    # 탭 삭제 시 모델 정보도 함께 삭제
                    del st.session_state.tab_models[tab_id]
                    st.rerun()
            
            # 채팅 메시지 표시
            for message in st.session_state.messages[tab_id]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # 사용자 입력 처리
            if user_input := st.chat_input("질문을 입력하세요:", key=f"input_{tab_id}"):
                st.chat_message("user").markdown(user_input)
                st.session_state.messages[tab_id].append({"role": "user", "content": user_input})

                with st.spinner("답변 생성 중..."):
                    # 저장된 모델 정보로 쿼리 실행
                    if st.session_state.tab_models[tab_id] == "AWS Bedrock Cloud 3.5":
                        response = query_bedrock_agent(user_input)
                    else:
                        response = query_ollama_optimized(user_input)

                    st.chat_message("assistant").markdown(response)
                    st.session_state.messages[tab_id].append({"role": "assistant", "content": response})
else:
    st.info("👈 사이드바에서 '새 채팅 시작' 버튼을 클릭하여 채팅을 시작하세요.")
