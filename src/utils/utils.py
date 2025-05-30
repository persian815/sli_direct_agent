import random
import streamlit as st
from typing import Dict, List, Tuple, Any, Optional
import logging
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # 터미널에 출력
    ]
)
logger = logging.getLogger(__name__)

# 로그 레벨 설정 확인
logger.setLevel(logging.INFO)
logger.info("Utils module initialized")  # 시작 로그 추가

def evaluate_response_quality(response):
    """응답의 품질을 1~100 사이의 점수로 평가하는 함수"""
    # 실제 구현에서는 더 복잡한 평가 로직을 사용할 수 있습니다.
    # 여기서는 간단한 예시로 구현합니다.
    
    # 응답 길이에 따른 기본 점수 (최대 30점)
    length_score = min(len(response) / 100, 30)
    length_reason = f"응답 길이: {len(response)}자 (최대 30점)"
    
    # 응답의 다양성 점수 (최대 20점)
    # 단어 다양성, 문장 구조 다양성 등을 고려할 수 있습니다.
    words = response.split()
    unique_words = len(set(words))
    diversity_score = min(unique_words / 50, 20)
    diversity_reason = f"단어 다양성: {unique_words}개 고유 단어 (최대 20점)"
    
    # 응답의 일관성 점수 (최대 20점)
    # 문장 간 연결성, 논리적 흐름 등을 고려할 수 있습니다.
    consistency_score = random.uniform(10, 20)  # 예시로 랜덤 값 사용
    consistency_reason = f"응답 일관성: {consistency_score:.1f}점 (최대 20점)"
    
    # 응답의 정확성 점수 (최대 30점)
    # 실제 구현에서는 외부 지식 베이스나 검증 로직을 사용할 수 있습니다.
    accuracy_score = random.uniform(15, 30)  # 예시로 랜덤 값 사용
    accuracy_reason = f"응답 정확성: {accuracy_score:.1f}점 (최대 30점)"
    
    # 총점 계산 (1~100 사이)
    total_score = int(length_score + diversity_score + consistency_score + accuracy_score)
    
    # 1~100 사이로 제한
    final_score = max(1, min(100, total_score))
    
    # 판단 사유 생성
    reason = f"{length_reason} | {diversity_reason} | {consistency_reason} | {accuracy_reason}"
    
    return final_score, reason

def get_quality_level_color(score):
    """품질 점수에 따른 색상 반환"""
    if score is None:
        return "#808080"  # 기본 회색
    if score >= 80:
        return "#4CAF50"  # 녹색
    elif score >= 60:
        return "#FFC107"  # 노란색
    else:
        return "#F44336"  # 빨간색

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
        st.session_state.professional_role = "통합 전문가"
    if "character" not in st.session_state:
        st.session_state.character = "친절한 미영씨"
    if "chat_tabs_enabled" not in st.session_state:
        st.session_state.chat_tabs_enabled = False

def evaluate_user_knowledge_level(user_input):
    """
    사용자의 질문을 분석하여 지식 레벨을 평가하는 함수
    
    Args:
        user_input (str): 사용자가 입력한 질문
        
    Returns:
        tuple: (지식 레벨 점수, 레벨 측정 사유)
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
    term_reasons = []
    for category, levels in professional_terms.items():
        for level, terms in levels.items():
            found_terms = [term for term in terms if term in user_input]
            if found_terms:
                count = len(found_terms)
                if level == "basic":
                    term_score += count * 2
                    term_reasons.append(f"기본 {category} 용어 {', '.join(found_terms)} 사용")
                elif level == "intermediate":
                    term_score += count * 3
                    term_reasons.append(f"중급 {category} 용어 {', '.join(found_terms)} 사용")
                else:  # advanced
                    term_score += count * 4
                    term_reasons.append(f"고급 {category} 용어 {', '.join(found_terms)} 사용")
    
    # 질문 형식 점수 계산 (최대 20점)
    question_score = 0
    question_reasons = []
    for level, patterns in question_patterns.items():
        found_patterns = [pattern for pattern in patterns if pattern in user_input]
        if found_patterns:
            count = len(found_patterns)
            if level == "basic":
                question_score += count * 2
                question_reasons.append(f"기본 질문 형식 {', '.join(found_patterns)} 사용")
            elif level == "intermediate":
                question_score += count * 3
                question_reasons.append(f"중급 질문 형식 {', '.join(found_patterns)} 사용")
            else:  # advanced
                question_score += count * 4
                question_reasons.append(f"고급 질문 형식 {', '.join(found_patterns)} 사용")
    
    # 문장 길이 점수 계산 (최대 10점)
    sentence_length = len(user_input.split())
    length_score = min(sentence_length // 2, 10)
    length_reason = f"문장 길이 {sentence_length}단어"
    
    # 최종 점수 계산
    final_score = base_score + min(term_score, 40) + min(question_score, 20) + length_score
    
    # 점수 범위 제한 (1-100)
    final_score = max(1, min(100, final_score))
    
    # 레벨 측정 사유 생성
    reasons = []
    if term_reasons:
        reasons.extend(term_reasons)
    if question_reasons:
        reasons.extend(question_reasons)
    if length_reason:
        reasons.append(length_reason)
    
    reason_text = " | ".join(reasons) if reasons else "기본 점수 30점"
    
    return final_score, reason_text

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

def evaluate_user_temperature(user_input):
    """
    사용자의 질문을 분석하여 성향이나 말투를 온도로 평가하는 함수
    
    Args:
        user_input (str): 사용자가 입력한 질문
        
    Returns:
        tuple: (온도 점수, 온도 측정 사유)
    """
    # 온도 점수 초기화 (기본 체온 36.5도 기준)
    base_temperature = 36.5
    temperature_score = base_temperature
    reasons = []
    
    # 질문 길이에 따른 온도 조정
    if len(user_input) < 10:
        temperature_score -= 0.5
        reasons.append("짧은 질문")
    elif len(user_input) > 100:
        temperature_score += 0.5
        reasons.append("상세한 질문")
    
    # 존댓말 사용 여부 확인
    if "요" in user_input or "니다" in user_input or "습니다" in user_input or "세요" in user_input:
        temperature_score += 0.3
        reasons.append("존댓말 사용")
    elif "다" in user_input or "까" in user_input or "요" not in user_input:
        temperature_score -= 0.3
        reasons.append("반말 사용")
    
    # 친절한 표현 확인
    friendly_terms = ["부탁", "도움", "감사", "고맙", "죄송", "죄송합니다", "부탁드립니다", "도와주세요"]
    for term in friendly_terms:
        if term in user_input:
            temperature_score += 0.2
            reasons.append(f"친절한 표현: '{term}'")
            break
    
    # 불친절한 표현 확인
    unfriendly_terms = ["바보", "멍청", "짜증", "화나", "짜증나", "짜증난다", "짜증납니다"]
    for term in unfriendly_terms:
        if term in user_input:
            temperature_score -= 0.5
            reasons.append(f"불친절한 표현: '{term}'")
            break
    
    # 온도 범위 제한 (35.0 ~ 38.0)
    temperature_score = max(35.0, min(38.0, temperature_score))
    
    # 측정 사유 생성
    reason = " | ".join(reasons) if reasons else "기본 온도"
    
    return temperature_score, reason

def get_temperature_color(temperature):
    """온도에 따른 색상 반환"""
    if temperature is None:
        return "#808080"  # 기본 회색
    if temperature >= 37.5:
        return "#FF5252"  # 빨간색
    elif temperature >= 37.0:
        return "#FFC107"  # 노란색
    else:
        return "#4CAF50"  # 녹색

def send_chat_log_to_api(question, answer):
    """채팅 로그를 API로 전송하는 함수"""
    import requests
    import json
    
    api_url = "https://team2-webapp-g2a2cgb8hvemdzc6.koreacentral-01.azurewebsites.net/api/chat/log"
    
    # 전송할 데이터 준비
    data = {
        "question": question,
        "answer": answer
    }
    
    try:
        logger.info(f"Preparing to send chat log to API: {data}")
        
        # API 호출
        response = requests.post(api_url, json=data)
        
        # 응답 확인
        if response.status_code == 200:
            # 응답 내용에서 헤더 정보 제외
            response_text = response.text
            if "Response headers:" in response_text:
                response_text = response_text.split("Response headers:")[0].strip()
            logger.info(f"Chat log sent successfully: {response_text}")
            add_function_log(f"채팅 로그 전송 성공: {response_text}")
            return True
        else:
            # 응답 내용에서 헤더 정보 제외
            response_text = response.text
            if "Response headers:" in response_text:
                response_text = response_text.split("Response headers:")[0].strip()
            logger.error(f"Failed to send chat log: {response.status_code} - {response_text}")
            add_function_log(f"채팅 로그 전송 실패: {response.status_code} - {response_text}")
            return False
    except Exception as e:
        logger.error(f"Error while sending chat log: {str(e)}")
        add_function_log(f"채팅 로그 전송 중 오류 발생: {str(e)}")
        return False

def get_chat_history_from_api():
    """API에서 채팅 히스토리를 가져오는 함수"""
    import requests
    import json
    
    api_url = "https://team2-webapp-g2a2cgb8hvemdzc6.koreacentral-01.azurewebsites.net/api/chat/log"
    
    try:
        # API 호출
        response = requests.get(api_url)
        
        # 응답 확인
        if response.status_code == 200:
            # 응답 내용에서 헤더 정보 제외
            response_text = response.text
            if "Response headers:" in response_text:
                response_text = response_text.split("Response headers:")[0].strip()
            
            # JSON 파싱
            try:
                chat_history = json.loads(response_text)
                add_function_log(f"채팅 히스토리 가져오기 성공: {len(chat_history)}개 항목")
                return chat_history
            except json.JSONDecodeError:
                add_function_log(f"채팅 히스토리 JSON 파싱 실패: {response_text}")
                return []
        else:
            add_function_log(f"채팅 히스토리 가져오기 실패: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        add_function_log(f"채팅 히스토리 가져오기 중 오류 발생: {str(e)}")
        return []

def get_role_specific_message(agent_role):
    """
    역할에 따른 맞춤 환영 메시지를 반환하는 함수
    
    Args:
        agent_role (str): 에이전트의 역할
    
    Returns:
        str: 역할에 맞는 환영 메시지
    """
    if agent_role == "통합 전문가":
        return "어떤 도움이 필요하신가요?"
    elif agent_role == "질병 전문가":
        return "어떤 고민이 있으신가요?"
    elif agent_role == "라이프 전문가":
        return "평소 어떤 생활을 하시나요?"
    else:
        return "어떤 도움이 필요하신가요?" 