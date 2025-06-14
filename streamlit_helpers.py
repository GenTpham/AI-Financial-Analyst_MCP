"""
Helper functions cho Streamlit AI Financial Analyst App
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO
from datetime import datetime, timedelta

def set_page_style():
    """Thiết lập custom CSS cho Streamlit app"""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header gradient */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-weight: 700;
        font-size: 2.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    .metric-card h4 {
        color: #2c3e50;
        margin: 0 0 0.5rem 0;
        font-weight: 600;
    }
    
    .metric-card h2 {
        color: #667eea;
        margin: 0;
        font-weight: 700;
        font-size: 2rem;
    }
    
    /* Risk cards */
    .risk-card {
        background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #e53e3e;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(229, 62, 62, 0.1);
    }
    
    .success-card {
        background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #38a169;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(56, 161, 105, 0.1);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fffbf0 0%, #feebc8 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #d69e2e;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(214, 158, 46, 0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8fafc;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        background-color: #f1f5f9;
        border-radius: 8px;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Progress bar */
    .stProgress .st-bo {
        background-color: #667eea;
    }
    </style>
    """, unsafe_allow_html=True)

def display_welcome_screen():
    """Hiển thị màn hình chào mừng"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2 style="color: #667eea; margin-bottom: 1rem;">🎯 Chào mừng đến với AI Financial Analyst</h2>
            <p style="font-size: 1.1rem; color: #64748b; margin-bottom: 2rem;">
                Hệ thống phân tích tài chính thông minh sử dụng AI và Machine Learning
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="success-card">
            <h3>📊 Phân tích kỹ thuật</h3>
            <ul>
                <li>RSI, MACD, Bollinger Bands</li>
                <li>Moving Averages (20, 50, 200)</li>
                <li>Stochastic Oscillator</li>
                <li>Volume Analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-card">
            <h3>⚠️ Phân tích rủi ro</h3>
            <ul>
                <li>Volatility Analysis</li>
                <li>Sharpe Ratio</li>
                <li>Maximum Drawdown</li>
                <li>Value at Risk (VaR)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🤖 AI Analysis</h3>
            <ul>
                <li>Deepseek AI Integration</li>
                <li>Smart Recommendations</li>
                <li>Market Sentiment Analysis</li>
                <li>Automated Insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="risk-card">
            <h3>📈 Visualization</h3>
            <ul>
                <li>Interactive Plotly Charts</li>
                <li>Multi-panel Dashboard</li>
                <li>Real-time Data Updates</li>
                <li>Professional Reports</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Instructions
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
                padding: 2rem; border-radius: 12px; margin: 2rem 0; 
                border-left: 5px solid #0ea5e9;">
        <h3 style="color: #0c4a6e; margin-top: 0;">🚀 Cách sử dụng:</h3>
        <ol style="color: #0c4a6e;">
            <li><b>Nhập mã cổ phiếu</b> vào sidebar (VD: AAPL,GOOGL,MSFT)</li>
            <li><b>Chọn thời gian</b> phân tích (3mo, 6mo, 1y, 2y, 5y)</li>
            <li><b>Bật/tắt</b> các tính năng phân tích</li>
            <li><b>Nhấn</b> "🚀 Bắt đầu phân tích"</li>
        </ol>
        <p style="color: #0c4a6e; margin-bottom: 0;">
            <b>👈 Bắt đầu bằng cách nhập mã cổ phiếu trong sidebar!</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, change=None, change_color="normal", description=None):
    """Tạo metric card với styling đẹp"""
    if change is not None:
        change_color_style = "#28a745" if change_color == "normal" and change >= 0 else "#dc3545"
        change_arrow = "▲" if change >= 0 else "▼"
        change_text = f'<p style="color: {change_color_style}; margin: 0.5rem 0 0 0; font-weight: 500;">{change_arrow} {change:+.2f}%</p>'
    else:
        change_text = ""
    
    desc_text = f'<p style="color: #64748b; margin: 0.5rem 0 0 0; font-size: 0.9rem;">{description}</p>' if description else ""
    
    return f"""
    <div class="metric-card">
        <h4>{title}</h4>
        <h2>{value}</h2>
        {change_text}
        {desc_text}
    </div>
    """

def create_status_card(title, status, status_type="info"):
    """Tạo status card với màu sắc tương ứng"""
    card_class = {
        "success": "success-card",
        "warning": "warning-card", 
        "danger": "risk-card",
        "info": "metric-card"
    }.get(status_type, "metric-card")
    
    return f"""
    <div class="{card_class}">
        <h4>{title}</h4>
        <p style="margin: 0; font-weight: 500;">{status}</p>
    </div>
    """

def format_currency(value, currency="$"):
    """Format currency với proper formatting"""
    if abs(value) >= 1e12:
        return f"{currency}{value/1e12:.2f}T"
    elif abs(value) >= 1e9:
        return f"{currency}{value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"{currency}{value/1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"{currency}{value/1e3:.2f}K"
    else:
        return f"{currency}{value:.2f}"

def create_technical_indicator_chart(data, symbol):
    """Tạo biểu đồ technical indicators compact"""
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=['Price & Volume', 'RSI', 'MACD', 'Bollinger Bands', 'Moving Averages', 'Stochastic'],
        vertical_spacing=0.08,
        horizontal_spacing=0.1
    )
    
    # Price & Volume
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'], 
        low=data['Low'],
        close=data['Close'],
        name='Price'
    ), row=1, col=1)
    
    # Volume
    fig.add_trace(go.Bar(
        x=data.index,
        y=data['Volume'],
        name='Volume',
        opacity=0.6
    ), row=1, col=2)
    
    fig.update_layout(
        height=800,
        showlegend=False,
        title=f"{symbol} - Technical Analysis Dashboard"
    )
    
    return fig

def get_recommendation_color(recommendation):
    """Lấy màu sắc cho recommendation"""
    rec_lower = recommendation.lower()
    if "buy" in rec_lower or "mua" in rec_lower:
        return "#28a745"
    elif "sell" in rec_lower or "bán" in rec_lower:
        return "#dc3545"  
    else:
        return "#ffc107"

def display_ai_insights(ai_data):
    """Hiển thị AI insights với formatting đẹp"""
    if not ai_data:
        st.info("🤖 AI insights không khả dụng. Kiểm tra cấu hình API hoặc balance.")
        return
    
    # Market sentiment
    sentiment = ai_data.get('market_sentiment', 'Neutral')
    sentiment_color = get_recommendation_color(sentiment)
    
    st.markdown(f"""
    <div class="metric-card">
        <h3>🧠 AI Market Sentiment</h3>
        <h2 style="color: {sentiment_color}">{sentiment}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Key insights
    insights = ai_data.get('key_insights', [])
    if insights:
        st.markdown("### 💡 Key Insights")
        for i, insight in enumerate(insights, 1):
            st.markdown(f"""
            <div class="success-card">
                <p><b>{i}.</b> {insight}</p>
            </div>
            """, unsafe_allow_html=True)

def create_performance_summary(data_dict):
    """Tạo bảng tóm tắt performance"""
    summary_data = []
    
    for symbol, result in data_dict.items():
        data = result['data']
        analysis = result['analysis']
        
        # Calculate metrics
        current_price = data['Close'].iloc[-1]
        price_change = ((current_price / data['Close'].iloc[-2]) - 1) * 100
        
        risk_data = analysis.get('risk_analysis', {})
        volatility = risk_data.get('volatility', 0) * 100
        sharpe = risk_data.get('sharpe_ratio', 0)
        
        technical = analysis.get('technical_analysis', {})
        rsi = technical.get('rsi', {}).get('current', 0)
        
        summary_data.append({
            'Symbol': symbol,
            'Price': f"${current_price:.2f}",
            'Change %': f"{price_change:+.2f}%",
            'Volatility %': f"{volatility:.2f}%",
            'Sharpe Ratio': f"{sharpe:.2f}",
            'RSI': f"{rsi:.1f}"
        })
    
    df = pd.DataFrame(summary_data)
    return df

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_market_data(symbols, period):
    """Cache market data để improve performance"""
    # This would be implemented with actual data loading
    pass

def show_loading_animation():
    """Hiển thị loading animation đẹp"""
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; padding: 2rem;">
        <div style="text-align: center;">
            <div style="display: inline-block; width: 40px; height: 40px; border: 4px solid #f3f3f3; 
                        border-top: 4px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite;">
            </div>
            <p style="margin-top: 1rem; color: #667eea; font-weight: 500;">Đang phân tích dữ liệu...</p>
        </div>
    </div>
    
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

def export_to_pdf(html_content, filename):
    """Export analysis to PDF"""
    # This would implement PDF export functionality
    # For now, return download link for HTML
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}.html">📥 Download Report</a>'
    return href 