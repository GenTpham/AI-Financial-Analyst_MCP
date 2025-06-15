import streamlit as st

# Set page config FIRST - before any other Streamlit commands
st.set_page_config(
    page_title="AI Financial Analyst",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

import asyncio
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import base64
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/api_keys.env')

# Add current directory to Python path
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our existing agents
try:
    from src.agents.data_retrieval_agent import DataRetrievalAgent
    from src.agents.data_analysis_agent import DataAnalysisAgent
    from src.agents.visualization_agent import VisualizationAgent
    from src.agents.report_generation_agent import ReportGenerationAgent
    from config_manager import ConfigManager
    
    # Import helpers
    from streamlit_helpers import (
        set_page_style, display_welcome_screen, create_metric_card,
        create_status_card, format_currency, get_recommendation_color,
        display_ai_insights, create_performance_summary
    )
    AGENTS_AVAILABLE = True
except ImportError as e:
    st.error(f"❌ Lỗi import modules: {e}")
    st.info("💡 Hãy đảm bảo bạn đang chạy từ thư mục gốc của project")
    AGENTS_AVAILABLE = False

# Apply custom styling
if AGENTS_AVAILABLE:
    set_page_style()
else:
    # Basic styling fallback
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 AI Financial Analyst</h1>
    <p>Phân tích tài chính thông minh với AI và Machine Learning</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None

# Helper functions
def show_loading_animation():
    """Show loading animation"""
    import time
    with st.spinner("Đang tải..."):
        time.sleep(1)

def get_rsi_signal(rsi):
    """Get RSI signal interpretation"""
    if rsi > 70:
        return {"color": "#dc3545", "text": "Overbought - Có thể bán"}
    elif rsi < 30:
        return {"color": "#28a745", "text": "Oversold - Có thể mua"}
    else:
        return {"color": "#ffc107", "text": "Trung tính"}

def get_macd_signal(macd_data):
    """Get MACD signal interpretation"""
    macd = macd_data.get('macd', 0)
    signal = macd_data.get('signal', 0)
    
    # Handle case where values might be lists
    if isinstance(macd, list):
        macd = macd[-1] if macd else 0
    if isinstance(signal, list):
        signal = signal[-1] if signal else 0
    
    if macd > signal:
        return {"color": "#28a745", "text": "Bullish Signal"}
    else:
        return {"color": "#dc3545", "text": "Bearish Signal"}

def get_volatility_level(vol):
    """Get volatility level interpretation"""
    if vol > 30:
        return {"color": "#dc3545", "text": "Rủi ro cao"}
    elif vol > 20:
        return {"color": "#ffc107", "text": "Rủi ro trung bình"}
    else:
        return {"color": "#28a745", "text": "Rủi ro thấp"}

def get_sharpe_level(sharpe):
    """Get Sharpe ratio level interpretation"""
    if sharpe > 1.5:
        return {"color": "#28a745", "text": "Rất tốt"}
    elif sharpe > 1:
        return {"color": "#28a745", "text": "Tốt"}
    elif sharpe > 0.5:
        return {"color": "#ffc107", "text": "Chấp nhận được"}
    else:
        return {"color": "#dc3545", "text": "Kém"}

def get_drawdown_level(drawdown):
    """Get drawdown level interpretation"""
    if abs(drawdown) > 20:
        return {"color": "#dc3545", "text": "Rủi ro rất cao"}
    elif abs(drawdown) > 10:
        return {"color": "#ffc107", "text": "Rủi ro cao"}
    else:
        return {"color": "#28a745", "text": "Chấp nhận được"}

def create_basic_chart(data, symbol):
    """Create modern, beautiful chart with professional styling"""
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    

    
    # Modern color scheme
    colors = {
        'background': '#0E1117',
        'paper': '#1E2329', 
        'text': '#FAFAFA',
        'grid': '#2B2F36',
        'green': '#00D4AA',
        'red': '#F23645',
        'blue': '#1f77b4',
        'volume': '#4A90E2',
        'annotation': '#262730'
    }
    
    fig = make_subplots(
        rows=2, cols=1, 
        subplot_titles=[f'📈 {symbol} Stock Price', '📊 Trading Volume'],
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],  # Give more space to volume
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    # Price chart with modern candlestick styling and detailed tooltips
    # Create hover text for each candlestick - Use direct index access
    hover_texts = []
    
    # Debug: Check data index type
    print(f"Chart data index type: {type(data.index)}")
    print(f"Chart data index sample: {data.index[:3] if len(data) > 0 else 'Empty'}")
    
    for i in range(len(data)):
        try:
            # Get actual timestamp from index
            timestamp = data.index[i]
            row = data.iloc[i]
            
            # Format timestamp properly with better handling
            if isinstance(data.index, pd.DatetimeIndex):
                # This is a proper DatetimeIndex
                month = timestamp.month
                day = timestamp.day
                time_12hr = timestamp.strftime("%I:%M %p").lstrip('0')
                date_str = f"{month}/{day} {time_12hr}"
            elif hasattr(timestamp, 'strftime') and hasattr(timestamp, 'month'):
                # This is a datetime object
                month = timestamp.month
                day = timestamp.day
                time_12hr = timestamp.strftime("%I:%M %p").lstrip('0')
                date_str = f"{month}/{day} {time_12hr}"
            else:
                # Fallback: try to convert or use position
                try:
                    # Try to convert to datetime
                    dt = pd.to_datetime(timestamp)
                    month = dt.month
                    day = dt.day
                    time_12hr = dt.strftime("%I:%M %p").lstrip('0')
                    date_str = f"{month}/{day} {time_12hr}"
                except:
                    # Last resort: use data point number
                    date_str = f"Data Point {i+1}"
            
            # Calculate metrics
            change = row['Close'] - row['Open']
            change_pct = (change / row['Open'] * 100) if row['Open'] != 0 else 0
            range_val = row['High'] - row['Low']
            
            hover_text = (f"{symbol} Stock<br>"
                         f"Date: {date_str}<br>"
                         f"Open: ${row['Open']:.2f}<br>"
                         f"High: ${row['High']:.2f}<br>"
                         f"Low: ${row['Low']:.2f}<br>"
                         f"Close: ${row['Close']:.2f}<br>"
                         f"Change: ${change:.2f} ({change_pct:+.2f}%)<br>"
                         f"Range: ${range_val:.2f}")
            hover_texts.append(hover_text)
        except Exception as e:
            hover_texts.append(f"{symbol} - Data point {i}")
    
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=symbol,
        increasing=dict(
            line=dict(color=colors['green'], width=2),  # Increased width
            fillcolor=colors['green']
        ),
        decreasing=dict(
            line=dict(color=colors['red'], width=2),  # Increased width
            fillcolor=colors['red']
        ),
        hovertext=hover_texts,
        hoverinfo='text'
    ), row=1, col=1)
    
    # Volume chart with gradient effect - Fix volume display
    # Check if volume data exists and is not all zeros
    if 'Volume' in data.columns and data['Volume'].sum() > 0:
        volume_colors = ['rgba(74, 144, 226, 0.7)' if close >= open else 'rgba(242, 54, 69, 0.7)' 
                         for close, open in zip(data['Close'], data['Open'])]
        
        # Create volume hover data
        volume_avg = data['Volume'].mean()
        volume_customdata = []
        volume_text = []
        
        for close, open_price, volume in zip(data['Close'], data['Open'], data['Volume']):
            vs_avg = ((volume / volume_avg - 1) * 100) if volume_avg != 0 else 0
            turnover = volume * close
            volume_customdata.append([close, vs_avg, turnover])
            volume_text.append('Bullish' if close >= open_price else 'Bearish')
        
        # Create volume hover texts manually - Use direct index access
        volume_hover_texts = []
        for i in range(len(data)):
            try:
                # Get actual timestamp from index
                timestamp = data.index[i]
                row = data.iloc[i]
                
                # Format timestamp properly with better handling
                if isinstance(data.index, pd.DatetimeIndex):
                    # This is a proper DatetimeIndex
                    month = timestamp.month
                    day = timestamp.day
                    time_12hr = timestamp.strftime("%I:%M %p").lstrip('0')
                    date_str = f"{month}/{day} {time_12hr}"
                elif hasattr(timestamp, 'strftime') and hasattr(timestamp, 'month'):
                    # This is a datetime object
                    month = timestamp.month
                    day = timestamp.day
                    time_12hr = timestamp.strftime("%I:%M %p").lstrip('0')
                    date_str = f"{month}/{day} {time_12hr}"
                else:
                    # Fallback: try to convert or use position
                    try:
                        # Try to convert to datetime
                        dt = pd.to_datetime(timestamp)
                        month = dt.month
                        day = dt.day
                        time_12hr = dt.strftime("%I:%M %p").lstrip('0')
                        date_str = f"{month}/{day} {time_12hr}"
                    except:
                        # Last resort: use data point number
                        date_str = f"Data Point {i+1}"
                
                volume = row['Volume']
                close_price = row['Close']
                open_price = row['Open']
                vs_avg = ((volume / volume_avg - 1) * 100) if volume_avg != 0 else 0
                turnover = volume * close_price
                trend = 'Bullish' if close_price >= open_price else 'Bearish'
                
                hover_text = (f"Trading Volume<br>"
                             f"Date: {date_str}<br>"
                             f"Volume: {volume:,.0f} shares<br>"
                             f"Close Price: ${close_price:.2f}<br>"
                             f"Trend: {trend}<br>"
                             f"vs Avg: {vs_avg:+.1f}%<br>"
                             f"Turnover: ${turnover:,.0f}")
                volume_hover_texts.append(hover_text)
            except Exception as e:
                volume_hover_texts.append(f"Volume data point {i}")
        
        fig.add_trace(go.Bar(
            x=data.index, 
            y=data['Volume'], 
            name='Volume',
            marker=dict(
                color=volume_colors,
                line=dict(width=0)
            ),
            hovertext=volume_hover_texts,
            hoverinfo='text'
        ), row=2, col=1)
    else:
        # If no volume data, show placeholder
        fig.add_trace(go.Scatter(
            x=data.index,
            y=[0] * len(data.index),
            mode='lines',
            name='No Volume Data',
            line=dict(color='gray', dash='dash'),
            hovertext='No volume data available',
            hoverinfo='text'
        ), row=2, col=1)
    
    # Add timestamp information to title
    latest_timestamp = data.index[-1]
    earliest_timestamp = data.index[0]
    
    # Safe timestamp formatting for title
    try:
        if hasattr(earliest_timestamp, 'strftime'):
            start_str = earliest_timestamp.strftime('%m/%d')
        else:
            start_str = str(earliest_timestamp)[:5]
        
        if hasattr(latest_timestamp, 'strftime'):
            month = latest_timestamp.month
            day = latest_timestamp.day
            time_12hr = latest_timestamp.strftime("%I:%M %p").lstrip('0')
            end_str = f"{month}/{day} {time_12hr}"
        else:
            end_str = str(latest_timestamp)[:16]
        
        title_text = f"{symbol} Trading Analysis | {start_str} - {end_str}"
    except:
        title_text = f"{symbol} Trading Analysis"
    
    # Modern layout with dark theme
    fig.update_layout(
        height=600,
        title=dict(
            text=title_text,
            x=0.5,
            font=dict(size=20, color=colors['text'], family="Arial Black")
        ),
        showlegend=False,
        hovermode='closest',
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['paper'],
        font=dict(color=colors['text'], family="Arial"),
        margin=dict(l=60, r=60, t=80, b=60),
        
        # X-axis styling
        xaxis=dict(
            gridcolor=colors['grid'],
            gridwidth=0.5,
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=12, color=colors['text']),  # Increased font size
            title=dict(text="Time", font=dict(size=14, color=colors['text']))
        ),
        xaxis2=dict(
            gridcolor=colors['grid'],
            gridwidth=0.5,
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=12, color=colors['text'])  # Increased font size
        ),
        
        # Y-axis styling
        yaxis=dict(
            gridcolor=colors['grid'],
            gridwidth=0.5,
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=12, color=colors['text']),  # Increased font size
            title=dict(text="Price ($)", font=dict(size=14, color=colors['text'])),
            tickformat='$.2f'
        ),
        yaxis2=dict(
            gridcolor=colors['grid'],
            gridwidth=0.5,
            showgrid=True,
            zeroline=False,
            tickfont=dict(size=12, color=colors['text']),  # Increased font size
            title=dict(text="Volume", font=dict(size=14, color=colors['text'])),
            tickformat='.2s'
        )
    )
    
    # Remove range slider for cleaner look
    fig.update_xaxes(rangeslider_visible=False)
    
    # Add data freshness annotation with modern styling
    try:
        # Handle timezone-aware timestamps
        if hasattr(latest_timestamp, 'tz') and latest_timestamp.tz is not None:
            latest_naive = latest_timestamp.tz_convert('UTC').tz_localize(None)
            now_naive = pd.Timestamp.now(tz='UTC').tz_localize(None)
        else:
            latest_naive = latest_timestamp
            now_naive = pd.Timestamp.now()
        
        data_age = now_naive - latest_naive
        total_seconds = data_age.total_seconds()
    except:
        # Fallback calculation
        import datetime
        now_dt = datetime.datetime.now()
        if hasattr(latest_timestamp, 'to_pydatetime'):
            latest_dt = latest_timestamp.to_pydatetime().replace(tzinfo=None)
        else:
            latest_dt = pd.to_datetime(latest_timestamp).replace(tzinfo=None)
        data_age = now_dt - latest_dt
        total_seconds = data_age.seconds + data_age.days * 86400

    freshness_text = "Live" if total_seconds < 3600 else "Recent" if total_seconds < 86400 else "Delayed"
    
    # Safe annotation formatting (American style)
    try:
        if hasattr(latest_timestamp, 'strftime'):
            # Windows-compatible format for M/D H:MM AM/PM
            month = latest_timestamp.month
            day = latest_timestamp.day
            time_12hr = latest_timestamp.strftime("%I:%M %p").lstrip('0')
            date_str = f"{month}/{day} {time_12hr}"
        else:
            date_str = str(latest_timestamp)[:16]
        
        annotation_text = f"{freshness_text} | Last Update: {date_str}"
    except:
        annotation_text = f"{freshness_text} | Market Data"
    
    # Modern annotation with glassmorphism effect
    fig.add_annotation(
        text=annotation_text,
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        showarrow=False,
        font=dict(size=11, color=colors['text'], family="Arial"),
        bgcolor="rgba(38, 39, 48, 0.8)",
        bordercolor="rgba(255, 255, 255, 0.1)",
        borderwidth=1,
        borderpad=8,
        opacity=0.9
    )
    
    # Add market status indicator
    import datetime
    now = datetime.datetime.now()
    market_status = "Market Open" if 9 <= now.hour < 16 and now.weekday() < 5 else "Market Closed"
    
    fig.add_annotation(
        text=market_status,
        xref="paper", yref="paper",
        x=0.98, y=0.98,
        showarrow=False,
        font=dict(size=11, color=colors['text'], family="Arial"),
        bgcolor="rgba(38, 39, 48, 0.8)",
        bordercolor="rgba(255, 255, 255, 0.1)",
        borderwidth=1,
        borderpad=8,
        opacity=0.9
    )
    
    # Add subtle animations
    fig.update_traces(
        selector=dict(type='candlestick'),
        line=dict(width=1.2)
    )
    
    return fig

def run_async_safely(coro):
    """Safely run async function in Streamlit"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, use asyncio.create_task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return asyncio.run(coro)
    except RuntimeError:
        # Fallback: create new event loop
        return asyncio.run(coro)

def run_analysis(symbols, period, enable_ai, enable_technical, enable_risk):
    """Run comprehensive financial analysis"""
    if not AGENTS_AVAILABLE:
        st.error("❌ Không thể chạy phân tích - Agents không khả dụng")
        return {}
    
    try:
        # Create config dictionaries for agents
        config = {
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY'),
            'deepseek_base_url': os.getenv('DEEPSEEK_BASE_URL'),
            'default_period': '6mo',
            'reports_directory': './output/reports',
            'charts_directory': './output/charts'
        }
        
        data_sources_config = {
            'yahoo_finance': {'enabled': True},
            'alpha_vantage': {'enabled': True},
            'csv_data': {'data_directory': './data/csv'}
        }
        
        # Initialize agents
        data_agent = DataRetrievalAgent(config, data_sources_config)
        analysis_agent = DataAnalysisAgent(config, data_sources_config)
        viz_agent = VisualizationAgent(config, data_sources_config)
        report_agent = ReportGenerationAgent(config, data_sources_config)
        
        results = {}
        
        for symbol in symbols:
            try:
                # Get data
                data_result = run_async_safely(data_agent.fetch_stock_data(symbol, period))
                if not data_result or 'data' not in data_result:
                    st.warning(f"Không thể lấy dữ liệu cho {symbol}")
                    continue
                
                # Extract historical data as DataFrame
                historical_data = data_result['data']['historical']
                if not historical_data:
                    st.warning(f"Không có dữ liệu lịch sử cho {symbol}")
                    continue
                
                # Convert to DataFrame and ensure proper datetime index
                import pandas as pd
                data_df = pd.DataFrame(historical_data)
                
                # Debug: print data structure
                print(f"Debug data_df columns: {data_df.columns.tolist()}")
                print(f"Debug data_df index: {data_df.index}")
                print(f"Debug data_df index type: {type(data_df.index)}")
                
                # Ensure proper datetime index
                if 'Date' in data_df.columns:
                    # Convert Date column to datetime and set as index
                    data_df['Date'] = pd.to_datetime(data_df['Date'])
                    data_df.set_index('Date', inplace=True)
                elif 'date' in data_df.columns:
                    # Handle lowercase date column
                    data_df['date'] = pd.to_datetime(data_df['date'])
                    data_df.set_index('date', inplace=True)
                    data_df.index.name = 'Date'
                elif not isinstance(data_df.index, pd.DatetimeIndex):
                    # If no date column found, try to create from index
                    if len(data_df) > 0:
                        # Create a date range for the data
                        end_date = pd.Timestamp.now()
                        start_date = end_date - pd.Timedelta(days=len(data_df))
                        date_range = pd.date_range(start=start_date, periods=len(data_df), freq='D')
                        data_df.index = date_range
                        data_df.index.name = 'Date'
                
                # Final check
                print(f"Debug final index type: {type(data_df.index)}")
                print(f"Debug final index sample: {data_df.index[:3] if len(data_df) > 0 else 'Empty'}")
                
                # Analyze data
                analysis = run_async_safely(analysis_agent.analyze_stock(symbol, data_result))
                
                # Generate visualizations (skip if error)
                chart_html = ''
                try:
                    chart_result = run_async_safely(viz_agent.create_visualization(data_result, "candlestick", f"{symbol}_chart", symbol=symbol, analysis=analysis))
                    chart_html = chart_result.get('save_path', '') if chart_result else ''
                except Exception as e:
                    st.warning(f"Không thể tạo biểu đồ cho {symbol}: {str(e)}")
                
                # Skip report generation to avoid async issues
                report_html = ''
                
                results[symbol] = {
                    'data': data_df,
                    'analysis': analysis,
                    'chart_html': chart_html,
                    'report_html': report_html
                }
                
            except Exception as e:
                st.error(f"Lỗi khi phân tích {symbol}: {str(e)}")
                st.error(f"Chi tiết lỗi: {type(e).__name__}")
                continue
        
        return results
    except Exception as e:
        st.error(f"❌ Lỗi khởi tạo system: {str(e)}")
        return {}

# Sidebar for input
with st.sidebar:
    st.header("📊 Cấu hình phân tích")
    
    # Stock symbols input
    symbols_input = st.text_input(
        "Mã cổ phiếu (ngăn cách bằng dấu phẩy)",
        value="AAPL,GOOGL,MSFT",
        help="Ví dụ: AAPL,GOOGL,MSFT,TSLA"
    )
    
    # Period selection
    period = st.selectbox(
        "Thời gian phân tích",
        options=["3mo", "6mo", "1y", "2y", "5y"],
        index=2,
        help="Chọn khoảng thời gian để phân tích dữ liệu lịch sử"
    )
    
    # Analysis options
    st.subheader("🔧 Tùy chọn phân tích")
    
    enable_ai = st.checkbox("Sử dụng AI Analysis", value=True, help="Sử dụng Deepseek AI để phân tích thông minh")
    enable_technical = st.checkbox("Technical Analysis", value=True, help="Phân tích kỹ thuật với các chỉ báo")
    enable_risk = st.checkbox("Risk Analysis", value=True, help="Phân tích rủi ro đầu tư")
    
    # Run analysis button
    if st.button("🚀 Bắt đầu phân tích", type="primary", use_container_width=True):
        symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
        
        if not symbols:
            st.error("Vui lòng nhập ít nhất một mã cổ phiếu!")
        else:
            with st.spinner("Đang phân tích dữ liệu... Vui lòng chờ"):
                try:
                    # Run analysis
                    analysis_data = run_analysis(symbols, period, enable_ai, enable_technical, enable_risk)
                    st.session_state.analysis_data = analysis_data
                    st.session_state.analysis_complete = True
                    st.success("Phân tích hoàn thành!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi khi phân tích: {str(e)}")

# Main content area
if st.session_state.analysis_complete and st.session_state.analysis_data:
    data = st.session_state.analysis_data
    
    # Overview metrics
    st.header("📈 Tổng quan thị trường")
    
    # Display data timestamp info
    if data:
        first_symbol = list(data.keys())[0]
        first_result = data[first_symbol]
        if not first_result['data'].empty:
            latest_date = first_result['data'].index[-1]
            
            # Handle timezone-aware timestamps properly
            try:
                # Convert to timezone-naive for comparison
                if hasattr(latest_date, 'tz') and latest_date.tz is not None:
                    # Convert to UTC then remove timezone info
                    latest_date_naive = latest_date.tz_convert('UTC').tz_localize(None)
                    now_naive = pd.Timestamp.now(tz='UTC').tz_localize(None)
                else:
                    latest_date_naive = latest_date
                    now_naive = pd.Timestamp.now()
                
                data_age = now_naive - latest_date_naive
            except Exception as e:
                # Fallback: use simple datetime difference
                import datetime
                now_naive = datetime.datetime.now()
                if hasattr(latest_date, 'to_pydatetime'):
                    latest_dt = latest_date.to_pydatetime().replace(tzinfo=None)
                else:
                    latest_dt = pd.to_datetime(latest_date).replace(tzinfo=None)
                data_age = now_naive - latest_dt
            
            # Format timestamp display
            if hasattr(latest_date, 'strftime'):
                date_str = latest_date.strftime("%Y-%m-%d %H:%M:%S")
                if hasattr(latest_date, 'tz') and latest_date.tz:
                    timezone = str(latest_date.tz)
                    date_str += f" ({timezone})"
            else:
                date_str = str(latest_date)
            
            # Color code based on data freshness
            try:
                total_seconds = data_age.total_seconds()
            except:
                total_seconds = data_age.seconds + data_age.days * 86400
                
            if total_seconds < 3600:  # Less than 1 hour
                freshness_color = "🟢"
                freshness_text = "Fresh"
            elif total_seconds < 86400:  # Less than 1 day
                freshness_color = "🟡"
                freshness_text = "Recent"
            else:
                freshness_color = "🔴"
                freshness_text = "Delayed"
            
            st.info(f"📅 **Dữ liệu cập nhật:** {date_str} | {freshness_color} **{freshness_text}** | ⏱️ **Độ tuổi:** {str(data_age).split('.')[0]}")
    
    cols = st.columns(len(data))
    for i, (symbol, result) in enumerate(data.items()):
        with cols[i]:
            # Get latest data with timestamp
            latest_price = result['data']['Close'].iloc[-1]
            latest_timestamp = result['data'].index[-1]
            price_change = ((result['data']['Close'].iloc[-1] / result['data']['Close'].iloc[-2]) - 1) * 100
            
            # Format timestamp for display (American style: M/D H:MM AM/PM)
            if hasattr(latest_timestamp, 'strftime'):
                # Windows-compatible format for M/D H:MM AM/PM
                month = latest_timestamp.month
                day = latest_timestamp.day
                time_12hr = latest_timestamp.strftime("%I:%M %p").lstrip('0')
                date_str = f"{month}/{day} {time_12hr}"
                day_str = latest_timestamp.strftime('%A') if hasattr(latest_timestamp, 'strftime') else ""
            else:
                date_str = str(latest_timestamp)
                day_str = ""
            
            delta_color = "normal" if price_change >= 0 else "inverse"
            st.metric(
                label=f"{symbol}",
                value=f"${latest_price:.2f}",
                delta=f"{price_change:+.2f}%",
                delta_color=delta_color,
                help=f"Cập nhật lúc: {date_str}" + (f" ({day_str})" if day_str else "")
            )
    
    # Detailed analysis for each stock
    for symbol, result in data.items():
        st.header(f"📊 Phân tích chi tiết: {symbol}")
        
        # Add data info section
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            data_points = len(result['data'])
            st.metric("📊 Số điểm dữ liệu", data_points)
        
        with col2:
            try:
                start_timestamp = result['data'].index[0]
                if hasattr(start_timestamp, 'strftime'):
                    start_date = start_timestamp.strftime("%Y-%m-%d")
                else:
                    start_date = str(start_timestamp)[:10]
                st.metric("📅 Từ ngày", start_date)
            except Exception as e:
                st.metric("📅 Từ ngày", "N/A")
        
        with col3:
            try:
                end_timestamp = result['data'].index[-1]
                if hasattr(end_timestamp, 'strftime'):
                    end_date = end_timestamp.strftime("%Y-%m-%d")
                else:
                    end_date = str(end_timestamp)[:10]
                st.metric("📅 Đến ngày", end_date)
            except Exception as e:
                st.metric("📅 Đến ngày", "N/A")
        
        with col4:
            try:
                # Calculate data span safely
                start_ts = result['data'].index[0]
                end_ts = result['data'].index[-1]
                
                if hasattr(start_ts, 'to_pydatetime') and hasattr(end_ts, 'to_pydatetime'):
                    data_span = (end_ts - start_ts).days
                else:
                    data_span = len(result['data'])
                
                st.metric("📈 Khoảng thời gian", f"{data_span} ngày")
            except Exception as e:
                st.metric("📈 Khoảng thời gian", "N/A")
        
        # Show latest data timestamp with more detail
        try:
            latest_timestamp = result['data'].index[-1]
            latest_price = result['data']['Close'].iloc[-1]
            latest_volume = result['data']['Volume'].iloc[-1]
            
            # Safe timestamp formatting (American style)
            if hasattr(latest_timestamp, 'strftime'):
                # Windows-compatible format for M/D H:MM AM/PM
                month = latest_timestamp.month
                day = latest_timestamp.day
                time_12hr = latest_timestamp.strftime("%I:%M %p").lstrip('0')
                date_str = f"{month}/{day} {time_12hr}"
                day_str = latest_timestamp.strftime('%A') if hasattr(latest_timestamp, 'strftime') else ""
            else:
                date_str = str(latest_timestamp)
                day_str = ""
            
            # Safe current time formatting
            try:
                current_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            except:
                import datetime
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h4>🕐 Thông tin dữ liệu mới nhất:</h4>
                <p><strong>📅 Ngày giờ:</strong> {date_str} {f"({day_str})" if day_str else ""}</p>
                <p><strong>💰 Giá đóng cửa:</strong> ${latest_price:.2f}</p>
                <p><strong>📊 Khối lượng:</strong> {latest_volume:,.0f}</p>
                <p><strong>⏰ Cập nhật:</strong> {current_time} (Thời gian hệ thống)</p>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"Không thể hiển thị thông tin timestamp chi tiết: {str(e)}")
        
        # Create tabs for organized display
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Biểu đồ", "🔍 Phân tích kỹ thuật", "⚠️ Phân tích rủi ro", "📝 Báo cáo AI"])
        
        with tab1:
            # Display interactive chart
            try:
                # Always create basic chart for better reliability
                fig = create_basic_chart(result['data'], symbol)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Lỗi hiển thị biểu đồ: {str(e)}")
                st.info("Dữ liệu có sẵn nhưng không thể hiển thị biểu đồ.")
        
        with tab2:
            # Technical analysis
            analysis = result['analysis']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Chỉ báo kỹ thuật")
                
                # RSI
                rsi_data = analysis.get('technical_analysis', {}).get('rsi', {})
                rsi = rsi_data.get('current', 0)
                
                # Handle case where RSI might be a list
                if isinstance(rsi, list):
                    rsi = rsi[-1] if rsi else 0
                
                rsi_signal = get_rsi_signal(rsi)
                st.markdown(f"""
                <div class="metric-card">
                    <h4>RSI (14)</h4>
                    <h2>{rsi:.2f}</h2>
                    <p style="color: {rsi_signal['color']}">{rsi_signal['text']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # MACD
                macd_data = analysis.get('technical_analysis', {}).get('macd', {})
                macd_signal = get_macd_signal(macd_data)
                
                # Safe extraction of MACD values
                macd_value = macd_data.get('macd', 0)
                signal_value = macd_data.get('signal', 0)
                
                # Handle case where values might be lists
                if isinstance(macd_value, list):
                    macd_value = macd_value[-1] if macd_value else 0
                if isinstance(signal_value, list):
                    signal_value = signal_value[-1] if signal_value else 0
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>MACD</h4>
                    <p><b>MACD:</b> {macd_value:.4f}</p>
                    <p><b>Signal:</b> {signal_value:.4f}</p>
                    <p style="color: {macd_signal['color']}">{macd_signal['text']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 📈 Moving Averages")
                
                ma_data = analysis.get('technical_analysis', {}).get('moving_averages', {})
                
                for ma_type, value in ma_data.items():
                    if isinstance(value, (int, float)):
                        current_price = result['data']['Close'].iloc[-1]
                        position = "Trên" if current_price > value else "Dưới"
                        color = "#28a745" if current_price > value else "#dc3545"
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <h5>{ma_type.upper()}</h5>
                            <p><b>Giá trị:</b> ${value:.2f}</p>
                            <p style="color: {color}">Giá hiện tại {position} MA</p>
                        </div>
                        """, unsafe_allow_html=True)
        
        with tab3:
            # Risk analysis
            risk_data = analysis.get('risk_analysis', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ⚠️ Chỉ số rủi ro")
                
                volatility_data = risk_data.get('basic_metrics', {})
                if isinstance(volatility_data, dict):
                    volatility = volatility_data.get('volatility_annual', 0) * 100
                else:
                    volatility = risk_data.get('volatility', 0) * 100
                volatility_level = get_volatility_level(volatility)
                
                st.markdown(f"""
                <div class="risk-card">
                    <h4>Volatility</h4>
                    <h2>{volatility:.2f}%</h2>
                    <p style="color: {volatility_level['color']}">{volatility_level['text']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                sharpe = risk_data.get('sharpe_ratio', 0)
                sharpe_level = get_sharpe_level(sharpe)
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>Sharpe Ratio</h4>
                    <h2>{sharpe:.2f}</h2>
                    <p style="color: {sharpe_level['color']}">{sharpe_level['text']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 📉 Drawdown Analysis")
                
                max_drawdown_data = risk_data.get('max_drawdown', {})
                if isinstance(max_drawdown_data, dict):
                    max_drawdown = max_drawdown_data.get('max_drawdown', 0) * 100
                else:
                    max_drawdown = max_drawdown_data * 100 if max_drawdown_data else 0
                drawdown_level = get_drawdown_level(max_drawdown)
                
                st.markdown(f"""
                <div class="risk-card">
                    <h4>Maximum Drawdown</h4>
                    <h2>{max_drawdown:.2f}%</h2>
                    <p style="color: {drawdown_level['color']}">{drawdown_level['text']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                var_data = risk_data.get('value_at_risk', {})
                if isinstance(var_data, dict):
                    var_95 = var_data.get('var_95', 0) * 100
                else:
                    var_95 = risk_data.get('var_95', 0) * 100
                
                st.markdown(f"""
                <div class="warning-card">
                    <h4>VaR (95%)</h4>
                    <h2>{var_95:.2f}%</h2>
                    <p>Rủi ro tối đa trong 1 ngày (95% tin cậy)</p>
                </div>
                """, unsafe_allow_html=True)
        
        with tab4:
            # AI Report
            st.markdown("### 🤖 Báo cáo AI")
            
            # Display AI insights if available
            analysis = result['analysis']
            ai_insights = analysis.get('ai_insights', {})
            
            if ai_insights and ai_insights.get('enabled', False):
                st.markdown("#### 💡 Phân tích Gemini AI:")
                
                # Display AI source and confidence
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"🤖 Nguồn: {ai_insights.get('source', 'AI')}")
                with col2:
                    st.success(f"🎯 Độ tin cậy: {ai_insights.get('confidence', 'High')}")
                
                # Market sentiment
                sentiment = ai_insights.get('market_sentiment', 'Trung tính')
                sentiment_color = "#28a745" if sentiment == "Tích cực" else "#dc3545" if sentiment == "Tiêu cực" else "#ffc107"
                st.markdown(f"""
                <div style="background-color: {sentiment_color}; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 10px 0;">
                    <h4>📈 Market Sentiment: {sentiment}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # AI insights content
                insights_text = ai_insights.get('insights', '')
                if insights_text:
                    st.markdown("#### 📝 Phân tích chi tiết:")
                    # Display first 1000 characters with expand option
                    if len(insights_text) > 1000:
                        with st.expander("Xem phân tích đầy đủ", expanded=False):
                            st.markdown(insights_text)
                        st.markdown(insights_text[:1000] + "...")
                    else:
                        st.markdown(insights_text)
                
                # Key factors
                key_factors = ai_insights.get('key_factors', [])
                if key_factors:
                    st.markdown("#### 🔑 Các yếu tố chính:")
                    for i, factor in enumerate(key_factors[:5], 1):
                        st.markdown(f"**{i}.** {factor}")
                
                # Generation timestamp
                generated_at = ai_insights.get('generated_at', '')
                if generated_at:
                    st.caption(f"Tạo lúc: {generated_at}")
                
            else:
                # Show fallback message
                error_msg = ai_insights.get('error', 'AI insights không khả dụng')
                st.info(f"🔄 {error_msg}")
                
                # Show rule-based analysis as fallback
                st.markdown("#### 📊 Phân tích tự động:")
                
                # Price trend
                latest_price = result['data']['Close'].iloc[-1]
                prev_price = result['data']['Close'].iloc[-2]
                price_change = ((latest_price / prev_price) - 1) * 100
                
                if price_change > 0:
                    st.success(f"📈 Giá tăng {price_change:.2f}% so với phiên trước")
                else:
                    st.error(f"📉 Giá giảm {abs(price_change):.2f}% so với phiên trước")
                
                # Technical summary
                rsi_data = analysis.get('technical_analysis', {}).get('rsi', {})
                rsi = rsi_data.get('current', 50)
                
                # Handle case where RSI might be a list
                if isinstance(rsi, list):
                    rsi = rsi[-1] if rsi else 50
                
                if rsi > 70:
                    st.warning("⚠️ RSI cho thấy tình trạng overbought")
                elif rsi < 30:
                    st.info("💡 RSI cho thấy tình trạng oversold - có thể là cơ hội mua")
                else:
                    st.success("✅ RSI ở mức trung tính")
                
                # Volume analysis
                avg_volume = result['data']['Volume'].tail(20).mean()
                current_volume = result['data']['Volume'].iloc[-1]
                if current_volume > avg_volume * 1.5:
                    st.info("📊 Khối lượng giao dịch cao hơn bình thường")
                
                st.markdown("---")
                st.caption("💡 Đây là phân tích tự động. Vui lòng tham khảo thêm các nguồn khác trước khi đầu tư.")

else:
    # Welcome screen
    if AGENTS_AVAILABLE:
        display_welcome_screen()
        
        # Demo section
        st.markdown("---")
        st.markdown("### 📈 Demo với dữ liệu mẫu")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🎬 Xem Demo với AAPL", type="secondary", use_container_width=True):
                st.session_state.demo_symbols = "AAPL"
                # Trigger demo analysis
                show_loading_animation()
                try:
                    demo_data = run_analysis(["AAPL"], "6mo", True, True, True)
                    st.session_state.analysis_data = demo_data
                    st.session_state.analysis_complete = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Lỗi demo: {str(e)}")
    else:
        # Fallback welcome screen
        st.markdown("""
        ## 🎯 Chào mừng đến với AI Financial Analyst
        
        ❌ **Lỗi**: Không thể load các modules cần thiết.
        
        ### 🔧 Cách khắc phục:
        1. Đảm bảo bạn đang chạy từ thư mục gốc của project
        2. Kiểm tra các file agents/ có tồn tại không
        3. Chạy lại với: `streamlit run streamlit_app.py`
        
        ### 📁 Cấu trúc thư mục cần thiết:
        ```
        AI-Financial-Analyst_MCP/
        ├── agents/
        │   ├── data_retrieval_agent.py
        │   ├── data_analysis_agent.py
        │   ├── visualization_agent.py
        │   └── report_generation_agent.py
        ├── utils/
        │   └── config_manager.py
        └── streamlit_app.py
        ```
        """)



if __name__ == "__main__":
    st.markdown("---")
    st.markdown("*Powered by AI Financial Analyst - Phiên bản Streamlit 🚀*") 