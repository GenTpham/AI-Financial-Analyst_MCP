"""
MCP Client cho AI Financial Analyst
Client để tương tác với MCP Server và thực hiện các yêu cầu phân tích tài chính
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
from mcp.client import ClientSession
from mcp.types import (
    CallToolRequest, ListResourcesRequest, ListToolsRequest, 
    ReadResourceRequest, GetPromptRequest
)

class MCPFinancialAnalystClient:
    """MCP Client cho AI Financial Analyst"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session = None
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def connect(self):
        """Kết nối tới MCP Server"""
        try:
            self.session = ClientSession()
            await self.session.initialize()
            self.logger.info(f"Connected to MCP Server at {self.server_url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to server: {e}")
            return False
    
    async def disconnect(self):
        """Ngắt kết nối"""
        if self.session:
            await self.session.close()
            self.logger.info("Disconnected from MCP Server")
    
    async def list_available_tools(self) -> List[Dict[str, Any]]:
        """Lấy danh sách các tools có sẵn"""
        try:
            response = await self.session.list_tools(ListToolsRequest())
            tools = []
            for tool in response.tools:
                tools.append({
                    'name': tool.name,
                    'description': tool.description,
                    'schema': tool.inputSchema
                })
            return tools
        except Exception as e:
            self.logger.error(f"Error listing tools: {e}")
            return []
    
    async def fetch_stock_data(
        self, 
        symbol: str, 
        period: str = "1y", 
        interval: str = "1d", 
        source: str = "yahoo"
    ) -> Dict[str, Any]:
        """
        Lấy dữ liệu cổ phiếu
        
        Args:
            symbol: Mã cổ phiếu
            period: Khoảng thời gian
            interval: Khoảng cách dữ liệu
            source: Nguồn dữ liệu
        
        Returns:
            Dữ liệu cổ phiếu
        """
        try:
            request = CallToolRequest(
                name="fetch_stock_data",
                arguments={
                    "symbol": symbol,
                    "period": period,
                    "interval": interval,
                    "source": source
                }
            )
            
            response = await self.session.call_tool(request)
            
            if response.isError:
                raise Exception(f"Error fetching stock data: {response.content}")
            
            # Parse response content
            result = json.loads(response.content[0].text)
            self.logger.info(f"Successfully fetched data for {symbol}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error fetching stock data for {symbol}: {e}")
            raise
    
    async def analyze_stock(
        self, 
        symbol: str, 
        analysis_types: List[str] = None,
        indicators: List[str] = None
    ) -> Dict[str, Any]:
        """
        Phân tích cổ phiếu
        
        Args:
            symbol: Mã cổ phiếu
            analysis_types: Các loại phân tích
            indicators: Các chỉ báo kỹ thuật
        
        Returns:
            Kết quả phân tích
        """
        try:
            if analysis_types is None:
                analysis_types = ["technical", "fundamental", "risk"]
            
            request = CallToolRequest(
                name="analyze_stock",
                arguments={
                    "symbol": symbol,
                    "analysis_types": analysis_types,
                    "indicators": indicators
                }
            )
            
            response = await self.session.call_tool(request)
            
            if response.isError:
                raise Exception(f"Error analyzing stock: {response.content}")
            
            # Parse response content
            result = json.loads(response.content[0].text)
            self.logger.info(f"Successfully analyzed {symbol}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing stock {symbol}: {e}")
            raise
    
    async def create_visualization(
        self, 
        data: Dict[str, Any], 
        chart_type: str,
        title: str = None,
        save_path: str = None
    ) -> Dict[str, Any]:
        """
        Tạo biểu đồ
        
        Args:
            data: Dữ liệu để vẽ biểu đồ
            chart_type: Loại biểu đồ
            title: Tiêu đề biểu đồ
            save_path: Đường dẫn lưu biểu đồ
        
        Returns:
            Thông tin biểu đồ đã tạo
        """
        try:
            request = CallToolRequest(
                name="create_visualization",
                arguments={
                    "data": data,
                    "chart_type": chart_type,
                    "title": title,
                    "save_path": save_path
                }
            )
            
            response = await self.session.call_tool(request)
            
            if response.isError:
                raise Exception(f"Error creating visualization: {response.content}")
            
            # Parse response content
            result = json.loads(response.content[0].text)
            self.logger.info(f"Successfully created {chart_type} chart")
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating {chart_type} chart: {e}")
            raise
    
    async def generate_report(
        self, 
        symbol: str, 
        analysis_data: Dict[str, Any],
        report_format: str = "html",
        include_charts: bool = True
    ) -> Dict[str, Any]:
        """
        Tạo báo cáo
        
        Args:
            symbol: Mã cổ phiếu
            analysis_data: Dữ liệu phân tích
            report_format: Định dạng báo cáo
            include_charts: Bao gồm biểu đồ
        
        Returns:
            Thông tin báo cáo đã tạo
        """
        try:
            request = CallToolRequest(
                name="generate_report",
                arguments={
                    "symbol": symbol,
                    "analysis_data": analysis_data,
                    "report_format": report_format,
                    "include_charts": include_charts
                }
            )
            
            response = await self.session.call_tool(request)
            
            if response.isError:
                raise Exception(f"Error generating report: {response.content}")
            
            # Parse response content
            result = json.loads(response.content[0].text)
            self.logger.info(f"Successfully generated {report_format} report for {symbol}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating report for {symbol}: {e}")
            raise
    
    async def compare_stocks(
        self, 
        symbols: List[str], 
        metrics: List[str] = None,
        period: str = "1y"
    ) -> Dict[str, Any]:
        """
        So sánh nhiều cổ phiếu
        
        Args:
            symbols: Danh sách mã cổ phiếu
            metrics: Các chỉ số để so sánh
            period: Khoảng thời gian
        
        Returns:
            Kết quả so sánh
        """
        try:
            request = CallToolRequest(
                name="compare_stocks",
                arguments={
                    "symbols": symbols,
                    "metrics": metrics,
                    "period": period
                }
            )
            
            response = await self.session.call_tool(request)
            
            if response.isError:
                raise Exception(f"Error comparing stocks: {response.content}")
            
            # Parse response content
            result = json.loads(response.content[0].text)
            self.logger.info(f"Successfully compared stocks: {', '.join(symbols)}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error comparing stocks: {e}")
            raise
    
    async def get_available_resources(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tài nguyên có sẵn"""
        try:
            response = await self.session.list_resources(ListResourcesRequest())
            resources = []
            for resource in response.resources:
                resources.append({
                    'uri': resource.uri,
                    'name': resource.name,
                    'description': resource.description,
                    'mimeType': resource.mimeType
                })
            return resources
        except Exception as e:
            self.logger.error(f"Error listing resources: {e}")
            return []
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Đọc tài nguyên"""
        try:
            request = ReadResourceRequest(uri=uri)
            response = await self.session.read_resource(request)
            
            return {
                'uri': uri,
                'content': response.contents[0].text if response.contents else None
            }
        except Exception as e:
            self.logger.error(f"Error reading resource {uri}: {e}")
            return {}
    
    async def run_complete_analysis(
        self, 
        symbol: str, 
        analysis_types: List[str] = None,
        create_charts: bool = True,
        generate_report: bool = True,
        report_format: str = "html"
    ) -> Dict[str, Any]:
        """
        Chạy phân tích hoàn chỉnh cho một cổ phiếu
        
        Args:
            symbol: Mã cổ phiếu
            analysis_types: Các loại phân tích
            create_charts: Tạo biểu đồ
            generate_report: Tạo báo cáo
            report_format: Định dạng báo cáo
        
        Returns:
            Kết quả phân tích hoàn chỉnh
        """
        try:
            self.logger.info(f"Starting complete analysis for {symbol}")
            
            # 1. Fetch stock data
            self.logger.info("Fetching stock data...")
            stock_data = await self.fetch_stock_data(symbol)
            
            # 2. Analyze stock
            self.logger.info("Analyzing stock...")
            analysis_result = await self.analyze_stock(symbol, analysis_types)
            
            results = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'stock_data': stock_data,
                'analysis': analysis_result,
                'charts': [],
                'reports': []
            }
            
            # 3. Create charts if requested
            if create_charts:
                self.logger.info("Creating charts...")
                try:
                    # Create candlestick chart
                    candlestick_chart = await self.create_visualization(
                        data=analysis_result,
                        chart_type="candlestick",
                        title=f"{symbol} - Candlestick Chart"
                    )
                    results['charts'].append(candlestick_chart)
                    
                    # Create technical analysis chart
                    technical_chart = await self.create_visualization(
                        data=analysis_result,
                        chart_type="technical",
                        title=f"{symbol} - Technical Analysis"
                    )
                    results['charts'].append(technical_chart)
                    
                    # Create dashboard
                    dashboard = await self.create_visualization(
                        data=analysis_result,
                        chart_type="dashboard",
                        title=f"{symbol} - Analysis Dashboard"
                    )
                    results['charts'].append(dashboard)
                    
                except Exception as e:
                    self.logger.warning(f"Error creating charts: {e}")
            
            # 4. Generate report if requested
            if generate_report:
                self.logger.info("Generating report...")
                try:
                    report = await self.generate_report(
                        symbol=symbol,
                        analysis_data=analysis_result,
                        report_format=report_format,
                        include_charts=create_charts
                    )
                    results['reports'].append(report)
                except Exception as e:
                    self.logger.warning(f"Error generating report: {e}")
            
            self.logger.info(f"Complete analysis finished for {symbol}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in complete analysis for {symbol}: {e}")
            raise
    
    async def run_portfolio_analysis(
        self, 
        symbols: List[str],
        create_comparison_charts: bool = True,
        generate_summary_report: bool = True
    ) -> Dict[str, Any]:
        """
        Chạy phân tích danh mục đầu tư
        
        Args:
            symbols: Danh sách mã cổ phiếu
            create_comparison_charts: Tạo biểu đồ so sánh
            generate_summary_report: Tạo báo cáo tóm tắt
        
        Returns:
            Kết quả phân tích danh mục
        """
        try:
            self.logger.info(f"Starting portfolio analysis for {len(symbols)} stocks")
            
            portfolio_results = {
                'symbols': symbols,
                'timestamp': datetime.now().isoformat(),
                'individual_analysis': {},
                'comparison': {},
                'charts': [],
                'reports': []
            }
            
            # 1. Analyze each stock individually
            for symbol in symbols:
                self.logger.info(f"Analyzing {symbol}...")
                try:
                    analysis = await self.run_complete_analysis(
                        symbol=symbol,
                        create_charts=False,
                        generate_report=False
                    )
                    portfolio_results['individual_analysis'][symbol] = analysis
                except Exception as e:
                    self.logger.error(f"Error analyzing {symbol}: {e}")
                    continue
            
            # 2. Compare stocks
            if len(portfolio_results['individual_analysis']) > 1:
                self.logger.info("Comparing stocks...")
                try:
                    comparison = await self.compare_stocks(
                        symbols=list(portfolio_results['individual_analysis'].keys())
                    )
                    portfolio_results['comparison'] = comparison
                except Exception as e:
                    self.logger.warning(f"Error comparing stocks: {e}")
            
            # 3. Create comparison charts if requested
            if create_comparison_charts and portfolio_results['comparison']:
                self.logger.info("Creating comparison charts...")
                # Implementation would depend on visualization agent
                
            # 4. Generate summary report if requested
            if generate_summary_report:
                self.logger.info("Generating summary report...")
                # Implementation would depend on report generation agent
            
            self.logger.info("Portfolio analysis completed")
            return portfolio_results
            
        except Exception as e:
            self.logger.error(f"Error in portfolio analysis: {e}")
            raise

# Convenience functions for easy usage
class FinancialAnalystAPI:
    """Simplified API wrapper cho easy usage"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.client = MCPFinancialAnalystClient(server_url)
        self._connected = False
    
    async def __aenter__(self):
        await self.client.connect()
        self._connected = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._connected:
            await self.client.disconnect()
    
    async def analyze(self, symbol: str, **kwargs) -> Dict[str, Any]:
        """Quick analysis function"""
        return await self.client.run_complete_analysis(symbol, **kwargs)
    
    async def compare(self, symbols: List[str], **kwargs) -> Dict[str, Any]:
        """Quick comparison function"""
        return await self.client.run_portfolio_analysis(symbols, **kwargs)
    
    async def get_data(self, symbol: str, **kwargs) -> Dict[str, Any]:
        """Quick data fetch function"""
        return await self.client.fetch_stock_data(symbol, **kwargs)
    
    async def create_chart(self, data: Dict[str, Any], chart_type: str, **kwargs) -> Dict[str, Any]:
        """Quick chart creation function"""
        return await self.client.create_visualization(data, chart_type, **kwargs) 