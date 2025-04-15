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
        st.session_state.professional_role = "보험 전문가"
    if "character" not in st.session_state:
        st.session_state.character = "미영 FC"
    if "chat_tabs_enabled" not in st.session_state:
        st.session_state.chat_tabs_enabled = False

def evaluate_user_knowledge_level(user_input):
    """
    사용자의 질문을 분석하여 지식 레벨을 평가하는 함수
    
    Args:
        user_input (str): 사용자가 입력한 질문
        
    Returns:
        int: 1-100 사이의 지식 레벨 점수
    """
    # 전문 용어 카테고리별 점수
    professional_terms = {
        "보험": {
            "basic": ["보험", "보험료", "가입", "해지", "보장"],
            "intermediate": ["보험금", "보험사", "보험상품", "보험계약", "보험가입자"],
            "advanced": ["보험계리사", "보험리스크", "보험자산운용", "보험재보험", "보험규제"]
        },
        "재무": {
            "basic": ["재무", "자산", "부채", "수익", "비용"],
            "intermediate": ["재무제표", "재무분석", "재무비율", "재무계획", "재무상태"],
            "advanced": ["재무공시", "재무리스크", "재무구조조정", "재무파생상품", "재무투자"]
        },
        "투자": {
            "basic": ["투자", "주식", "채권", "펀드", "예금"],
            "intermediate": ["투자전략", "포트폴리오", "위험관리", "수익률", "투자분석"],
            "advanced": ["파생상품", "헤지펀드", "알파전략", "베타전략", "투자은행"]
        },
        "세금": {
            "basic": ["세금", "소득세", "부가세", "세율", "신고"],
            "intermediate": ["세무조사", "세무대리", "세무회계", "세무법인", "세무전문가"],
            "advanced": ["세무전략", "세무컨설팅", "세무리스크", "세무규제", "세무법률"]
        },
        "법률": {
            "basic": ["법률", "법규", "법조문", "법원", "변호사"],
            "intermediate": ["법률자문", "법률검토", "법률대리", "법률상담", "법률서류"],
            "advanced": ["법률전략", "법률리스크", "법률컨설팅", "법률규제", "법률분쟁"]
        },
        "의료": {
            "basic": ["의료", "병원", "의사", "약", "치료"],
            "intermediate": ["의료보험", "의료진", "의료기관", "의료서비스", "의료비"],
            "advanced": ["의료법", "의료분쟁", "의료사고", "의료보험", "의료규제"]
        },
        "기술": {
            "basic": ["기술", "소프트웨어", "하드웨어", "시스템", "데이터"],
            "intermediate": ["기술개발", "기술혁신", "기술투자", "기술분석", "기술경영"],
            "advanced": ["기술전략", "기술컨설팅", "기술리스크", "기술규제", "기술특허"]
        },
        "과학": {
            "basic": ["과학", "연구", "실험", "분석", "데이터"],
            "intermediate": ["과학연구", "과학기술", "과학분석", "과학데이터", "과학기법"],
            "advanced": ["과학전략", "과학컨설팅", "과학리스크", "과학규제", "과학특허"]
        },
        "경제": {
            "basic": ["경제", "시장", "가격", "수요", "공급"],
            "intermediate": ["경제분석", "경제정책", "경제지표", "경제성장", "경제위기"],
            "advanced": ["경제전략", "경제컨설팅", "경제리스크", "경제규제", "경제특허"]
        },
        "정책": {
            "basic": ["정책", "법규", "규제", "지원", "보조"],
            "intermediate": ["정책분석", "정책평가", "정책수립", "정책집행", "정책모니터링"],
            "advanced": ["정책전략", "정책컨설팅", "정책리스크", "정책규제", "정책특허"]
        },
        "질병": {
            "basic": ["감기", "기침", "발열", "두통", "통증"],
            "intermediate": ["고혈압", "당뇨병", "심장병", "폐렴", "관절염"],
            "advanced": ["심근경색", "뇌졸중", "암", "자가면역질환", "만성신부전"]
        },
        "건강": {
            "basic": ["운동", "식이", "수면", "스트레스", "면역력"],
            "intermediate": ["건강검진", "생활습관", "영양관리", "체중관리", "운동처방"],
            "advanced": ["건강증진", "질병예방", "건강관리", "건강컨설팅", "건강프로그램"]
        }
    }
    
    # 질문 형식 분석
    question_patterns = {
        "basic": ["어떻게", "왜", "어떤", "어디서", "언제", "누가"],
        "intermediate": ["어떻게 하면", "왜 그런", "어떤 것이", "어디서 볼", "언제부터", "누가 하는"],
        "advanced": ["어떻게 하면 좋을까", "왜 그런 것일까", "어떤 것이 더 나을까", "어디서 확인할 수 있을까", "언제부터 시작해야 할까", "누가 담당하는 것이 좋을까"]
    }
    
    # 점수 계산
    base_score = 30  # 기본 점수
    
    # 전문 용어 점수 계산 (최대 40점)
    term_score = 0
    for category, levels in professional_terms.items():
        for level, terms in levels.items():
            count = sum(1 for term in terms if term in user_input)
            if level == "basic":
                term_score += count * 2
            elif level == "intermediate":
                term_score += count * 3
            else:  # advanced
                term_score += count * 4
    
    # 질문 형식 점수 계산 (최대 20점)
    question_score = 0
    for level, patterns in question_patterns.items():
        count = sum(1 for pattern in patterns if pattern in user_input)
        if level == "basic":
            question_score += count * 2
        elif level == "intermediate":
            question_score += count * 3
        else:  # advanced
            question_score += count * 4
    
    # 문장 길이 점수 계산 (최대 10점)
    sentence_length = len(user_input.split())
    length_score = min(sentence_length // 2, 10)
    
    # 최종 점수 계산
    final_score = base_score + min(term_score, 40) + min(question_score, 20) + length_score
    
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