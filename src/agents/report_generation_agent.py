"""
Report Generation Agent - Tạo báo cáo tài chính toàn diện
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime
from pathlib import Path
import json
import html
import os
from jinja2 import Template
import asyncio
import aiohttp
from openai import AsyncOpenAI
from .gemini_ai_client import GeminiAIClient

class ReportGenerationAgent:
    """Agent chịu trách nhiệm tạo báo cáo tài chính"""
    
    def __init__(self, config: Dict[str, Any], data_sources_config: Dict[str, Any]):
        self.config = config
        self.data_sources_config = data_sources_config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Gemini AI client
        self.gemini_client = GeminiAIClient()
        self.ai_enabled = self.gemini_client.is_enabled
        
        if self.ai_enabled:
            self.logger.info("✅ Gemini AI client initialized for report enhancement")
        else:
            self.logger.warning("⚠️ Gemini AI not available, using basic report generation")
        
        # Output directories
        self.reports_dir = Path(config.get('reports_directory', './output/reports'))
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Output settings
        self.reports_directory = Path(config.get('reports_directory', './output/reports'))
        self.default_format = config.get('default_report_format', 'html')
        
        # Create reports directory if it doesn't exist
        self.reports_directory.mkdir(parents=True, exist_ok=True)
        
        # Report templates
        self.setup_templates()
    
    def setup_templates(self):
        """Setup report templates"""
        self.html_template = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .summary-box {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .metric {
            display: inline-block;
            margin: 10px 20px 10px 0;
            padding: 10px 15px;
            background-color: #3498db;
            color: white;
            border-radius: 5px;
        }
        .positive {
            background-color: #27ae60;
        }
        .negative {
            background-color: #e74c3c;
        }
        .neutral {
            background-color: #95a5a6;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #bdc3c7;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #34495e;
            color: white;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .recommendation {
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }
        .ai-insights {
            background-color: #f8f9fa;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .ai-insights h4 {
            color: #17a2b8;
            margin-top: 0;
        }
        .sentiment-positive {
            color: #28a745;
            font-weight: bold;
        }
        .sentiment-negative {
            color: #dc3545;
            font-weight: bold;
        }
        .sentiment-neutral {
            color: #6c757d;
            font-weight: bold;
        }
        .footer {
            margin-top: 40px;
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        {{ content }}
        <div class="footer">
            <p>Báo cáo được tạo bởi AI Financial Analyst MCP | {{ timestamp }}</p>
        </div>
    </div>
</body>
</html>
        """
    
    async def generate_report(
        self,
        symbol: str,
        analysis_data: Dict[str, Any],
        report_format: str = "html",
        include_charts: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate comprehensive financial analysis report
        
        Args:
            symbol: Stock symbol
            analysis_data: Analysis results from DataAnalysisAgent
            report_format: Report format (html, pdf, json)
            include_charts: Whether to include charts
            **kwargs: Additional parameters
        
        Returns:
            Dict containing report information
        """
        try:
            # Generate report based on format
            if report_format.lower() == "html":
                result = await self._generate_html_report(symbol, analysis_data, include_charts, **kwargs)
            elif report_format.lower() == "json":
                result = await self._generate_json_report(symbol, analysis_data, **kwargs)
            elif report_format.lower() == "text":
                result = await self._generate_text_report(symbol, analysis_data, **kwargs)
            else:
                raise ValueError(f"Unsupported report format: {report_format}")
            
            self.logger.info(f"Generated {report_format} report for {symbol}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating report for {symbol}: {e}")
            raise
    
    async def _generate_html_report(self, symbol: str, analysis_data: Dict[str, Any], include_charts: bool, **kwargs) -> Dict[str, Any]:
        """Generate HTML report"""
        try:
            # Extract data
            price_analysis = analysis_data.get('price_analysis', {})
            technical_analysis = analysis_data.get('technical_analysis', {})
            fundamental_analysis = analysis_data.get('fundamental_analysis', {})
            risk_analysis = analysis_data.get('risk_analysis', {})
            volume_analysis = analysis_data.get('volume_analysis', {})
            trend_analysis = analysis_data.get('trend_analysis', {})
            ai_insights = analysis_data.get('ai_insights', {})
            
            # Build report content
            content = f"""
            <h1>Báo Cáo Phân Tích Tài Chính: {symbol}</h1>
            
            <div class="summary-box">
                <h2>Tóm Tắt Thực Hiện</h2>
                {self._create_executive_summary(symbol, analysis_data)}
            </div>
            
            <h2>1. Phân Tích Giá Cả</h2>
            {self._create_price_analysis_section(price_analysis)}
            
            <h2>2. Phân Tích Kỹ Thuật</h2>
            {self._create_technical_analysis_section(technical_analysis)}
            
            <h2>3. Phân Tích Cơ Bản</h2>
            {self._create_fundamental_analysis_section(fundamental_analysis)}
            
            <h2>4. Phân Tích Rủi Ro</h2>
            {self._create_risk_analysis_section(risk_analysis)}
            
            <h2>5. Phân Tích Khối Lượng</h2>
            {self._create_volume_analysis_section(volume_analysis)}
            
            <h2>6. Phân Tích Xu Hướng</h2>
            {self._create_trend_analysis_section(trend_analysis)}
            
            <h2>7. AI Market Insights</h2>
            {self._create_ai_insights_section(ai_insights)}
            
            <h2>8. Khuyến Nghị Đầu Tư</h2>
            {self._create_recommendations(symbol, analysis_data)}
            """
            
            # Create final HTML
            template = Template(self.html_template)
            html_content = template.render(
                title=f"Báo Cáo Phân Tích {symbol}",
                content=content,
                timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            )
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_report_{symbol}_{timestamp}.html"
            report_path = self.reports_directory / filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                'report_type': 'html',
                'symbol': symbol,
                'report_path': str(report_path),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Error generating HTML report: {e}")
    
    async def _generate_json_report(self, symbol: str, analysis_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate JSON report"""
        try:
            # Create comprehensive JSON report
            report_data = {
                'metadata': {
                    'symbol': symbol,
                    'report_generated': datetime.now().isoformat(),
                    'report_type': 'financial_analysis',
                    'version': '1.0'
                },
                'analysis': analysis_data,
                'summary': {
                    'current_price': analysis_data.get('price_analysis', {}).get('current_price', 0),
                    'price_change_1d': analysis_data.get('price_analysis', {}).get('price_changes', {}).get('1_day', 0),
                    'price_change_20d': analysis_data.get('price_analysis', {}).get('price_changes', {}).get('20_day', 0),
                    'volatility': analysis_data.get('risk_analysis', {}).get('basic_metrics', {}).get('volatility_annual', 0),
                    'sharpe_ratio': analysis_data.get('risk_analysis', {}).get('sharpe_ratio', 0)
                },
                'recommendations': self._generate_recommendations_data(symbol, analysis_data)
            }
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_report_{symbol}_{timestamp}.json"
            report_path = self.reports_directory / filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            return {
                'report_type': 'json',
                'symbol': symbol,
                'report_path': str(report_path),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Error generating JSON report: {e}")
    
    async def _generate_text_report(self, symbol: str, analysis_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate text report"""
        try:
            # Create text report
            report_lines = [
                f"BÁO CÁO PHÂN TÍCH TÀI CHÍNH: {symbol}",
                "=" * 50,
                f"Ngày tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                "",
                "TÓM TẮT THỰC HIỆN:",
                "-" * 20,
            ]
            
            # Add price analysis
            price_analysis = analysis_data.get('price_analysis', {})
            if price_analysis:
                report_lines.extend([
                    f"Giá hiện tại: ${price_analysis.get('current_price', 'N/A'):.2f}",
                    f"Thay đổi 1 ngày: {price_analysis.get('price_changes', {}).get('1_day', 0):.2f}%",
                    f"Thay đổi 20 ngày: {price_analysis.get('price_changes', {}).get('20_day', 0):.2f}%",
                    ""
                ])
            
            # Add technical analysis
            technical_analysis = analysis_data.get('technical_analysis', {})
            if technical_analysis:
                report_lines.extend([
                    "PHÂN TÍCH KỸ THUẬT:",
                    "-" * 20,
                ])
                
                # RSI
                rsi_data = technical_analysis.get('rsi', {})
                if rsi_data:
                    report_lines.append(f"RSI: {rsi_data.get('current', 'N/A'):.2f} - {rsi_data.get('signal', 'N/A')}")
                
                # Moving averages
                ma_data = technical_analysis.get('moving_averages', {})
                for ma_name, ma_info in ma_data.items():
                    current_value = ma_info.get('current', 'N/A')
                    signal = ma_info.get('signal', 'N/A')
                    report_lines.append(f"{ma_name.upper()}: {current_value:.2f} - {signal}")
                
                report_lines.append("")
            
            # Add risk analysis
            risk_analysis = analysis_data.get('risk_analysis', {})
            if risk_analysis:
                report_lines.extend([
                    "PHÂN TÍCH RỦI RO:",
                    "-" * 20,
                    f"Độ biến động hàng năm: {risk_analysis.get('basic_metrics', {}).get('volatility_annual', 0):.2%}",
                    f"Tỷ lệ Sharpe: {risk_analysis.get('sharpe_ratio', 0):.2f}",
                    f"Rút vốn tối đa: {risk_analysis.get('max_drawdown', 0):.2%}",
                    ""
                ])
            
            # Add recommendations
            recommendations = self._generate_text_recommendations(symbol, analysis_data)
            report_lines.extend([
                "KHUYẾN NGHỊ:",
                "-" * 20,
                recommendations,
                ""
            ])
            
            # Join all lines
            report_content = "\n".join(report_lines)
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_report_{symbol}_{timestamp}.txt"
            report_path = self.reports_directory / filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            return {
                'report_type': 'text',
                'symbol': symbol,
                'report_path': str(report_path),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            raise Exception(f"Error generating text report: {e}")
    
    def _create_executive_summary(self, symbol: str, analysis_data: Dict[str, Any]) -> str:
        """Create executive summary section"""
        price_analysis = analysis_data.get('price_analysis', {})
        risk_analysis = analysis_data.get('risk_analysis', {})
        technical_analysis = analysis_data.get('technical_analysis', {})
        
        current_price = price_analysis.get('current_price', 0)
        price_change_1d = price_analysis.get('price_changes', {}).get('1_day', 0)
        volatility = risk_analysis.get('basic_metrics', {}).get('volatility_annual', 0)
        
        # Determine price change class
        price_class = "positive" if price_change_1d > 0 else "negative" if price_change_1d < 0 else "neutral"
        
        return f"""
        <div class="metric">Giá hiện tại: ${current_price:.2f}</div>
        <div class="metric {price_class}">Thay đổi 1 ngày: {price_change_1d:.2f}%</div>
        <div class="metric">Độ biến động: {volatility:.2%}</div>
        <p>Cổ phiếu {symbol} đang giao dịch ở mức ${current_price:.2f}, 
        {'tăng' if price_change_1d > 0 else 'giảm' if price_change_1d < 0 else 'không đổi'} 
        {abs(price_change_1d):.2f}% so với phiên trước.</p>
        """
    
    def _create_price_analysis_section(self, price_analysis: Dict[str, Any]) -> str:
        """Create price analysis section"""
        if not price_analysis:
            return "<p>Không có dữ liệu phân tích giá.</p>"
        
        current_price = price_analysis.get('current_price', 0)
        price_changes = price_analysis.get('price_changes', {})
        
        html = f"""
        <table>
            <tr><th>Thời kỳ</th><th>Thay đổi (%)</th></tr>
            <tr><td>Giá hiện tại</td><td>${current_price:.2f}</td></tr>
        """
        
        for period, change in price_changes.items():
            change_class = "positive" if change > 0 else "negative" if change < 0 else "neutral"
            html += f"<tr><td>{period}</td><td class='{change_class}'>{change:.2f}%</td></tr>"
        
        html += "</table>"
        return html
    
    def _create_technical_analysis_section(self, technical_analysis: Dict[str, Any]) -> str:
        """Create technical analysis section"""
        if not technical_analysis:
            return "<p>Không có dữ liệu phân tích kỹ thuật.</p>"
        
        html = "<table><tr><th>Chỉ báo</th><th>Giá trị</th><th>Tín hiệu</th></tr>"
        
        # RSI
        rsi_data = technical_analysis.get('rsi', {})
        if rsi_data:
            rsi_value = rsi_data.get('current', 'N/A')
            rsi_signal = rsi_data.get('signal', 'N/A')
            html += f"<tr><td>RSI</td><td>{rsi_value:.2f}</td><td>{rsi_signal}</td></tr>"
        
        # Moving Averages
        ma_data = technical_analysis.get('moving_averages', {})
        for ma_name, ma_info in ma_data.items():
            current_value = ma_info.get('current', 'N/A')
            signal = ma_info.get('signal', 'N/A')
            html += f"<tr><td>{ma_name.upper()}</td><td>{current_value:.2f}</td><td>{signal}</td></tr>"
        
        # MACD
        macd_data = technical_analysis.get('macd', {})
        if macd_data:
            macd_signal = macd_data.get('trading_signal', 'N/A')
            html += f"<tr><td>MACD</td><td>-</td><td>{macd_signal}</td></tr>"
        
        html += "</table>"
        return html
    
    def _create_fundamental_analysis_section(self, fundamental_analysis: Dict[str, Any]) -> str:
        """Create fundamental analysis section"""
        if not fundamental_analysis:
            return "<p>Không có dữ liệu phân tích cơ bản.</p>"
        
        html = ""
        
        # Company info
        company_info = fundamental_analysis.get('company_info', {})
        if company_info:
            html += "<h3>Thông tin công ty</h3><table>"
            html += f"<tr><td>Ngành</td><td>{company_info.get('sector', 'N/A')}</td></tr>"
            html += f"<tr><td>Lĩnh vực</td><td>{company_info.get('industry', 'N/A')}</td></tr>"
            html += f"<tr><td>Vốn hóa thị trường</td><td>${company_info.get('market_cap', 0):,}</td></tr>"
            html += "</table>"
        
        # Financial ratios
        ratios = fundamental_analysis.get('financial_ratios', {})
        if ratios:
            html += "<h3>Tỷ lệ tài chính</h3><table>"
            for ratio_name, ratio_value in ratios.items():
                if ratio_value:
                    html += f"<tr><td>{ratio_name.replace('_', ' ').title()}</td><td>{ratio_value:.2f}</td></tr>"
            html += "</table>"
        
        return html if html else "<p>Không có dữ liệu phân tích cơ bản.</p>"
    
    def _create_risk_analysis_section(self, risk_analysis: Dict[str, Any]) -> str:
        """Create risk analysis section"""
        if not risk_analysis:
            return "<p>Không có dữ liệu phân tích rủi ro.</p>"
        
        html = "<table>"
        
        basic_metrics = risk_analysis.get('basic_metrics', {})
        if basic_metrics:
            html += f"<tr><td>Độ biến động hàng ngày</td><td>{basic_metrics.get('volatility_daily', 0):.4f}</td></tr>"
            html += f"<tr><td>Độ biến động hàng năm</td><td>{basic_metrics.get('volatility_annual', 0):.2%}</td></tr>"
            html += f"<tr><td>Lợi nhuận trung bình hàng năm</td><td>{basic_metrics.get('mean_return_annual', 0):.2%}</td></tr>"
        
        if 'sharpe_ratio' in risk_analysis:
            html += f"<tr><td>Tỷ lệ Sharpe</td><td>{risk_analysis['sharpe_ratio']:.2f}</td></tr>"
        
        if 'max_drawdown' in risk_analysis:
            html += f"<tr><td>Rút vốn tối đa</td><td>{risk_analysis['max_drawdown']:.2%}</td></tr>"
        
        var_data = risk_analysis.get('value_at_risk', {})
        if var_data:
            html += f"<tr><td>VaR 95%</td><td>{var_data.get('var_95', 0):.2%}</td></tr>"
        
        html += "</table>"
        return html
    
    def _create_volume_analysis_section(self, volume_analysis: Dict[str, Any]) -> str:
        """Create volume analysis section"""
        if not volume_analysis:
            return "<p>Không có dữ liệu phân tích khối lượng.</p>"
        
        html = "<table>"
        html += f"<tr><td>Khối lượng hiện tại</td><td>{volume_analysis.get('current_volume', 0):,}</td></tr>"
        html += f"<tr><td>Khối lượng trung bình 20 ngày</td><td>{volume_analysis.get('average_volume_20', 0):,.0f}</td></tr>"
        html += "</table>"
        
        return html
    
    def _create_trend_analysis_section(self, trend_analysis: Dict[str, Any]) -> str:
        """Create trend analysis section"""
        if not trend_analysis:
            return "<p>Không có dữ liệu phân tích xu hướng.</p>"
        
        trend_direction = trend_analysis.get('trend_direction', 'N/A')
        
        html = f"""
        <p>Xu hướng hiện tại: <strong>{trend_direction}</strong></p>
        """
        
        return html
    
    def _create_ai_insights_section(self, ai_insights: Dict[str, Any]) -> str:
        """Create AI insights section"""
        if not ai_insights or not ai_insights.get('enabled', False):
            return "<div class='ai-insights'><p>AI Insights không khả dụng hoặc chưa được cấu hình.</p></div>"
        
        sentiment_class = 'sentiment-neutral'
        if ai_insights.get('market_sentiment') == 'Tích cực':
            sentiment_class = 'sentiment-positive'
        elif ai_insights.get('market_sentiment') == 'Tiêu cực':
            sentiment_class = 'sentiment-negative'
        
        html = f"""
        <div class='ai-insights'>
            <h4>🤖 AI Market Insights</h4>
            <p><strong>Market Sentiment:</strong> <span class='{sentiment_class}'>{ai_insights.get('market_sentiment', 'Unknown')}</span></p>
            
            <h5>Chi tiết phân tích:</h5>
            <div style='background: white; padding: 10px; border-radius: 5px; white-space: pre-wrap;'>
                {ai_insights.get('insights', 'Không có insights chi tiết')}
            </div>
            
            <h5>Các yếu tố chính:</h5>
            <ul>
        """
        
        key_factors = ai_insights.get('key_factors', [])
        if key_factors:
            for factor in key_factors:
                html += f"<li>{factor}</li>"
        else:
            html += "<li>Không có yếu tố chính được xác định</li>"
        
        html += f"""
            </ul>
            <p><small>Nguồn: {ai_insights.get('source', 'AI Analysis')} | {ai_insights.get('generated_at', 'N/A')}</small></p>
        </div>
        """
        
        return html
    
    def _create_recommendations(self, symbol: str, analysis_data: Dict[str, Any]) -> str:
        """Create recommendations section"""
        recommendations = self._generate_recommendations_data(symbol, analysis_data)
        
        html = f"""
        <div class="recommendation">
            <h3>Khuyến nghị đầu tư</h3>
            <p><strong>Quyết định:</strong> {recommendations['decision']}</p>
            <p><strong>Lý do:</strong> {recommendations['reasoning']}</p>
            <p><strong>Mức rủi ro:</strong> {recommendations['risk_level']}</p>
            {recommendations.get('ai_insights', '')}
        </div>
        """
        
        return html
    
    def _generate_recommendations_data(self, symbol: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investment recommendations - now async wrapper"""
        # Run async method in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._generate_ai_recommendations(symbol, analysis_data))
        finally:
            loop.close()
    
    async def _generate_ai_recommendations(self, symbol: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered investment recommendations using Gemini AI"""
        try:
            if not self.ai_enabled:
                return await self._generate_rule_based_recommendations(symbol, analysis_data)
            
            # Call Gemini AI for investment recommendations
            response = await self.gemini_client.generate_investment_recommendation(symbol, analysis_data)
            
            if response.get('enabled', False):
                return {
                    'decision': response.get('decision', 'GIỮ'),
                    'reasoning': response.get('reasoning', 'Không có lý do cụ thể'),
                    'risk_level': response.get('risk_level', 'Trung bình'),
                    'ai_insights': f'<div class="ai-insights"><h4>Phân tích Gemini AI:</h4><p>{response.get("reasoning", "")}</p></div>',
                    'source': 'Gemini AI'
                }
            else:
                # Fallback to rule-based if AI fails
                return await self._generate_rule_based_recommendations(symbol, analysis_data)
            
        except Exception as e:
            self.logger.error(f"Error generating AI recommendations: {e}")
            # Fallback to rule-based recommendations
            return await self._generate_rule_based_recommendations(symbol, analysis_data)
    
    def _create_analysis_prompt(self, symbol: str, analysis_data: Dict[str, Any]) -> str:
        """Create detailed prompt for AI analysis"""
        price_analysis = analysis_data.get('price_analysis', {})
        technical_analysis = analysis_data.get('technical_analysis', {})
        risk_analysis = analysis_data.get('risk_analysis', {})
        fundamental_analysis = analysis_data.get('fundamental_analysis', {})
        
        prompt = f"""
Phân tích cổ phiếu {symbol} dựa trên dữ liệu sau:

PHÂN TÍCH GIÁ:
- Giá hiện tại: {price_analysis.get('current_price', 'N/A')}
- Thay đổi 1 ngày: {price_analysis.get('price_changes', {}).get('1_day', 0):.2%}
- Thay đổi 5 ngày: {price_analysis.get('price_changes', {}).get('5_day', 0):.2%}
- Thay đổi 20 ngày: {price_analysis.get('price_changes', {}).get('20_day', 0):.2%}
- Giá cao nhất 52 tuần: {price_analysis.get('high_52w', 'N/A')}
- Giá thấp nhất 52 tuần: {price_analysis.get('low_52w', 'N/A')}

PHÂN TÍCH KỸ THUẬT:
- RSI: {technical_analysis.get('rsi', {}).get('current_value', 'N/A')} ({technical_analysis.get('rsi', {}).get('signal', 'N/A')})
- MACD: {technical_analysis.get('macd', {}).get('macd_value', 'N/A')} (Signal: {technical_analysis.get('macd', {}).get('signal', 'N/A')})
- Bollinger Bands: {technical_analysis.get('bollinger_bands', {}).get('signal', 'N/A')}
- Moving Averages: MA20: {technical_analysis.get('moving_averages', {}).get('ma_20', 'N/A')}, MA50: {technical_analysis.get('moving_averages', {}).get('ma_50', 'N/A')}

PHÂN TÍCH RỦI RO:
- Độ biến động hàng năm: {risk_analysis.get('basic_metrics', {}).get('volatility_annual', 0):.2%}
- Tỷ lệ Sharpe: {risk_analysis.get('sharpe_ratio', 'N/A')}
- Rút vốn tối đa: {risk_analysis.get('max_drawdown', 0):.2%}
- VaR 95%: {risk_analysis.get('value_at_risk', {}).get('var_95', 0):.2%}

PHÂN TÍCH CƠ BẢN:
- P/E Ratio: {fundamental_analysis.get('financial_ratios', {}).get('pe_ratio', 'N/A')}
- Market Cap: {fundamental_analysis.get('company_info', {}).get('market_cap', 'N/A')}

Hãy đưa ra:
1. Quyết định đầu tư: MUA/BÁN/GIỮ
2. Lý do chi tiết (tối thiểu 100 từ)
3. Mức độ rủi ro: Thấp/Trung bình/Cao
4. Khuyến nghị thời gian nắm giữ
5. Mức giá mục tiêu (nếu có)
6. Điều kiện dừng lỗ

Trả lời bằng tiếng Việt, ngắn gọn và chuyên nghiệp.
        """
        
        return prompt
    
    def _parse_ai_response(self, ai_response: str, symbol: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        try:
            # Extract decision (MUA/BÁN/GIỮ)
            decision = "GIỮ"  # default
            if "MUA" in ai_response.upper():
                decision = "MUA"
            elif "BÁN" in ai_response.upper() or "BAN" in ai_response.upper():
                decision = "BÁN"
            
            # Extract risk level
            risk_level = "Trung bình"  # default
            if "RỦI RO THẤP" in ai_response.upper() or "THẤP" in ai_response.upper():
                risk_level = "Thấp"
            elif "RỦI RO CAO" in ai_response.upper() or "CAO" in ai_response.upper():
                risk_level = "Cao"
            
            return {
                'decision': decision,
                'reasoning': ai_response,
                'risk_level': risk_level,
                'ai_insights': f'<div class="ai-insights"><h4>Phân tích AI chi tiết:</h4><p>{ai_response}</p></div>',
                'source': 'Gemini AI'
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing AI response: {e}")
            return {
                'decision': 'GIỮ',
                'reasoning': 'Lỗi phân tích AI, sử dụng khuyến nghị mặc định',
                'risk_level': 'Không xác định',
                'ai_insights': '',
                'source': 'Error'
            }

    async def _generate_rule_based_recommendations(self, symbol: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate rule-based recommendations (fallback method)"""
        try:
            # Extract key metrics
            price_analysis = analysis_data.get('price_analysis', {})
            technical_analysis = analysis_data.get('technical_analysis', {})
            risk_analysis = analysis_data.get('risk_analysis', {})
            
            # Score calculation
            score = 0
            reasoning_parts = []
            
            # Price momentum
            price_change_20d = price_analysis.get('price_changes', {}).get('20_day', 0)
            if price_change_20d > 5:
                score += 2
                reasoning_parts.append("xu hướng giá tích cực")
            elif price_change_20d < -5:
                score -= 2
                reasoning_parts.append("xu hướng giá tiêu cực")
            
            # Technical indicators
            rsi_data = technical_analysis.get('rsi', {})
            if rsi_data:
                rsi_signal = rsi_data.get('signal', '')
                if rsi_signal == 'Oversold':
                    score += 1
                    reasoning_parts.append("RSI cho tín hiệu oversold")
                elif rsi_signal == 'Overbought':
                    score -= 1
                    reasoning_parts.append("RSI cho tín hiệu overbought")
            
            # Risk metrics
            sharpe_ratio = risk_analysis.get('sharpe_ratio', 0)
            if sharpe_ratio > 1:
                score += 1
                reasoning_parts.append("tỷ lệ Sharpe tốt")
            elif sharpe_ratio < 0:
                score -= 1
                reasoning_parts.append("tỷ lệ Sharpe kém")
            
            # Volatility
            volatility = risk_analysis.get('basic_metrics', {}).get('volatility_annual', 0)
            if volatility > 0.4:
                score -= 1
                reasoning_parts.append("độ biến động cao")
            
            # Decision making
            if score >= 2:
                decision = "MUA"
                risk_level = "Trung bình" if volatility < 0.3 else "Cao"
            elif score <= -2:
                decision = "BÁN"
                risk_level = "Cao"
            else:
                decision = "GIỮ"
                risk_level = "Trung bình"
            
            reasoning = ", ".join(reasoning_parts) if reasoning_parts else "phân tích toàn diện các chỉ số"
            
            return {
                'decision': decision,
                'reasoning': f"Dựa trên {reasoning}",
                'risk_level': risk_level,
                'score': score,
                'source': 'Rule-based'
            }
            
        except Exception as e:
            return {
                'decision': 'GIỮ',
                'reasoning': 'Không đủ dữ liệu để đưa ra khuyến nghị',
                'risk_level': 'Không xác định',
                'score': 0,
                'source': 'Error'
            }
    
    def _generate_text_recommendations(self, symbol: str, analysis_data: Dict[str, Any]) -> str:
        """Generate text recommendations"""
        recommendations = self._generate_recommendations_data(symbol, analysis_data)
        
        return f"""
Quyết định: {recommendations['decision']}
Lý do: {recommendations['reasoning']}
Mức rủi ro: {recommendations['risk_level']}
        """
    
    async def generate_summary_report(self, multiple_stocks_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary report for multiple stocks"""
        try:
            summary_data = {
                'metadata': {
                    'report_type': 'multi_stock_summary',
                    'generated_at': datetime.now().isoformat(),
                    'total_stocks': len(multiple_stocks_data)
                },
                'stocks': {}
            }
            
            for symbol, data in multiple_stocks_data.items():
                summary_data['stocks'][symbol] = {
                    'current_price': data.get('price_analysis', {}).get('current_price', 0),
                    'price_change_1d': data.get('price_analysis', {}).get('price_changes', {}).get('1_day', 0),
                    'volatility': data.get('risk_analysis', {}).get('basic_metrics', {}).get('volatility_annual', 0),
                    'recommendation': self._generate_recommendations_data(symbol, data)
                }
            
            # Save summary report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"summary_report_{timestamp}.json"
            report_path = self.reports_directory / filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False, default=str)
            
            return {
                'report_type': 'summary',
                'report_path': str(report_path),
                'stocks_analyzed': list(multiple_stocks_data.keys()),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Error generating summary report: {e}")
            raise 