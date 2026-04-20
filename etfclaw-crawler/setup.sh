#!/bin/bash
# ETFClaw 爬虫安装脚本 - Ubuntu/Debian Linux

set -e

echo "=========================================="
echo "  ETFClaw 爬虫安装脚本"
echo "=========================================="

# 1. 更新系统
echo ""
echo "📦 1. 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装 Python 和 pip
echo ""
echo "🐍 2. 安装 Python 3..."
if command -v python3 &> /dev/null; then
    echo "   Python3 已安装: $(python3 --version)"
else
    sudo apt install -y python3 python3-pip python3-venv
fi

# 3. 创建项目目录
echo ""
echo "📁 3. 创建项目目录..."
PROJECT_DIR="$HOME/etfclaw-crawler"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 4. 创建虚拟环境
echo ""
echo "🌐 4. 创建 Python 虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 5. 安装依赖
echo ""
echo "📥 5. 安装 Python 依赖包..."
pip install requests beautifulsoup4 lxml

# 6. 下载爬虫脚本
echo ""
echo "📥 6. 下载爬虫脚本..."
# 注意：需要把 crawler.py 上传到服务器

# 7. 设置定时任务
echo ""
echo "⏰ 8. 设置定时任务（每5分钟执行一次）..."
(crontab -l 2>/dev/null | grep -v "crawler.py"; echo "*/5 * * * * cd $PROJECT_DIR && source venv/bin/activate && python3 crawler.py >> logs/crawler.log 2>&1") | crontab -

# 8. 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

# 9. 创建 Cookie 配置提示
echo ""
echo "=========================================="
echo "  安装完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 上传 crawler.py 到 $PROJECT_DIR"
echo ""
echo "2. 编辑 crawler.py 填入 Cookie:"
echo "   - 雪球 Cookie: 登录 xueqiu.com 后按 F12 复制 cookie"
echo "   - 微博 Cookie: 登录 weibo.com 后按 F12 复制 cookie"
echo ""
echo "3. (可选) 申请 Groq API 免费 Key:"
echo "   https://console.groq.com/keys"
echo ""
echo "4. 测试运行:"
echo "   cd $PROJECT_DIR"
echo "   source venv/bin/activate"
echo "   python3 crawler.py"
echo ""
echo "5. 查看生成的页面:"
echo "   cat data/index.html"
echo ""
echo "6. 定时任务已设置，每5分钟自动执行"
echo ""
