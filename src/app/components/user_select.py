import streamlit as st
from src.data.users_data import USERS
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_user_desc(user_info):
    # 기본정보
    basic = user_info.get('info', {}).get('기본정보', {})
    age_group = basic.get('연령대', '')
    gender = basic.get('성별', '')
    
    # 설명문구 조합
    desc = f"{age_group} {gender}"
    return desc

def render_user_select():
    st.markdown("""
    <h2 style="margin-bottom:0.5em;">AI 보장분석을 진행할<br>캐릭터를 선택해 주세요</h2>
    <p style="color: #888; font-size: 0.95em; margin-bottom:2em;">
        캐릭터를 선택해 주시면 미리 설정해 놓은 보험가입, 건강검진 데이터를 활용하여 답변해 드릴게요.
    </p>
    """, unsafe_allow_html=True)

    # 사용자 id와 이름 매핑
    user_id_name_map = {
        "User1": "곰철수",
        "User2": "곰영희",
        "User3": "곰순이",
        "User4": "곰돌이"
    }
    
    # 사용자 이미지 매핑
    user_images = {
        "User1": "static/image/user1.png",
        "User2": "static/image/user2.png",
        "User3": "static/image/user3.png",
        "User4": "static/image/user4.png"
    }

    # 컬럼 생성
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 현재 선택된 사용자 이미지 표시
        current_user = st.session_state.get("user", "User1")
        st.markdown("""
        <style>
        @media (max-width: 768px) {
            [data-testid="stImage"] {
                display: block;
                margin-left: auto;
                margin-right: auto;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        st.image(user_images[current_user], width=150)
        st.markdown(f"### {user_id_name_map[current_user]} ({get_user_desc(USERS[current_user])})")

    with col2:
        # 사용자 선택 셀렉트 박스
        user_options = [f"{user_id_name_map[uid]} ({uid})" for uid in user_id_name_map.keys()]
        user_id_map = {f"{user_id_name_map[uid]} ({uid})": uid for uid in user_id_name_map.keys()}
        
        current_user_label = f"{user_id_name_map[current_user]} ({current_user})"
        
        selected_label = st.selectbox(
            "사용자 선택",
            user_options,
            index=user_options.index(current_user_label),
            key="user_select_box"
        )
        selected_user_id = user_id_map[selected_label]
        
        # 선택된 사용자가 변경되면 세션 상태 업데이트
        if selected_user_id != current_user:
            st.session_state["user"] = selected_user_id
            st.rerun()

        # 대화 시작 버튼
        if st.button("대화 시작하기", key="start_test_btn", use_container_width=True):
            st.session_state["selected_user"] = selected_user_id
            st.success(f"대화를 시작합니다: {user_id_name_map[selected_user_id]}")
            st.rerun() 