# 🚀 Quick Start Guide - AI Financial Analyst MCP

Hướng dẫn nhanh để bắt đầu sử dụng hệ thống AI phân tích tài chính với MCP.

## ⚡ Cài đặt nhanh (5 phút)

### Bước 1: Setup môi trường
```bash
# Clone repository
git clone <repository-url>
cd AI-Financial-Analyst_MCP

# Chạy setup tự động
python setup.py
```

### Bước 2: Cấu hình API Keys
```bash
# Chỉnh sửa file .env (đã được tạo tự động)
# Thêm Alpha Vantage API key (miễn phí tại alphavantage.co)
ALPHA_VANTAGE_API_KEY=your_actual_api_key_here
```

### Bước 3: Khởi chạy hệ thống
```bash
# Terminal 1: Chạy MCP Server
python main.py

# Terminal 2: Chạy ví dụ
python examples/basic_usage.py
```

## 🎯 Ví dụ sử dụng cơ bản

### Phân tích một cổ phiếu
```python
from src.client.mcp_client import FinancialAnalystAPI

async with FinancialAnalystAPI() as api:
    # Phân tích AAPL với báo cáo và biểu đồ
    result = await api.analyze("AAPL")
    print(f"Giá hiện tại: ${result['analysis']['price_analysis']['current_price']}")
```

### So sánh nhiều cổ phiếu
```python
async with FinancialAnalystAPI() as api:
    # So sánh top tech stocks
    comparison = await api.compare(["AAPL", "GOOGL", "MSFT", "TSLA"])
    print("Kết quả so sánh đã được lưu!")
```

### Tạo biểu đồ chuyên nghiệp
```python
async with FinancialAnalystAPI() as api:
    # Lấy dữ liệu
    data = await api.get_data("NVDA", period="6mo")
    
    # Tạo dashboard
    dashboard = await api.create_chart(
        data=data, 
        chart_type="dashboard",
        title="NVDA - Comprehensive Analysis"
    )
```

## 📊 Các tính năng chính

| Tính năng | Mô tả | Ví dụ |
|-----------|-------|-------|
| **Truy xuất dữ liệu** | Yahoo Finance, Alpha Vantage, CSV | `api.get_data("AAPL")` |
| **Phân tích kỹ thuật** | RSI, MACD, Bollinger Bands | Tự động trong `analyze()` |
| **Phân tích cơ bản** | P/E, ROE, Market Cap | Tự động từ Yahoo Finance |
| **Phân tích rủi ro** | Sharpe, VaR, Volatility | Tự động tính toán |
| **Biểu đồ** | Candlestick, Technical, Dashboard | `create_chart()` |
| **Báo cáo** | HTML, JSON, Text | Tự động tạo |

## 🎨 Loại biểu đồ có sẵn

```python
# Các loại biểu đồ
chart_types = [
    "line",          # Đường giá đơn giản
    "candlestick",   # Nến Nhật với volume
    "technical",     # Phân tích kỹ thuật đầy đủ
    "dashboard",     # Tổng quan toàn diện
    "bar"           # Biểu đồ cột
]

# Sử dụng
for chart_type in chart_types:
    await api.create_chart(data, chart_type)
```

## 📁 Output Files

Sau khi chạy, kiểm tra các thư mục:

```
output/
├── charts/           # File biểu đồ (.html, .png)
│   ├── candlestick_20241201_143022.html
│   ├── technical_20241201_143025.html
│   └── dashboard_20241201_143028.html
└── reports/          # File báo cáo
    ├── financial_report_AAPL_20241201_143030.html
    └── financial_report_AAPL_20241201_143030.json
```

## 🔧 Cấu hình nâng cao

### Tùy chỉnh phân tích
```python
result = await api.analyze(
    symbol="AAPL",
    analysis_types=["technical", "risk"],  # Chỉ phân tích kỹ thuật và rủi ro
    create_charts=True,
    report_format="json"  # Báo cáo JSON thay vì HTML
)
```

### Sử dụng nguồn dữ liệu khác
```python
# Yahoo Finance (mặc định, miễn phí)
yahoo_data = await api.get_data("AAPL", source="yahoo")

# Alpha Vantage (cần API key)
av_data = await api.get_data("AAPL", source="alpha_vantage")

# CSV file local
csv_data = await api.get_data("SAMPLE", source="csv")
```

## 🚨 Xử lý lỗi thường gặp

### 1. Lỗi kết nối MCP Server
```
❌ Failed to connect to server
```
**Giải pháp**: Đảm bảo MCP Server đang chạy (`python main.py`)

### 2. Lỗi API Key
```
❌ Alpha Vantage client not initialized
```
**Giải pháp**: Kiểm tra API key trong file `.env`

### 3. Lỗi thiếu dependencies
```
❌ ModuleNotFoundError: No module named 'plotly'
```
**Giải pháp**: Chạy `pip install -r requirements.txt`

### 4. Lỗi permissions
```
❌ Permission denied: output/charts/
```
**Giải pháp**: Chạy `python setup.py` để tạo thư mục

## 💡 Tips và tricks

### 1. Chạy phân tích hàng loạt
```python
symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
for symbol in symbols:
    try:
        result = await api.analyze(symbol)
        print(f"✅ {symbol} completed")
    except Exception as e:
        print(f"❌ {symbol} failed: {e}")
```

### 2. Cache dữ liệu để tăng tốc
```python
# Dữ liệu được cache tự động trong 5 phút
# Gọi lại trong thời gian này sẽ trả về cache
data1 = await api.get_data("AAPL")  # Từ API
data2 = await api.get_data("AAPL")  # Từ cache (nhanh hơn)
```

### 3. Sử dụng với Jupyter Notebook
```python
# Trong Jupyter Notebook
import asyncio
from src.client.mcp_client import FinancialAnalystAPI

async def analyze_stock(symbol):
    async with FinancialAnalystAPI() as api:
        return await api.analyze(symbol)

# Chạy
result = await analyze_stock("AAPL")
```

## 📊 Workflow hoàn chỉnh

```python
async def complete_analysis_workflow():
    async with FinancialAnalystAPI() as api:
        # 1. Phân tích cơ bản
        result = await api.analyze("AAPL")
        
        # 2. So sánh với competitors
        comparison = await api.compare(["AAPL", "GOOGL", "MSFT"])
        
        # 3. Tạo biểu đồ tùy chỉnh
        custom_chart = await api.create_chart(
            data=result,
            chart_type="technical",
            title="AAPL - Deep Technical Analysis"
        )
        
        print("🎉 Phân tích hoàn tất!")
        print(f"📊 Biểu đồ: {custom_chart['save_path']}")
        print(f"📄 Báo cáo: {result['reports'][0]['report_path']}")

# Chạy workflow
asyncio.run(complete_analysis_workflow())
```

## 🎯 Next Steps

1. **Tùy chỉnh agents**: Chỉnh sửa logic trong `src/agents/`
2. **Thêm data sources**: Mở rộng `DataRetrievalAgent`
3. **Custom indicators**: Thêm chỉ báo mới trong `DataAnalysisAgent`
4. **API integration**: Tích hợp với hệ thống khác
5. **Production deployment**: Deploy lên server

## 📚 Tài liệu tham khảo

- [README.md](README.md) - Tài liệu đầy đủ
- [examples/](examples/) - Thêm ví dụ
- [src/](src/) - Source code
- [config/](config/) - File cấu hình

---

🎉 **Chúc bạn sử dụng AI Financial Analyst MCP thành công!**

*Có câu hỏi? Tạo issue trên GitHub hoặc xem documentation.* 