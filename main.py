#!/usr/bin/env python3
"""
Main entry point cho AI Financial Analyst MCP Server
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.mcp_server import MCPFinancialAnalystServer

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Financial Analyst MCP Server")
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/mcp_config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Server host"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Set up environment
    if not os.path.exists(".env"):
        print("Warning: .env file not found. Creating from config/api_keys.env")
        if os.path.exists("config/api_keys.env"):
            import shutil
            shutil.copy("config/api_keys.env", ".env")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create and run server
    try:
        server = MCPFinancialAnalystServer(config_path=args.config)
        print(f"Starting AI Financial Analyst MCP Server on {args.host}:{args.port}")
        print("Press Ctrl+C to stop the server")
        
        asyncio.run(server.run())
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 