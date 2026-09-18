@echo off
chcp 65001 >nul 2>&1
title Python 教学网页服务器

echo ====================================================
echo   高中数学竞赛 - Python 编程基础 教学网页
echo ====================================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.x
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 安装依赖
echo [1/2] 检查并安装依赖...
pip install -r requirements.txt -q

:: 启动服务器
echo [2/2] 启动服务器...
echo.
echo   请在浏览器打开: http://127.0.0.1:5000
echo   按 Ctrl+C 停止服务器
echo.

python server.py

pause
