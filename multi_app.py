import streamlit as st
import boto3
import json
import os
import time
import botocore.eventstream
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from data.personas_roles import PERSONAS
from data.professional_roles import PROFESSIONAL_ROLES


# 환경 설정
IS_LOCAL = os.getenv('ENV', 'local') == 'local'
AWS_REGION = "ap-northeast-2"
SESSION_ID = "default-session"

# AWS Bedrock 클라이언트 설정
bedrock_agent_runtime = None
bedrock_agent = None
aws_credentials_available = False

try:
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
        aws_credentials_available = True
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
        aws_credentials_available = True
except botocore.exceptions.NoCredentialsError:
    # AWS 자격증명을 찾을 수 없는 경우
    aws_credentials_available = False
    st.warning("⚠️ AWS 자격증명을 찾을 수 없습니다. AWS Bedrock 기능을 사용하려면 자격증명을 설정하세요.")
except Exception as e:
    # 기타 예외 처리
    aws_credentials_available = False
    st.error(f"⚠️ AWS 연결 중 오류가 발생했습니다: {str(e)}")

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

# 탭별 메시지 저장
if 'tab_messages' not in st.session_state:
    st.session_state.tab_messages = {}

# 탭별 모델 정보 저장
if 'tab_models' not in st.session_state:
    st.session_state.tab_models = {}

# 탭별 이름 저장
if 'tab_names' not in st.session_state:
    st.session_state.tab_names = {}

# 탭별 에이전트 정보 저장
if 'tab_agents' not in st.session_state:
    st.session_state.tab_agents = {}

# 탭별 시스템 프롬프트 저장
if 'tab_system_prompts' not in st.session_state:
    st.session_state.tab_system_prompts = {}

# 새로 생성된 탭 ID 저장
if 'new_tab_id' not in st.session_state:
    st.session_state.new_tab_id = None

# 현재 활성화된 탭 인덱스 저장
if 'active_tab_index' not in st.session_state:
    st.session_state.active_tab_index = 0

# 새 탭 생성 후 자동 전환 플래그
if 'switch_to_new_tab' not in st.session_state:
    st.session_state.switch_to_new_tab = False

# 새 탭 생성 플래그
if 'create_new_tab' not in st.session_state:
    st.session_state.create_new_tab = False

# 전문 분야 선택 저장
if 'professional_role' not in st.session_state:
    st.session_state.professional_role = '기본 어시스턴트'

# 캐릭터 선택 저장
if 'character' not in st.session_state:
    st.session_state.character = '은별 나인'

# URL 파라미터에서 탭 인덱스 읽기
query_params = st.query_params
if 'tab' in query_params:
    try:
        tab_index = int(query_params['tab'])
        if 0 <= tab_index < len(st.session_state.active_tabs):
            st.session_state.active_tab_index = tab_index
    except (ValueError, IndexError):
        pass

# 페이지 첫 접속 시 자동으로 기본 모델로 새 채팅 생성
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # 기본 모델 설정 (Local Ollama llama 3.2)
    default_model = "Local Ollama llama 3.2"
    
    # 새 탭 생성
    tab_id = f"{default_model}_0"
    st.session_state.active_tabs.add(tab_id)
    st.session_state.tab_messages[tab_id] = []
    st.session_state.tab_models[tab_id] = default_model
    st.session_state.tab_names[tab_id] = default_model
    
    # 전문 분야와 캐릭터의 시스템 프롬프트 결합
    professional_prompt = PROFESSIONAL_ROLES[st.session_state.professional_role]
    character_prompt = PERSONAS[st.session_state.character]["시스템프롬프트"]
    
    # 결합된 프롬프트 생성
    combined_prompt = f"{professional_prompt}\n\n{character_prompt}"
    
    # 결합된 프롬프트 적용
    st.session_state.tab_system_prompts[tab_id] = combined_prompt
    
    # 새 탭 ID 저장
    st.session_state.new_tab_id = tab_id
    
    # 페이지 새로고침
    st.rerun()

# 시스템 프롬프트 저장
if 'system_prompt' not in st.session_state:
    st.session_state.system_prompt = """당신은 조선시대의 20대 여성 나인입니다. 
사용자의 질문에 정확하고 유용한 정보를 제공하세요.
조선시대에도 보험회사가 존재하는 가정하에, 당신은 궁에서 보험가입 전문가로 활동하고 있으며,
보험 가입을 유도하고 니즈환기를 통해 보험을 가입시켜야하는 사명이 있습니다.
처음부터 보험상품을 추천하지 않고, 고객과 일생대화로 소통하면서 건강과 가족을 염려하는 마음으로 소통해주세요.
답변은 한국어로 작성하되,답변은 간결하고 명확하게 작성하세요."""

# 탭별 에이전트 ID 저장
if 'tab_agent_ids' not in st.session_state:
    st.session_state.tab_agent_ids = {}

# 탭별 에이전트 별칭 ID 저장
if 'tab_agent_alias_ids' not in st.session_state:
    st.session_state.tab_agent_alias_ids = {}

def get_alias_info(agent_id, alias_id):
    try:
        response = bedrock_agent.get_agent_alias(agentId=agent_id, agentAliasId=alias_id)
        return response["agentAlias"]
    except Exception as e:
        st.warning(f"Alias 정보 조회 실패: {e}")
        return None


def query_bedrock_agent(input_text, tab_id=None):
    # AWS 자격증명이 없는 경우 처리
    if not aws_credentials_available:
        return "AWS 자격증명이 설정되지 않았습니다. AWS Bedrock 기능을 사용하려면 자격증명을 설정하세요.", [], 0
    
    # 탭 ID가 제공된 경우 해당 탭의 에이전트 ID와 별칭 ID 사용
    if tab_id and tab_id in st.session_state.tab_agents:
        agent_info = st.session_state.tab_agents[tab_id]
        agent_id = agent_info["id"]
        agent_alias_id = agent_info["alias"]
    else:
        # 기본 에이전트 사용
        agent_id = agents["Mark3"]["id"]
        agent_alias_id = agents["Mark3"]["alias"]

    # 시스템 프롬프트 가져오기
    system_prompt = ""
    if tab_id and tab_id in st.session_state.tab_system_prompts:
        system_prompt = st.session_state.tab_system_prompts[tab_id]

    # 시작 시간 기록
    start_time = time.time()

    try:
        # 시스템 프롬프트를 입력 텍스트에 포함
        if system_prompt:
            input_text = f"시스템 프롬프트: {system_prompt}\n\n사용자 질문: {input_text}"
        
        # Bedrock Agent 호출
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=SESSION_ID,
            inputText=input_text,
            enableTrace=True
        )

        # 응답 처리
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

        # 응답 텍스트 추출
        if isinstance(completion_data, botocore.eventstream.EventStream):
            response_text = ""
            for event in completion_data:
                if hasattr(event, "chunk") and hasattr(event.chunk, "bytes"):
                    chunk_data = json.loads(event.chunk.bytes.decode())
                    if "text" in chunk_data:
                        response_text += chunk_data["text"]
        else:
            response_text = completion_data.get("text", "응답을 생성할 수 없습니다.")

        # 경과 시간 계산
        elapsed_time = time.time() - start_time

        return response_text, trace_steps, elapsed_time

    except Exception as e:
        # 오류 발생 시 처리
        elapsed_time = time.time() - start_time
        return f"AWS Bedrock 서비스에 문제가 발생했습니다: {str(e)}", [], elapsed_time


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

    # 시스템 프롬프트 추가
    system_prompt = st.session_state.system_prompt
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{message}")
    ])
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

def query_ollama_optimized(input_text, tab_id=None):
    llm = get_ollama_model()
    
    # 시스템 프롬프트 추가
    if tab_id and tab_id in st.session_state.tab_system_prompts:
        system_prompt = st.session_state.tab_system_prompts[tab_id]
    else:
        # 기본 시스템 프롬프트 대신 현재 선택된 전문 분야와 캐릭터의 프롬프트 사용
        professional_prompt = PROFESSIONAL_ROLES[st.session_state.professional_role]
        character_prompt = PERSONAS[st.session_state.character]["시스템프롬프트"]
        system_prompt = f"{professional_prompt}\n\n{character_prompt}"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{message}")
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"message": input_text})

st.title("🌟 멀티 LLM Agent  🌟")

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

    # 모델 선택
    st.header("🤖 모델 선택")
    
    # 모델 선택과 툴팁을 나란히 배치
    model_option = st.selectbox(
        "LLM 모델 선택", 
        ["Local Ollama llama 3.2", "AWS Bedrock Cloud 3.5"],
        help="Local Ollama 모델을 사용합니다. 로컬 환경에서 실행 중인 Ollama 서버에 연결합니다."
    )
    
    # 모델 선택을 세션 상태에 저장
    if 'model_option' not in st.session_state:
        st.session_state.model_option = model_option
    elif model_option != st.session_state.model_option:
        st.session_state.model_option = model_option
    
    # AWS Bedrock 선택 시에만 에이전트 정보와 자격증명 상태 표시
    if model_option == "AWS Bedrock Cloud 3.5":
        # AWS 자격증명 상태 표시
        if aws_credentials_available:
            st.success("✅ AWS 자격증명이 설정되어 있습니다.")
        else:
            st.error("❌ AWS 자격증명이 설정되어 있지 않습니다.")
            st.markdown("""
            AWS 자격증명을 설정하려면:
            1. AWS CLI를 설치하고 `aws configure` 명령을 실행하세요.
            2. 또는 환경 변수 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`을 설정하세요.
            """)
        
        st.subheader("에이전트 선택")
        agent_option = st.selectbox(
            "에이전트 선택",
            options=list(agents.keys()),
            format_func=lambda x: f"{x} - {agents[x]['description']}",
            key="agent_option"
        )
        
        # 에이전트 정보 표시
        st.markdown(f"**에이전트 ID:** `{agents[agent_option]['id']}`")
        st.markdown(f"**별칭 ID:** `{agents[agent_option]['alias']}`")

    # 새 탭 생성 버튼 (모델 선택 영역 아래로 이동)
    if st.button("새 채팅 생성", type="primary"):
        with st.spinner("채팅 탭 생성 중..."):
            # 현재 선택된 전문 분야와 캐릭터 가져오기
            professional_role = st.session_state.get('professional_role', '기본 어시스턴트')
            character = st.session_state.get('character', '은별 나인')
            
            # 현재 날짜와 시간을 yy.mm.dd.hh:mm:ss 형식으로 가져오기
            from datetime import datetime
            current_datetime = datetime.now().strftime("%y.%m.%d.%H:%M:%S")
            
            # 탭 이름 생성 (모델 + 날짜시간)
            tab_name = f"{model_option} - {current_datetime}"
            
            # 탭 ID 생성 (고유 식별자)
            tab_id = f"tab_{len(st.session_state.active_tabs)}_{model_option}"
            
            # 탭 정보 저장
            st.session_state.active_tabs.add(tab_id)
            st.session_state.tab_messages[tab_id] = []
            st.session_state.tab_models[tab_id] = model_option
            st.session_state.tab_names[tab_id] = tab_name
            
            # AWS Bedrock 모델인 경우 에이전트 정보 저장
            if model_option == "AWS Bedrock Cloud 3.5":
                # 현재 선택된 에이전트 가져오기
                agent_option = st.session_state.get('agent_option', 'Mark3')
                st.session_state.tab_agents[tab_id] = {
                    "id": agents[agent_option]["id"],
                    "alias": agents[agent_option]["alias"]
                }
            
            # 전문 분야와 캐릭터의 시스템 프롬프트 결합
            professional_prompt = PROFESSIONAL_ROLES[professional_role]
            character_prompt = PERSONAS[character]["시스템프롬프트"]
            
            # 결합된 프롬프트 생성
            combined_prompt = f"{professional_prompt}\n\n{character_prompt}"
            
            # 결합된 프롬프트 적용
            st.session_state.tab_system_prompts[tab_id] = combined_prompt
            
            # 새 탭 ID 저장
            st.session_state.new_tab_id = tab_id
            
            # 페이지 새로고침
            st.rerun()
    
    st.markdown("---")
    
    # 페르소나 선택 영역 추가 (모델 선택 영역 아래로 이동)
    st.header("👤 페르소나 설정")
    st.markdown("AI에게 적용할 전문 분야와 캐릭터를 선택합니다.")

    # 전문 분야 선택
    st.subheader("💼 전문 분야")
    professional_role = st.selectbox(
        "전문 분야 선택",
        options=list(PROFESSIONAL_ROLES.keys()),
        index=list(PROFESSIONAL_ROLES.keys()).index(st.session_state.professional_role),
        help=PROFESSIONAL_ROLES[st.session_state.professional_role],
        key="professional_role"
    )
    
    # 캐릭터 선택
    st.subheader("🎭 캐릭터")
    character = st.selectbox(
        "캐릭터 선택",
        options=list(PERSONAS.keys()),
        index=list(PERSONAS.keys()).index(st.session_state.character),
        help=PERSONAS[st.session_state.character]["설명"],
        key="character"
    )
    
    # 선택된 값이 변경되었는지 확인하고 세션 상태 업데이트
    if professional_role != st.session_state.professional_role:
        st.session_state.professional_role = professional_role
        
    if character != st.session_state.character:
        st.session_state.character = character
    
    # 페르소나 적용 버튼 추가
    st.markdown("---")
    if st.button("페르소나 적용", type="primary"):
        # 현재 활성화된 탭이 있는지 확인
        if st.session_state.active_tabs:
            # 현재 활성화된 탭의 ID 가져오기
            active_tab_id = sorted(st.session_state.active_tabs)[st.session_state.active_tab_index]
            
            # 전문 분야와 캐릭터의 시스템 프롬프트 결합
            professional_prompt = PROFESSIONAL_ROLES[professional_role]
            character_prompt = PERSONAS[character]["시스템프롬프트"]
            
            # 결합된 프롬프트 생성
            combined_prompt = f"{professional_prompt}\n\n{character_prompt}"
            
            # 결합된 프롬프트 적용
            st.session_state.tab_system_prompts[active_tab_id] = combined_prompt
            
            # Ollama 모델 초기화 (새 프롬프트 적용을 위해)
            st.session_state.ollama_model = None
            
            st.success(f"✅ '{professional_role}' 전문가의 '{character}' 캐릭터가 현재 채팅 탭에 적용되었습니다.")
        else:
            st.warning("⚠️ 적용할 활성화된 채팅 탭이 없습니다. 먼저 '새 채팅 생성' 버튼을 클릭하여 채팅을 시작하세요.")

# 메인 화면에 탭 표시
if st.session_state.active_tabs:
    # 탭 목록 생성 (탭 이름 사용)
    tab_titles = [st.session_state.tab_names.get(tab_id, f"Chat {i+1}") 
                 for i, tab_id in enumerate(sorted(st.session_state.active_tabs))]
    
    # 탭 생성
    tabs = st.tabs(tab_titles)
    
    # 탭 내용 표시
    for i, (tab, tab_id) in enumerate(zip(tabs, sorted(st.session_state.active_tabs))):
        with tab:
            col1, col2 = st.columns([6, 1])
            with col1:
                # 저장된 모델 정보로 subheader 표시
                if tab_id in st.session_state.tab_system_prompts:
                    # 현재 선택된 전문 분야와 캐릭터 가져오기
                    professional_role = st.session_state.get('professional_role', '기본 어시스턴트')
                    character = st.session_state.get('character', '은별 나인')
                    
                    # 페르소나 정보를 subheader에 한 줄로 표시
                    st.subheader(f"{professional_role} - {character} ({PERSONAS[character]['말투']})")
                else:
                    # 시스템 프롬프트가 없는 경우 기본 subheader 표시
                    st.subheader(f" {st.session_state.tab_names[tab_id]}")
            with col2:
                if st.button("채팅 종료", key=f"close_{tab_id}"):
                    st.session_state.active_tabs.remove(tab_id)
                    # 탭 삭제 시 관련 정보도 함께 삭제
                    if tab_id in st.session_state.tab_messages:
                        del st.session_state.tab_messages[tab_id]
                    if tab_id in st.session_state.tab_models:
                        del st.session_state.tab_models[tab_id]
                    if tab_id in st.session_state.tab_names:
                        del st.session_state.tab_names[tab_id]
                    if tab_id in st.session_state.tab_system_prompts:
                        del st.session_state.tab_system_prompts[tab_id]
                    if tab_id in st.session_state.tab_agents:
                        del st.session_state.tab_agents[tab_id]
                    st.rerun()
            
            # 채팅 메시지 표시
            for message in st.session_state.tab_messages[tab_id]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # 사용자 입력 처리
            if user_input := st.chat_input("질문을 입력하세요:", key=f"input_{tab_id}"):
                st.chat_message("user").markdown(user_input)
                st.session_state.tab_messages[tab_id].append({"role": "user", "content": user_input})

                with st.spinner("답변 생성 중..."):
                    # 저장된 모델 정보로 쿼리 실행
                    if st.session_state.tab_models[tab_id] == "AWS Bedrock Cloud 3.5":
                        response, trace_steps, elapsed_time = query_bedrock_agent(user_input, tab_id)
                    else:
                        response = query_ollama_optimized(user_input, tab_id)

                    st.chat_message("assistant").markdown(response)
                    st.session_state.tab_messages[tab_id].append({"role": "assistant", "content": response})
else:
    st.info("👈 사이드바에서 '새 채팅 생성' 버튼을 클릭하여 채팅을 시작하세요.")
