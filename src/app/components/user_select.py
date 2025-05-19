import streamlit as st
from src.data.users_data import USERS
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_user_desc(user_info):
    # 기본정보
    basic = user_info.get('기본정보', {})
    age_group = basic.get('연령대', '')
    gender = basic.get('성별', '')
    # 건강검진 위험 요약
    health = user_info.get('건강검진정보', {})
    risks = [k for k, v in health.items() if isinstance(v, dict) and v.get('위험등급') == '위험']
    risk_str = ', '.join(risks) if risks else None
    # 보험가입내역 요약
    ins = user_info.get('보험가입내역', [])
    ins_str = f"보험 {len(ins)}건 가입" if ins else "보험 가입 없음"
    # 설명문구 조합
    desc = f"{age_group} {gender}, {ins_str}"
    if risk_str:
        desc += f" / 건강 위험: {risk_str}"
    return desc

def render_user_select():
    st.markdown("""
    <style>
    .character-scroll-row {
        display: flex;
        flex-direction: row;
        gap: 10px;
        overflow-x: auto;
        padding-bottom: 8px;
        margin-bottom: 12px;
        justify-content: space-between;
    }
    .character-card {
        border-radius: 18px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        padding: 12px 4px 8px 4px;
        background: #f5f6fa;
        transition: border 0.2s;
        border: 2px solid #fff;
        min-width: 80px;
        max-width: 100px;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        align-items: center;
        flex-shrink: 0;
        flex-basis: 25%;
        color: #222;
        cursor: pointer;
        position: relative;
    }
    .character-card.selected {
        border: 2.5px solid #3B82F6;
        box-shadow: 0 4px 16px rgba(59,130,246,0.10);
    }
    .character-img {
        width: 40px;
        height: 40px;
        object-fit: contain;
        margin-bottom: 8px;
    }
    .character-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #222;
        margin-bottom: 2px;
    }
    .character-desc {
        font-size: 0.8rem;
        color: #666;
        margin-bottom: 4px;
    }
    .character-card:hover {
        box-shadow: 0 4px 16px rgba(59,130,246,0.15);
        border: 2.5px solid #60a5fa;
    }
    @media (max-width: 600px) {
        .character-card { min-width: 22vw; max-width: 24vw; padding: 6px 2px 6px 2px; }
        .character-img { width: 32px; height: 32px; }
    }
    </style>
    <script>
    function selectCharacter(id) {
        window.parent.postMessage({type: 'streamlit:setComponentValue', key: 'selected_character', value: id}, '*');
    }
    </script>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h2 style="margin-bottom:0.5em;">AI 보장분석을 진행할<br>캐릭터를 선택해 주세요</h2>
    <p style="color: #888; font-size: 0.95em; margin-bottom:2em;">
        캐릭터를 선택해 주시면 미리 설정해 놓은 보험가입, 건강검진 데이터를 활용하여 답변해 드릴게요.
    </p>
    """, unsafe_allow_html=True)

    # USERS에서 정보 추출
    users = []
    for user_id, user_data in USERS.items():
        info = user_data.get('info', {})
        name = info.get('기본정보', {}).get('이름', user_id)
        desc = get_user_desc(info)
        img = f"static/image/char{user_id[-1]}.png"
        users.append({"id": user_id, "desc": desc, "img": img, "name": name})

    current_user = st.session_state.get("user", "User1")
    logger.debug(f"현재 선택된 사용자: {current_user}")

    # 가로 스크롤 row로 캐릭터 카드 나열
    cards_html = '<div class="character-scroll-row">'
    for user in users:
        selected = "selected" if user['id'] == current_user else ""
        # 카드 전체에 JS 클릭 이벤트 부여
        cards_html += f'''
        <div class="character-card {selected}" onclick="window.parent.postMessage({{isStreamlitMessage: true, type: 'streamlit:setComponentValue', key: 'selected_character', value: '{user['id']}' }}, '*')">
            <img src="{user['img']}" class="character-img" />
            <div class="character-title">{user['name']}</div>
            <div class="character-desc">{user['desc']}</div>
        </div>
        '''
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # Streamlit 버튼 대신 카드 클릭으로 선택 처리
    for user in users:
        if st.session_state.get('selected_character') == user['id']:
            st.session_state['user'] = user['id']
            st.session_state['selected_user'] = user['id']
            st.session_state['selected_character'] = None
            st.experimental_rerun() 