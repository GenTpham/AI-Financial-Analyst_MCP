"""
MCP Server chính cho AI Financial Analyst
Quản lý các agents và xử lý requests từ client
"""

import asyncio
import json
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

from mcp.server import Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolResult, ListResourcesResult, ListToolsResult, ReadResourceResult
)

from ..agents.data_retrieval_agent import DataRetrievalAgent
from ..agents.data_analysis_agent import DataAnalysisAgent
from ..agents.visualization_agent import VisualizationAgent
from ..agents.report_generation_agent import ReportGenerationAgent

class MCPFinancialAnalystServer:
    """MCP Server cho AI Financial Analyst"""
    
    def __init__(self, config_path: str = "config/mcp_config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.server = Server("ai-financial-analyst")
        self.agents = {}
        self._setup_logging()
        self._initialize_agents()
        self._register_tools()
        self._register_resources()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration từ YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logging.error(f"Config file not found: {self.config_path}")
            return {}
        except yaml.YAMLError as e:
            logging.error(f"Error parsing config file: {e}")
            return {}
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        log_level = log_config.get('level', 'INFO')
        log_file = log_config.get('file', 'logs/mcp_server.log')
        
        # Tạo thư mục logs nếu chưa tồn tại
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _initialize_agents(self):
        """Initialize all agents"""
        agents_config = self.config.get('agents', {})
        
        # Initialize Data Retrieval Agent
        self.agents['data_retrieval'] = DataRetrievalAgent(
            config=agents_config.get('data_retrieval_agent', {}),
            data_sources_config=self.config.get('data_sources', {})
        )
        
        # Initialize Data Analysis Agent
        self.agents['data_analysis'] = DataAnalysisAgent(
            config=agents_config.get('data_analysis_agent', {}),
            analysis_config=self.config.get('analysis', {})
        )
        
        # Initialize Visualization Agent
        self.agents['visualization'] = VisualizationAgent(
            config=agents_config.get('visualization_agent', {}),
            output_config=self.config.get('output', {})
        )
        
        # Initialize Report Generation Agent
        self.agents['report_generation'] = ReportGenerationAgent(
            config=agents_config.get('report_generation_agent', {}),
            output_config=self.config.get('output', {})
        )
        
        self.logger.info("All agents initialized successfully")
    
    def _register_tools(self):
        """Register all available tools"""
        
        # Data Retrieval Tools
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List all available tools"""
            tools = [
                Tool(
                    name="fetch_stock_data",
                    description="Fetch stock data from various sources (Yahoo Finance, Alpha Vantage, CSV)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "Stock symbol (e.g., AAPL, GOOGL)"},
                            "period": {"type": "string", "description": "Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"},
                            "source": {"type": "string", "description": "Data source (yahoo, alpha_vantage, csv)", "default": "yahoo"},
                            "interval": {"type": "string", "description": "Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)", "default": "1d"}
                        },
                        "required": ["symbol"]
                    }
                ),
                Tool(
                    name="analyze_stock",
                    description="Perform comprehensive stock analysis including technical and fundamental analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "Stock symbol"},
                            "analysis_types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Types of analysis to perform (technical, fundamental, risk, correlation)"
                            },
                            "indicators": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Technical indicators to calculate"
                            }
                        },
                        "required": ["symbol"]
                    }
                ),
                Tool(
                    name="create_visualization",
                    description="Create various types of financial charts and visualizations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "data": {"type": "object", "description": "Data to visualize"},
                            "chart_type": {"type": "string", "description": "Chart type (line, candlestick, bar, heatmap, dashboard)"},
                            "title": {"type": "string", "description": "Chart title"},
                            "save_path": {"type": "string", "description": "Path to save the chart"}
                        },
                        "required": ["data", "chart_type"]
                    }
                ),
                Tool(
                    name="generate_report",
                    description="Generate comprehensive financial analysis report",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "Stock symbol"},
                            "analysis_data": {"type": "object", "description": "Analysis results"},
                            "report_format": {"type": "string", "description": "Report format (pdf, html, excel)", "default": "pdf"},
                            "include_charts": {"type": "boolean", "description": "Include charts in report", "default": True}
                        },
                        "required": ["symbol", "analysis_data"]
                    }
                ),
                Tool(
                    name="compare_stocks",
                    description="Compare multiple stocks with various metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbols": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of stock symbols to compare"
                            },
                            "metrics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Metrics to compare (price, volume, volatility, correlation)"
                            },
                            "period": {"type": "string", "description": "Time period for comparison", "default": "1y"}
                        },
                        "required": ["symbols"]
                    }
                )
            ]
            return ListToolsResult(tools=tools)
        
        # Tool execution handlers
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool execution"""
            try:
                self.logger.info(f"Executing tool: {name} with arguments: {arguments}")
                
                if name == "fetch_stock_data":
                    result = await self.agents['data_retrieval'].fetch_stock_data(**arguments)
                    
                elif name == "analyze_stock":
                    # First fetch data
                    symbol = arguments['symbol']
                    stock_data = await self.agents['data_retrieval'].fetch_stock_data(symbol=symbol)
                    
                    # Then analyze
                    result = await self.agents['data_analysis'].analyze_stock(
                        data=stock_data,
                        **arguments
                    )
                    
                elif name == "create_visualization":
                    result = await self.agents['visualization'].create_visualization(**arguments)
                    
                elif name == "generate_report":
                    result = await self.agents['report_generation'].generate_report(**arguments)
                    
                elif name == "compare_stocks":
                    # Fetch data for all symbols
                    symbols = arguments['symbols']
                    all_data = {}
                    for symbol in symbols:
                        data = await self.agents['data_retrieval'].fetch_stock_data(symbol=symbol)
                        all_data[symbol] = data
                    
                    # Analyze comparison
                    result = await self.agents['data_analysis'].compare_stocks(
                        data=all_data,
                        **arguments
                    )
                    
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return CallToolResult(
                    content=[TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
                )
                
            except Exception as e:
                self.logger.error(f"Error executing tool {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
    
    def _register_resources(self):
        """Register available resources"""
        
        @self.server.list_resources()
        async def handle_list_resources() -> ListResourcesResult:
            """List available resources"""
            resources = [
                Resource(
                    uri="config://mcp_config",
                    name="MCP Configuration",
                    description="Current MCP server configuration",
                    mimeType="application/yaml"
                ),
                Resource(
                    uri="data://sample_stocks",
                    name="Sample Stock Data",
                    description="Sample stock symbols for testing",
                    mimeType="application/json"
                )
            ]
            return ListResourcesResult(resources=resources)
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> ReadResourceResult:
            """Read resource content"""
            if uri == "config://mcp_config":
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=yaml.dump(self.config, default_flow_style=False)
                        )
                    ]
                )
            elif uri == "data://sample_stocks":
                sample_data = {
                    "popular_stocks": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
                    "crypto": ["BTC-USD", "ETH-USD", "ADA-USD"],
                    "indices": ["^GSPC", "^DJI", "^IXIC"]
                }
                return ReadResourceResult(
                    contents=[
                        TextContent(
                            type="text",
                            text=json.dumps(sample_data, indent=2)
                        )
                    ]
                )
            else:
                raise ValueError(f"Unknown resource: {uri}")
    
    async def run(self):
        """Run the MCP server"""
        host = self.config.get('server', {}).get('host', 'localhost')
        port = self.config.get('server', {}).get('port', 8000)
        
        self.logger.info(f"Starting MCP Financial Analyst Server on {host}:{port}")
        
        # Create necessary directories
        Path("logs").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        Path("output").mkdir(exist_ok=True)
        Path("output/charts").mkdir(exist_ok=True)
        Path("output/reports").mkdir(exist_ok=True)
        
        # Start server
        await self.server.run()

# Server instance
mcp_server = MCPFinancialAnalystServer()

if __name__ == "__main__":
    asyncio.run(mcp_server.run()) 