#!/usr/bin/env python3
"""
Setup script cho AI Financial Analyst MCP
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_directories():
    """Tạo các thư mục cần thiết"""
    directories = [
        "data",
        "data/csv",
        "output",
        "output/charts",
        "output/reports",
        "logs",
        "src/agents",
        "src/core",
        "src/client",
        "config",
        "examples"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def setup_environment():
    """Setup environment file"""
    env_template = """# AI Financial Analyst MCP Environment Variables

# Alpha Vantage API Key (Free tier: 5 requests/minute, 500 requests/day)
# Get your key at: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# Financial Modeling Prep API Key (Optional)
FMP_API_KEY=your_fmp_api_key_here

# IEX Cloud API Key (Optional)
IEX_CLOUD_API_KEY=your_iex_cloud_api_key_here

# Quandl API Key (Optional)
QUANDL_API_KEY=your_quandl_api_key_here

# Deepseek API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Database Configuration
DATABASE_URL=sqlite:///./data/financial_data.db

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
"""
    
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_template)
        print("✅ Created .env file")
    else:
        print("⚠️ .env file already exists")

def install_dependencies():
    """Cài đặt dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    
    return True

def create_sample_data():
    """Tạo dữ liệu mẫu"""
    sample_csv = """Date,Open,High,Low,Close,Volume
2024-01-01,150.00,152.50,149.00,151.00,1000000
2024-01-02,151.00,153.00,150.50,152.50,1100000
2024-01-03,152.50,154.00,151.00,153.00,1200000
2024-01-04,153.00,155.00,152.00,154.50,1300000
2024-01-05,154.50,156.00,153.50,155.00,1400000
"""
    
    sample_file = Path("data/csv/SAMPLE.csv")
    if not sample_file.exists():
        with open(sample_file, "w") as f:
            f.write(sample_csv)
        print("✅ Created sample CSV data")

def check_python_version():
    """Kiểm tra phiên bản Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python version: {sys.version}")
    return True

def create_run_scripts():
    """Tạo script chạy hệ thống"""
    
    # Windows batch file
    windows_script = """@echo off
echo Starting AI Financial Analyst MCP Server...
python main.py
pause
"""
    
    with open("run_server.bat", "w") as f:
        f.write(windows_script)
    
    # Unix shell script
    unix_script = """#!/bin/bash
echo "Starting AI Financial Analyst MCP Server..."
python main.py
"""
    
    with open("run_server.sh", "w") as f:
        f.write(unix_script)
    
    # Make shell script executable
    os.chmod("run_server.sh", 0o755)
    
    print("✅ Created run scripts (run_server.bat, run_server.sh)")

def main():
    """Main setup function"""
    print("🚀 AI Financial Analyst MCP Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Setup environment
    print("\n🔧 Setting up environment...")
    setup_environment()
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not install_dependencies():
        print("❌ Setup failed due to dependency installation errors")
        sys.exit(1)
    
    # Create sample data
    print("\n📊 Creating sample data...")
    create_sample_data()
    
    # Create run scripts
    print("\n🏃 Creating run scripts...")
    create_run_scripts()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run the server: python main.py")
    print("3. Run examples: python examples/basic_usage.py")
    print("\n📚 Documentation: README.md")

if __name__ == "__main__":
    main() 