import streamlit as st
import time
import os
import re
from src.llm import (
    evaluate_user_knowledge_level, get_knowledge_level_color
)
from src.visualization.visualization import (
    format_knowledge_level_html,
    format_metrics_html
)
from src.utils.utils import (
    evaluate_response_quality,
    get_quality_level_color,
    evaluate_user_temperature,
    get_temperature_color,
    send_chat_log_to_api
)
from src.llm.ms_functions import query_ms_agent

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
        "User1": "static/image/char1.png",
        "User2": "static/image/char2.png",
        "User3": "static/image/char3.png",
        "User4": "static/image/char4.png"
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

def render_chat_interface(model: str):
    """채팅 인터페이스를 렌더링합니다."""
    # CSS 로드
    load_css()
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    user_icon = get_user_icon()
    character_icon = get_character_icon(st.session_state.get("character", "논리적인 테스형"))
    
    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar=user_icon):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=character_icon):
                st.markdown(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요"):
        # 사용자 메시지 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=user_icon):
            st.markdown(prompt)
        # 답변 작성 중 spinner
        with st.spinner("답변 작성 중..."):
            # 답변 3개 생성
            # response, _, elapsed_time, input_tokens, output_tokens, start_time = query_ms_agent(prompt)
            dummy_ms = "안녕하세요, 곰철수님! 다시 만나 뵙게 되어 반갑습니다.\n고객님의 건강 상태와 보험 가입 상황을 바탕으로 아래와 같은 분석을 제공합니다.\n\n예상 응답:\n- AWS Bedrock은 Amazon의 완전 관리형 서비스로, 다양한 파운데이션 모델을 제공합니다.\n- 현재 API 연동 작업이 진행 중이며, 곧 서비스가 시작될 예정입니다.\n- 더 자세한 정보는 AWS Bedrock 공식 문서를 참조하세요."
            dummy_aws = "안녕하세요, 곰철수님! 다시 만나 뵙게 되어 반갑습니다.\n고객님의 건강 상태와 보험 가입 상황을 바탕으로 아래와 같은 분석을 제공합니다.\n\n예상 응답:\n- AWS Bedrock은 Amazon의 완전 관리형 서비스로, 다양한 파운데이션 모델을 제공합니다.\n- 현재 API 연동 작업이 진행 중이며, 곧 서비스가 시작될 예정입니다.\n- 더 자세한 정보는 AWS Bedrock 공식 문서를 참조하세요."
            dummy_sds = "안녕하세요, 곰철수님! 다시 만나 뵙게 되어 반갑습니다.\n고객님의 건강 상태와 보험 가입 상황을 바탕으로 아래와 같은 분석을 제공합니다.\n\n예상 응답:\n- SDS AI는 삼성 SDS의 AI 플랫폼으로, 다양한 비즈니스 솔루션을 제공합니다.\n- 현재 API 연동 작업이 진행 중이며, 곧 서비스가 시작될 예정입니다.\n- 더 자세한 정보는 SDS AI 공식 문서를 참조하세요."

            # 답변 카드 row (HTML/CSS + JS)
            ms_tokens = int(len(prompt.split()) // 1.3)
            aws_tokens = int(len(prompt.split()) // 1.3)
            sds_tokens = int(len(prompt.split()) // 1.3)
            cards_html = f"""
<div class=\"answer-scroll-row\">\n    <div class=\"answer-card\">\n        <div>{dummy_ms}</div>\n        <div style=\"font-size:0.9em;color:#888;margin-top:10px;\">\n            입력 토큰: {ms_tokens} / 출력 토큰: 150 / 처리 시간: 2.5초\n        </div>\n        <button class=\"like-btn\" disabled>👍 좋아요</button>\n    </div>\n    <div class=\"answer-card\">\n        <div>{dummy_aws}</div>\n        <div style=\"font-size:0.9em;color:#888;margin-top:10px;\">\n            입력 토큰: {aws_tokens} / 출력 토큰: 150 / 처리 시간: 2.5초\n        </div>\n        <button class=\"like-btn\" disabled>👍 좋아요</button>\n    </div>\n    <div class=\"answer-card\">\n        <div>{dummy_sds}</div>\n        <div style=\"font-size:0.9em;color:#888;margin-top:10px;\">\n            입력 토큰: {sds_tokens} / 출력 토큰: 120 / 처리 시간: 1.8초\n        </div>\n        <button class=\"like-btn\" disabled>👍 좋아요</button>\n    </div>\n</div>
"""
            st.markdown(cards_html, unsafe_allow_html=True)

            # 메시지 히스토리에는 strip_html_tags(response) 등 순수 텍스트만 저장
            plain_response = strip_html_tags(dummy_ms)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"Azure AI Foundry: {plain_response}\n\nAWS Bedrock: API 연동 중\n\nSDS AI: API 연동 중"
            })

def generate_tab_name(role, character):
    """전문 역할, 캐릭터, 날짜, 시간을 조합하여 탭 이름을 생성하는 함수"""
    import datetime
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M")
    return f"{role}_{character}_{date_str}_{time_str}" 