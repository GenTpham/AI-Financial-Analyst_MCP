# 🚀 AI Financial Analyst - Streamlit Web App

## 📝 Mô tả
Ứng dụng web phân tích tài chính thông minh sử dụng AI và Machine Learning, được xây dựng với Streamlit để có giao diện người dùng đẹp mắt và dễ sử dụng.

## ✨ Tính năng chính

### 🤖 AI-Powered Analysis
- **Deepseek AI Integration**: Phân tích thông minh với AI
- **Smart Recommendations**: Khuyến nghị đầu tư tự động
- **Market Insights**: Phân tích xu hướng thị trường

### 📊 Technical Analysis
- **RSI (Relative Strength Index)**: Chỉ báo momentum
- **MACD**: Moving Average Convergence Divergence  
- **Bollinger Bands**: Phân tích biến động giá
- **Moving Averages**: MA20, MA50, MA200
- **Stochastic Oscillator**: Chỉ báo overbought/oversold

### ⚠️ Risk Analysis
- **Volatility Analysis**: Phân tích độ biến động
- **Sharpe Ratio**: Tỷ lệ risk-adjusted return
- **Maximum Drawdown**: Mức thua lỗ tối đa
- **VaR (Value at Risk)**: Rủi ro tài chính

### 📈 Visualization
- **Interactive Charts**: Biểu đồ tương tác với Plotly
- **Multi-panel Dashboard**: Giao diện dashboard chuyên nghiệp
- **Real-time Data**: Dữ liệu thời gian thực từ Yahoo Finance

## 🛠️ Cài đặt

### 1. Clone Repository
```bash
git clone <repository-url>
cd AI-Financial-Analyst_MCP
```

### 2. Cài đặt Dependencies
```bash
pip install -r requirements.txt
```

### 3. Cấu hình Environment
Tạo file `.env` và thêm API key:
```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

## 🚀 Chạy ứng dụng

### Cách 1: Sử dụng script khởi động
```bash
python run_streamlit.py
```

### Cách 2: Chạy trực tiếp Streamlit
```bash
streamlit run streamlit_app.py
```

Ứng dụng sẽ chạy tại: **http://localhost:8501**

## 📱 Cách sử dụng

### 1. Nhập thông tin phân tích
- **Mã cổ phiếu**: Nhập các mã cổ phiếu (VD: AAPL,GOOGL,MSFT)
- **Thời gian**: Chọn period phân tích (3mo, 6mo, 1y, 2y, 5y)
- **Tùy chọn**: Bật/tắt AI Analysis, Technical Analysis, Risk Analysis

### 2. Chạy phân tích
- Nhấn nút **"🚀 Bắt đầu phân tích"**
- Chờ hệ thống xử lý dữ liệu

### 3. Xem kết quả
- **📈 Tổng quan thị trường**: Giá và biến động hôm nay
- **📊 Biểu đồ**: Charts tương tác với các chỉ báo kỹ thuật
- **🔍 Phân tích kỹ thuật**: RSI, MACD, Moving Averages chi tiết
- **⚠️ Phân tích rủi ro**: Volatility, Sharpe Ratio, Drawdown
- **📝 Báo cáo AI**: Khuyến nghị đầu tư từ AI

## 🎯 Demo
Nhấn nút **"🎬 Xem Demo với AAPL"** để xem demo với dữ liệu mẫu.

## 🔧 Cấu hình nâng cao

### Streamlit Configuration
File `.streamlit/config.toml` chứa cấu hình:
- Theme và colors
- Server settings  
- Performance optimization

### Environment Variables
```env
# Deepseek AI
DEEPSEEK_API_KEY=sk-your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Optional: Yahoo Finance settings
YAHOO_FINANCE_TIMEOUT=30
```

## 📊 Supported Stock Symbols
- **US Stocks**: AAPL, GOOGL, MSFT, TSLA, AMZN, etc.
- **ETFs**: SPY, QQQ, IWM, etc.
- **Indices**: ^GSPC (S&P 500), ^IXIC (NASDAQ), etc.

## 🚨 Troubleshooting

### Lỗi thường gặp:

1. **"Insufficient Balance" khi dùng AI**
   - Kiểm tra API key Deepseek
   - Đảm bảo tài khoản có balance

2. **Không tải được dữ liệu cổ phiếu**
   - Kiểm tra mã cổ phiếu có đúng không
   - Thử lại với period ngắn hơn

3. **App chạy chậm**
   - Giảm số lượng cổ phiếu phân tích
   - Tắt một số tính năng không cần thiết

### Performance Tips:
- Sử dụng ít cổ phiếu trong 1 lần phân tích
- Chọn period phù hợp (1y thường đủ)
- Tắt AI analysis nếu không cần thiết

## 🎨 Customization

### Thay đổi Theme
Chỉnh sửa file `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#your-color"
backgroundColor = "#your-bg-color"
```

### Thêm chỉ báo kỹ thuật
Chỉnh sửa `agents/data_analysis_agent.py` để thêm các chỉ báo mới.

## 📈 Architecture
```
streamlit_app.py          # Main UI application
├── agents/              # Core analysis agents
│   ├── data_retrieval_agent.py
│   ├── data_analysis_agent.py  
│   ├── visualization_agent.py
│   └── report_generation_agent.py
├── utils/               # Utilities
│   └── config_manager.py
├── .streamlit/          # Streamlit configuration
│   └── config.toml
└── requirements.txt     # Dependencies
```

## 🤝 Contributing
1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License
MIT License - xem file LICENSE để biết thêm chi tiết.

## 🎉 Credits
- **Streamlit**: Web app framework
- **Plotly**: Interactive visualizations
- **Deepseek AI**: Intelligent analysis
- **Yahoo Finance**: Stock data source
- **Pandas/NumPy**: Data processing

---
*Powered by AI Financial Analyst - Streamlit Edition 🚀* 