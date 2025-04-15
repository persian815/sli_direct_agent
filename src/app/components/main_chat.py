import streamlit as st
import time

# Set page configuration
st.set_page_config(
    page_title="김상성님 - 친절한 금자씨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Global styles */
    body {
        background-color: #1A1A1A;
        color: white;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell;
    }
    
    /* Header styling */
    .header-container {
        text-align: center;
        padding: 1rem 0;
        margin-top: 2rem;
    }
    
    .header-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 18px;
        margin-top: 0.5rem;
    }
    
    /* Avatar styling */
    .avatar-container {
        display: flex;
        justify-content: center;
        margin: 1.5rem 0;
    }
    
    .avatar-circle {
        width: 112px;
        height: 112px;
        border-radius: 50%;
        background-color: #FFB800;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .avatar-image {
        width: 96px;
        height: 96px;
        border-radius: 50%;
        object-fit: cover;
    }
    
    /* Assistant name styling */
    .assistant-name {
        text-align: center;
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 0.75rem;
    }
    
    /* Pagination dots */
    .pagination-dots {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    
    .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: white;
        margin: 0 4px;
    }
    
    .dot.inactive {
        opacity: 0.5;
    }
    
    /* Message styling */
    .user-message {
        background-color: #0066FF;
        color: white;
        border-radius: 10px;
        border-bottom-right-radius: 0;
        padding: 8px 16px;
        margin: 8px 0;
        text-align: right;
        float: right;
        clear: both;
        max-width: 80%;
    }
    
    .bot-message {
        background-color: #444444;
        color: white;
        border-radius: 10px;
        border-bottom-left-radius: 0;
        padding: 8px 16px;
        margin: 8px 0;
        text-align: left;
        float: left;
        clear: both;
        max-width: 80%;
    }
    
    .message-container {
        overflow-y: auto;
        height: 400px;
        padding: 10px;
    }
    
    /* Input area styling */
    .input-area {
        background-color: #1A1A1A;
        padding: 0.75rem 1rem;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
    }
    
    /* Main container to give space for fixed input */
    .main-container {
        margin-bottom: 70px;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    .stApp {
        background-color: #1A1A1A;
    }
    
    div.stTextInput > div > div > input {
        background-color: #222222;
        color: white;
        border: 1px solid #333333;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state to store messages if not already defined
if 'messages' not in st.session_state:
    st.session_state.messages = []

# App container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown('''
<div class="header-container">
    <div class="header-title">김상성님</div>
    <div class="header-subtitle">무엇을 도와드릴까요?</div>
</div>
''', unsafe_allow_html=True)

# Avatar
st.markdown('''
<div class="avatar-container">
    <div class="avatar-circle">
        <img class="avatar-image" src="https://your-image-url.com/avatar.png" alt="친절한 금자씨">
    </div>
</div>
''', unsafe_allow_html=True)

# Assistant name
st.markdown('<div class="assistant-name">친절한 금자씨</div>', unsafe_allow_html=True)

# Pagination dots
st.markdown('''
<div class="pagination-dots">
    <div class="dot"></div>
    <div class="dot inactive"></div>
    <div class="dot inactive"></div>
    <div class="dot inactive"></div>
</div>
''', unsafe_allow_html=True)

# Display chat messages
st.markdown('<div class="message-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    if message['sender'] == 'user':
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Close main container
st.markdown('</div>', unsafe_allow_html=True)

# Input area with form to prevent page reloading
with st.container():
    st.markdown('<div class="input-area">', unsafe_allow_html=True)
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("", placeholder="AI 에이전트에게 궁금한 점을 물어보세요", label_visibility="collapsed")
        submit_button = st.form_submit_button(label="전송", use_container_width=True)

        if submit_button and user_input:
            # Add user message to session state
            st.session_state.messages.append({
                "content": user_input,
                "sender": "user"
            })
            
            # Simulate bot response
            placeholder = st.empty()
            placeholder.markdown('<div class="bot-message">입력 중...</div>', unsafe_allow_html=True)
            time.sleep(1)  # Simulate delay
            
            # Add bot response to session state
            bot_response = "죄송합니다, 지금은 응답할 수 없습니다."
            st.session_state.messages.append({
                "content": bot_response,
                "sender": "bot"
            })
            
            # Rerun to update chat interface
            st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Add JavaScript to auto-scroll to bottom and focus on input
st.markdown("""
<script>
    // Auto-scroll to the bottom of the messages container
    function scrollToBottom() {
        const messageContainer = document.querySelector('.message-container');
        if (messageContainer) {
            messageContainer.scrollTop = messageContainer.scrollHeight;
        }
    }
    
    // Focus on the input field
    function focusInput() {
        const inputField = document.querySelector('input[type="text"]');
        if (inputField) {
            inputField.focus();
        }
    }
    
    // Run these functions when the page loads
    window.onload = function() {
        scrollToBottom();
        focusInput();
    };
</script>
""", unsafe_allow_html=True)
