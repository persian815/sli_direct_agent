import streamlit as st
from src.app.config import initialize_app, load_js
from src.app.components import render_sidebar, render_chat_interface

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