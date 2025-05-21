import streamlit as st
import time
import os
import re
import logging
import sys
from typing import Dict

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # 터미널에 출력
    ]
)
logger = logging.getLogger(__name__)

# 로그 레벨 설정 확인
logger.setLevel(logging.INFO)

from src.llm import (
    evaluate_user_knowledge_level, get_knowledge_level_color
)
from src.utils.utils import (
    evaluate_response_quality,
    get_quality_level_color,
    evaluate_user_temperature,
    get_temperature_color,
    send_chat_log_to_api
)
from src.llm.ms_functions import query_ms_agent
from src.llm.aws_functions import query_bedrock_agent, aws_credentials_available
from src.data.personas_roles import PERSONAS

def load_css():
    """CSS 파일을 로드하는 함수"""
    css_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../static/css/styles.css"))
    with open(css_file) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def get_character_icon(character_name: str) -> str:
    """
    캐릭터 이름에 해당하는 아이콘 경로를 반환하는 함수
    
    Args:
        character_name (str): 캐릭터 이름
        
    Returns:
        str: 아이콘 이미지 경로
    """
    # 캐릭터 이름과 이미지 파일명 매핑
    character_icon_map = {
        "친절한 미영씨": "static/image/친절한 미영씨.png",
        "친절한 금자씨": "static/image/친절한 금자씨.png",
        "공감의녀 장금이": "static/image/공감의녀 장금이.png",
        "감성충만 애순이": "static/image/감성충만 애순이.png",
        "논리적인 테스형": "static/image/논리적인 테스형.png"
    }
    
    # 기본 아이콘 경로
    default_icon = "static/image/논리적인 테스형.png"
    
    # 캐릭터 이름이 매핑에 있으면 해당 아이콘 반환, 없으면 기본 아이콘 반환
    return character_icon_map.get(character_name, default_icon)

def get_user_icon() -> str:
    """
    사용자 아이콘 경로를 반환하는 함수
    
    Returns:
        str: 사용자 아이콘 이미지 경로
    """
    # 현재 선택된 사용자 ID 가져오기
    current_user = st.session_state.get("user", "User1")
    
    # 사용자 ID에 따른 이미지 매핑
    user_icon_map = {
        "User1": "static/image/user1.png",
        "User2": "static/image/user2.png",
        "User3": "static/image/user3.png",
        "User4": "static/image/user4.png"
    }
    
    # 기본 아이콘 경로
    default_icon = "static/image/사용자.png"
    
    # 사용자 ID가 매핑에 있으면 해당 아이콘 반환, 없으면 기본 아이콘 반환
    return user_icon_map.get(current_user, default_icon)

def strip_html_tags(text):
    # 마크다운 코드블록 전체 제거
    text = re.sub(r'```[\\s\\S]*?```', '', text)
    # script, style 태그 전체 제거
    text = re.sub(r'<(script|style)[^>]*>[\\s\\S]*?</\\1>', '', text, flags=re.IGNORECASE)
    # 모든 HTML 태그 제거 (여러 줄, 들여쓰기 포함)
    text = re.sub(r'<[^>]+>', '', text)
    return text

def _format_user_info(user_info: Dict) -> str:
    """사용자 정보를 문자열로 포맷팅합니다."""
    if not user_info:
        return ""
        
    user_data = []
    
    # 기본정보
    basic_info = user_info.get('기본정보', {})
    if basic_info:
        user_data.append("사용자 기본정보:")
        for key, value in basic_info.items():
            user_data.append(f"- {key}: {value}")
    
    # 건강검진정보
    health_info = user_info.get('건강검진정보', {})
    if health_info:
        user_data.append("\n건강검진정보:")
        for key, value in health_info.items():
            user_data.append(f"- {key}: {value}")
    
    # 보험가입내역
    insurance_info = user_info.get('보험가입내역', [])
    if isinstance(insurance_info, list) and insurance_info:
        user_data.append("\n보험가입내역:")
        for item in insurance_info:
            user_data.append(
                f"- {item.get('상품명', '')} / {item.get('보장급부', '')} / "
                f"{item.get('보장내용', '')} / 보장금액: {item.get('보장금액(만원)', '')}만원 / "
                f"보험료: {item.get('보험료(만원)', '')}만원\n  설명: {item.get('설명', '')}"
            )
    elif isinstance(insurance_info, dict):
        user_data.append("\n보험가입내역:")
        for key, value in insurance_info.items():
            user_data.append(f"- {key}: {value}")
    
    return "\n".join(user_data)

def _prepare_message(input_text: str) -> str:
    """사용자 정보와 입력 텍스트를 결합하여 최종 메시지를 생성합니다."""
    from src.data.users_data import USERS
    
    # 사용자 정보 준비
    user = st.session_state.get("user", "User1")
    if user not in USERS:
        logger.warning(f"user({user})가 USERS에 없습니다. User1로 fallback.")
        user = "User1"
        
    user_info = USERS.get(user, {}).get('info', {})
    if isinstance(user_info, list):
        user_info = user_info[0] if user_info else {}
        
    # 메시지 구성
    user_data = _format_user_info(user_info)
    final_message = f"{user_data}\n\n질문: {input_text}" if user_data else f"질문: {input_text}"
    
    return final_message

def render_chat_interface(model: str):
    """채팅 인터페이스를 렌더링하는 함수"""
    load_css()
    
    # 세션 상태 초기화 (함수 맨 앞에서만)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_answer_idx" not in st.session_state:
        st.session_state.selected_answer_idx = None
        st.session_state.selected_answer_content = None
    if "cached_responses" not in st.session_state:
        st.session_state.cached_responses = {}

    user_icon = get_user_icon()
    character = st.session_state.get("character", "논리적인 테스형")
    character_icon = get_character_icon(character)

    # PERSONAS에서 웰컴 메시지 가져오기
    welcome_message = PERSONAS.get(character, {}).get("welcome_message", "안녕하세요! 무엇을 도와드릴까요?")

    # 웰컴 메시지가 채팅 히스토리에 없는 경우에만 표시
    welcome_message_exists = any(
        msg["role"] == "assistant" and msg["content"] == welcome_message 
        for msg in st.session_state.messages
    )

    if not welcome_message_exists:
        with st.chat_message("assistant", avatar=character_icon):
            st.markdown(welcome_message)
            
            # 추천 질문 버튼들
            st.markdown("### 추천 질문")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("보험을 분석해서 상품을 추천해줘", key="q1"):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": "보험을 분석해서 상품을 추천해줘",
                        "knowledge_level": 50,  # 중급 수준
                        "temperature": 36.5
                    })
                    st.rerun()
            
            with col2:
                if st.button("뇌졸중를 예방하는 방법을 알려줘", key="q2"):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": "뇌졸중를 예방하는 방법을 알려줘",
                        "knowledge_level": 20,  # 초급 수준
                        "temperature": 36.5
                    })
                    st.rerun()
            
            with col3:
                if st.button("검진 데이터를 기반으로 위험을 예측해줘", key="q3"):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": "검진 데이터를 기반으로 위험을 예측해줘",
                        "knowledge_level": 70,  # 중급 수준
                        "temperature": 36.5
                    })
                    st.rerun()

    # 2. 채팅 히스토리 표시 (user/assistant 모두)
    for message in st.session_state.messages:
        # 웰컴 메시지와 동일한 assistant 메시지는 건너뜀
        if message["role"] == "assistant" and message["content"] == welcome_message:
            continue
        if message["role"] == "user":
            with st.chat_message("user", avatar=user_icon):
                st.markdown(message["content"])
                # 사용자 메시지의 경우 지식레벨과 온도 표시
                if "knowledge_level" in message:
                    knowledge_level = message["knowledge_level"]
                    knowledge_color = get_knowledge_level_color(knowledge_level)
                    if st.session_state.get('developer_mode', False):
                        st.markdown(f"<div style='color: {knowledge_color}; font-size: 0.8em;'>지식레벨: {knowledge_level}</div>", unsafe_allow_html=True)
                if "temperature" in message:
                    temperature = message["temperature"]
                    temperature_color = get_temperature_color(temperature)
                    if st.session_state.get('developer_mode', False):
                        st.markdown(f"<div style='color: {temperature_color}; font-size: 0.8em;'>사용자 온도: {temperature:.1f}°C</div>", unsafe_allow_html=True)
        elif message["role"] == "assistant":
            with st.chat_message("assistant", avatar=character_icon):
                st.markdown(message["content"])
                # 어시스턴트 메시지의 경우 응답 품질 표시 (개발자 모드 활성화 시에만)
                if "quality_score" in message and st.session_state.get('developer_mode', False):
                    quality_score = message["quality_score"]
                    quality_color = get_quality_level_color(quality_score)
                    st.markdown(f"<div style='color: {quality_color}; font-size: 0.8em;'>응답 품질: {quality_score}</div>", unsafe_allow_html=True)

    # 입력창 항상 하나만 표시
    prompt = st.chat_input("질문을 입력하세요")
    if prompt:
        # 새로운 질문이 들어오면 이전 선택값 초기화
        st.session_state.selected_answer_idx = None
        st.session_state.selected_answer_content = None

        # 사용자 메시지에 지식레벨과 온도 추가
        knowledge_level, knowledge_reason = evaluate_user_knowledge_level(prompt)
        temperature, temperature_reason = evaluate_user_temperature(prompt)
        
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "knowledge_level": knowledge_level,
            "temperature": temperature
        })
        
        with st.chat_message("user", avatar=user_icon):
            st.markdown(prompt)
            # 개발자 모드가 활성화된 경우에만 지식레벨과 온도 표시
            if st.session_state.get('developer_mode', False):
                knowledge_color = get_knowledge_level_color(knowledge_level)
                temperature_color = get_temperature_color(temperature)
                st.markdown(f"<div style='color: {knowledge_color}; font-size: 0.8em;'>지식레벨: {knowledge_level}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: {temperature_color}; font-size: 0.8em;'>사용자 온도: {temperature:.1f}°C</div>", unsafe_allow_html=True)

    # 답변 생성 및 카드/버튼 렌더링은 오직 여기서만!
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user" and st.session_state.selected_answer_idx is None:
        last_user_message = st.session_state.messages[-1]["content"]
        
        # 더미 모드가 활성화된 경우 더미 답변 사용
        if st.session_state.get('dummy_mode', True):
            # 답변 3개 생성
            dummy_ms = "안녕하세요, 곰철수님! 다시 만나 뵙게 되어 반갑습니다.\n고객님의 건강 상태와 보험 가입 상황을 바탕으로 아래와 같은 분석을 제공합니다.\n\n예상 응답:\n- Azure Foundry  AI는 MS의 완전 관리형 서비스로, 다양한 파운데이션 모델을 제공합니다.\n- 현재 API 연동 작업이 진행 중이며, 곧 서비스가 시작될 예정입니다.\n- 더 자세한 정보는 Azure Foundry AI 공식 문서를 참조하세요."
            dummy_aws = "안녕하세요, 곰철수님! 다시 만나 뵙게 되어 반갑습니다.\n고객님의 건강 상태와 보험 가입 상황을 바탕으로 아래와 같은 분석을 제공합니다.\n\n예상 응답:\n- AWS Bedrock은 Amazon의 완전 관리형 서비스로, 다양한 파운데이션 모델을 제공합니다.\n- 현재 API 연동 작업이 진행 중이며, 곧 서비스가 시작될 예정입니다.\n- 더 자세한 정보는 AWS Bedrock 공식 문서를 참조하세요."
            dummy_sds = "안녕하세요, 곰철수님! 다시 만나 뵙게 되어 반갑습니다.\n고객님의 건강 상태와 보험 가입 상황을 바탕으로 아래와 같은 분석을 제공합니다.\n\n예상 응답:\n- SDS AI는 삼성 SDS의 AI 플랫폼으로, 다양한 비즈니스 솔루션을 제공합니다.\n- 현재 API 연동 작업이 진행 중이며, 곧 서비스가 시작될 예정입니다.\n- 더 자세한 정보는 SDS AI 공식 문서를 참조하세요."
            answers = [dummy_ms, dummy_aws, dummy_sds]
        else:
            # 더미 모드가 비활성화된 경우 실제 AI 플랫폼 호출
            try:
                # 캐시된 응답이 있는지 확인
                if last_user_message in st.session_state.cached_responses:
                    answers = st.session_state.cached_responses[last_user_message]
                else:
                    
                    # 최종 메시지 구성
                    final_message = _prepare_message(last_user_message)
                    logger.info(f"Prepared message: {final_message}")
                    
                    # MS Agent 호출
                    response = query_ms_agent(final_message)
                    if isinstance(response, tuple):
                        ms_response = response[0]  # 첫 번째 값만 사용
                    else:
                        ms_response = response

                    # AWS Agent 호출
                    if aws_credentials_available():
                        aws_response, _, _, _, _, _ = query_bedrock_agent(final_message)
                    else:
                        aws_response = "AWS Bedrock 서비스를 사용하기 위해서는 AWS 자격 증명이 필요합니다.\n\n자격 증명 설정 방법:\n1. AWS CLI 설치\n2. `aws configure` 명령어로 자격 증명 설정\n3. AWS_ACCESS_KEY_ID와 AWS_SECRET_ACCESS_KEY 환경 변수 설정"

                    # SDS Agent 호출 (구현 필요)
                    sds_response = "SDS AI 응답 준비 중..."
                    
                    answers = [ms_response, aws_response, sds_response]
                    # 응답 캐싱
                    st.session_state.cached_responses[last_user_message] = answers
            except Exception as e:
                st.error(f"AI 플랫폼 호출 중 오류 발생: {str(e)}")
                return

        label_list = ["1번 답변 👍", "2번 답변 👍", "3번 답변 👍"]

        if st.session_state.selected_answer_idx is None:
            # 카드/버튼 렌더링 (여기서만!)
            cards_html = f"""
            <div class="answer-scroll-row">
                <div class="answer-card">
                    <div>{answers[0]}</div>
                </div>
                <div class="answer-card">
                    <div>{answers[1]}</div>
                </div>
                <div class="answer-card">
                    <div>{answers[2]}</div>
                </div>
            </div>
            """
            st.markdown(cards_html, unsafe_allow_html=True)
            
            cols = st.columns(3)
            for idx, col in enumerate(cols):
                with col:
                    if st.button(label_list[idx], key=f"like_{idx}"):
                        st.session_state.selected_answer_idx = idx
                        st.session_state.selected_answer_content = answers[idx]
                        
                        # 답변의 품질 평가
                        quality_score, quality_reason = evaluate_response_quality(answers[idx])
                        
                        # 답변을 messages에 저장
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answers[idx],
                            "quality_score": quality_score
                        })
                        st.rerun()
        else:
            # 선택된 답변만 노출 (히스토리에 이미 있으므로 별도 출력하지 않음)
            idx = st.session_state.selected_answer_idx
            selected_text = st.session_state.selected_answer_content
            selected_card_html = f"""
            <div class="answer-scroll-row">
              <div class="answer-card">
                <div>{selected_text}</div>
              </div>
            </div>
            """
            # st.markdown(selected_card_html, unsafe_allow_html=True) 