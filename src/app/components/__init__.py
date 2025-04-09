"""
UI 컴포넌트를 포함하는 패키지
"""

from src.app.components.sidebar import render_sidebar
from src.app.components.chat import render_chat_interface, generate_tab_name

__all__ = [
    'render_sidebar',
    'render_chat_interface',
    'generate_tab_name'
] 