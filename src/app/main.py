import streamlit as st
from src.app.config import initialize_app, load_js
from src.app.components import render_sidebar, render_chat_interface

# Page config - 반드시 첫 번째 Streamlit 명령이어야 함
st.set_page_config(
    page_title="다이렉트 ai FIT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize the application
    initialize_app()

    # Title
    st.title("다이렉트 ai FIT")

    # Render sidebar and get selected options
    model, role, character, _ = render_sidebar()

    # Render chat interface
    render_chat_interface(model)

    # Load JavaScript at the end of the page
    load_js()

if __name__ == "__main__":
    main() 