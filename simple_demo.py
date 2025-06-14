"""
AI Financial Analyst - Simple Demo
Showcases all major features without MCP server
"""

import asyncio
import os
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from dotenv import load_dotenv

# Load environment
load_dotenv()

class SimpleFinancialAnalyst:
    """Simplified version of the AI Financial Analyst"""
    
    def __init__(self):
        self.symbol = None
        self.data = None
        
    def fetch_data(self, symbol: str, period: str = "6mo"):
        """Fetch stock data"""
        print(f"📊 Fetching data for {symbol}...")
        
        try:
            ticker = yf.Ticker(symbol)
            self.data = ticker.history(period=period)
            self.symbol = symbol
            
            if not self.data.empty:
                print(f"✅ Retrieved {len(self.data)} days of data")
                return True
            else:
                print("❌ No data retrieved")
                return False
                
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return False
    
    def technical_analysis(self):
        """Perform technical analysis"""
        if self.data is None or self.data.empty:
            return None
            
        print(f"🔍 Performing technical analysis for {self.symbol}...")
        
        df = self.data.copy()
        
        # Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
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
        
        # Current values
        current = df.iloc[-1]
        
        analysis = {
            'current_price': current['Close'],
            'sma_20': current['SMA_20'],
            'sma_50': current['SMA_50'],
            'rsi': current['RSI'],
            'macd': current['MACD'],
            'macd_signal': current['MACD_Signal'],
            'bb_position': 'Upper' if current['Close'] > current['BB_Upper'] else 'Lower' if current['Close'] < current['BB_Lower'] else 'Middle'
        }
        
        # Signals
        signals = []
        
        if current['Close'] > current['SMA_20'] > current['SMA_50']:
            signals.append("📈 Strong bullish trend")
        elif current['Close'] < current['SMA_20'] < current['SMA_50']:
            signals.append("📉 Strong bearish trend")
        else:
            signals.append("🔄 Sideways trend")
            
        if current['RSI'] > 70:
            signals.append("⚠️ Overbought (RSI > 70)")
        elif current['RSI'] < 30:
            signals.append("💡 Oversold (RSI < 30)")
        else:
            signals.append("✅ RSI in normal range")
            
        if current['MACD'] > current['MACD_Signal']:
            signals.append("📈 MACD bullish crossover")
        else:
            signals.append("📉 MACD bearish crossover")
        
        analysis['signals'] = signals
        self.technical_data = df
        
        print("✅ Technical analysis completed")
        return analysis
    
    def risk_analysis(self):
        """Perform risk analysis"""
        if self.data is None or self.data.empty:
            return None
            
        print(f"⚠️ Performing risk analysis for {self.symbol}...")
        
        returns = self.data['Close'].pct_change().dropna()
        
        # Basic metrics
        volatility_daily = returns.std()
        volatility_annual = volatility_daily * np.sqrt(252)
        mean_return_annual = returns.mean() * 252
        
        # Sharpe ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02
        sharpe_ratio = (mean_return_annual - risk_free_rate) / volatility_annual
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative / running_max - 1)
        max_drawdown = drawdown.min()
        
        # Value at Risk (95%)
        var_95 = np.percentile(returns, 5)
        
        risk_metrics = {
            'volatility_daily': volatility_daily,
            'volatility_annual': volatility_annual,
            'mean_return_annual': mean_return_annual,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'var_95': var_95
        }
        
        print("✅ Risk analysis completed")
        return risk_metrics
    
    def create_comprehensive_chart(self):
        """Create comprehensive visualization"""
        if self.data is None or not hasattr(self, 'technical_data'):
            return None
            
        print(f"📊 Creating comprehensive chart for {self.symbol}...")
        
        df = self.technical_data
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(
                f'{self.symbol} - Price & Moving Averages',
                'RSI',
                'MACD',
                'Volume'
            ),
            row_width=[0.3, 0.2, 0.2, 0.3]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=self.symbol
            ),
            row=1, col=1
        )
        
        # Moving averages
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['SMA_20'],
                line=dict(color='orange', width=1),
                name='SMA 20'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['SMA_50'],
                line=dict(color='blue', width=1),
                name='SMA 50'
            ),
            row=1, col=1
        )
        
        # Bollinger Bands
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['BB_Upper'],
                line=dict(color='gray', width=1, dash='dash'),
                name='BB Upper',
                showlegend=False
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['BB_Lower'],
                line=dict(color='gray', width=1, dash='dash'),
                name='BB Lower',
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['RSI'],
                line=dict(color='purple'),
                name='RSI'
            ),
            row=2, col=1
        )
        
        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", row=2, col=1)
        
        # MACD
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['MACD'],
                line=dict(color='blue'),
                name='MACD'
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df['MACD_Signal'],
                line=dict(color='red'),
                name='MACD Signal'
            ),
            row=3, col=1
        )
        
        # MACD Histogram
        colors = ['green' if val >= 0 else 'red' for val in df['MACD_Histogram']]
        fig.add_trace(
            go.Bar(
                x=df.index, y=df['MACD_Histogram'],
                name='MACD Histogram',
                marker_color=colors
            ),
            row=3, col=1
        )
        
        # Volume
        fig.add_trace(
            go.Bar(
                x=df.index, y=df['Volume'],
                name='Volume',
                marker_color='lightblue'
            ),
            row=4, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=f"{self.symbol} - Comprehensive Technical Analysis",
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True,
            template="plotly_white"
        )
        
        # Save chart
        chart_file = f"output/charts/{self.symbol.lower()}_comprehensive_analysis.html"
        os.makedirs("output/charts", exist_ok=True)
        fig.write_html(chart_file)
        
        print(f"✅ Comprehensive chart saved: {chart_file}")
        return chart_file
    
    def generate_report(self, technical_analysis, risk_analysis):
        """Generate HTML report"""
        print(f"📄 Generating comprehensive report for {self.symbol}...")
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine recommendation
        signals = technical_analysis.get('signals', [])
        bullish_signals = sum(1 for s in signals if '📈' in s)
        bearish_signals = sum(1 for s in signals if '📉' in s)
        
        if bullish_signals > bearish_signals:
            recommendation = "MUA"
            recommendation_class = "positive"
        elif bearish_signals > bullish_signals:
            recommendation = "BÁN"
            recommendation_class = "negative"
        else:
            recommendation = "GIỮ"
            recommendation_class = "neutral"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo Cáo Phân Tích: {self.symbol}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary-box {{ background-color: #ecf0f1; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; padding: 10px 15px; background-color: #3498db; color: white; border-radius: 5px; }}
        .positive {{ background-color: #27ae60; }}
        .negative {{ background-color: #e74c3c; }}
        .neutral {{ background-color: #95a5a6; }}
        .recommendation {{ background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #bdc3c7; padding: 12px; text-align: left; }}
        th {{ background-color: #34495e; color: white; }}
        .footer {{ margin-top: 40px; text-align: center; color: #7f8c8d; font-size: 12px; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ background: #f8f9fa; margin: 5px 0; padding: 10px; border-left: 3px solid #3498db; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Báo Cáo Phân Tích Tài Chính: {self.symbol}</h1>
        
        <div class="summary-box">
            <h2>Tóm Tắt Thực Hiện</h2>
            <div class="metric">Giá hiện tại: ${technical_analysis['current_price']:.2f}</div>
            <div class="metric">RSI: {technical_analysis['rsi']:.1f}</div>
            <div class="metric">Volatility: {risk_analysis['volatility_annual']:.1%}</div>
            <div class="metric {recommendation_class}">Khuyến nghị: {recommendation}</div>
        </div>
        
        <h2>1. Phân Tích Kỹ Thuật</h2>
        <table>
            <tr><th>Chỉ Số</th><th>Giá Trị</th><th>Ý Nghĩa</th></tr>
            <tr><td>Giá hiện tại</td><td>${technical_analysis['current_price']:.2f}</td><td>Giá đóng cửa mới nhất</td></tr>
            <tr><td>SMA 20</td><td>${technical_analysis['sma_20']:.2f}</td><td>Đường trung bình động 20 ngày</td></tr>
            <tr><td>SMA 50</td><td>${technical_analysis['sma_50']:.2f}</td><td>Đường trung bình động 50 ngày</td></tr>
            <tr><td>RSI</td><td>{technical_analysis['rsi']:.1f}</td><td>{'Quá mua' if technical_analysis['rsi'] > 70 else 'Quá bán' if technical_analysis['rsi'] < 30 else 'Bình thường'}</td></tr>
            <tr><td>MACD</td><td>{technical_analysis['macd']:.3f}</td><td>Động lực giá</td></tr>
            <tr><td>Bollinger Bands</td><td>{technical_analysis['bb_position']}</td><td>Vị trí trong dải Bollinger</td></tr>
        </table>
        
        <h3>Tín Hiệu Kỹ Thuật</h3>
        <ul>
        """
        
        for signal in technical_analysis['signals']:
            html_content += f"<li>{signal}</li>"
        
        html_content += f"""
        </ul>
        
        <h2>2. Phân Tích Rủi Ro</h2>
        <table>
            <tr><th>Metric</th><th>Giá Trị</th><th>Ý Nghĩa</th></tr>
            <tr><td>Volatility hàng ngày</td><td>{risk_analysis['volatility_daily']:.2%}</td><td>Độ biến động trong ngày</td></tr>
            <tr><td>Volatility hàng năm</td><td>{risk_analysis['volatility_annual']:.2%}</td><td>Độ biến động dự kiến trong năm</td></tr>
            <tr><td>Lợi nhuận trung bình/năm</td><td>{risk_analysis['mean_return_annual']:.2%}</td><td>Lợi nhuận kỳ vọng</td></tr>
            <tr><td>Tỷ lệ Sharpe</td><td>{risk_analysis['sharpe_ratio']:.2f}</td><td>{'Tốt' if risk_analysis['sharpe_ratio'] > 1 else 'Trung bình' if risk_analysis['sharpe_ratio'] > 0 else 'Kém'}</td></tr>
            <tr><td>Max Drawdown</td><td>{risk_analysis['max_drawdown']:.2%}</td><td>Tổn thất lớn nhất có thể</td></tr>
            <tr><td>VaR 95%</td><td>{risk_analysis['var_95']:.2%}</td><td>Rủi ro trong 95% trường hợp</td></tr>
        </table>
        
        <div class="recommendation">
            <h2>3. Khuyến Nghị Đầu Tư</h2>
            <p><strong>Quyết định: <span class="{recommendation_class}">{recommendation}</span></strong></p>
            <p><strong>Lý do:</strong> Dựa trên phân tích kỹ thuật và rủi ro, cổ phiếu {self.symbol} hiện tại thể hiện {len(technical_analysis['signals'])} tín hiệu chính. 
            Với volatility {risk_analysis['volatility_annual']:.1%} và Sharpe ratio {risk_analysis['sharpe_ratio']:.2f}, 
            {'khuyến nghị mua để tận dụng momentum tích cực' if recommendation == 'MUA' else 'khuyến nghị bán để tránh rủi ro' if recommendation == 'BÁN' else 'khuyến nghị giữ và quan sát thêm'}.</p>
            <p><strong>Mức rủi ro:</strong> {'Cao' if risk_analysis['volatility_annual'] > 0.3 else 'Trung bình' if risk_analysis['volatility_annual'] > 0.15 else 'Thấp'}</p>
        </div>
        
        <div class="footer">
            <p>Báo cáo được tạo bởi AI Financial Analyst | {current_time}</p>
            <p>⚠️ Đây chỉ là phân tích tham khảo, không phải lời khuyên đầu tư</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Save report
        report_file = f"output/reports/{self.symbol.lower()}_analysis_report.html"
        os.makedirs("output/reports", exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Comprehensive report saved: {report_file}")
        return report_file

async def main():
    """Main demo function"""
    print("🚀 AI FINANCIAL ANALYST - COMPREHENSIVE DEMO")
    print("=" * 70)
    
    analyst = SimpleFinancialAnalyst()
    
    # Test multiple stocks
    symbols = ["AAPL", "GOOGL", "MSFT"]
    
    for symbol in symbols:
        print(f"\n{'='*50}")
        print(f"🔍 ANALYZING {symbol}")
        print(f"{'='*50}")
        
        if analyst.fetch_data(symbol):
            # Perform analyses
            tech_analysis = analyst.technical_analysis()
            risk_analysis = analyst.risk_analysis()
            
            if tech_analysis and risk_analysis:
                # Create visualizations
                chart_file = analyst.create_comprehensive_chart()
                
                # Generate report
                report_file = analyst.generate_report(tech_analysis, risk_analysis)
                
                print(f"\n✅ Analysis completed for {symbol}")
                print(f"📊 Chart: {chart_file}")
                print(f"📄 Report: {report_file}")
            else:
                print(f"❌ Analysis failed for {symbol}")
        else:
            print(f"❌ Data fetch failed for {symbol}")
    
    print(f"\n{'='*70}")
    print("🎉 COMPREHENSIVE DEMO COMPLETED!")
    print("\n📁 Output files:")
    print("├── output/charts/ - Interactive charts")  
    print("└── output/reports/ - HTML analysis reports")
    print("\n🌐 Open HTML files in your browser to view results")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main()) 