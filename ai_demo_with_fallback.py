"""
AI Financial Analyst - Demo with AI Integration & Fallback
Showcases AI capabilities with smart fallback when API unavailable
"""

import asyncio
import os
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load environment
load_dotenv()

class AIFinancialAnalyst:
    """AI-Enhanced Financial Analyst with Fallback"""
    
    def __init__(self):
        self.ai_enabled = False
        self.ai_client = None
        self._setup_ai_client()
        
    def _setup_ai_client(self):
        """Setup Deepseek AI client"""
        try:
            from openai import AsyncOpenAI
            
            deepseek_key = os.getenv('DEEPSEEK_API_KEY')
            deepseek_base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
            
            if deepseek_key and deepseek_key != 'your_deepseek_api_key_here':
                self.ai_client = AsyncOpenAI(
                    api_key=deepseek_key,
                    base_url=deepseek_base_url
                )
                self.ai_enabled = True
                print(f"✅ Deepseek AI client initialized: {deepseek_key[:20]}...")
            else:
                print("⚠️ Deepseek API key not found, using fallback mode")
                
        except Exception as e:
            print(f"⚠️ AI client setup error: {e}")
            self.ai_enabled = False
    
    async def get_ai_market_insights(self, symbol: str, analysis_data: dict):
        """Get AI market insights with fallback"""
        print(f"\n🤖 Generating AI Market Insights for {symbol}...")
        
        if not self.ai_enabled:
            return self._fallback_market_insights(symbol, analysis_data)
        
        try:
            # Create comprehensive prompt
            prompt = self._create_market_analysis_prompt(symbol, analysis_data)
            
            # Call Deepseek API
            response = await self.ai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "Bạn là chuyên gia phân tích thị trường tài chính hàng đầu với 20+ năm kinh nghiệm. Hãy đưa ra phân tích chuyên sâu, khách quan và có căn cứ."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                'enabled': True,
                'source': 'Deepseek-AI',
                'insights': ai_response,
                'market_sentiment': self._extract_sentiment(ai_response),
                'key_factors': self._extract_key_factors(ai_response),
                'confidence': 'High',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ AI API error: {e}")
            print("🔄 Falling back to advanced rule-based analysis...")
            return self._fallback_market_insights(symbol, analysis_data)
    
    def _create_market_analysis_prompt(self, symbol: str, data: dict):
        """Create comprehensive analysis prompt"""
        current_price = data.get('current_price', 0)
        rsi = data.get('rsi', 50)
        volatility = data.get('volatility_annual', 0.2)
        sharpe = data.get('sharpe_ratio', 0)
        trend = data.get('trend', 'sideways')
        
        return f"""
Phân tích thị trường chuyên sâu cho cổ phiếu {symbol}:

THÔNG TIN TÀI CHÍNH:
- Giá hiện tại: ${current_price:.2f}
- RSI: {rsi:.1f} ({'Quá mua' if rsi > 70 else 'Quá bán' if rsi < 30 else 'Bình thường'})
- Volatility hàng năm: {volatility:.1%}
- Sharpe Ratio: {sharpe:.2f}
- Xu hướng hiện tại: {trend}

YÊU CẦU PHÂN TÍCH:
1. Đánh giá tình hình thị trường tổng quan
2. Phân tích sentiment và tâm lý nhà đầu tư
3. Nhận diện 3-5 yếu tố chính ảnh hưởng giá
4. Dự báo xu hướng ngắn hạn (1-3 tháng)
5. Khuyến nghị đầu tư cụ thể (MUA/BÁN/GIỮ)
6. Mức giá mục tiêu và điểm dừng lỗ
7. Thời gian nắm giữ khuyến nghị

Trả lời bằng tiếng Việt, chuyên nghiệp và có căn cứ rõ ràng.
        """
    
    def _fallback_market_insights(self, symbol: str, data: dict):
        """Advanced rule-based market insights when AI unavailable"""
        current_price = data.get('current_price', 0)
        rsi = data.get('rsi', 50)
        volatility = data.get('volatility_annual', 0.2)
        sharpe = data.get('sharpe_ratio', 0)
        
        # Advanced analysis logic
        market_conditions = []
        key_factors = []
        
        # RSI Analysis
        if rsi > 75:
            market_conditions.append("Thị trường trong trạng thái quá mua nghiêm trọng")
            key_factors.append(f"RSI cao ({rsi:.1f}) cho thấy áp lực bán tăng")
        elif rsi > 70:
            market_conditions.append("Thị trường có dấu hiệu quá mua")
            key_factors.append(f"RSI ({rsi:.1f}) gần vùng quá mua")
        elif rsi < 25:
            market_conditions.append("Thị trường trong trạng thái quá bán nghiêm trọng")
            key_factors.append(f"RSI thấp ({rsi:.1f}) tạo cơ hội mua vào")
        elif rsi < 30:
            market_conditions.append("Thị trường có dấu hiệu quá bán")
            key_factors.append(f"RSI ({rsi:.1f}) cho thấy áp lực mua tăng")
        else:
            market_conditions.append("RSI trong vùng cân bằng")
            key_factors.append(f"RSI ({rsi:.1f}) cho thấy thị trường cân bằng")
        
        # Volatility Analysis
        if volatility > 0.4:
            market_conditions.append("Độ biến động cao, rủi ro lớn")
            key_factors.append(f"Volatility {volatility:.1%} cao hơn bình thường")
        elif volatility > 0.25:
            market_conditions.append("Độ biến động trung bình đến cao")
            key_factors.append(f"Volatility {volatility:.1%} ở mức trung bình cao")
        else:
            market_conditions.append("Thị trường tương đối ổn định")
            key_factors.append(f"Volatility thấp {volatility:.1%} cho thấy ổn định")
        
        # Sharpe Ratio Analysis
        if sharpe > 1.5:
            market_conditions.append("Hiệu suất đầu tư rất tốt")
            key_factors.append(f"Sharpe ratio cao ({sharpe:.2f}) cho thấy hiệu quả vượt trội")
        elif sharpe > 1:
            market_conditions.append("Hiệu suất đầu tư tốt")
            key_factors.append(f"Sharpe ratio {sharpe:.2f} cho thấy hiệu quả tốt")
        elif sharpe > 0:
            market_conditions.append("Hiệu suất đầu tư chấp nhận được")
            key_factors.append(f"Sharpe ratio dương ({sharpe:.2f}) nhưng chưa ấn tượng")
        else:
            market_conditions.append("Hiệu suất đầu tư kém")
            key_factors.append(f"Sharpe ratio âm ({sharpe:.2f}) cho thấy rủi ro cao")
        
        # Recommendation Logic
        score = 0
        if rsi < 30: score += 2
        elif rsi > 70: score -= 2
        
        if volatility < 0.2: score += 1
        elif volatility > 0.4: score -= 1
        
        if sharpe > 1: score += 2
        elif sharpe < 0: score -= 2
        
        if score >= 3:
            recommendation = "MUA"
            reasoning = "Các chỉ số kỹ thuật và rủi ro đều tích cực"
        elif score <= -3:
            recommendation = "BÁN"
            reasoning = "Nhiều tín hiệu tiêu cực, nên giảm tỷ trọng"
        else:
            recommendation = "GIỮ"
            reasoning = "Thị trường có tín hiệu trái chiều, nên quan sát thêm"
        
        # Generate comprehensive insights
        insights = f"""
🏢 TÌNH HÌNH THỊ TRƯỜNG TỔNG QUAN CHO {symbol}:

📊 Phân tích hiện tại:
{chr(10).join(f"• {condition}" for condition in market_conditions)}

🎯 CÁC YẾU TỐ CHÍNH:
{chr(10).join(f"• {factor}" for factor in key_factors)}

💡 ĐÁNH GIÁ CHUYÊN NGHIỆP:
Dựa trên phân tích kỹ thuật toàn diện, {symbol} hiện đang thể hiện {len(key_factors)} yếu tố quan trọng. 
Với giá hiện tại ${current_price:.2f}, cổ phiếu này có độ biến động {volatility:.1%} và RSI {rsi:.1f}.

📈 KHUYẾN NGHỊ ĐẦU TƯ: {recommendation}
Lý do: {reasoning}

⏰ THỜI GIAN KHUYẾN NGHỊ: 
{'Ngắn hạn (1-2 tháng)' if volatility > 0.3 else 'Trung hạn (3-6 tháng)'}

⚠️ LƯU Ý: Đây là phân tích kỹ thuật tự động, nhà đầu tư nên xem xét thêm các yếu tố cơ bản và thị trường chung.
        """
        
        sentiment = 'Tích cực' if score > 0 else 'Tiêu cực' if score < 0 else 'Trung tính'
        
        return {
            'enabled': True,
            'source': 'Advanced-Rule-Based-Analysis',
            'insights': insights,
            'market_sentiment': sentiment,
            'key_factors': key_factors,
            'confidence': 'Medium-High',
            'recommendation': recommendation,
            'generated_at': datetime.now().isoformat()
        }
    
    def _extract_sentiment(self, text: str):
        """Extract sentiment from AI response"""
        text_upper = text.upper()
        positive = ['TÍCH CỰC', 'TĂNG', 'MUA', 'BULLISH', 'TẠI CỰC']
        negative = ['TIÊU CỰC', 'GIẢM', 'BÁN', 'BEARISH', 'RỦI RO']
        
        pos_count = sum(1 for word in positive if word in text_upper)
        neg_count = sum(1 for word in negative if word in text_upper)
        
        if pos_count > neg_count:
            return 'Tích cực'
        elif neg_count > pos_count:
            return 'Tiêu cực'
        else:
            return 'Trung tính'
    
    def _extract_key_factors(self, text: str):
        """Extract key factors from text"""
        lines = text.split('\n')
        factors = []
        
        for line in lines:
            line = line.strip()
            if any(marker in line.lower() for marker in ['•', '-', '1.', '2.', '3.', 'yếu tố', 'nguyên nhân']):
                if len(line) > 10 and len(line) < 150:
                    factors.append(line.lstrip('•-123456789. '))
        
        return factors[:5]

async def demo_ai_analysis():
    """Demo AI-enhanced analysis"""
    print("🚀 AI FINANCIAL ANALYST - ENHANCED DEMO")
    print("=" * 70)
    
    analyst = AIFinancialAnalyst()
    
    # Test with AAPL
    symbol = "AAPL"
    print(f"\n🔍 AI Analysis for {symbol}")
    print("=" * 50)
    
    try:
        # Get basic data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="3mo")
        
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            
            # Calculate basic metrics
            returns = data['Close'].pct_change().dropna()
            volatility_annual = returns.std() * np.sqrt(252)
            
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = (100 - (100 / (1 + rs))).iloc[-1]
            
            # Sharpe ratio
            mean_return = returns.mean() * 252
            sharpe_ratio = (mean_return - 0.02) / volatility_annual
            
            analysis_data = {
                'current_price': current_price,
                'rsi': rsi,
                'volatility_annual': volatility_annual,
                'sharpe_ratio': sharpe_ratio,
                'trend': 'sideways'
            }
            
            # Get AI insights
            ai_insights = await analyst.get_ai_market_insights(symbol, analysis_data)
            
            # Display results
            print(f"\n📊 ANALYSIS RESULTS:")
            print(f"Current Price: ${current_price:.2f}")
            print(f"RSI: {rsi:.1f}")
            print(f"Volatility: {volatility_annual:.1%}")
            print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
            
            print(f"\n🤖 AI INSIGHTS:")
            print(f"Source: {ai_insights['source']}")
            print(f"Confidence: {ai_insights['confidence']}")
            print(f"Market Sentiment: {ai_insights['market_sentiment']}")
            
            if ai_insights.get('recommendation'):
                print(f"Recommendation: {ai_insights['recommendation']}")
            
            print(f"\n📝 DETAILED ANALYSIS:")
            print("=" * 50)
            print(ai_insights['insights'])
            print("=" * 50)
            
            print(f"\n🔑 KEY FACTORS ({len(ai_insights['key_factors'])}):")
            for i, factor in enumerate(ai_insights['key_factors'], 1):
                print(f"{i}. {factor}")
        
        else:
            print("❌ No data available")
            
    except Exception as e:
        print(f"❌ Error in analysis: {e}")

if __name__ == "__main__":
    asyncio.run(demo_ai_analysis()) 