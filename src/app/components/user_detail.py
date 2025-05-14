import streamlit as st
import os
from PIL import Image
import io

USER_DETAILS = {
    "사용자 1": {
        "desc": "40대 남성으로 간 수치가 높으며 가족력이 있어 간 관련 질환에 대한 위험이 높습니다.",
        "img": "static/image/char1.png",
        "risks": [
            {"name": "뇌혈관질환", "percent": 12, "note": None},
            {"name": "급성심근경색", "percent": 20, "note": None},
            {"name": "간암", "percent": 33, "note": "주의"},
        ]
    },
    # ... 사용자 2, 3, 4도 추가
}

def render_user_select():
    st.markdown("""
    <style>
    .character-card {
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        padding: 24px 12px 12px 12px;
        margin-bottom: 24px;
        text-align: center;
        transition: box-shadow 0.2s, border 0.2s;
        border: 2px solid transparent;
    }
    .character-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.16);
        border: 2px solid #4CAF50;
    }
    .character-img {
        width: 100px;
        height: 100px;
        object-fit: contain;
        margin-bottom: 12px;
    }
    .character-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #222;
        margin-bottom: 4px;
    }
    .character-desc {
        font-size: 0.95rem;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h2 style="margin-bottom:0.5em;">AI 보장분석을 진행할<br>사용자를 선택해 주세요</h2>
    <p style="color: #888; font-size: 0.95em; margin-bottom:2em;">
        사용자를 선택해 주시면 미리 설정해 놓은 보험가입, 건강검진 데이터를 활용하여 답변해 드릴게요.
    </p>
    """, unsafe_allow_html=True)

    users = [
        {"name": "사용자 1", "desc": "설명 문구", "img": "static/image/char1.png"},
        {"name": "사용자 2", "desc": "설명 문구", "img": "static/image/char2.png"},
        {"name": "사용자 3", "desc": "설명 문구", "img": "static/image/char3.png"},
        {"name": "사용자 4", "desc": "설명 문구", "img": "static/image/char4.png"},
    ]

    cols = st.columns(2)
    for i, user in enumerate(users):
        with cols[i % 2]:
            st.markdown(f"<div class='character-card'>", unsafe_allow_html=True)
            img_path = os.path.join(os.getcwd(), user['img'])
            if not os.path.exists(img_path):
                st.error(f"이미지 파일이 존재하지 않습니다: {img_path}")
            else:
                st.image(img_path, width=100)
            st.markdown(f"<div class='character-title'>{user['name']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='character-desc'>{user['desc']}</div>", unsafe_allow_html=True)
            if st.button(f"{user['name']} 선택", key=user['name']):
                st.session_state.selected_user = user['name']
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# render_user_detail 함수 전체 삭제 