import streamlit as st
import time
from src.llm import (
    query_bedrock_agent, query_ollama_optimized, query_ms_agent,
    evaluate_user_knowledge_level, get_knowledge_level_color
)
from src.visualization.visualization import (
    format_knowledge_level_html,
    format_metrics_html
)

def render_chat_interface(model):
    """채팅 인터페이스를 렌더링하는 함수"""
    # 기본 스트림릿 컴포넌트를 사용하여 UI 구성
    #st.title("채팅 인터페이스")
    
    # 간단한 스타일링 추가
    st.markdown("""
    <style>
        /* 사용자 메시지 스타일 */
        .user-message {
            background-color: #e6f3ff;
            border-radius: 10px;
            padding: 10px 15px;
            margin: 5px 0;
            border-left: 5px solid #0066cc;
        }
        
        /* 어시스턴트 메시지 스타일 */
        .assistant-message {
            background-color: #f0f0f0;
            border-radius: 10px;
            padding: 10px 15px;
            margin: 5px 0;
            border-left: 5px solid #4CAF50;
        }
        
        /* 메시지 컨테이너 스타일 */
        .message-container {
            max-height: 500px;
            overflow-y: auto;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        
        /* 입력 영역 스타일 */
        .input-area {
            margin-top: 20px;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 메시지 컨테이너
    st.markdown('<div class="message-container">', unsafe_allow_html=True)
    
    # 메시지가 없는 경우 초기 메시지 표시
    if not st.session_state.messages:
        st.markdown('<div class="assistant-message">안녕하세요! 무엇을 도와드릴까요?</div>', unsafe_allow_html=True)
    
    # 메시지 표시
    for message in st.session_state.messages:
        if message['role'] == 'user':
            st.markdown(f'<div class="user-message"><strong>사용자:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            # 개발자 모드가 켜져 있을 때만 Knowledge Level 표시
            if st.session_state.get('developer_mode', False) and 'knowledge_level' in message:
                knowledge_level = message['knowledge_level']
                st.caption(f"Knowledge Level: {knowledge_level}")
        else:
            st.markdown(f'<div class="assistant-message"><strong>어시스턴트:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            # 개발자 모드가 켜져 있을 때만 메트릭스 표시
            if st.session_state.get('developer_mode', False) and 'metrics' in message:
                metrics = message['metrics']
                st.caption(f"Request Time: {metrics['request_time']:.2f}s | Response Time: {metrics['response_time']:.2f}s | Input Tokens: {metrics['input_tokens']:.1f} | Output Tokens: {metrics['output_tokens']:.1f}")
    
    # 답변 작성 중 메시지
    if st.session_state.get('is_generating', False):
        st.markdown('<div class="assistant-message">답변 작성 중...</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 입력 영역
    st.markdown('<div class="input-area">', unsafe_allow_html=True)
    with st.form(key="message_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("메시지를 입력하세요", key="user_input")
        with col2:
            submit_button = st.form_submit_button("전송")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 폼 제출 처리
    if submit_button and user_input:
        # 사용자 메시지 추가
        knowledge_level = evaluate_user_knowledge_level(user_input)
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "knowledge_level": knowledge_level
        })
        
        # 답변 작성 중 상태 설정
        st.session_state.is_generating = True
        
        # 어시스턴트 응답 생성
        with st.spinner("답변 작성 중..."):
            start_time = time.time()
            if model == "AWS Bedrock (클로드 3.5)":
                response, trace_steps, elapsed_time, input_tokens, output_tokens, start_time = query_bedrock_agent(user_input)
                # metrics 딕셔너리 생성
                metrics = {
                    "request_time": elapsed_time,
                    "response_time": elapsed_time,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                }
            elif model == "Azure AI Foundry (GPT-4.0)":
                response, trace_steps, elapsed_time, input_tokens, output_tokens, start_time = query_ms_agent(user_input)
                # metrics 딕셔너리 생성
                metrics = {
                    "request_time": elapsed_time,
                    "response_time": elapsed_time,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                }
            else:
                # Ollama 함수는 5개의 값을 반환합니다
                response, response_time, input_tokens, output_tokens, _ = query_ollama_optimized(user_input)
                # metrics 딕셔너리 생성
                metrics = {
                    "request_time": time.time() - start_time,
                    "response_time": response_time,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                }
            
            # 답변 작성 중 상태 해제
            st.session_state.is_generating = False
            
            # 어시스턴트 메시지 추가
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "metrics": metrics
            })
            
        # 페이지 새로고침
        st.rerun()

def generate_tab_name(role, character):
    """전문 역할, 캐릭터, 날짜, 시간을 조합하여 탭 이름을 생성하는 함수"""
    import datetime
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M")
    return f"{role}_{character}_{date_str}_{time_str}" 