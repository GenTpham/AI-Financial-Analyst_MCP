@echo off
title AI Financial Analyst - Streamlit App
color 0A

echo.
echo  ================================================
echo   🚀 AI FINANCIAL ANALYST - STREAMLIT APP
echo  ================================================
echo.
echo  Đang khởi động ứng dụng web...
echo  Vui lòng chờ trong giây lát...
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ❌ Python không được cài đặt hoặc không có trong PATH
    echo  Vui lòng cài đặt Python 3.8+ và thử lại
    pause
    exit /b 1
)

REM Kiểm tra Streamlit
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo  ⚠️  Streamlit chưa được cài đặt
    echo  Đang cài đặt dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo  ❌ Lỗi cài đặt dependencies
        pause
        exit /b 1
    )
)

echo  ✅ Tất cả dependencies đã sẵn sàng
echo.
echo  🌐 Khởi động web app...
echo  📊 App sẽ mở tại: http://localhost:8501
echo.
echo  💡 Tip: Để tắt app, nhấn Ctrl+C trong terminal này
echo.

REM Khởi động Streamlit
python -m streamlit run streamlit_app.py --server.port=8501 --server.address=localhost --browser.gatherUsageStats=false

echo.
echo  ✅ App đã tắt
pause 