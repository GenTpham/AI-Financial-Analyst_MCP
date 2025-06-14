"""
Test script để kiểm tra việc tích hợp Deepseek AI
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.client.mcp_client import FinancialAnalystAPI
from dotenv import load_dotenv

async def test_deepseek_integration():
    """Test Deepseek AI integration"""
    print("🤖 Testing Deepseek AI Integration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if not deepseek_key or deepseek_key == 'your_deepseek_api_key_here':
        print("❌ DEEPSEEK_API_KEY not found or not configured properly")
        print("Please set your Deepseek API key in .env file")
        return
    
    print(f"✅ Deepseek API key found: {deepseek_key[:20]}...")
    
    # Test analysis with AI insights
    async with FinancialAnalystAPI() as api:
        print("\n📊 Analyzing AAPL with AI insights...")
        try:
            result = await api.analyze("AAPL")
            
            # Check if AI insights are present
            ai_insights = result.get('ai_insights', {})
            if ai_insights and ai_insights.get('enabled', False):
                print("✅ AI Insights successfully generated!")
                print(f"Market Sentiment: {ai_insights.get('market_sentiment', 'N/A')}")
                print(f"Key Factors: {len(ai_insights.get('key_factors', []))} identified")
                print(f"Source: {ai_insights.get('source', 'N/A')}")
                
                print("\n🔍 AI Analysis Preview:")
                insights_text = ai_insights.get('insights', '')
                if insights_text:
                    # Show first 200 characters
                    preview = insights_text[:200] + "..." if len(insights_text) > 200 else insights_text
                    print(preview)
                
            else:
                print("❌ AI Insights not generated or disabled")
                if 'error' in ai_insights:
                    print(f"Error: {ai_insights['error']}")
                    
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
    
    # Test report generation with AI recommendations
    async with FinancialAnalystAPI() as api:
        print("\n📄 Generating report with AI recommendations...")
        try:
            report = await api.generate_report("AAPL", format="html")
            
            if report.get('status') == 'success':
                print("✅ Report with AI recommendations generated successfully!")
                print(f"Report path: {report.get('report_path', 'N/A')}")
                
                # Check if report contains AI content
                report_path = report.get('report_path')
                if report_path and os.path.exists(report_path):
                    with open(report_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'AI Market Insights' in content:
                            print("✅ AI content found in report")
                        else:
                            print("⚠️ AI content not found in report")
                            
            else:
                print("❌ Failed to generate report")
                
        except Exception as e:
            print(f"❌ Error generating report: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 DEEPSEEK AI INTEGRATION TEST")
    print("=" * 60)
    
    asyncio.run(test_deepseek_integration())
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60) 