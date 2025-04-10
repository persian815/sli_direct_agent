import streamlit as st
from typing import Dict, List, Tuple, Any, Optional

def initialize_session_state():
    """세션 상태 초기화 함수"""
    # 세션 상태 초기화
    if "active_tabs" not in st.session_state:
        st.session_state.active_tabs = []
    if "tab_messages" not in st.session_state:
        st.session_state.tab_messages = {}
    if "tab_models" not in st.session_state:
        st.session_state.tab_models = {}
    if "tab_names" not in st.session_state:
        st.session_state.tab_names = {}
    if "tab_system_prompts" not in st.session_state:
        st.session_state.tab_system_prompts = {}
    if "tab_agents" not in st.session_state:
        st.session_state.tab_agents = {}
    if "tab_agent_alias_ids" not in st.session_state:
        st.session_state.tab_agent_alias_ids = {}
    if "function_logs" not in st.session_state:
        st.session_state.function_logs = []
    if "ollama_model" not in st.session_state:
        st.session_state.ollama_model = None
    if "current_tab_index" not in st.session_state:
        st.session_state.current_tab_index = 0
    if "professional_role" not in st.session_state:
        st.session_state.professional_role = "보험 설계사"
    if "character" not in st.session_state:
        st.session_state.character = "은별 나인"

def evaluate_user_knowledge_level(user_input):
    """
    사용자의 질문을 분석하여 지식 레벨을 평가하는 함수
    
    Args:
        user_input (str): 사용자가 입력한 질문
        
    Returns:
        int: 1-100 사이의 지식 레벨 점수
    """
    # 간단한 지식 레벨 평가 로직
    # 실제로는 더 복잡한 분석이 필요할 수 있음
    
    # 전문 용어 사용 빈도 확인
    professional_terms = ["보험", "재무", "투자", "세금", "법률", "의료", "기술", "과학", "경제", "정책"]
    term_count = sum(1 for term in professional_terms if term in user_input)
    
    # 문장 길이 및 복잡성 확인
    sentence_length = len(user_input.split())
    
    # 질문 형식 확인 (개방형 질문인지, 닫힌 질문인지)
    is_open_question = any(q in user_input for q in ["어떻게", "왜", "어떤", "어디서", "언제", "누가"])
    
    # 점수 계산 (1-100 사이)
    base_score = 50  # 기본 점수
    
    # 전문 용어 사용에 따른 점수 조정
    term_score = min(term_count * 10, 30)  # 최대 30점 추가
    
    # 문장 길이에 따른 점수 조정
    length_score = min(sentence_length, 10)  # 최대 10점 추가
    
    # 질문 형식에 따른 점수 조정
    question_score = 10 if is_open_question else 0
    
    # 최종 점수 계산
    final_score = base_score + term_score + length_score + question_score
    
    # 점수 범위 제한 (1-100)
    return max(1, min(100, final_score))

def get_knowledge_level_color(level):
    """
    지식 레벨에 따른 색상 반환
    
    Args:
        level (int): 1-100 사이의 지식 레벨
        
    Returns:
        str: CSS 색상 코드
    """
    if level <= 30:
        return "#ff6b6b"  # 빨간색 (낮은 레벨)
    elif level <= 70:
        return "#ffd166"  # 노란색 (중간 레벨)
    else:
        return "#06d6a0"  # 초록색 (높은 레벨)

def add_function_log(log_entry: str) -> None:
    """함수 호출 로그를 추가하는 함수"""
    if "function_logs" not in st.session_state:
        st.session_state.function_logs = []
    
    timestamp = st.session_state.get("current_timestamp", "")
    st.session_state.function_logs.append(f"{timestamp} - {log_entry}")

def log_function_call(func):
    """함수 호출을 로깅하는 데코레이터"""
    def wrapper(*args, **kwargs):
        # Skip logging for display_function_logs to prevent recursion
        if func.__name__ == "display_function_logs":
            return func(*args, **kwargs)
        
        # 현재 타임스탬프 저장
        st.session_state.current_timestamp = st.session_state.get("current_timestamp", "")
        
        # 함수 호출 로그 추가
        add_function_log(f"함수 호출: {func.__name__}")
        
        # 함수 실행
        result = func(*args, **kwargs)
        
        # 함수 완료 로그 추가
        add_function_log(f"함수 완료: {func.__name__}")
        
        return result
    
    return wrapper 