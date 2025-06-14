"""
Simple Config Manager for Streamlit App
"""
import os
from dotenv import load_dotenv

class ConfigManager:
    """Simple configuration manager"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # API Configuration
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.deepseek_base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        
        # Default settings
        self.default_period = '1y'
        self.default_symbols = ['AAPL', 'GOOGL', 'MSFT']
        
    def get_deepseek_config(self):
        """Get Deepseek API configuration"""
        return {
            'api_key': self.deepseek_api_key,
            'base_url': self.deepseek_base_url
        }
    
    def has_deepseek_key(self):
        """Check if Deepseek API key is configured"""
        return bool(self.deepseek_api_key and len(self.deepseek_api_key) > 10)
    
    def get_default_symbols(self):
        """Get default stock symbols"""
        return self.default_symbols
    
    def get_default_period(self):
        """Get default analysis period"""
        return self.default_period 