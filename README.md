# 🚀 AI Financial Analyst - MCP System

> **Hệ thống phân tích tài chính thông minh sử dụng AI và Machine Learning**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Gemini AI](https://img.shields.io/badge/Gemini%20AI-Integrated-green.svg)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 **Tính năng chính**

### 🤖 **AI-Powered Analysis**
- **Gemini AI Integration** - Phân tích thông minh với Google Gemini AI
- **Market Sentiment Analysis** - Đánh giá tâm lý thị trường real-time
- **Investment Recommendations** - Khuyến nghị đầu tư chi tiết với AI
- **Risk Assessment** - Phân tích rủi ro chuyên sâu
- **Real-time Data Display** - Hiển thị ngày giờ và dữ liệu real-time

### 📊 **Advanced Technical Analysis**
- **Technical Indicators** - RSI, MACD, Bollinger Bands, Moving Averages
- **Price Pattern Recognition** - Nhận diện mô hình giá tự động
- **Volume Analysis** - Phân tích khối lượng giao dịch chi tiết
- **Support/Resistance Levels** - Xác định vùng hỗ trợ/kháng cự
- **Professional Charts** - Biểu đồ candlestick với styling chuyên nghiệp

### 📈 **Data Sources & Real-time Updates**
- **Yahoo Finance** - Dữ liệu real-time miễn phí
- **Alpha Vantage** - Dữ liệu chuyên nghiệp
- **CSV Import** - Hỗ trợ dữ liệu tùy chỉnh
- **Multi-timeframe** - 3M, 6M, 1Y, 2Y, 5Y
- **Live Data Updates** - Cập nhật dữ liệu theo thời gian thực

### 🎨 **Modern Visualization**
- **Interactive Charts** - Plotly candlestick charts với tương tác cao
- **Technical Overlays** - Chỉ báo kỹ thuật trực quan
- **Professional Dashboard** - Giao diện hiện đại, responsive
- **Export Options** - HTML, PNG, PDF
- **Dark/Light Theme** - Hỗ trợ nhiều theme

## 🚀 **Quick Start**

### **1. Clone Repository**
```bash
git clone https://github.com/GenTpham/AI-Financial-Analyst_MCP.git
cd AI-Financial-Analyst_MCP
```

### **2. Setup Environment**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Configure API Keys**
```bash
# Copy template file
cp config/api_keys.env.template config/api_keys.env

# Edit with your API keys
# Required: GEMINI_API_KEY
# Optional: ALPHA_VANTAGE_API_KEY, DEEPSEEK_API_KEY
```

### **4. Run Application**

#### **🌐 Streamlit Web App (Recommended)**
```bash
# Windows - Quick Start
start_app.bat

# Or manually
python -m streamlit run streamlit_app.py

# Open in browser: http://localhost:8501
```

#### **📊 Console Demo**
```bash
# Simple demo
python simple_demo.py

# Full analysis demo with AI
python final_ai_demo.py

# Test Gemini AI integration
python test_gemini_integration.py
```

## 🏗️ **Architecture**

```
AI-Financial-Analyst_MCP/
├── 🌐 streamlit_app.py          # Main web application (Updated!)
├── 🤖 src/agents/               # AI Agents
│   ├── gemini_ai_client.py      # Gemini AI integration
│   ├── data_retrieval_agent.py  # Data fetching
│   ├── data_analysis_agent.py   # Technical analysis
│   ├── visualization_agent.py   # Chart generation
│   └── report_generation_agent.py # Report creation
├── ⚙️ config/                   # Configuration
│   ├── api_keys.env.template    # API keys template
│   └── mcp_config.yaml          # MCP settings
├── 📊 output/                   # Generated files
│   ├── charts/                  # Interactive charts
│   └── reports/                 # Analysis reports
├── 🎯 examples/                 # Usage examples
├── 📚 docs/                     # Documentation
├── 🚀 final_ai_demo.py          # Latest AI demo
└── 📱 Various demo files        # Multiple demo options
```

## 🔧 **Configuration**

### **API Keys Required**

| Service | Required | Purpose | Get Key |
|---------|----------|---------|---------|
| **Gemini AI** | ✅ Yes | AI Analysis | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| Alpha Vantage | ⚪ Optional | Professional Data | [Alpha Vantage](https://www.alphavantage.co/support/#api-key) |
| Deepseek AI | ⚪ Optional | Backup AI | [Deepseek Platform](https://platform.deepseek.com/) |

### **Environment Variables**
```bash
# Primary AI Engine
GEMINI_API_KEY=your_gemini_api_key_here

# Data Sources
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# Backup AI (Optional)
DEEPSEEK_API_KEY=your_deepseek_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

## 📱 **Usage Examples**

### **Web Interface**
1. Open http://localhost:8501
2. Enter stock symbols: `AAPL,GOOGL,MSFT,NVDA`
3. Select timeframe: `6mo`
4. Enable AI Analysis ✅
5. Click "🚀 Bắt đầu phân tích"
6. View real-time results with date/time stamps

### **Python API**
```python
from src.agents.gemini_ai_client import GeminiAIClient
from src.agents.data_retrieval_agent import DataRetrievalAgent

# Initialize clients
ai_client = GeminiAIClient()
data_agent = DataRetrievalAgent(config, data_sources_config)

# Get stock data
data = await data_agent.fetch_stock_data("AAPL", "6mo")

# Generate AI insights
insights = await ai_client.generate_market_insights("AAPL", data)
print(insights['market_sentiment'])  # "Tích cực" / "Tiêu cực" / "Trung tính"
```

## 🎯 **Features Showcase**

### **🤖 AI Analysis Sample**
```
📊 Market Sentiment: Tích cực
🎯 Recommendation: MUA
💰 Target Price: $200.00
⚠️ Risk Level: Trung bình
🕐 Analysis Time: 2024-01-15 14:30:25
🔑 Key Factors:
  1. Strong technical indicators
  2. Positive market momentum  
  3. Favorable risk-reward ratio
  4. Solid fundamental metrics
  5. Growing market demand
```

### **📈 Technical Indicators**
- **RSI (14)**: 52.3 - Trung tính
- **MACD**: Bullish Signal ↗️
- **Bollinger Bands**: Price within bands
- **Moving Averages**: SMA20 > SMA50 (Bullish)
- **Volume**: Above average (+15%)

## 🛠️ **Development**

### **Recent Updates**
- ✅ Enhanced chart visualization with professional styling
- ✅ Real-time date/time display
- ✅ Improved UI/UX with modern design
- ✅ Better error handling and loading states
- ✅ Multiple demo files for different use cases

### **Project Structure**
```python
# Core Components
├── MCP Server          # Multi-agent coordination
├── Data Agents         # Yahoo Finance, Alpha Vantage
├── Analysis Agents     # Technical, Fundamental, Risk
├── AI Agents          # Gemini AI, Deepseek AI
├── Visualization      # Enhanced Plotly charts
└── Report Generation  # HTML, JSON, PDF
```

### **Adding New Features**
1. Create new agent in `src/agents/`
2. Register in MCP server
3. Add to Streamlit interface
4. Update documentation

## 📊 **Performance**

- **Data Processing**: ~2-3 seconds per stock
- **AI Analysis**: ~5-10 seconds per stock  
- **Chart Generation**: ~1-2 seconds per chart (Enhanced!)
- **Memory Usage**: ~100-200MB
- **Concurrent Stocks**: Up to 10 stocks
- **Real-time Updates**: Every 15 minutes

## 🚀 **Latest Features**

### **Enhanced Streamlit App**
- Modern, professional chart styling
- Real-time date and time display
- Improved loading animations
- Better error handling
- Responsive design

### **Multiple Demo Options**
- `final_ai_demo.py` - Latest full-featured demo
- `simple_demo.py` - Basic functionality demo
- `ai_demo_with_fallback.py` - Fallback options demo
- `demo_gemini_analysis.py` - Gemini AI specific demo

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Google Gemini AI** - Advanced AI analysis capabilities
- **Yahoo Finance** - Free financial data APIs
- **Alpha Vantage** - Professional market data
- **Plotly** - Interactive visualization library
- **Streamlit** - Modern web application framework

## 📞 **Support**

- 💬 Issues: [GitHub Issues](https://github.com/GenTpham/AI-Financial-Analyst_MCP/issues)
- 📖 Documentation: [Wiki](https://github.com/GenTpham/AI-Financial-Analyst_MCP/wiki)
- 📧 Contact: For support and questions

---

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by GenTpham | Last Updated: $(date)
