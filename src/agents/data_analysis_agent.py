"""
Data Analysis Agent - Phân tích dữ liệu tài chính
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime, timedelta
import warnings
import os
import asyncio
from openai import AsyncOpenAI
import ta
from .gemini_ai_client import GeminiAIClient

# Technical analysis libraries
try:
    import ta
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    print("Warning: TA-Lib not available, some technical indicators may not work")

# Technical analysis - using numpy and pandas for calculations

class DataAnalysisAgent:
    """Agent chịu trách nhiệm phân tích dữ liệu tài chính"""
    
    def __init__(self, config: Dict[str, Any], data_sources_config: Dict[str, Any]):
        self.config = config
        self.data_sources_config = data_sources_config
        self.logger = logging.getLogger(__name__)
        
        # Initialize Gemini AI client
        self.gemini_client = GeminiAIClient()
        self.ai_enabled = self.gemini_client.is_enabled
        
        if self.ai_enabled:
            self.logger.info("✅ Gemini AI client initialized for market insights")
        else:
            self.logger.warning("⚠️ Gemini AI not available, using rule-based analysis")
        
        # Default technical indicators
        self.default_indicators = config.get('technical_indicators', [
            'sma_20', 'sma_50', 'rsi_14', 'macd', 'bollinger_bands'
        ])
        
        # Risk metrics
        self.risk_metrics = config.get('risk_metrics', [
            'sharpe_ratio', 'max_drawdown', 'volatility', 'var_95'
        ])
    
    async def analyze_stock(
        self, 
        symbol: str,
        data: Dict[str, Any], 
        analysis_types: List[str] = None,
        indicators: List[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive stock analysis
        
        Args:
            symbol: Stock symbol
            data: Stock data from DataRetrievalAgent
            analysis_types: Types of analysis to perform
            indicators: Technical indicators to calculate
        
        Returns:
            Dict containing analysis results
        """
        try:
            if analysis_types is None:
                analysis_types = ['technical', 'fundamental', 'risk']
            
            if indicators is None:
                indicators = self.default_indicators
            
            # Convert historical data to DataFrame
            historical_data = data.get('data', {}).get('historical', [])
            if not historical_data:
                raise ValueError("No historical data available for analysis")
            
            df = pd.DataFrame(historical_data)
            
            # Ensure we have required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert to datetime index if not already
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
            elif not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            
            # Sort by date
            df = df.sort_index()
            
            analysis_results = {
                'symbol': symbol,
                'analysis_timestamp': datetime.now().isoformat(),
                'data_period': {
                    'start_date': df.index.min().isoformat(),
                    'end_date': df.index.max().isoformat(),
                    'data_points': len(df)
                }
            }
            
            # Technical Analysis
            if 'technical' in analysis_types:
                analysis_results['technical_analysis'] = await self._technical_analysis(df, indicators)
            
            # Fundamental Analysis
            if 'fundamental' in analysis_types:
                analysis_results['fundamental_analysis'] = await self._fundamental_analysis(data)
            
            # Risk Analysis
            if 'risk' in analysis_types:
                analysis_results['risk_analysis'] = await self._risk_analysis(df)
            
            # Price Analysis
            analysis_results['price_analysis'] = await self._price_analysis(df)
            
            # Volume Analysis
            analysis_results['volume_analysis'] = await self._volume_analysis(df)
            
            # Trend Analysis
            analysis_results['trend_analysis'] = await self._trend_analysis(df)
            
            # AI Market Insights
            ai_insights = await self.generate_market_insights(symbol, {
                'price_analysis': analysis_results['price_analysis'],
                'technical_analysis': analysis_results['technical_analysis'],
                'risk_analysis': analysis_results['risk_analysis'],
                'trend_analysis': analysis_results['trend_analysis']
            })
            
            analysis_results['ai_insights'] = ai_insights
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error in stock analysis for {symbol}: {e}")
            raise
    
    async def _technical_analysis(self, df: pd.DataFrame, indicators: List[str]) -> Dict[str, Any]:
        """Perform technical analysis"""
        technical_results = {}
        
        try:
            close = df['Close'].values
            high = df['High'].values
            low = df['Low'].values
            
            # Moving Averages
            if any('sma' in ind for ind in indicators):
                technical_results['moving_averages'] = {}
                for ind in indicators:
                    if 'sma' in ind:
                        period = int(ind.split('_')[1])
                        sma = df['Close'].rolling(window=period).mean()
                        technical_results['moving_averages'][f'sma_{period}'] = {
                            'values': sma.tolist(),
                            'current': float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else None,
                            'signal': self._get_sma_signal(close, sma.values)
                        }
            
            # RSI
            if 'rsi_14' in indicators or 'rsi' in indicators:
                rsi = self._calculate_rsi(df['Close'], 14)
                technical_results['rsi'] = {
                    'values': rsi.tolist(),
                    'current': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
                    'signal': self._get_rsi_signal(rsi.iloc[-1])
                }
            
            # MACD
            if 'macd' in indicators:
                macd_data = self._calculate_macd(df['Close'])
                technical_results['macd'] = {
                    'macd': macd_data['macd'].tolist(),
                    'signal': macd_data['signal'].tolist(),
                    'histogram': macd_data['histogram'].tolist(),
                    'current': {
                        'macd': float(macd_data['macd'].iloc[-1]) if not pd.isna(macd_data['macd'].iloc[-1]) else None,
                        'signal': float(macd_data['signal'].iloc[-1]) if not pd.isna(macd_data['signal'].iloc[-1]) else None,
                        'histogram': float(macd_data['histogram'].iloc[-1]) if not pd.isna(macd_data['histogram'].iloc[-1]) else None
                    },
                    'trading_signal': self._get_macd_signal(macd_data['macd'], macd_data['signal'], macd_data['histogram'])
                }
            
            # Bollinger Bands
            if 'bollinger_bands' in indicators:
                bb_data = self._calculate_bollinger_bands(df['Close'])
                technical_results['bollinger_bands'] = {
                    'upper': bb_data['upper'].tolist(),
                    'middle': bb_data['middle'].tolist(),
                    'lower': bb_data['lower'].tolist(),
                    'current': {
                        'price': float(close[-1]),
                        'upper': float(bb_data['upper'].iloc[-1]) if not pd.isna(bb_data['upper'].iloc[-1]) else None,
                        'middle': float(bb_data['middle'].iloc[-1]) if not pd.isna(bb_data['middle'].iloc[-1]) else None,
                        'lower': float(bb_data['lower'].iloc[-1]) if not pd.isna(bb_data['lower'].iloc[-1]) else None
                    },
                    'signal': self._get_bollinger_signal(close, bb_data['upper'].values, bb_data['lower'].values)
                }
            
            return technical_results
            
        except Exception as e:
            self.logger.error(f"Error in technical analysis: {e}")
            return {'error': str(e)}
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        
        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    
    async def _fundamental_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform fundamental analysis"""
        try:
            fundamental_results = {}
            
            # Get company info
            info = data.get('data', {}).get('info', {})
            if info:
                fundamental_results['company_info'] = {
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A'),
                    'market_cap': info.get('marketCap', 0),
                    'enterprise_value': info.get('enterpriseValue', 0),
                    'employees': info.get('fullTimeEmployees', 0)
                }
                
                # Key financial ratios
                fundamental_results['financial_ratios'] = {
                    'pe_ratio': info.get('trailingPE', 0),
                    'forward_pe': info.get('forwardPE', 0),
                    'peg_ratio': info.get('pegRatio', 0),
                    'price_to_book': info.get('priceToBook', 0),
                    'price_to_sales': info.get('priceToSalesTrailing12Months', 0)
                }
                
                # Profitability metrics
                fundamental_results['profitability'] = {
                    'profit_margin': info.get('profitMargins', 0),
                    'operating_margin': info.get('operatingMargins', 0),
                    'return_on_assets': info.get('returnOnAssets', 0),
                    'return_on_equity': info.get('returnOnEquity', 0)
                }
            
            return fundamental_results
            
        except Exception as e:
            self.logger.error(f"Error in fundamental analysis: {e}")
            return {'error': str(e)}
    
    async def _risk_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform risk analysis"""
        try:
            risk_results = {}
            
            # Calculate returns
            df['returns'] = df['Close'].pct_change()
            returns = df['returns'].dropna()
            
            if len(returns) == 0:
                return {'error': 'No returns data available'}
            
            # Basic risk metrics
            risk_results['basic_metrics'] = {
                'volatility_daily': float(returns.std()),
                'volatility_annual': float(returns.std() * np.sqrt(252)),
                'mean_return_daily': float(returns.mean()),
                'mean_return_annual': float(returns.mean() * 252)
            }
            
            # Sharpe Ratio
            risk_free_rate = 0.02
            excess_returns = returns.mean() * 252 - risk_free_rate
            sharpe_ratio = excess_returns / (returns.std() * np.sqrt(252))
            risk_results['sharpe_ratio'] = float(sharpe_ratio)
            
            # Maximum Drawdown
            cumulative_returns = (1 + returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            risk_results['max_drawdown'] = float(max_drawdown)
            
            # Value at Risk
            var_95 = np.percentile(returns, 5)
            risk_results['value_at_risk'] = {'var_95': float(var_95)}
            
            return risk_results
            
        except Exception as e:
            self.logger.error(f"Error in risk analysis: {e}")
            return {'error': str(e)}
    
    async def _price_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze price movements"""
        try:
            current_price = float(df['Close'].iloc[-1])
            
            price_results = {
                'current_price': current_price,
                'price_changes': {
                    '1_day': float((df['Close'].iloc[-1] / df['Close'].iloc[-2] - 1) * 100) if len(df) > 1 else 0,
                    '20_day': float((df['Close'].iloc[-1] / df['Close'].iloc[-21] - 1) * 100) if len(df) > 20 else 0
                }
            }
            
            return price_results
            
        except Exception as e:
            self.logger.error(f"Error in price analysis: {e}")
            return {'error': str(e)}
    
    async def _volume_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume patterns"""
        try:
            volume_results = {
                'current_volume': int(df['Volume'].iloc[-1]),
                'average_volume_20': float(df['Volume'].tail(20).mean())
            }
            
            return volume_results
            
        except Exception as e:
            self.logger.error(f"Error in volume analysis: {e}")
            return {'error': str(e)}
    
    async def _trend_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends"""
        try:
            trend_results = {}
            
            # Simple trend analysis
            if len(df) >= 20:
                sma_20 = df['Close'].rolling(window=20).mean()
                sma_50 = df['Close'].rolling(window=50).mean() if len(df) >= 50 else sma_20
                
                trend_results['trend_direction'] = 'Upward' if df['Close'].iloc[-1] > sma_20.iloc[-1] else 'Downward'
                
            return trend_results
            
        except Exception as e:
            self.logger.error(f"Error in trend analysis: {e}")
            return {'error': str(e)}
    
    async def compare_stocks(self, data: Dict[str, Dict[str, Any]], symbols: List[str], metrics: List[str] = None) -> Dict[str, Any]:
        """Compare multiple stocks"""
        try:
            comparison_results = {
                'symbols': symbols,
                'comparison_timestamp': datetime.now().isoformat(),
                'metrics': {}
            }
            
            # Process each stock
            stock_data = {}
            for symbol in symbols:
                if symbol in data:
                    historical = data[symbol].get('data', {}).get('historical', [])
                    df = pd.DataFrame(historical)
                    if not df.empty and 'Close' in df.columns:
                        stock_data[symbol] = df
            
            if not stock_data:
                return {'error': 'No valid stock data for comparison'}
            
            # Compare prices
            comparison_results['metrics']['price_comparison'] = {
                symbol: {
                    'current_price': float(df['Close'].iloc[-1]),
                    'price_change_20d': float((df['Close'].iloc[-1] / df['Close'].iloc[-21] - 1) * 100) if len(df) > 20 else 0
                }
                for symbol, df in stock_data.items()
            }
            
            return comparison_results
            
        except Exception as e:
            self.logger.error(f"Error in stock comparison: {e}")
            return {'error': str(e)}
    
    # Helper methods
    def _get_sma_signal(self, close, sma):
        if pd.isna(sma[-1]):
            return 'No Signal'
        return 'Buy' if close[-1] > sma[-1] else 'Sell'
    
    def _get_rsi_signal(self, rsi_value):
        if pd.isna(rsi_value):
            return 'No Signal'
        if rsi_value > 70:
            return 'Overbought'
        elif rsi_value < 30:
            return 'Oversold'
        else:
            return 'Neutral'
    
    def _get_macd_signal(self, macd, signal, histogram):
        if pd.isna(macd.iloc[-1]) or pd.isna(signal.iloc[-1]):
            return 'No Signal'
        
        if macd.iloc[-1] > signal.iloc[-1]:
            return 'Bullish'
        else:
            return 'Bearish'
    
    def _get_bollinger_signal(self, close, upper, lower):
        current_price = close[-1]
        if pd.isna(upper[-1]) or pd.isna(lower[-1]):
            return 'No Signal'
        
        if current_price > upper[-1]:
            return 'Overbought'
        elif current_price < lower[-1]:
            return 'Oversold'
        else:
            return 'Neutral'
    
    async def generate_market_insights(self, symbol: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI market insights based on analysis results"""
        try:
            if not self.ai_enabled:
                return {
                    'enabled': False,
                    'insights': 'AI insights disabled - no API key provided',
                    'market_sentiment': 'Unknown',
                    'key_factors': []
                }
            
            # Call Gemini AI for market insights
            response = await self.gemini_client.generate_market_insights(symbol, analysis_results)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating market insights for {symbol}: {e}")
            return {
                'enabled': False,
                'insights': f'Error generating insights: {str(e)}',
                'market_sentiment': 'Unknown',
                'key_factors': [],
                'error': str(e)
            }
    
    def _create_market_insights_prompt(self, symbol: str, analysis_results: Dict[str, Any]) -> str:
        """Create prompt for AI market insights"""
        price_analysis = analysis_results.get('price_analysis', {})
        technical_analysis = analysis_results.get('technical_analysis', {})
        risk_analysis = analysis_results.get('risk_analysis', {})
        trend_analysis = analysis_results.get('trend_analysis', {})
        
        prompt = f"""
Phân tích chuyên sâu về thị trường cho cổ phiếu {symbol}:

THÔNG TIN GIÁ CẢ:
- Giá hiện tại: {price_analysis.get('current_price', 'N/A')}
- Biến động 1 ngày: {price_analysis.get('price_changes', {}).get('1_day', 0):.2%}
- Biến động 1 tuần: {price_analysis.get('price_changes', {}).get('5_day', 0):.2%}
- Biến động 1 tháng: {price_analysis.get('price_changes', {}).get('20_day', 0):.2%}
- Vùng giá 52 tuần: {price_analysis.get('low_52w', 'N/A')} - {price_analysis.get('high_52w', 'N/A')}

CHỈ SỐ KỸ THUẬT:
- RSI: {technical_analysis.get('rsi', {}).get('current_value', 'N/A')} - {technical_analysis.get('rsi', {}).get('signal', 'N/A')}
- MACD: {technical_analysis.get('macd', {}).get('signal', 'N/A')}
- Bollinger Bands: {technical_analysis.get('bollinger_bands', {}).get('signal', 'N/A')}

RỦI RO VÀ BIẾN ĐỘNG:
- Volatility hàng năm: {risk_analysis.get('basic_metrics', {}).get('volatility_annual', 0):.2%}
- Sharpe Ratio: {risk_analysis.get('sharpe_ratio', 'N/A')}
- Max Drawdown: {risk_analysis.get('max_drawdown', 0):.2%}

XU HƯỚNG:
- Hướng xu hướng: {trend_analysis.get('trend_direction', 'N/A')}

Hãy đưa ra:
1. Tình hình thị trường tổng quan cho cổ phiếu này
2. Các yếu tố chính ảnh hưởng đến giá
3. Sentiment thị trường (Tích cực/Tiêu cực/Trung tính)
4. Cơ hội và rủi ro tiềm ẩn
5. Khuyến nghị về thời điểm quan sát hoặc hành động

Trả lời bằng tiếng Việt, chuyên nghiệp và chi tiết.
        """
        
        return prompt
    
    def _extract_sentiment(self, ai_response: str) -> str:
        """Extract market sentiment from AI response"""
        response_upper = ai_response.upper()
        
        positive_indicators = ['TÍCH CỰC', 'TĂNG TRƯỞNG', 'BULLISH', 'MUA', 'TÍCH CƯC']
        negative_indicators = ['TIÊU CỰC', 'GIẢM', 'BEARISH', 'BÁN', 'RỦI RO CAO']
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in response_upper)
        negative_count = sum(1 for indicator in negative_indicators if indicator in response_upper)
        
        if positive_count > negative_count:
            return 'Tích cực'
        elif negative_count > positive_count:
            return 'Tiêu cực'
        else:
            return 'Trung tính'
    
    def _extract_key_factors(self, ai_response: str) -> List[str]:
        """Extract key factors from AI response"""
        # Simple extraction based on common patterns
        factors = []
        
        # Look for numbered lists or bullet points
        lines = ai_response.split('\n')
        for line in lines:
            line = line.strip()
            if any(pattern in line.lower() for pattern in ['yếu tố', 'nguyên nhân', 'lý do', 'ảnh hưởng']):
                if len(line) > 10 and len(line) < 200:  # Reasonable length
                    factors.append(line)
        
        return factors[:5]  # Return max 5 factors 