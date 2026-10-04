#!/bin/bash
# 一键配置 TeX Live 环境 (macOS) — 使用 TUNA 镜像源
# 用途：为数学竞赛论文写作配置完整的 LaTeX 编译环境

set -e

echo "===================================================="
echo "  一键配置 TeX Live (macOS + TUNA 镜像源)"
echo "===================================================="
echo

# ── 0. 平台检查 ──
if [[ "$(uname)" != "Darwin" ]]; then
    echo "[错误] 此脚本仅支持 macOS，当前系统: $(uname)"
    exit 1
fi

# ── 1. 安装 Homebrew（如未安装）──
if ! command -v brew &> /dev/null; then
    echo "[1/4] 安装 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # M 系列芯片: brew 装在 /opt/homebrew 下
    if [[ -f /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    echo "[1/4] Homebrew 已安装 ✓"
fi

# ── 2. 安装 MacTeX（TeX Live 完整版）──
if command -v pdflatex &> /dev/null; then
    echo "[2/4] TeX Live 已安装 ✓"
else
    echo "[2/4] 安装 MacTeX（TeX Live 完整版，约 4GB，请耐心等待）..."
    echo "       如需精简版 (~100MB)，请 Ctrl+C 后运行: brew install --cask basictex"
    brew install --cask mactex
    # 刷新 PATH 以识别新安装的 TeX 命令
    if [[ -d /Library/TeX/texbin ]]; then
        export PATH="/Library/TeX/texbin:$PATH"
    fi
fi

# ── 3. 配置 TUNA 镜像源 ──
TUNA_MIRROR="https://mirrors.tuna.tsinghua.edu.cn/CTAN/"
echo "[3/4] 配置 TUNA（清华）镜像源..."

if tlmgr option repository "$TUNA_MIRROR" 2>/dev/null; then
    echo "       镜像源已设置: $TUNA_MIRROR"
else
    echo "       普通权限不足，使用 sudo..."
    sudo tlmgr option repository "$TUNA_MIRROR"
    echo "       镜像源已设置: $TUNA_MIRROR"
fi

# ── 4. 更新 TeX Live 及安装中文宏包 ──
echo "[4/4] 更新 TeX Live 并安装中文支持宏包..."
echo "       首次更新可能需要几分钟，TUNA 源速度较快请放心等待..."

sudo tlmgr update --self
sudo tlmgr update --all

# 中文论文必备宏包
sudo tlmgr install cjk cjkpunct ctex xecjk zhnumber zhmetrics

echo
echo "===================================================="
echo "  ✅ TeX Live 环境配置完成！"
echo "===================================================="
echo
echo "  TeX 版本:  $(pdflatex --version | head -1)"
echo "  镜像源:    $TUNA_MIRROR"
echo
echo "  编译论文:  xelatex my-paper.tex"
echo "  更新宏包:  sudo tlmgr update --all"
echo "  安装宏包:  sudo tlmgr install <包名>"
echo
