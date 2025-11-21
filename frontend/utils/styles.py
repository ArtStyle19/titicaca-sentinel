"""
CSS Styles for the Streamlit frontend
Centralized styling configuration
"""
from frontend.utils.config import COLORS


def get_custom_css() -> str:
    """Generate custom CSS styles for the application"""
    return f"""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    .main {{
        background-color: {COLORS['background']};
    }}
    
    /* Header Styles */
    .header-container {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    
    .main-title {{
        font-size: 2.8rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin: 0;
        letter-spacing: -0.5px;
    }}
    
    .subtitle {{
        font-size: 1.1rem;
        font-weight: 400;
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        margin-top: 0.5rem;
    }}
    
    /* Card Styles */
    .metric-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid {COLORS['primary']};
        margin-bottom: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }}
    
    .metric-label {{
        font-size: 0.875rem;
        font-weight: 600;
        color: {COLORS['text']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['primary']};
        line-height: 1.2;
    }}
    
    /* Info Cards */
    .info-card {{
        background: white;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid {COLORS['light']};
        margin-bottom: 1rem;
    }}
    
    .info-card-content {{
        font-size: 0.9rem;
        color: {COLORS['text']};
        line-height: 1.6;
    }}
    
    /* Risk Badges */
    .risk-badge {{
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .risk-low {{
        background-color: rgba(46, 204, 113, 0.15);
        color: {COLORS['risk_low']};
    }}
    
    .risk-medium {{
        background-color: rgba(243, 156, 18, 0.15);
        color: {COLORS['risk_medium']};
    }}
    
    .risk-high {{
        background-color: rgba(231, 76, 60, 0.15);
        color: {COLORS['risk_high']};
    }}
    
    /* Alerts */
    .alert {{
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        line-height: 1.6;
    }}
    
    .alert-info {{
        background-color: rgba(0, 163, 224, 0.1);
        border-left: 4px solid {COLORS['secondary']};
        color: {COLORS['text']};
    }}
    
    .alert-success {{
        background-color: rgba(46, 204, 113, 0.1);
        border-left: 4px solid {COLORS['success']};
        color: {COLORS['text']};
    }}
    
    .alert-warning {{
        background-color: rgba(243, 156, 18, 0.1);
        border-left: 4px solid {COLORS['warning']};
        color: {COLORS['text']};
    }}
    
    /* Sidebar Styles */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['dark']};
    }}
    
    section[data-testid="stSidebar"] > div {{
        background-color: {COLORS['dark']};
    }}
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {{
        color: white !important;
    }}
    
    /* Button Styles */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.3px;
        transition: all 0.3s;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
    }}
    
    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: white;
        padding: 0.5rem;
        border-radius: 12px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        border-radius: 8px;
        padding: 0 24px;
        background-color: transparent;
        font-weight: 500;
        color: {COLORS['text']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
    }}
    
    /* Legend Styles */
    .legend-container {{
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-top: 1rem;
    }}
    
    .legend-title {{
        font-size: 0.95rem;
        font-weight: 600;
        color: {COLORS['dark']};
        margin-bottom: 0.75rem;
    }}
    
    .legend-item {{
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }}
    
    .legend-color {{
        width: 20px;
        height: 20px;
        border-radius: 4px;
        margin-right: 0.75rem;
    }}
    
    /* Statistics Table */
    .stats-table {{
        width: 100%;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }}
    
    .stats-table th {{
        background-color: {COLORS['primary']};
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
    }}
    
    .stats-table td {{
        padding: 0.875rem 1rem;
        border-bottom: 1px solid {COLORS['light']};
        font-size: 0.9rem;
        color: {COLORS['text']};
    }}
    
    .stats-table tr:hover {{
        background-color: {COLORS['background']};
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {COLORS['light']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {COLORS['primary']};
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['secondary']};
    }}
</style>
"""
