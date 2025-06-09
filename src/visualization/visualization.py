import plotly.graph_objs as go

def create_knowledge_distribution_graph(knowledge_levels):
    """
    지식 레벨 분포 그래프를 생성합니다.
    knowledge_levels: [초급, 중급, 고급] 리스트
    """
    labels = ['초급', '중급', '고급']
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=knowledge_levels,
        marker_color=['#6fa8dc', '#f6b26b', '#e06666']
    )])
    fig.update_layout(
        title='지식 레벨 분포',
        xaxis_title='레벨',
        yaxis_title='인원수',
        template='simple_white'
    )
    return fig

def create_temperature_distribution_graph(temperature_data):
    """
    사용자 온도 분포 그래프를 생성합니다.
    temperature_data: 온도 값 리스트
    """
    fig = go.Figure(data=[go.Histogram(
        x=temperature_data,
        nbinsx=10,
        marker_color='#93c47d'
    )])
    fig.update_layout(
        title='사용자 온도 분포',
        xaxis_title='온도(℃)',
        yaxis_title='빈도',
        template='simple_white'
    )
    return fig

def format_knowledge_level_html(level: int, color: str) -> str:
    """
    Format knowledge level information as HTML.
    Args:
        level: Knowledge level score (1-100)
        color: CSS color code for the level
    Returns:
        str: Formatted HTML string
    """
    return f"""
        <div class="knowledge-level">
            <div>Knowledge Level</div>
            <div class="knowledge-level-bar" style="width: {level}%; background-color: {color};"></div>
            <div class="knowledge-level-text">{level}/100</div>
        </div>
    """

def format_metrics_html(response_time: float, input_tokens: int, output_tokens: int) -> str:
    """
    Format metrics information as HTML.
    Args:
        response_time: Time taken for the response (seconds)
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
    Returns:
        str: Formatted HTML string
    """
    return f"""
        <div class="metrics">
            Response Time: {response_time:.2f}s | 
            Input Tokens: {input_tokens} | Output Tokens: {output_tokens}
        </div>
    """ 