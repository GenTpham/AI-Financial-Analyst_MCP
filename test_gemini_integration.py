"""
Test Gemini AI Integration - Kiểm tra tích hợp Gemini AI
"""

import asyncio
import os
import sys
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

# Load environment from correct path
load_dotenv('config/api_keys.env')

from agents.gemini_ai_client import GeminiAIClient

async def test_gemini_basic():
    """Test basic Gemini AI functionality"""
    print("🧪 TESTING GEMINI AI INTEGRATION")
    print("=" * 60)
    
    # Initialize client
    client = GeminiAIClient()
    
    if not client.is_enabled:
        print("❌ Gemini AI client not enabled")
        print("Please check your GEMINI_API_KEY in config/api_keys.env")
        return False
    
    print("✅ Gemini AI client initialized successfully")
    return True

async def test_market_insights():
    """Test market insights generation"""
    print("\n📊 TESTING MARKET INSIGHTS GENERATION")
    print("-" * 50)
    
    client = GeminiAIClient()
    
    if not client.is_enabled:
        print("❌ Gemini AI not available")
        return
    
    # Get real data for AAPL
    try:
        ticker = yf.Ticker("AAPL")
        data = ticker.history(period="3mo")
        
        if data.empty:
            print("❌ No data available for AAPL")
            return
        
        # Calculate basic metrics
        current_price = data['Close'].iloc[-1]
        returns = data['Close'].pct_change().dropna()
        volatility_annual = returns.std() * np.sqrt(252)
        
        # RSI calculation
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # Sharpe ratio
        mean_return = returns.mean() * 252
        sharpe_ratio = (mean_return - 0.02) / volatility_annual
        
        # Prepare analysis data
        analysis_data = {
            'price_analysis': {
                'current_price': current_price
            },
            'technical_analysis': {
                'rsi': {'current': rsi},
                'macd': {'macd': 0.5}
            },
            'risk_analysis': {
                'basic_metrics': {'volatility_annual': volatility_annual},
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': {'max_drawdown': -0.15}
            }
        }
        
        print(f"📈 Testing with AAPL data:")
        print(f"   Current Price: ${current_price:.2f}")
        print(f"   RSI: {rsi:.1f}")
        print(f"   Volatility: {volatility_annual:.2%}")
        print(f"   Sharpe Ratio: {sharpe_ratio:.2f}")
        
        print("\n🤖 Generating AI insights...")
        
        # Generate insights
        insights = await client.generate_market_insights("AAPL", analysis_data)
        
        if insights.get('enabled', False):
            print("✅ AI Insights generated successfully!")
            print(f"Source: {insights.get('source', 'N/A')}")
            print(f"Market Sentiment: {insights.get('market_sentiment', 'N/A')}")
            print(f"Key Factors: {len(insights.get('key_factors', []))} identified")
            
            print("\n📝 AI ANALYSIS:")
            print("=" * 50)
            print(insights.get('insights', 'No insights available'))
            print("=" * 50)
            
            if insights.get('key_factors'):
                print(f"\n🔑 KEY FACTORS:")
                for i, factor in enumerate(insights['key_factors'], 1):
                    print(f"{i}. {factor}")
        else:
            print("❌ Failed to generate AI insights")
            print(f"Error: {insights.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error in market insights test: {e}")

async def test_investment_recommendation():
    """Test investment recommendation generation"""
    print("\n💡 TESTING INVESTMENT RECOMMENDATIONS")
    print("-" * 50)
    
    client = GeminiAIClient()
    
    if not client.is_enabled:
        print("❌ Gemini AI not available")
        return
    
    # Sample analysis data
    analysis_data = {
        'price_analysis': {'current_price': 150.0},
        'technical_analysis': {
            'rsi': {'current': 45.0},
            'macd': {'macd': 0.2}
        },
        'risk_analysis': {
            'basic_metrics': {'volatility_annual': 0.25},
            'sharpe_ratio': 1.2,
            'max_drawdown': {'max_drawdown': -0.12}
        }
    }
    
    print("🤖 Generating investment recommendation...")
    
    try:
        recommendation = await client.generate_investment_recommendation("AAPL", analysis_data)
        
        if recommendation.get('enabled', False):
            print("✅ Investment recommendation generated!")
            print(f"Decision: {recommendation.get('decision', 'N/A')}")
            print(f"Risk Level: {recommendation.get('risk_level', 'N/A')}")
            print(f"Source: {recommendation.get('source', 'N/A')}")
            
            print("\n📋 DETAILED RECOMMENDATION:")
            print("=" * 50)
            print(recommendation.get('reasoning', 'No reasoning available'))
            print("=" * 50)
        else:
            print("❌ Failed to generate recommendation")
            print(f"Error: {recommendation.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error in recommendation test: {e}")

async def main():
    """Main test function"""
    print("🚀 GEMINI AI INTEGRATION TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test basic functionality
    basic_ok = await test_gemini_basic()
    
    if basic_ok:
        # Test market insights
        await test_market_insights()
        
        # Test investment recommendations
        await test_investment_recommendation()
    
    print("\n" + "=" * 60)
    print("🎉 TEST SUITE COMPLETED!")
    print(f"Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main()) 