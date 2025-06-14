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
    """Create basic chart if HTML not available"""
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    
    fig = make_subplots(rows=2, cols=1, 
                       subplot_titles=[f'{symbol} Stock Price', 'Volume'],
                       vertical_spacing=0.1,
                       row_width=[0.7, 0.3])
    
    # Price chart
    fig.add_trace(go.Candlestick(x=data.index,
                                open=data['Open'],
                                high=data['High'],
                                low=data['Low'],
                                close=data['Close'],
                                name=symbol), row=1, col=1)
    
    # Volume chart
    fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume'), row=2, col=1)
    
    fig.update_layout(height=600, showlegend=False)
    fig.update_xaxes(rangeslider_visible=False)
    
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
                
                # Convert to DataFrame
                import pandas as pd
                data_df = pd.DataFrame(historical_data)
                if 'Date' in data_df.columns:
                    data_df.set_index('Date', inplace=True)
                elif data_df.index.name != 'Date':
                    # If index is already datetime, keep it
                    pass
                
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
    
    cols = st.columns(len(data))
    for i, (symbol, result) in enumerate(data.items()):
        with cols[i]:
            latest_price = result['data']['Close'].iloc[-1]
            price_change = ((result['data']['Close'].iloc[-1] / result['data']['Close'].iloc[-2]) - 1) * 100
            
            delta_color = "normal" if price_change >= 0 else "inverse"
            st.metric(
                label=f"{symbol}",
                value=f"${latest_price:.2f}",
                delta=f"{price_change:+.2f}%",
                delta_color=delta_color
            )
    
    # Detailed analysis for each stock
    for symbol, result in data.items():
        st.header(f"📊 Phân tích chi tiết: {symbol}")
        
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