"""
Chart components using Plotly
"""
import plotly.graph_objects as go
import pandas as pd
from frontend.utils.config import COLORS, CHART_CONFIG


def create_risk_donut_chart(risk_df):
    """Create donut chart for risk distribution"""
    fig = go.Figure(data=[go.Pie(
        labels=risk_df['Level'],
        values=risk_df['Pixels'],
        hole=0.4,
        marker=dict(colors=risk_df['Color']),
        textinfo='label+percent',
        textfont=dict(size=14, color='white', family='Inter'),
        hovertemplate='<b>%{label}</b><br>Pixels: %{value:,}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        showlegend=False,
        height=300,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


def create_distribution_bar_chart(data, title, ylabel):
    """Create bar chart for statistical distribution"""
    fig = go.Figure(data=[
        go.Bar(
            x=data['Percentile'],
            y=data['Value'],
            marker_color=[COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['success']],
            text=[f"{v:.3f}" for v in data['Value']],
            textposition='outside',
            textfont=dict(size=12, family='Inter')
        )
    ])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, family='Inter', color=COLORS['dark'])),
        xaxis_title='',
        yaxis_title=ylabel,
        height=350,
        margin=dict(t=50, b=50, l=50, r=50),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', color=COLORS['text'])
    )
    
    return fig


def create_radar_chart(categories, values_mean, values_p90):
    """Create radar chart for index comparison"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values_mean,
        theta=categories,
        fill='toself',
        name='Mean',
        line=dict(color=COLORS['primary'], width=2),
        fillcolor=f"rgba(0, 102, 204, 0.2)"
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=values_p90,
        theta=categories,
        fill='toself',
        name='P90',
        line=dict(color=COLORS['accent'], width=2),
        fillcolor=f"rgba(255, 107, 53, 0.2)"
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                gridcolor=COLORS['light']
            ),
            angularaxis=dict(gridcolor=COLORS['light'])
        ),
        showlegend=True,
        height=400,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Inter', color=COLORS['text'])
    )
    
    return fig


def create_time_series_chart(df, lat, lon):
    """Create multi-line time series chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['ndci'],
        mode='lines+markers',
        name='NDCI',
        line=dict(color=COLORS['primary'], width=2),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['ndwi'],
        mode='lines+markers',
        name='NDWI',
        line=dict(color=COLORS['secondary'], width=2),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Date'], y=df['turbidity'],
        mode='lines+markers',
        name='Turbidity',
        line=dict(color=COLORS['accent'], width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=dict(
            text=f'Water Quality Trends at ({lat:.4f}, {lon:.4f})', 
            font=dict(size=18, family='Inter', color=COLORS['dark'])
        ),
        xaxis_title='Date',
        yaxis_title='Index Value',
        hovermode='x unified',
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', color=COLORS['text']),
        xaxis=dict(gridcolor=COLORS['light']),
        yaxis=dict(gridcolor=COLORS['light'])
    )
    
    return fig


def create_single_metric_chart(df, metric_name, color):
    """Create single metric time series with fill"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df[metric_name],
        mode='lines+markers',
        name=metric_name,
        line=dict(color=color, width=3),
        marker=dict(size=8, symbol='circle'),
        fill='tonexty',
        fillcolor=f"rgba{tuple(list(int(color[i:i+2], 16) for i in (1, 3, 5)) + [0.2])}"
    ))
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title=metric_name,
        hovermode='x',
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', color=COLORS['text']),
        xaxis=dict(gridcolor=COLORS['light']),
        yaxis=dict(gridcolor=COLORS['light'])
    )
    
    return fig
