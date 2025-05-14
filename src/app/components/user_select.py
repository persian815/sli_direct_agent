import streamlit as st
from src.data.users_data import USERS
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def render_user_select():
    st.title("AI 보장분석을 진행할 사용자를 선택해 주세요")
    st.caption("사용자를 선택해 주시면 미리 설정해 놓은 보험가입, 건강검진 데이터를 활용하여 답변해 드릴게요.")

    # 사용자 정보 (이미지명과 매칭)
    users = [
        {"id": "User1", "desc": "고혈압/당뇨/고지혈증 보유", "img": "static/image/char1.png"},
        {"id": "User2", "desc": "건강한 상태", "img": "static/image/char2.png"},
        {"id": "User3", "desc": "가족력 있음", "img": "static/image/char3.png"},
        {"id": "User4", "desc": "특이사항 없음", "img": "static/image/char4.png"},
    ]

    # 현재 선택된 사용자 확인
    current_user = st.session_state.get("user", "User1")
    logger.debug(f"현재 선택된 사용자: {current_user}")

    cols = st.columns(2)
    for i, user in enumerate(users):
        with cols[i % 2]:
            # 사용자 정보 가져오기
            user_info = USERS.get(user['id'], {})
            if isinstance(user_info, list):
                user_info = user_info[0] if user_info else {}
            
            # 기본 정보 가져오기
            basic_info = user_info.get('기본정보', {})
            name = basic_info.get('이름', '')
            age = basic_info.get('나이', '')
            
            # 사용자 이름과 나이 표시
            display_name = f"{name} ({age}세)" if name and age else user['id']
            
            # 컨테이너 생성
            with st.container():
                st.image(user['img'], use_column_width=True)
                st.write(f"**{display_name}**")
                st.write(user['desc'])
                
                # 선택 버튼
                if st.button(f"{display_name} 선택", key=f"select_{user['id']}"):
                    st.session_state['user'] = user['id']
                    st.session_state['selected_user'] = user['id']
                    st.experimental_rerun() 