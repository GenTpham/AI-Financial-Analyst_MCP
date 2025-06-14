"""
AI Financial Analyst - FINAL COMPREHENSIVE DEMO
Complete showcase of AI-enhanced financial analysis system
"""

import asyncio
import os
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dotenv import load_dotenv

# Load environment
load_dotenv()

class ComprehensiveAIFinancialAnalyst:
    """Complete AI-Enhanced Financial Analysis System"""
    
    def __init__(self):
        self.ai_enabled = False
        self.ai_client = None
        self._setup_ai_client()
        print("🚀 AI Financial Analyst System Initialized")
        
    def _setup_ai_client(self):
        """Setup Deepseek AI client"""
        try:
            from openai import AsyncOpenAI
            
            deepseek_key = os.getenv('DEEPSEEK_API_KEY')
            if deepseek_key and deepseek_key != 'your_deepseek_api_key_here':
                self.ai_client = AsyncOpenAI(
                    api_key=deepseek_key,
                    base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
                )
                self.ai_enabled = True
                print(f"✅ AI Engine: Deepseek-AI ({deepseek_key[:15]}...)")
            else:
                print("⚠️ AI Engine: Advanced Rule-Based (Fallback Mode)")
                
        except Exception as e:
            print(f"⚠️ AI Engine: Rule-Based Fallback ({str(e)[:50]}...)")
            self.ai_enabled = False
    
    async def complete_analysis(self, symbol: str):
        """Perform complete AI-enhanced analysis"""
        print(f"\n{'='*70}")
        print(f"🎯 COMPLETE AI ANALYSIS: {symbol}")
        print(f"{'='*70}")
        
        try:
            # Step 1: Data Retrieval
            print("📊 Step 1: Data Retrieval...")
            data = await self._fetch_and_process_data(symbol)
            if not data:
                return None
                
            # Step 2: Technical Analysis
            print("🔍 Step 2: Technical Analysis...")
            tech_analysis = await self._technical_analysis(data)
            
            # Step 3: Risk Analysis
            print("⚠️ Step 3: Risk Analysis...")
            risk_analysis = await self._risk_analysis(data)
            
            # Step 4: AI Market Insights
            print("🤖 Step 4: AI Market Insights...")
            ai_insights = await self._get_ai_insights(symbol, tech_analysis, risk_analysis)
            
            # Step 5: AI Investment Recommendations
            print("💡 Step 5: AI Investment Recommendations...")
            recommendations = await self._get_ai_recommendations(symbol, tech_analysis, risk_analysis, ai_insights)
            
            # Step 6: Advanced Visualization
            print("📊 Step 6: Advanced Visualization...")
            chart_file = await self._create_advanced_chart(symbol, data, tech_analysis)
            
            # Step 7: AI-Enhanced Report
            print("📄 Step 7: AI-Enhanced Report Generation...")
            report_file = await self._generate_ai_report(symbol, tech_analysis, risk_analysis, ai_insights, recommendations)
            
            return {
                'symbol': symbol,
                'technical_analysis': tech_analysis,
                'risk_analysis': risk_analysis,
                'ai_insights': ai_insights,
                'recommendations': recommendations,
                'chart_file': chart_file,
                'report_file': report_file,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Analysis failed for {symbol}: {e}")
            return None
    
    async def _fetch_and_process_data(self, symbol: str):
        """Fetch and process stock data"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1y")  # 1 year of data
            
            if not data.empty:
                print(f"   ✅ Retrieved {len(data)} days of historical data")
                return data
            else:
                print("   ❌ No data available")
                return None
                
        except Exception as e:
            print(f"   ❌ Data retrieval error: {e}")
            return None
    
    async def _technical_analysis(self, data):
        """Comprehensive technical analysis"""
        df = data.copy()
        
        # Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        
        # Stochastic Oscillator
        low_min = df['Low'].rolling(window=14).min()
        high_max = df['High'].rolling(window=14).max()
        df['%K'] = 100 * ((df['Close'] - low_min) / (high_max - low_min))
        df['%D'] = df['%K'].rolling(window=3).mean()
        
        current = df.iloc[-1]
        
        # Advanced signals
        signals = []
        
        # Trend Analysis
        if current['Close'] > current['SMA_20'] > current['SMA_50'] > current['SMA_200']:
            signals.append("📈 Strong uptrend (All MAs aligned)")
            trend_strength = "Very Strong Bullish"
        elif current['Close'] > current['SMA_20'] > current['SMA_50']:
            signals.append("📈 Moderate uptrend")
            trend_strength = "Moderate Bullish"
        elif current['Close'] < current['SMA_20'] < current['SMA_50'] < current['SMA_200']:
            signals.append("📉 Strong downtrend (All MAs aligned)")
            trend_strength = "Very Strong Bearish"
        elif current['Close'] < current['SMA_20'] < current['SMA_50']:
            signals.append("📉 Moderate downtrend")
            trend_strength = "Moderate Bearish"
        else:
            signals.append("🔄 Sideways/Consolidation")
            trend_strength = "Neutral"
        
        # RSI Analysis
        rsi_val = current['RSI']
        if rsi_val > 80:
            signals.append("🔴 Extremely overbought (RSI > 80)")
        elif rsi_val > 70:
            signals.append("⚠️ Overbought territory (RSI > 70)")
        elif rsi_val < 20:
            signals.append("🟢 Extremely oversold (RSI < 20)")
        elif rsi_val < 30:
            signals.append("💡 Oversold territory (RSI < 30)")
        else:
            signals.append("✅ RSI in neutral zone")
        
        # MACD Analysis
        if current['MACD'] > current['MACD_Signal'] and current['MACD_Histogram'] > 0:
            signals.append("📈 MACD bullish momentum")
        elif current['MACD'] < current['MACD_Signal'] and current['MACD_Histogram'] < 0:
            signals.append("📉 MACD bearish momentum")
        else:
            signals.append("🔄 MACD mixed signals")
        
        # Bollinger Bands
        if current['Close'] > current['BB_Upper']:
            signals.append("⚠️ Price above upper Bollinger Band")
        elif current['Close'] < current['BB_Lower']:
            signals.append("💡 Price below lower Bollinger Band")
        else:
            signals.append("✅ Price within Bollinger Bands")
        
        print(f"   ✅ {len(signals)} technical signals identified")
        
        return {
            'current_price': current['Close'],
            'sma_20': current['SMA_20'],
            'sma_50': current['SMA_50'],
            'sma_200': current['SMA_200'],
            'rsi': current['RSI'],
            'macd': current['MACD'],
            'macd_signal': current['MACD_Signal'],
            'bb_position': 'Upper' if current['Close'] > current['BB_Upper'] else 'Lower' if current['Close'] < current['BB_Lower'] else 'Middle',
            'stochastic_k': current['%K'],
            'stochastic_d': current['%D'],
            'signals': signals,
            'trend_strength': trend_strength,
            'data': df
        }
    
    async def _risk_analysis(self, data):
        """Comprehensive risk analysis"""
        returns = data['Close'].pct_change().dropna()
        
        # Basic metrics
        volatility_daily = returns.std()
        volatility_annual = volatility_daily * np.sqrt(252)
        mean_return_annual = returns.mean() * 252
        
        # Sharpe ratio
        risk_free_rate = 0.02
        sharpe_ratio = (mean_return_annual - risk_free_rate) / volatility_annual if volatility_annual > 0 else 0
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative / running_max - 1)
        max_drawdown = drawdown.min()
        
        # Value at Risk
        var_95 = np.percentile(returns, 5)
        var_99 = np.percentile(returns, 1)
        
        # Beta calculation (using SPY as market proxy)
        try:
            spy = yf.Ticker("SPY")
            spy_data = spy.history(period="1y")
            spy_returns = spy_data['Close'].pct_change().dropna()
            
            # Align data
            common_index = returns.index.intersection(spy_returns.index)
            if len(common_index) > 50:
                aligned_returns = returns.loc[common_index]
                aligned_spy = spy_returns.loc[common_index]
                beta = np.cov(aligned_returns, aligned_spy)[0][1] / np.var(aligned_spy)
            else:
                beta = 1.0
        except:
            beta = 1.0
        
        # Risk rating
        if volatility_annual < 0.15:
            risk_rating = "Low"
        elif volatility_annual < 0.25:
            risk_rating = "Moderate"
        elif volatility_annual < 0.4:
            risk_rating = "High"
        else:
            risk_rating = "Very High"
        
        print(f"   ✅ Risk rating: {risk_rating} (Volatility: {volatility_annual:.1%})")
        
        return {
            'volatility_daily': volatility_daily,
            'volatility_annual': volatility_annual,
            'mean_return_annual': mean_return_annual,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'var_95': var_95,
            'var_99': var_99,
            'beta': beta,
            'risk_rating': risk_rating
        }
    
    async def _get_ai_insights(self, symbol: str, tech_analysis: dict, risk_analysis: dict):
        """Get AI market insights"""
        if self.ai_enabled:
            try:
                prompt = f"""
Phân tích thị trường chuyên sâu cho {symbol}:

TECHNICAL ANALYSIS:
- Giá hiện tại: ${tech_analysis['current_price']:.2f}
- Trend: {tech_analysis['trend_strength']}
- RSI: {tech_analysis['rsi']:.1f}
- MACD: {tech_analysis['macd']:.3f}
- Bollinger Position: {tech_analysis['bb_position']}

RISK METRICS:
- Volatility: {risk_analysis['volatility_annual']:.1%}
- Sharpe Ratio: {risk_analysis['sharpe_ratio']:.2f}
- Max Drawdown: {risk_analysis['max_drawdown']:.1%}
- Beta: {risk_analysis['beta']:.2f}
- Risk Rating: {risk_analysis['risk_rating']}

SIGNALS:
{chr(10).join(f"• {signal}" for signal in tech_analysis['signals'][:5])}

Hãy đưa ra phân tích thị trường chuyên nghiệp với:
1. Tổng quan thị trường và sentiment
2. Các yếu tố chính ảnh hưởng giá
3. Cơ hội và rủi ro
4. Outlook ngắn và trung hạn
                """
                
                response = await self.ai_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "Bạn là chuyên gia phân tích tài chính senior với 20+ năm kinh nghiệm."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                
                ai_response = response.choices[0].message.content
                print(f"   ✅ AI insights generated (Deepseek)")
                
                return {
                    'source': 'Deepseek-AI',
                    'insights': ai_response,
                    'confidence': 'High'
                }
                
            except Exception as e:
                print(f"   ⚠️ AI API error, using fallback: {str(e)[:50]}...")
        
        # Fallback analysis
        insights = f"""
🏢 MARKET ANALYSIS FOR {symbol}:

📊 CURRENT SITUATION:
• Price: ${tech_analysis['current_price']:.2f}
• Trend: {tech_analysis['trend_strength']}
• Volatility: {risk_analysis['volatility_annual']:.1%} ({risk_analysis['risk_rating']} risk)
• Performance: Sharpe ratio {risk_analysis['sharpe_ratio']:.2f}

🎯 KEY FACTORS:
• Technical momentum shows {tech_analysis['trend_strength'].lower()} pattern
• RSI at {tech_analysis['rsi']:.1f} indicates {'overbought' if tech_analysis['rsi'] > 70 else 'oversold' if tech_analysis['rsi'] < 30 else 'neutral'} conditions
• Risk level is {risk_analysis['risk_rating'].lower()} with {risk_analysis['volatility_annual']:.1%} annual volatility
• Beta of {risk_analysis['beta']:.2f} shows {'higher' if risk_analysis['beta'] > 1.2 else 'lower' if risk_analysis['beta'] < 0.8 else 'similar'} market sensitivity

💡 PROFESSIONAL ASSESSMENT:
Based on comprehensive technical and risk analysis, {symbol} presents {len(tech_analysis['signals'])} key signals.
The combination of {tech_analysis['trend_strength'].lower()} trend and {risk_analysis['risk_rating'].lower()} risk profile
suggests {'active monitoring' if risk_analysis['risk_rating'] == 'High' else 'suitable for consideration'} for portfolio inclusion.
        """
        
        print(f"   ✅ Advanced rule-based insights generated")
        
        return {
            'source': 'Advanced-Rule-Based',
            'insights': insights,
            'confidence': 'Medium-High'
        }
    
    async def _get_ai_recommendations(self, symbol: str, tech_analysis: dict, risk_analysis: dict, ai_insights: dict):
        """Generate AI investment recommendations"""
        
        # Scoring system
        score = 0
        
        # Technical score
        if 'Strong' in tech_analysis['trend_strength'] and 'Bullish' in tech_analysis['trend_strength']:
            score += 3
        elif 'Moderate' in tech_analysis['trend_strength'] and 'Bullish' in tech_analysis['trend_strength']:
            score += 2
        elif 'Bearish' in tech_analysis['trend_strength']:
            score -= 2
        
        # RSI score
        rsi = tech_analysis['rsi']
        if rsi < 30:
            score += 2
        elif rsi > 70:
            score -= 2
        
        # Risk score
        if risk_analysis['sharpe_ratio'] > 1:
            score += 2
        elif risk_analysis['sharpe_ratio'] < 0:
            score -= 2
        
        if risk_analysis['risk_rating'] == 'Low':
            score += 1
        elif risk_analysis['risk_rating'] == 'Very High':
            score -= 2
        
        # Final recommendation
        if score >= 4:
            decision = "STRONG BUY"
            reasoning = "Multiple positive technical and risk indicators align"
            risk_level = "Moderate"
        elif score >= 2:
            decision = "BUY"
            reasoning = "Favorable technical outlook with acceptable risk"
            risk_level = "Moderate"
        elif score <= -4:
            decision = "STRONG SELL"
            reasoning = "Multiple negative indicators suggest high risk"
            risk_level = "High"
        elif score <= -2:
            decision = "SELL"
            reasoning = "Unfavorable risk-return profile"
            risk_level = "High"
        else:
            decision = "HOLD"
            reasoning = "Mixed signals suggest cautious approach"
            risk_level = "Moderate"
        
        print(f"   ✅ Investment recommendation: {decision}")
        
        return {
            'decision': decision,
            'reasoning': reasoning,
            'risk_level': risk_level,
            'confidence': ai_insights['confidence'],
            'score': score,
            'target_horizon': '3-6 months',
            'generated_at': datetime.now().isoformat()
        }
    
    async def _create_advanced_chart(self, symbol: str, data: pd.DataFrame, tech_analysis: dict):
        """Create advanced visualization"""
        df = tech_analysis['data']
        
        fig = make_subplots(
            rows=5, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.02,
            subplot_titles=(
                f'{symbol} - Price Action & Technical Indicators',
                'RSI (14)',
                'MACD',
                'Stochastic Oscillator',
                'Volume'
            ),
            row_heights=[0.4, 0.15, 0.15, 0.15, 0.15]
        )
        
        # Main chart with candlesticks and indicators
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name=symbol
        ), row=1, col=1)
        
        # Moving averages
        for ma, color in [('SMA_20', 'orange'), ('SMA_50', 'blue'), ('SMA_200', 'red')]:
            fig.add_trace(go.Scatter(
                x=df.index, y=df[ma], line=dict(color=color, width=1),
                name=ma
            ), row=1, col=1)
        
        # Bollinger Bands
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Upper'],
            line=dict(color='gray', width=1, dash='dash'),
            name='BB Upper', showlegend=False
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['BB_Lower'],
            line=dict(color='gray', width=1, dash='dash'),
            name='BB Lower', fill='tonexty',
            fillcolor='rgba(128,128,128,0.1)', showlegend=False
        ), row=1, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(
            x=df.index, y=df['RSI'],
            line=dict(color='purple'), name='RSI'
        ), row=2, col=1)
        
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MACD'],
            line=dict(color='blue'), name='MACD'
        ), row=3, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MACD_Signal'],
            line=dict(color='red'), name='Signal'
        ), row=3, col=1)
        
        # Stochastic
        fig.add_trace(go.Scatter(
            x=df.index, y=df['%K'],
            line=dict(color='blue'), name='%K'
        ), row=4, col=1)
        
        fig.add_trace(go.Scatter(
            x=df.index, y=df['%D'],
            line=dict(color='red'), name='%D'
        ), row=4, col=1)
        
        fig.add_hline(y=80, line_dash="dash", line_color="red", row=4, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="green", row=4, col=1)
        
        # Volume
        fig.add_trace(go.Bar(
            x=df.index, y=df['Volume'],
            name='Volume', marker_color='lightblue'
        ), row=5, col=1)
        
        fig.update_layout(
            title=f"{symbol} - AI-Enhanced Technical Analysis",
            height=1000, showlegend=True,
            template="plotly_white"
        )
        
        chart_file = f"output/charts/{symbol.lower()}_ai_enhanced_analysis.html"
        os.makedirs("output/charts", exist_ok=True)
        fig.write_html(chart_file)
        
        print(f"   ✅ Advanced chart saved: {chart_file}")
        return chart_file
    
    async def _generate_ai_report(self, symbol: str, tech_analysis: dict, risk_analysis: dict, ai_insights: dict, recommendations: dict):
        """Generate comprehensive AI-enhanced report"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Financial Analysis: {symbol}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .header h1 {{ color: #2c3e50; margin: 0; font-size: 2.5em; }}
        .header .subtitle {{ color: #7f8c8d; font-size: 1.2em; margin-top: 10px; }}
        .ai-badge {{ background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 8px 16px; border-radius: 20px; font-size: 0.9em; display: inline-block; margin-top: 10px; }}
        .section {{ margin: 30px 0; padding: 25px; border-radius: 10px; }}
        .summary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .technical {{ background: #f8f9fa; border-left: 5px solid #3498db; }}
        .risk {{ background: #fff5f5; border-left: 5px solid #e74c3c; }}
        .ai-insights {{ background: #f0f8ff; border-left: 5px solid #667eea; }}
        .recommendations {{ background: #f8fff8; border-left: 5px solid #27ae60; }}
        .metric {{ display: inline-block; margin: 15px 20px 15px 0; padding: 15px 20px; border-radius: 8px; color: white; min-width: 120px; text-align: center; }}
        .metric.price {{ background: #3498db; }}
        .metric.positive {{ background: #27ae60; }}
        .metric.negative {{ background: #e74c3c; }}
        .metric.neutral {{ background: #95a5a6; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 15px; text-align: left; }}
        th {{ background: #34495e; color: white; }}
        .signal {{ background: #f8f9fa; margin: 8px 0; padding: 12px; border-left: 4px solid #3498db; border-radius: 4px; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 2px solid #ecf0f1; color: #7f8c8d; }}
        .recommendation-box {{ background: white; padding: 20px; border-radius: 10px; border: 3px solid; }}
        .strong-buy {{ border-color: #27ae60; }}
        .buy {{ border-color: #2ecc71; }}
        .hold {{ border-color: #f39c12; }}
        .sell {{ border-color: #e67e22; }}
        .strong-sell {{ border-color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI Financial Analysis</h1>
            <div class="subtitle">Comprehensive Analysis for {symbol}</div>
            <div class="ai-badge">Powered by {ai_insights['source']} | Confidence: {ai_insights['confidence']}</div>
        </div>
        
        <div class="section summary">
            <h2>📊 Executive Summary</h2>
            <div class="metric price">Current Price<br/>${tech_analysis['current_price']:.2f}</div>
            <div class="metric {'positive' if recommendations['decision'] in ['BUY', 'STRONG BUY'] else 'negative' if recommendations['decision'] in ['SELL', 'STRONG SELL'] else 'neutral'}">
                Recommendation<br/>{recommendations['decision']}
            </div>
            <div class="metric {'positive' if risk_analysis['risk_rating'] == 'Low' else 'negative' if risk_analysis['risk_rating'] == 'Very High' else 'neutral'}">
                Risk Level<br/>{risk_analysis['risk_rating']}
            </div>
            <div class="metric {'positive' if tech_analysis['rsi'] < 30 else 'negative' if tech_analysis['rsi'] > 70 else 'neutral'}">
                RSI<br/>{tech_analysis['rsi']:.1f}
            </div>
        </div>
        
        <div class="section technical">
            <h2>🔍 Technical Analysis</h2>
            <table>
                <tr><th>Indicator</th><th>Current Value</th><th>Signal</th></tr>
                <tr><td>Price</td><td>${tech_analysis['current_price']:.2f}</td><td>{tech_analysis['trend_strength']}</td></tr>
                <tr><td>SMA 20</td><td>${tech_analysis['sma_20']:.2f}</td><td>{'Above' if tech_analysis['current_price'] > tech_analysis['sma_20'] else 'Below'}</td></tr>
                <tr><td>SMA 50</td><td>${tech_analysis['sma_50']:.2f}</td><td>{'Above' if tech_analysis['current_price'] > tech_analysis['sma_50'] else 'Below'}</td></tr>
                <tr><td>RSI (14)</td><td>{tech_analysis['rsi']:.1f}</td><td>{'Overbought' if tech_analysis['rsi'] > 70 else 'Oversold' if tech_analysis['rsi'] < 30 else 'Neutral'}</td></tr>
                <tr><td>MACD</td><td>{tech_analysis['macd']:.3f}</td><td>{'Bullish' if tech_analysis['macd'] > tech_analysis['macd_signal'] else 'Bearish'}</td></tr>
                <tr><td>Bollinger Position</td><td>{tech_analysis['bb_position']}</td><td>{'Resistance' if tech_analysis['bb_position'] == 'Upper' else 'Support' if tech_analysis['bb_position'] == 'Lower' else 'Normal'}</td></tr>
            </table>
            
            <h3>Technical Signals</h3>
        """
        
        for signal in tech_analysis['signals']:
            html_content += f'<div class="signal">{signal}</div>'
        
        html_content += f"""
        </div>
        
        <div class="section risk">
            <h2>⚠️ Risk Analysis</h2>
            <table>
                <tr><th>Risk Metric</th><th>Value</th><th>Assessment</th></tr>
                <tr><td>Annual Volatility</td><td>{risk_analysis['volatility_annual']:.1%}</td><td>{risk_analysis['risk_rating']} Risk</td></tr>
                <tr><td>Sharpe Ratio</td><td>{risk_analysis['sharpe_ratio']:.2f}</td><td>{'Excellent' if risk_analysis['sharpe_ratio'] > 2 else 'Good' if risk_analysis['sharpe_ratio'] > 1 else 'Fair' if risk_analysis['sharpe_ratio'] > 0 else 'Poor'}</td></tr>
                <tr><td>Maximum Drawdown</td><td>{risk_analysis['max_drawdown']:.1%}</td><td>{'High Risk' if risk_analysis['max_drawdown'] < -0.3 else 'Moderate Risk' if risk_analysis['max_drawdown'] < -0.15 else 'Low Risk'}</td></tr>
                <tr><td>Beta</td><td>{risk_analysis['beta']:.2f}</td><td>{'High Volatility' if risk_analysis['beta'] > 1.5 else 'Market-like' if risk_analysis['beta'] > 0.8 else 'Defensive'}</td></tr>
                <tr><td>VaR (95%)</td><td>{risk_analysis['var_95']:.1%}</td><td>Daily Risk Estimate</td></tr>
            </table>
        </div>
        
        <div class="section ai-insights">
            <h2>🤖 AI Market Insights</h2>
            <div style="background: white; padding: 20px; border-radius: 8px; white-space: pre-wrap; line-height: 1.6;">
{ai_insights['insights']}
            </div>
        </div>
        
        <div class="section recommendations">
            <h2>💡 AI Investment Recommendations</h2>
            <div class="recommendation-box {recommendations['decision'].lower().replace(' ', '-')}">
                <h3>🎯 Investment Decision: {recommendations['decision']}</h3>
                <p><strong>Reasoning:</strong> {recommendations['reasoning']}</p>
                <p><strong>Risk Level:</strong> {recommendations['risk_level']}</p>
                <p><strong>Time Horizon:</strong> {recommendations['target_horizon']}</p>
                <p><strong>Confidence Level:</strong> {recommendations['confidence']}</p>
                <p><strong>Analysis Score:</strong> {recommendations['score']}/10</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>AI Financial Analyst System</strong> | Generated: {timestamp}</p>
            <p>⚠️ This analysis is for informational purposes only and should not be considered as financial advice.</p>
            <p>Always consult with a qualified financial advisor before making investment decisions.</p>
        </div>
    </div>
</body>
</html>
        """
        
        report_file = f"output/reports/{symbol.lower()}_ai_enhanced_report.html"
        os.makedirs("output/reports", exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"   ✅ AI-enhanced report saved: {report_file}")
        return report_file

async def main():
    """Main comprehensive demo"""
    print("🚀 AI FINANCIAL ANALYST - COMPLETE SYSTEM DEMO")
    print("=" * 80)
    
    analyst = ComprehensiveAIFinancialAnalyst()
    
    # Analyze multiple stocks
    symbols = ["AAPL", "GOOGL", "TSLA"]
    results = []
    
    for symbol in symbols:
        result = await analyst.complete_analysis(symbol)
        if result:
            results.append(result)
            
            print(f"\n✅ ANALYSIS COMPLETE FOR {symbol}")
            print(f"📊 Chart: {result['chart_file']}")
            print(f"📄 Report: {result['report_file']}")
            print(f"💡 Recommendation: {result['recommendations']['decision']}")
            print(f"⚠️ Risk: {result['risk_analysis']['risk_rating']}")
    
    print(f"\n{'='*80}")
    print("🎉 COMPLETE SYSTEM DEMO FINISHED!")
    print(f"\n📈 Analysis Summary:")
    print(f"├── Stocks Analyzed: {len(results)}")
    print(f"├── Charts Generated: {len([r for r in results if r['chart_file']])}")
    print(f"├── Reports Created: {len([r for r in results if r['report_file']])}")
    print(f"└── AI Engine: {results[0]['ai_insights']['source'] if results else 'N/A'}")
    
    print(f"\n📁 Output Locations:")
    print(f"├── Charts: output/charts/")
    print(f"└── Reports: output/reports/")
    
    print(f"\n🌐 Open HTML files in your browser to view detailed analysis")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main()) 