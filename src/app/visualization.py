def plot_knowledge_distribution():
    """지식 레벨 분포 그래프"""
    # 더미 데이터 대신 실제 채팅 히스토리에서 지식 레벨 데이터를 집계
    knowledge_data = {}
    for message in st.session_state.chat_history:
        if message.get("role") == "assistant":
            knowledge_level = message.get("knowledge_level", 0)
            knowledge_data[knowledge_level] = knowledge_data.get(knowledge_level, 0) + 1

    if not knowledge_data:
        st.warning("지식 레벨 데이터가 없습니다.")
        return

    fig = go.Figure(data=[
        go.Bar(
            x=list(knowledge_data.keys()),
            y=list(knowledge_data.values()),
            marker_color='#1f77b4'
        )
    ])
    fig.update_layout(
        title="지식 레벨 분포",
        xaxis_title="지식 레벨",
        yaxis_title="빈도",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_temperature_distribution():
    """사용자 온도 분포 그래프"""
    # 더미 데이터 대신 실제 채팅 히스토리에서 사용자 온도 데이터를 집계
    temperature_data = {}
    for message in st.session_state.chat_history:
        if message.get("role") == "assistant":
            temperature = message.get("temperature", 0)
            temperature_data[temperature] = temperature_data.get(temperature, 0) + 1

    if not temperature_data:
        st.warning("사용자 온도 데이터가 없습니다.")
        return

    fig = go.Figure(data=[
        go.Bar(
            x=list(temperature_data.keys()),
            y=list(temperature_data.values()),
            marker_color='#ff7f0e'
        )
    ])
    fig.update_layout(
        title="사용자 온도 분포",
        xaxis_title="온도",
        yaxis_title="빈도",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_response_quality():
    """응답 품질 그래프"""
    # 더미 데이터 대신 실제 채팅 히스토리에서 응답 품질 데이터를 집계
    quality_data = {}
    for message in st.session_state.chat_history:
        if message.get("role") == "assistant":
            quality = message.get("quality", 0)
            quality_data[quality] = quality_data.get(quality, 0) + 1

    if not quality_data:
        st.warning("응답 품질 데이터가 없습니다.")
        return

    fig = go.Figure(data=[
        go.Bar(
            x=list(quality_data.keys()),
            y=list(quality_data.values()),
            marker_color='#2ca02c'
        )
    ])
    fig.update_layout(
        title="응답 품질 분포",
        xaxis_title="품질",
        yaxis_title="빈도",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True) 