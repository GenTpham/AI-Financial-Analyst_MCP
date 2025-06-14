"""
Demo Gemini AI Financial Analysis - Showcase hoàn chỉnh
"""

import asyncio
import sys
import os
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment
load_dotenv('config/api_keys.env')

from agents.data_retrieval_agent import DataRetrievalAgent
from agents.data_analysis_agent import DataAnalysisAgent
from agents.visualization_agent import VisualizationAgent
from agents.report_generation_agent import ReportGenerationAgent

async def demo_full_gemini_analysis():
    """Demo phân tích hoàn chỉnh với Gemini AI"""
    
    print("🚀 DEMO PHÂN TÍCH TÀI CHÍNH VỚI GEMINI AI")
    print("=" * 70)
    print(f"Bắt đầu lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration
    config = {
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
    print("\n🔧 Khởi tạo các agents...")
    data_agent = DataRetrievalAgent(config, data_sources_config)
    analysis_agent = DataAnalysisAgent(config, data_sources_config)
    viz_agent = VisualizationAgent(config, data_sources_config)
    report_agent = ReportGenerationAgent(config, data_sources_config)
    
    # Test symbols
    symbols = ["AAPL", "GOOGL", "MSFT"]
    
    for symbol in symbols:
        print(f"\n{'='*50}")
        print(f"🔍 PHÂN TÍCH {symbol} VỚI GEMINI AI")
        print(f"{'='*50}")
        
        try:
            # Step 1: Get data
            print(f"📊 Bước 1: Lấy dữ liệu cho {symbol}...")
            data_result = await data_agent.fetch_stock_data(symbol, "6mo")
            
            if not data_result or 'data' not in data_result:
                print(f"❌ Không thể lấy dữ liệu cho {symbol}")
                continue
            
            print(f"✅ Đã lấy {data_result['metadata']['data_points']} điểm dữ liệu")
            
            # Step 2: Analysis
            print(f"🧮 Bước 2: Phân tích kỹ thuật và rủi ro...")
            analysis_result = await analysis_agent.analyze_stock(symbol, data_result)
            
            if not analysis_result:
                print(f"❌ Lỗi phân tích {symbol}")
                continue
            
            print(f"✅ Phân tích hoàn thành")
            
            # Step 3: AI Insights
            print(f"🤖 Bước 3: Tạo AI insights với Gemini...")
            ai_insights = await analysis_agent.generate_market_insights(symbol, analysis_result)
            
            if ai_insights.get('enabled', False):
                print(f"✅ AI insights được tạo thành công!")
                print(f"   Nguồn: {ai_insights.get('source', 'N/A')}")
                print(f"   Market Sentiment: {ai_insights.get('market_sentiment', 'N/A')}")
                print(f"   Key Factors: {len(ai_insights.get('key_factors', []))} yếu tố")
                
                # Display key insights
                insights_preview = ai_insights.get('insights', '')[:200]
                print(f"\n📝 Preview AI Analysis:")
                print(f"   {insights_preview}...")
                
            else:
                print(f"⚠️ AI insights không khả dụng: {ai_insights.get('error', 'Unknown error')}")
            
            # Step 4: Generate report
            print(f"📄 Bước 4: Tạo báo cáo...")
            
            # Add AI insights to analysis result
            analysis_result['ai_insights'] = ai_insights
            
            report_result = await report_agent.generate_report(
                symbol, 
                analysis_result, 
                format="html"
            )
            
            if report_result.get('status') == 'success':
                print(f"✅ Báo cáo được tạo: {report_result.get('report_path', 'N/A')}")
            else:
                print(f"⚠️ Lỗi tạo báo cáo: {report_result.get('error', 'Unknown error')}")
            
            # Step 5: Create visualization
            print(f"📊 Bước 5: Tạo biểu đồ...")
            
            chart_result = await viz_agent.create_comprehensive_chart(
                symbol,
                data_result,
                analysis_result
            )
            
            if chart_result.get('status') == 'success':
                print(f"✅ Biểu đồ được tạo: {chart_result.get('chart_path', 'N/A')}")
            else:
                print(f"⚠️ Lỗi tạo biểu đồ: {chart_result.get('error', 'Unknown error')}")
            
            print(f"🎉 Hoàn thành phân tích {symbol}!")
            
        except Exception as e:
            print(f"❌ Lỗi phân tích {symbol}: {str(e)}")
    
    print(f"\n{'='*70}")
    print("🎊 DEMO HOÀN THÀNH!")
    print(f"Kết thúc lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📁 Kiểm tra kết quả tại:")
    print("   📊 Charts: ./output/charts/")
    print("   📄 Reports: ./output/reports/")
    print("\n🌐 Mở Streamlit app tại: http://localhost:8501")

if __name__ == "__main__":
    asyncio.run(demo_full_gemini_analysis()) 