import streamlit as st
from app.config import initialize_app, load_js
from app.components import render_sidebar, render_chat_interface

def main():
    # Initialize the application
    initialize_app()

    # Title
    st.title("SLI 보장분석 Agent")

    # Render sidebar and get selected options
    model, role, character, _ = render_sidebar()

    # Render chat interface
    render_chat_interface(model)

    # Load JavaScript at the end of the page
    load_js()

if __name__ == "__main__":
    main() 