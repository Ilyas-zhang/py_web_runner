# LaTeX 环境配置说明（论文写作）

同学需要使用 LaTeX 撰写数学竞赛论文，需在本地安装 TeX Live 发行版。
本项目的网页公式渲染（KaTeX）不依赖本地 LaTeX，但**写论文必须装**。

## 一键安装（macOS）

```bash
chmod +x setup-latex.sh
./setup-latex.sh
```

脚本会自动完成：

1. 安装 Homebrew（如未安装）
2. 安装 MacTeX（即 TeX Live 完整版，约 4GB）
3. 配置 TUNA（清华）镜像源，加速宏包下载
4. 更新 TeX Live 及安装中文支持宏包（ctex、xecjk 等）

### 精简安装

磁盘空间有限时，可安装 BasicTeX（约 100MB），按需补充宏包：

```bash
brew install --cask basictex
export PATH="/Library/TeX/texbin:$PATH"
sudo tlmgr option repository https://mirrors.tuna.tsinghua.edu.cn/CTAN/
sudo tlmgr update --self
sudo tlmgr install cjk ctex xecjk cjkpunct zhnumber zhmetrics
```

> ⚠️ BasicTeX 仅含最小宏包集，编译论文时缺包用 `tlmgr install <包名>` 补装即可。

## 手动切换镜像源

已装 TeX Live 但下载慢？切换到 TUNA 源即可：

```bash
sudo tlmgr option repository https://mirrors.tuna.tsinghua.edu.cn/CTAN/
sudo tlmgr update --self --all
```

## 论文编译

中文论文请使用 `xelatex`（而非 `pdflatex`）：

```bash
xelatex my-paper.tex
```

## 常见问题

### M1/M2/M3 芯片 Mac brew 命令找不到

Homebrew 安装在 `/opt/homebrew` 下，需添加 PATH：

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### tlmgr 权限不足

macOS 上 tlmgr 操作系统级 TeX 目录需要 sudo：

```bash
sudo tlmgr update --all
sudo tlmgr install <包名>
```

### 编译中文论文报错

确保安装了中文宏包并用 xelatex 编译：

```bash
sudo tlmgr install ctex xecjk cjkpunct zhnumber
xelatex my-paper.tex    # 不要用 pdflatex
```
