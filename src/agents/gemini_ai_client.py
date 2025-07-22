"""
Gemini AI Client - Tích hợp Google Gemini AI cho phân tích tài chính
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from correct path
load_dotenv('config/api_keys.env')

class GeminiAIClient:
    """Client để tương tác với Google Gemini AI"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.model = None
        self.is_enabled = False
        self._setup_client()
    
    def _setup_client(self):
        """Khởi tạo Gemini AI client"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key or api_key == 'your_gemini_api_key_here':
                self.logger.warning("Gemini API key not found")
                return
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Initialize model
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.is_enabled = True
            
            self.logger.info(f"✅ Gemini AI client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error setting up Gemini client: {e}")
            self.is_enabled = False
    
    async def generate_market_insights(self, symbol: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo market insights sử dụng Gemini AI"""
        
        if not self.is_enabled:
            return {
                'enabled': False,
                'error': 'Gemini AI not available',
                'insights': 'AI insights không khả dụng',
                'market_sentiment': 'Unknown',
                'key_factors': []
            }
        
        try:
            # Tạo prompt chi tiết
            prompt = self._create_market_analysis_prompt(symbol, analysis_data)
            
            # Gọi Gemini API
            response = await asyncio.to_thread(
                self.model.generate_content, 
                prompt
            )
            
            ai_response = response.text
            
            # Parse response
            return {
                'enabled': True,
                'source': 'Gemini-AI',
                'insights': ai_response,
                'market_sentiment': self._extract_sentiment(ai_response),
                'key_factors': self._extract_key_factors(ai_response),
                'confidence': 'High',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating Gemini insights: {e}")
            return {
                'enabled': False,
                'error': str(e),
                'insights': f'Lỗi AI: {str(e)}',
                'market_sentiment': 'Unknown',
                'key_factors': []
            }
    
    def _create_market_analysis_prompt(self, symbol: str, analysis_data: Dict[str, Any]) -> str:
        """Tạo prompt chi tiết cho phân tích thị trường"""
        
        # Extract data safely
        technical_analysis = analysis_data.get('technical_analysis', {})
        risk_analysis = analysis_data.get('risk_analysis', {})
        price_analysis = analysis_data.get('price_analysis', {})
        
        # Get current price safely
        current_price = price_analysis.get('current_price', 0)
        if isinstance(current_price, (list, tuple)) and len(current_price) > 0:
            current_price = current_price[-1]
        elif not isinstance(current_price, (int, float)):
            current_price = 0
        
        # Get technical indicators safely
        rsi = technical_analysis.get('rsi', {})
        if isinstance(rsi, dict):
            rsi_value = rsi.get('current', 50)
            if isinstance(rsi_value, (list, tuple)) and len(rsi_value) > 0:
                rsi_value = rsi_value[-1]
        else:
            rsi_value = 50
        
        macd = technical_analysis.get('macd', {})
        if isinstance(macd, dict):
            macd_current = macd.get('current', {})
            if isinstance(macd_current, dict):
                macd_value = macd_current.get('macd', 0)
            else:
                macd_value = 0
        else:
            macd_value = 0
        
        # Get risk metrics safely
        risk_basic = risk_analysis.get('basic_metrics', {})
        volatility = risk_basic.get('volatility_annual', 0.2) if isinstance(risk_basic, dict) else 0.2
        
        sharpe_ratio = risk_analysis.get('sharpe_ratio', 0)
        if isinstance(sharpe_ratio, (list, tuple)) and len(sharpe_ratio) > 0:
            sharpe_ratio = sharpe_ratio[-1]
        elif not isinstance(sharpe_ratio, (int, float)):
            sharpe_ratio = 0
        
        max_drawdown = risk_analysis.get('max_drawdown', {})
        if isinstance(max_drawdown, dict):
            max_dd_value = max_drawdown.get('max_drawdown', 0)
        else:
            max_dd_value = 0
        
        # Ensure all values are numbers
        try:
            current_price = float(current_price) if current_price else 0
            rsi_value = float(rsi_value) if rsi_value else 50
            macd_value = float(macd_value) if macd_value else 0
            volatility = float(volatility) if volatility else 0.2
            sharpe_ratio = float(sharpe_ratio) if sharpe_ratio else 0
            max_dd_value = float(max_dd_value) if max_dd_value else 0
        except (ValueError, TypeError):
            # Use default values if conversion fails
            current_price = 0
            rsi_value = 50
            macd_value = 0
            volatility = 0.2
            sharpe_ratio = 0
            max_dd_value = 0
        
        # Get current date for analysis
        current_date = datetime.now().strftime("%d/%m/%Y")
        current_time = datetime.now().strftime("%H:%M")
        
        prompt = f"""
Bạn là một chuyên gia phân tích tài chính hàng đầu với 20+ năm kinh nghiệm. 
Hãy phân tích cổ phiếu {symbol} dựa trên dữ liệu MỚI NHẤT và đưa ra insights chuyên nghiệp.

⏰ THỜI GIAN PHÂN TÍCH: {current_date} lúc {current_time} (Dữ liệu thời gian thực)

📊 DỮ LIỆU PHÂN TÍCH MỚI NHẤT:

🏷️ Cổ phiếu: {symbol}
💰 Giá hiện tại: ${current_price:.2f} (cập nhật mới nhất)

📈 PHÂN TÍCH KỸ THUẬT:
• RSI: {rsi_value:.1f}
• MACD: {macd_value:.4f}
• Các tín hiệu kỹ thuật khác có sẵn

⚖️ PHÂN TÍCH RỦI RO:
• Volatility hàng năm: {volatility:.2%}
• Sharpe Ratio: {sharpe_ratio:.2f}
• Max Drawdown: {max_dd_value:.2%}

🎯 YÊU CẦU PHÂN TÍCH:

1. **TÌNH HÌNH THỊ TRƯỜNG HIỆN TẠI:**
   - Đánh giá tổng quan về xu hướng giá
   - Phân tích momentum và tâm lý thị trường

2. **CÁC YẾU TỐ CHÍNH:**
   - Xác định 3-5 yếu tố quan trọng nhất ảnh hưởng đến giá
   - Phân tích tín hiệu kỹ thuật và ý nghĩa

3. **ĐÁNH GIÁ RỦI RO:**
   - Mức độ rủi ro: Thấp/Trung bình/Cao
   - Các rủi ro tiềm ẩn cần lưu ý

4. **KHUYẾN NGHỊ ĐẦU TƯ:**
   - Quyết định: MUA/BÁN/GIỮ
   - Lý do chi tiết (tối thiểu 100 từ)
   - Thời gian nắm giữ khuyến nghị
   - Mức giá mục tiêu (nếu có)

5. **OUTLOOK:**
   - Dự báo ngắn hạn (1-3 tháng)
   - Các yếu tố cần theo dõi

⚠️ LƯU Ý QUAN TRỌNG:
- Sử dụng ngày {current_date} làm ngày phân tích
- KHÔNG sử dụng bất kỳ ngày nào khác (như 2023 hay các năm cũ)
- Đây là dữ liệu và phân tích HIỆN TẠI, không phải lịch sử
- Tập trung vào xu hướng và tình hình thị trường GẦN ĐÂY

Hãy trả lời bằng tiếng Việt, chuyên nghiệp và có căn cứ. 
Sử dụng emoji để làm rõ các phần và dễ đọc.
        """
        
        return prompt
    
    def _extract_sentiment(self, ai_response: str) -> str:
        """Trích xuất market sentiment từ AI response"""
        response_upper = ai_response.upper()
        
        # Positive indicators
        positive_words = ['MUA', 'BUY', 'TÍCH CỰC', 'TĂNG', 'BULLISH', 'TĂNG TRƯỞNG']
        negative_words = ['BÁN', 'SELL', 'TIÊU CỰC', 'GIẢM', 'BEARISH', 'RỦI RO CAO']
        
        positive_count = sum(1 for word in positive_words if word in response_upper)
        negative_count = sum(1 for word in negative_words if word in response_upper)
        
        if positive_count > negative_count:
            return 'Tích cực'
        elif negative_count > positive_count:
            return 'Tiêu cực'
        else:
            return 'Trung tính'
    
    def _extract_key_factors(self, ai_response: str) -> list:
        """Trích xuất key factors từ AI response"""
        factors = []
        
        # Split by common bullet points and numbering
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for bullet points or numbered items
            if any(marker in line for marker in ['•', '-', '*', '1.', '2.', '3.', '4.', '5.']):
                if len(line) > 10:  # Avoid very short lines
                    # Clean up the line
                    clean_line = line.lstrip('•-*123456789. ').strip()
                    if clean_line:
                        factors.append(clean_line)
        
        # Limit to top 5 factors
        return factors[:5]
    
    async def generate_investment_recommendation(self, symbol: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo khuyến nghị đầu tư chi tiết"""
        
        if not self.is_enabled:
            return {
                'enabled': False,
                'decision': 'GIỮ',
                'reasoning': 'AI không khả dụng',
                'risk_level': 'Không xác định'
            }
        
        try:
            prompt = self._create_investment_prompt(symbol, analysis_data)
            
            response = await asyncio.to_thread(
                self.model.generate_content, 
                prompt
            )
            
            ai_response = response.text
            
            # Parse recommendation
            decision = self._extract_decision(ai_response)
            risk_level = self._extract_risk_level(ai_response)
            
            return {
                'enabled': True,
                'source': 'Gemini-AI',
                'decision': decision,
                'reasoning': ai_response,
                'risk_level': risk_level,
                'confidence': 'High',
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating investment recommendation: {e}")
            return {
                'enabled': False,
                'decision': 'GIỮ',
                'reasoning': f'Lỗi AI: {str(e)}',
                'risk_level': 'Không xác định'
            }
    
    def _create_investment_prompt(self, symbol: str, analysis_data: Dict[str, Any]) -> str:
        """Tạo prompt cho khuyến nghị đầu tư"""
        
        # Get current date for analysis
        current_date = datetime.now().strftime("%d/%m/%Y")
        current_time = datetime.now().strftime("%H:%M")
        
        prompt = f"""
Bạn là một cố vấn đầu tư chuyên nghiệp. Hãy đưa ra khuyến nghị đầu tư cụ thể cho cổ phiếu {symbol}.

⏰ THỜI GIAN PHÂN TÍCH: {current_date} lúc {current_time} (Dữ liệu thời gian thực)

Dựa trên dữ liệu phân tích MỚI NHẤT đã có, hãy trả lời:

1. **QUYẾT ĐỊNH ĐẦU TƯ:** MUA/BÁN/GIỮ
2. **LÝ DO CHI TIẾT:** (tối thiểu 150 từ)
3. **MỨC ĐỘ RỦI RO:** Thấp/Trung bình/Cao
4. **THỜI GIAN NẮM GIỮ:** Ngắn hạn/Trung hạn/Dài hạn
5. **ĐIỀU KIỆN DỪNG LỖ:** Mức giá cụ thể
6. **MỤC TIÊU GIÁ:** (nếu có)

⚠️ LƯU Ý: Sử dụng ngày {current_date} làm ngày phân tích. Đây là khuyến nghị HIỆN TẠI, không phải lịch sử.

Hãy đưa ra khuyến nghị rõ ràng, có căn cứ và thực tế.
        """
        
        return prompt
    
    def _extract_decision(self, ai_response: str) -> str:
        """Trích xuất quyết định đầu tư"""
        response_upper = ai_response.upper()
        
        if any(word in response_upper for word in ['MUA', 'BUY', 'STRONG BUY']):
            return 'MUA'
        elif any(word in response_upper for word in ['BÁN', 'SELL', 'STRONG SELL']):
            return 'BÁN'
        else:
            return 'GIỮ'
    
    def _extract_risk_level(self, ai_response: str) -> str:
        """Trích xuất mức độ rủi ro"""
        response_upper = ai_response.upper()
        
        if 'RỦI RO THẤP' in response_upper or 'LOW RISK' in response_upper:
            return 'Thấp'
        elif 'RỦI RO CAO' in response_upper or 'HIGH RISK' in response_upper:
            return 'Cao'
        else:
            return 'Trung bình' 