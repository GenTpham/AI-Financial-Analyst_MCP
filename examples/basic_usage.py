#!/usr/bin/env python3
"""
Ví dụ sử dụng cơ bản cho AI Financial Analyst MCP
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.client.mcp_client import FinancialAnalystAPI

async def basic_analysis_example():
    """Ví dụ phân tích cơ bản"""
    print("=== VÍ DỤ PHÂN TÍCH CƠ BẢN ===")
    
    # Khởi tạo API client
    async with FinancialAnalystAPI() as api:
        # Phân tích một cổ phiếu
        symbol = "AAPL"
        print(f"Đang phân tích cổ phiếu {symbol}...")
        
        try:
            # Chạy phân tích hoàn chỉnh
            result = await api.analyze(
                symbol=symbol,
                analysis_types=["technical", "fundamental", "risk"],
                create_charts=True,
                generate_report=True,
                report_format="html"
            )
            
            print(f"✅ Phân tích hoàn tất cho {symbol}")
            print(f"📊 Số điểm dữ liệu: {result['analysis']['data_period']['data_points']}")
            print(f"💰 Giá hiện tại: ${result['analysis']['price_analysis']['current_price']:.2f}")
            print(f"📈 Thay đổi 1 ngày: {result['analysis']['price_analysis']['price_changes']['1_day']:.2f}%")
            print(f"📊 Biểu đồ đã tạo: {len(result['charts'])}")
            print(f"📄 Báo cáo đã tạo: {len(result['reports'])}")
            
            # In đường dẫn báo cáo
            for report in result['reports']:
                print(f"📋 Báo cáo: {report['report_path']}")
            
            # In đường dẫn biểu đồ
            for chart in result['charts']:
                print(f"📈 Biểu đồ: {chart['save_path']}")
                
        except Exception as e:
            print(f"❌ Lỗi khi phân tích {symbol}: {e}")

async def multiple_stocks_example():
    """Ví dụ phân tích nhiều cổ phiếu"""
    print("\n=== VÍ DỤ PHÂN TÍCH NHIỀU CỔ PHIẾU ===")
    
    async with FinancialAnalystAPI() as api:
        # Danh sách cổ phiếu cần phân tích
        symbols = ["AAPL", "GOOGL", "MSFT"]
        print(f"Đang phân tích danh mục: {', '.join(symbols)}")
        
        try:
            # Chạy phân tích danh mục
            portfolio_result = await api.compare(
                symbols=symbols,
                create_comparison_charts=True,
                generate_summary_report=True
            )
            
            print(f"✅ Phân tích danh mục hoàn tất")
            print(f"📊 Số cổ phiếu đã phân tích: {len(portfolio_result['individual_analysis'])}")
            
            # In kết quả từng cổ phiếu
            for symbol, analysis in portfolio_result['individual_analysis'].items():
                price_analysis = analysis['analysis']['price_analysis']
                print(f"  📈 {symbol}: ${price_analysis['current_price']:.2f} ({price_analysis['price_changes']['1_day']:+.2f}%)")
                
        except Exception as e:
            print(f"❌ Lỗi khi phân tích danh mục: {e}")

async def chart_creation_example():
    """Ví dụ tạo biểu đồ"""
    print("\n=== VÍ DỤ TẠO BIỂU ĐỒ ===")
    
    async with FinancialAnalystAPI() as api:
        symbol = "TSLA"
        print(f"Đang lấy dữ liệu và tạo biểu đồ cho {symbol}...")
        
        try:
            # Lấy dữ liệu
            data = await api.get_data(symbol, period="6mo")
            
            # Tạo các loại biểu đồ khác nhau
            chart_types = ["line", "candlestick", "technical", "dashboard"]
            
            for chart_type in chart_types:
                try:
                    chart_result = await api.create_chart(
                        data=data,
                        chart_type=chart_type,
                        title=f"{symbol} - {chart_type.title()} Chart"
                    )
                    print(f"✅ Đã tạo biểu đồ {chart_type}: {chart_result['save_path']}")
                except Exception as e:
                    print(f"❌ Lỗi tạo biểu đồ {chart_type}: {e}")
                    
        except Exception as e:
            print(f"❌ Lỗi khi tạo biểu đồ cho {symbol}: {e}")

async def data_sources_example():
    """Ví dụ sử dụng các nguồn dữ liệu khác nhau"""
    print("\n=== VÍ DỤ CÁC NGUỒN DỮ LIỆU ===")
    
    async with FinancialAnalystAPI() as api:
        symbol = "NVDA"
        
        # Test các nguồn dữ liệu khác nhau
        sources = ["yahoo", "alpha_vantage"]
        
        for source in sources:
            try:
                print(f"Đang lấy dữ liệu từ {source}...")
                data = await api.get_data(
                    symbol=symbol,
                    source=source,
                    period="3mo"
                )
                
                data_points = len(data['data']['historical'])
                print(f"✅ {source}: {data_points} điểm dữ liệu")
                
            except Exception as e:
                print(f"❌ Lỗi với nguồn {source}: {e}")

async def main():
    """Main function"""
    print("🚀 BẮT ĐẦU CÁC VÍ DỤ SỬ DỤNG AI FINANCIAL ANALYST MCP")
    print("=" * 60)
    
    try:
        # Chạy các ví dụ
        await basic_analysis_example()
        await multiple_stocks_example()
        await chart_creation_example()
        await data_sources_example()
        
        print("\n🎉 TẤT CẢ VÍ DỤ ĐÃ HOÀN THÀNH!")
        print("📁 Kiểm tra thư mục 'output' để xem báo cáo và biểu đồ")
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình chạy ví dụ: {e}")

if __name__ == "__main__":
    # Kiểm tra xem server có đang chạy không
    print("⚠️ Đảm bảo MCP Server đang chạy trước khi chạy ví dụ")
    print("   Chạy: python main.py")
    print("   Sau đó chạy ví dụ này trong terminal khác")
    input("Nhấn Enter để tiếp tục...")
    
    asyncio.run(main()) 