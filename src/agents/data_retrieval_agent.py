"""
Data Retrieval Agent - Truy xuất dữ liệu tài chính từ nhiều nguồn
"""

import asyncio
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import requests
import os
from typing import Dict, List, Any, Optional, Union
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json

class DataRetrievalAgent:
    """Agent chịu trách nhiệm truy xuất dữ liệu tài chính"""
    
    def __init__(self, config: Dict[str, Any], data_sources_config: Dict[str, Any]):
        self.config = config
        self.data_sources_config = data_sources_config
        self.logger = logging.getLogger(__name__)
        
        # Initialize API clients
        self._setup_api_clients()
        
        # Data cache
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
    
    def _setup_api_clients(self):
        """Setup API clients for different data sources"""
        try:
            # Alpha Vantage
            alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            if alpha_vantage_key and alpha_vantage_key != 'your_alpha_vantage_api_key_here':
                self.av_ts = TimeSeries(key=alpha_vantage_key, output_format='pandas')
                self.av_fd = FundamentalData(key=alpha_vantage_key, output_format='pandas')
                self.logger.info("Alpha Vantage client initialized")
            else:
                self.av_ts = None
                self.av_fd = None
                self.logger.warning("Alpha Vantage API key not found")
                
        except Exception as e:
            self.logger.error(f"Error setting up API clients: {e}")
    
    async def fetch_stock_data(
        self, 
        symbol: str, 
        period: str = "1y", 
        interval: str = "1d", 
        source: str = "yahoo"
    ) -> Dict[str, Any]:
        """
        Fetch stock data from specified source
        
        Args:
            symbol: Stock symbol
            period: Time period
            interval: Data interval
            source: Data source (yahoo, alpha_vantage, csv)
        
        Returns:
            Dict containing stock data and metadata
        """
        cache_key = f"{symbol}_{period}_{interval}_{source}"
        
        # Check cache first
        if self._is_cached(cache_key):
            self.logger.info(f"Returning cached data for {symbol}")
            return self.cache[cache_key]['data']
        
        try:
            if source == "yahoo":
                data = await self._fetch_yahoo_data(symbol, period, interval)
            elif source == "alpha_vantage":
                data = await self._fetch_alpha_vantage_data(symbol, period, interval)
            elif source == "csv":
                data = await self._fetch_csv_data(symbol)
            else:
                raise ValueError(f"Unsupported data source: {source}")
            
            # Cache the result
            self._cache_data(cache_key, data)
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol} from {source}: {e}")
            raise
    
    async def _fetch_yahoo_data(self, symbol: str, period: str, interval: str) -> Dict[str, Any]:
        """Fetch data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            hist_data = ticker.history(period=period, interval=interval)
            
            if hist_data.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Get additional info
            info = ticker.info
            
            # Get financials (if available)
            try:
                financials = ticker.financials
                balance_sheet = ticker.balance_sheet
                cash_flow = ticker.cashflow
            except:
                financials = pd.DataFrame()
                balance_sheet = pd.DataFrame()
                cash_flow = pd.DataFrame()
            
            result = {
                "symbol": symbol,
                "source": "yahoo_finance",
                "data": {
                    "historical": hist_data.to_dict('records'),
                    "info": info,
                    "financials": financials.to_dict() if not financials.empty else {},
                    "balance_sheet": balance_sheet.to_dict() if not balance_sheet.empty else {},
                    "cash_flow": cash_flow.to_dict() if not cash_flow.empty else {}
                },
                "metadata": {
                    "period": period,
                    "interval": interval,
                    "last_updated": datetime.now().isoformat(),
                    "data_points": len(hist_data)
                }
            }
            
            self.logger.info(f"Successfully fetched Yahoo data for {symbol}: {len(hist_data)} data points")
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching Yahoo data for {symbol}: {e}")
            raise
    
    async def _fetch_alpha_vantage_data(self, symbol: str, period: str, interval: str) -> Dict[str, Any]:
        """Fetch data from Alpha Vantage"""
        if not self.av_ts:
            raise ValueError("Alpha Vantage client not initialized")
        
        try:
            # Map interval to Alpha Vantage format
            av_interval_map = {
                "1d": "daily",
                "1wk": "weekly",
                "1mo": "monthly"
            }
            
            av_interval = av_interval_map.get(interval, "daily")
            
            # Get time series data
            if av_interval == "daily":
                data, meta_data = self.av_ts.get_daily_adjusted(symbol=symbol, outputsize='full')
            elif av_interval == "weekly":
                data, meta_data = self.av_ts.get_weekly_adjusted(symbol=symbol)
            elif av_interval == "monthly":
                data, meta_data = self.av_ts.get_monthly_adjusted(symbol=symbol)
            else:
                raise ValueError(f"Unsupported interval for Alpha Vantage: {interval}")
            
            # Filter by period
            if period != "max":
                days_map = {
                    "1d": 1, "5d": 5, "1mo": 30, "3mo": 90, 
                    "6mo": 180, "1y": 365, "2y": 730, "5y": 1825
                }
                days = days_map.get(period, 365)
                cutoff_date = datetime.now() - timedelta(days=days)
                data = data[data.index >= cutoff_date]
            
            # Get company overview
            try:
                overview = self.av_fd.get_company_overview(symbol)[0]
            except:
                overview = {}
            
            result = {
                "symbol": symbol,
                "source": "alpha_vantage",
                "data": {
                    "historical": data.to_dict('records'),
                    "overview": overview,
                    "meta_data": meta_data
                },
                "metadata": {
                    "period": period,
                    "interval": interval,
                    "last_updated": datetime.now().isoformat(),
                    "data_points": len(data)
                }
            }
            
            self.logger.info(f"Successfully fetched Alpha Vantage data for {symbol}: {len(data)} data points")
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching Alpha Vantage data for {symbol}: {e}")
            raise
    
    async def _fetch_csv_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch data from CSV files"""
        try:
            csv_dir = self.data_sources_config.get('csv_data', {}).get('data_directory', './data/csv')
            csv_path = Path(csv_dir) / f"{symbol}.csv"
            
            if not csv_path.exists():
                raise FileNotFoundError(f"CSV file not found: {csv_path}")
            
            # Read CSV data
            data = pd.read_csv(csv_path)
            
            # Try to parse date column
            date_columns = ['Date', 'date', 'Datetime', 'datetime', 'timestamp']
            date_col = None
            for col in date_columns:
                if col in data.columns:
                    date_col = col
                    break
            
            if date_col:
                data[date_col] = pd.to_datetime(data[date_col])
                data.set_index(date_col, inplace=True)
            
            result = {
                "symbol": symbol,
                "source": "csv",
                "data": {
                    "historical": data.to_dict('records'),
                    "columns": list(data.columns)
                },
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "data_points": len(data),
                    "file_path": str(csv_path)
                }
            }
            
            self.logger.info(f"Successfully loaded CSV data for {symbol}: {len(data)} data points")
            return result
            
        except Exception as e:
            self.logger.error(f"Error loading CSV data for {symbol}: {e}")
            raise
    
    async def fetch_market_data(self, indices: List[str] = None) -> Dict[str, Any]:
        """Fetch market indices data"""
        if indices is None:
            indices = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow Jones, NASDAQ
        
        market_data = {}
        
        for index in indices:
            try:
                data = await self.fetch_stock_data(index, period="1y", source="yahoo")
                market_data[index] = data
            except Exception as e:
                self.logger.warning(f"Failed to fetch data for index {index}: {e}")
        
        return {
            "market_data": market_data,
            "last_updated": datetime.now().isoformat()
        }
    
    async def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean fetched data"""
        validation_results = {
            "is_valid": True,
            "issues": [],
            "cleaned_data": data
        }
        
        try:
            historical_data = data.get('data', {}).get('historical', [])
            
            if not historical_data:
                validation_results["is_valid"] = False
                validation_results["issues"].append("No historical data found")
                return validation_results
            
            # Check for required columns
            df = pd.DataFrame(historical_data)
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            for col in required_columns:
                if col not in df.columns:
                    validation_results["issues"].append(f"Missing required column: {col}")
            
            # Check for null values
            null_counts = df.isnull().sum()
            for col, count in null_counts.items():
                if count > 0:
                    validation_results["issues"].append(f"Found {count} null values in {col}")
            
            # Check data types
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in numeric_columns:
                if col in df.columns:
                    if not pd.api.types.is_numeric_dtype(df[col]):
                        validation_results["issues"].append(f"Non-numeric data in {col}")
            
            # Basic data validation
            if 'High' in df.columns and 'Low' in df.columns:
                invalid_high_low = df[df['High'] < df['Low']]
                if not invalid_high_low.empty:
                    validation_results["issues"].append(f"Found {len(invalid_high_low)} rows where High < Low")
            
            if validation_results["issues"]:
                validation_results["is_valid"] = False
            
            return validation_results
            
        except Exception as e:
            validation_results["is_valid"] = False
            validation_results["issues"].append(f"Validation error: {str(e)}")
            return validation_results
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]['timestamp']
        return datetime.now() - cache_time < self.cache_duration
    
    def _cache_data(self, cache_key: str, data: Dict[str, Any]):
        """Cache data with timestamp"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    async def get_available_symbols(self) -> List[str]:
        """Get list of available symbols from all sources"""
        symbols = []
        
        # Add popular symbols
        popular_symbols = [
            "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "NFLX",
            "JPM", "JNJ", "V", "PG", "MA", "UNH", "HD", "BAC"
        ]
        symbols.extend(popular_symbols)
        
        # Add indices
        indices = ["^GSPC", "^DJI", "^IXIC", "^RUT"]
        symbols.extend(indices)
        
        # Add crypto
        crypto = ["BTC-USD", "ETH-USD", "ADA-USD", "BNB-USD"]
        symbols.extend(crypto)
        
        # Check CSV directory for additional symbols
        try:
            csv_dir = self.data_sources_config.get('csv_data', {}).get('data_directory', './data/csv')
            csv_path = Path(csv_dir)
            if csv_path.exists():
                csv_files = list(csv_path.glob("*.csv"))
                csv_symbols = [f.stem for f in csv_files]
                symbols.extend(csv_symbols)
        except Exception as e:
            self.logger.warning(f"Error reading CSV directory: {e}")
        
        return list(set(symbols))  # Remove duplicates 