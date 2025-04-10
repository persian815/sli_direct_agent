import plotly.graph_objects as go
from typing import List, Dict

def create_knowledge_distribution_graph(knowledge_levels: List[int]) -> go.Figure:
    """
    Create a bar graph showing the distribution of knowledge levels.
    
    Args:
        knowledge_levels: List of knowledge level scores (1-100)
        
    Returns:
        plotly.graph_objects.Figure: The generated bar graph
    """
    # Group knowledge levels into ranges (1-10, 11-20, ..., 91-100)
    level_ranges = {}
    for i in range(1, 101, 10):
        range_key = f"{i}-{i+9}"
        level_ranges[range_key] = sum(1 for level in knowledge_levels if i <= level < i+10)
    
    # Create bar graph
    fig = go.Figure(data=[
        go.Bar(
            x=list(level_ranges.keys()),
            y=list(level_ranges.values()),
            marker_color='#4CAF50',
            opacity=0.7
        )
    ])
    
    # Update layout
    fig.update_layout(
        title="Knowledge Level Distribution",
        xaxis_title="Knowledge Level Range",
        yaxis_title="Count",
        template="plotly_dark",
        paper_bgcolor="#1E1E1E",
        plot_bgcolor="#1E1E1E",
        font=dict(color="#FFFFFF"),
        margin=dict(t=30, l=40, r=20, b=40),
        height=300
    )
    
    # Update axes
    fig.update_xaxes(
        gridcolor="#2D2D2D",
        zerolinecolor="#2D2D2D"
    )
    fig.update_yaxes(
        gridcolor="#2D2D2D",
        zerolinecolor="#2D2D2D"
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

def format_metrics_html(request_time: float, response_time: float, 
                       input_tokens: int, output_tokens: int) -> str:
    """
    Format metrics information as HTML.
    
    Args:
        request_time: Time taken for the request (seconds)
        response_time: Time taken for the response (seconds)
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        str: Formatted HTML string
    """
    return f"""
        <div class="metrics">
            Request Time: {request_time:.2f}s | Response Time: {response_time:.2f}s | 
            Input Tokens: {input_tokens} | Output Tokens: {output_tokens}
        </div>
    """ 