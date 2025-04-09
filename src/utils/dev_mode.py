import streamlit as st
from datetime import datetime

# 함수 호출 로그 추가를 위한 래퍼 함수
def log_function_call(func):
    def wrapper(*args, **kwargs):
        # display_function_logs 함수는 로깅하지 않음 (재귀 방지)
        if func.__name__ == "display_function_logs":
            return func(*args, **kwargs)
            
        function_name = func.__name__
        parameters = {}
        
        # 위치 인자 처리
        for i, arg in enumerate(args):
            if i == 0 and hasattr(arg, "__class__"):
                # 첫 번째 인자가 클래스 인스턴스인 경우 (self)
                continue
            parameters[f"arg_{i}"] = str(arg)
        
        # 키워드 인자 처리
        for key, value in kwargs.items():
            parameters[key] = str(value)
        
        try:
            # LLM 응답 함수는 로깅을 건너뛰고 바로 실행
            if function_name in ["query_bedrock_agent", "query_ollama", "query_ollama_optimized"]:
                result = func(*args, **kwargs)
                # 결과는 나중에 로깅
                add_function_log(function_name, parameters, result="응답 생성됨 (로그 생략)")
                return result
            else:
                # 다른 함수는 정상적으로 로깅
                result = func(*args, **kwargs)
                add_function_log(function_name, parameters, result=result)
                return result
        except Exception as e:
            error_message = str(e)
            add_function_log(function_name, parameters, error=error_message)
            raise
    
    return wrapper

# 함수 호출 로그 추가 함수 (자체 로깅 방지)
def add_function_log(function_name, parameters=None, result=None, error=None):
    # add_function_log 함수 자체는 로깅하지 않음 (재귀 방지)
    if function_name == "add_function_log":
        return
        
    # function_logs가 없으면 초기화
    if "function_logs" not in st.session_state:
        st.session_state.function_logs = []
        
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "function": function_name,
        "parameters": parameters,
        "result": result,
        "error": error
    }
    st.session_state.function_logs.append(log_entry)
    # 로그 항목이 너무 많아지지 않도록 최대 50개만 유지
    if len(st.session_state.function_logs) > 50:
        st.session_state.function_logs = st.session_state.function_logs[-50:]

# 개발자 모드 UI 표시 함수
def display_dev_mode():
    st.markdown("---")
    st.header("👨‍💻 개발자 모드")

    # 개발자 모드 토글 (세션 상태에 저장)
    if "dev_mode" not in st.session_state:
        st.session_state.dev_mode = False

    # 토글 상태 변경 시에만 로그 표시 함수 호출
    dev_mode = st.toggle("개발자 모드 활성화", value=st.session_state.dev_mode)
    if dev_mode != st.session_state.dev_mode:
        st.session_state.dev_mode = dev_mode
        st.rerun()

    # 개발자 모드가 활성화된 경우에만 로그 표시
    if st.session_state.dev_mode:
        # 로그 표시 함수 직접 호출 (데코레이터 없이)
        st.markdown("### 📊 함수 호출 로그")
        
        # 로그 필터링 옵션
        filter_option = st.selectbox(
            "로그 필터",
            ["전체", "성공", "오류"],
            key="log_filter"
        )
        
        # 필터링된 로그 표시
        filtered_logs = st.session_state.function_logs
        if filter_option == "성공":
            filtered_logs = [log for log in filtered_logs if log["error"] is None]
        elif filter_option == "오류":
            filtered_logs = [log for log in filtered_logs if log["error"] is not None]
        
        # 로그 표시
        for log in reversed(filtered_logs):
            with st.expander(f"{log['timestamp']} - {log['function']}"):
                if log["parameters"]:
                    st.json(log["parameters"])
                if log["result"]:
                    st.success("결과:")
                    st.text(log["result"])
                if log["error"]:
                    st.error("오류:")
                    st.text(log["error"])
        
        # 로그가 없는 경우 안내 메시지 표시
        if not st.session_state.function_logs:
            st.info("아직 함수 호출 로그가 없습니다. 채팅을 시작하면 로그가 표시됩니다.")
            
        # 로그 초기화 버튼
        if st.button("로그 초기화", key="reset_logs"):
            st.session_state.function_logs = []
            st.rerun() 