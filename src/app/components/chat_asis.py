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
from src.utils.utils import (
    evaluate_response_quality,
    get_quality_level_color,
    evaluate_user_temperature,
    get_temperature_color
)

def render_chat_interface(model):
    """채팅 인터페이스를 렌더링하는 함수"""
    # Dark 테마 스타일링 추가
    st.markdown("""
    <style>
        /* Dark 테마 기본 스타일 */
        .stApp {
            background-color: #1E1E1E;
            color: #E0E0E0;
        }
        
        /* 채팅 메시지 스타일 */
        .stChatMessage {
            background-color: #2D2D2D;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #3D3D3D;
        }
        
        /* 사용자 메시지 스타일 */
        .stChatMessage[data-testid="stChatMessage"] {
            background-color: #1E3A5F;
            border-left: 4px solid #0066CC;
        }
        
        /* 어시스턴트 메시지 스타일 */
        .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
            background-color: #2D2D2D;
            border-left: 4px solid #4CAF50;
        }
        
        /* 입력 필드 스타일 */
        .stChatInputContainer {
            background-color: #2D2D2D;
            border-radius: 10px;
            padding: 10px;
            margin-top: 20px;
            border: 1px solid #3D3D3D;
        }
        
        div.stTextInput > div > div > input {
            background-color: #3D3D3D;
            color: #E0E0E0;
            border: 1px solid #4D4D4D;
            border-radius: 8px;
            padding: 10px 15px;
        }
        
        /* 캡션 스타일 */
        .stCaption {
            color: #A0A0A0;
            font-size: 0.85em;
        }
        
        /* 품질 점수 스타일 */
        .quality-score {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: bold;
            margin-top: 5px;
            margin-bottom: 5px;
        }
        
        /* 지식 수준 스타일 */
        .knowledge-level {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: bold;
            margin-top: 5px;
            margin-bottom: 5px;
        }
        
        /* 스크롤바 스타일 */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #2D2D2D;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #4D4D4D;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #5D5D5D;
        }
        
        /* 메트릭스 스타일 */
        .metrics {
            color: #A0A0A0;
            font-size: 0.85em;
            margin-top: 5px;
            margin-bottom: 5px;
        }
        
        /* 지식 수준 이유 스타일 */
        .knowledge-level-reason, .temperature-reason, .quality-reason {
            color: #A0A0A0;
            font-size: 0.8em;
            margin-top: 2px;
            margin-bottom: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # 메시지가 없는 경우 초기 메시지 표시
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("안녕하세요! 무엇을 도와드릴까요?")
    
    # 메시지 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # 개발자 모드가 켜져 있을 때만 Knowledge Level 표시
            if message['role'] == 'user' and st.session_state.get('developer_mode', False) and 'knowledge_level' in message:
                knowledge_level = message['knowledge_level']
                color = get_knowledge_level_color(knowledge_level)
                st.markdown(f'<div class="knowledge-level" style="background-color: {color}; color: white;">Knowledge Level: {knowledge_level}/100</div>', unsafe_allow_html=True)
                if 'knowledge_level_reason' in message:
                    st.markdown(f'<div class="knowledge-level-reason" style="color: #888888; font-size: 0.8em;">{message["knowledge_level_reason"]}</div>', unsafe_allow_html=True)
                
                # 사용자 온도 표시
                if 'temperature' in message:
                    temperature = message['temperature']
                    color = get_temperature_color(temperature)
                    st.markdown(f'<div class="temperature-level" style="background-color: {color}; color: white;">User Temperature: {temperature:.1f}°C</div>', unsafe_allow_html=True)
                    if 'temperature_reason' in message:
                        st.markdown(f'<div class="temperature-reason" style="color: #888888; font-size: 0.8em;">{message["temperature_reason"]}</div>', unsafe_allow_html=True)
            
            # 개발자 모드가 켜져 있을 때만 메트릭스 표시
            if message['role'] == 'assistant' and st.session_state.get('developer_mode', False):
                # 개발자 모드가 켜져 있을 때만 메트릭스 표시
                if st.session_state.get('developer_mode', False) and 'metrics' in message:
                    metrics = message['metrics']
                    st.markdown(f'<div class="metrics">Request Time: {metrics["request_time"]:.2f}s | Response Time: {metrics["response_time"]:.2f}s | Input Tokens: {metrics["input_tokens"]:.1f} | Output Tokens: {metrics["output_tokens"]:.1f}</div>', unsafe_allow_html=True)
                    
                    # Response Quality 표시 (quality_score가 None이 아닌 경우에만)
                    if 'quality_score' in message and message['quality_score'] is not None:
                        quality_score = message['quality_score']
                        color = get_quality_level_color(quality_score)
                        st.markdown(f'<div class="quality-score" style="background-color: {color}; color: white;">Response Quality: {quality_score}/100</div>', unsafe_allow_html=True)
                        if 'quality_reason' in message and message['quality_reason'] is not None:
                            st.markdown(f'<div class="quality-reason" style="color: #888888; font-size: 0.8em;">{message["quality_reason"]}</div>', unsafe_allow_html=True)
    
    # 답변 작성 중 메시지
    if st.session_state.get('is_generating', False):
        with st.chat_message("assistant"):
            st.markdown("답변 작성 중...")
    
    # 사용자 입력 받기
    if prompt := st.chat_input("메시지를 입력하세요"):
        # 사용자 입력 평가 (항상 수행)
        knowledge_level, knowledge_level_reason = evaluate_user_knowledge_level(prompt)
        temperature, temperature_reason = evaluate_user_temperature(prompt)
        
        # 사용자 메시지를 st.session_state.messages에 추가
        user_message = {
            "role": "user",
            "content": prompt,
            "knowledge_level": knowledge_level,
            "knowledge_level_reason": knowledge_level_reason,
            "temperature": temperature,
            "temperature_reason": temperature_reason
        }
        st.session_state.messages.append(user_message)
        
        # 사용자 메시지를 st.session_state.chat_messages에도 추가
        st.session_state.chat_messages.append(user_message)
        
        # 답변 작성 중 상태 설정
        st.session_state.is_generating = True
        
        # 어시스턴트 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("답변 작성 중..."):
                start_time = time.time()
                if model == "AWS Bedrock (클로드 3.5)":
                    response, trace_steps, elapsed_time, input_tokens, output_tokens, start_time = query_bedrock_agent(prompt)
                    # metrics 딕셔너리 생성
                    metrics = {
                        "request_time": elapsed_time,
                        "response_time": elapsed_time,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens
                    }
                elif model == "Azure AI Foundry (GPT-4.0)":
                    response, trace_steps, elapsed_time, input_tokens, output_tokens, start_time = query_ms_agent(prompt)
                    # metrics 딕셔너리 생성
                    metrics = {
                        "request_time": elapsed_time,
                        "response_time": elapsed_time,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens
                    }
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
                
                # 답변 작성 중 상태 해제
                st.session_state.is_generating = False
                
                # 응답 표시
                st.markdown(response)
                
                # 개발자 모드가 켜져 있을 때만 메트릭스 표시
                if st.session_state.get('developer_mode', False):
                    # 응답 품질 평가
                    quality_score, quality_reason = evaluate_response_quality(response)
                    color = get_quality_level_color(quality_score)
                    st.markdown(f'<div class="quality-score" style="background-color: {color}; color: white;">Response Quality: {quality_score}/100</div>', unsafe_allow_html=True)
                    if quality_reason:
                        st.markdown(f'<div class="quality-reason" style="color: #888888; font-size: 0.8em;">{quality_reason}</div>', unsafe_allow_html=True)
                    
                    # 메트릭스 표시
                    st.caption(f"Request Time: {metrics['request_time']:.2f}s | Response Time: {metrics['response_time']:.2f}s | Input Tokens: {metrics['input_tokens']:.1f} | Output Tokens: {metrics['output_tokens']:.1f}")
        
        # 어시스턴트 메시지 추가
        quality_score, quality_reason = evaluate_response_quality(response)
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "metrics": metrics,
            "quality_score": quality_score,
            "quality_reason": quality_reason
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