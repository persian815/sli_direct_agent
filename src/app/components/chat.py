import streamlit as st
import time
from src.llm import (
    query_bedrock_agent, query_ollama_optimized,
    evaluate_user_knowledge_level, get_knowledge_level_color
)
from src.visualization.visualization import (
    format_knowledge_level_html,
    format_metrics_html
)

def render_chat_interface(model):
    """채팅 인터페이스를 렌더링하는 함수"""
    # Main chat interface
    st.subheader(f"{model}")

    # Tab management
    col1, col2 = st.columns([6, 1])
    with col1:
        tabs = st.tabs(st.session_state.tabs)
    with col2:
        if st.button("에이전트 추가", key="new_chat"):
            tab_name = generate_tab_name(st.session_state.role, st.session_state.character)
            st.session_state.current_tab = tab_name
            st.session_state.tabs.append(tab_name)
            st.rerun()

    # Chat messages container
    st.markdown('<div class="chat-messages-container">', unsafe_allow_html=True)
    
    for i, tab in enumerate(tabs):
        with tab:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if message["role"] == "user" and "knowledge_level" in message:
                        st.markdown(
                            format_knowledge_level_html(
                                message["knowledge_level"],
                                get_knowledge_level_color(message["knowledge_level"])
                            ),
                            unsafe_allow_html=True
                        )
                    if "metrics" in message:
                        st.markdown(
                            format_metrics_html(
                                message["metrics"]["request_time"],
                                message["metrics"]["response_time"],
                                message["metrics"]["input_tokens"],
                                message["metrics"]["output_tokens"]
                            ),
                            unsafe_allow_html=True
                        )
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Chat input - Fixed at the bottom
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    
    # Create a container for the input that will be positioned within the fixed container
    with st.container():
        # Use a form to ensure the input is properly contained
        with st.form(key="chat_form", clear_on_submit=True):
            prompt = st.text_area("여기에 메시지를 입력하세요...", key="chat_input", label_visibility="collapsed")
            submit_button = st.form_submit_button("전송")
            
            if submit_button and prompt:
                # Add user message
                knowledge_level = evaluate_user_knowledge_level(prompt)
                st.session_state.messages.append({
                    "role": "user",
                    "content": prompt,
                    "knowledge_level": knowledge_level
                })
                
                # Generate response
                with st.chat_message("assistant"):
                    with st.spinner("답변 작성 중..."):
                        start_time = time.time()
                        if model == "AWS Bedrock (클로드 3.5)":
                            response, metrics = query_bedrock_agent(prompt)
                        else:
                            # Ollama 함수는 5개의 값을 반환합니다
                            response, response_time, input_tokens, output_tokens, _ = query_ollama_optimized(prompt)
                            # metrics 딕셔너리 생성
                            metrics = {
                                "request_time": time.time() - start_time,
                                "response_time": response_time,
                                "input_tokens": input_tokens,
                                "output_tokens": output_tokens
                            }
                        end_time = time.time()
                        
                        # Add metrics to response
                        metrics["request_time"] = end_time - start_time
                        metrics["response_time"] = metrics.get("response_time", 0)
                        
                        # Display response
                        st.markdown(response)
                        st.markdown(
                            format_metrics_html(
                                metrics["request_time"],
                                metrics["response_time"],
                                metrics["input_tokens"],
                                metrics["output_tokens"]
                            ),
                            unsafe_allow_html=True
                        )
                        
                        # Add assistant message
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "metrics": metrics
                        })
    
    st.markdown('</div>', unsafe_allow_html=True)

def generate_tab_name(role, character):
    """전문 역할, 캐릭터, 날짜, 시간을 조합하여 탭 이름을 생성하는 함수"""
    import datetime
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M")
    return f"{role}_{character}_{date_str}_{time_str}" 