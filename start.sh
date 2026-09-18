#!/bin/bash
# 高中数学竞赛 - Python 编程基础 教学网页启动脚本

cd "$(dirname "$0")"

echo "===================================================="
echo "  高中数学竞赛 - Python 编程基础 教学网页"
echo "===================================================="
echo

# 检查 Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[错误] 未找到 Python，请先安装 Python 3.x"
        exit 1
    fi
    PYTHON=python
else
    PYTHON=python3
fi

# 安装依赖
echo "[1/2] 检查并安装依赖..."
$PYTHON -m pip install -r requirements.txt -q

# 启动服务器
echo "[2/2] 启动服务器..."
echo
echo "  请在浏览器打开: http://127.0.0.1:5000"
echo "  按 Ctrl+C 停止服务器"
echo

$PYTHON server.py
