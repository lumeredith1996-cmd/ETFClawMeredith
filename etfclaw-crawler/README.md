# ETFClaw 爬虫 - 安装与使用指南

## 功能概述

- 自动抓取雪球、微博用户的投资观点
- AI 自动打标签（📂分类 / ⭐重要程度 / 😤情绪）
- 生成可直接浏览的 HTML 页面
- 定时任务自动更新

---

## 快速安装（腾讯云 Linux 服务器）

### 方式一：自动安装（推荐）

SSH 登录服务器后执行：

```bash
# 下载安装脚本（先把 setup.sh 上传到服务器）
chmod +x setup.sh
./setup.sh
```

### 方式二：手动安装

```bash
# 1. 安装 Python 3
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 2. 创建项目目录
mkdir -p ~/etfclaw-crawler
cd ~/etfclaw-crawler

# 3. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 4. 安装依赖
pip install requests beautifulsoup4 lxml
```

---

## 配置步骤

### 1. 获取 Cookie

**雪球 Cookie：**
1. 打开浏览器，登录 https://xueqiu.com
2. 按 F12 打开开发者工具
3. 切换到 Network（网络）标签
4. 刷新页面，点击任意请求
5. 在 Headers 里找到 Cookie，复制全部内容

**微博 Cookie：**
1. 打开浏览器，登录 https://weibo.com
2. 按 F12 打开开发者工具
3. 切换到 Network 标签
4. 刷新页面，点击任意请求
5. 复制 Cookie 内容

### 2. 编辑配置

打开 `crawler.py`，找到配置区：

```python
CONFIG = {
    # 雪球 Cookie（粘贴你复制的）
    'xueqiu_cookie': 'xq_a_token=xxx; xq_r_token=xxx; ...',
    
    # 微博 Cookie
    'weibo_cookie': 'SUB=xxx; _T_WM=xxx; ...',
    
    # 要抓取的用户 ID（从 URL 获取）
    'xueqiu_users': ['2780816299'],  # 你的雪球 ID
    'weibo_users': ['1954395575'],    # 你的微博 ID
    
    # Groq API Key（可选，免费申请）
    # https://console.groq.com/keys
    'groq_api_key': '',  # 有 API 效果更好，没有也能用规则匹配
}
```

### 3. 申请 Groq API Key（可选但推荐）

1. 打开 https://console.groq.com
2. 用 Google/GitHub 账号登录
3. 点 "API Keys" → "Create Key"
4. 复制 Key 填入配置

---

## 运行爬虫

```bash
# 进入项目目录
cd ~/etfclaw-crawler

# 激活虚拟环境
source venv/bin/activate

# 运行爬虫
python3 crawler.py
```

输出示例：
```
🚀 ETFClaw 爬虫启动 - 2024-04-18 21:30:00

📡 抓取雪球...
   🤖 AI 标签: 当前市场环境下...
✅ xueqiu: 保存了 5 条新帖子，共 50 条

📡 抓取微博...
   🤖 AI 标签: 分享一个投资机会...
✅ weibo: 保存了 3 条新帖子，共 30 条

📄 生成页面...
✅ 生成 index.html，共 80 条帖子

✅ 完成！抓取了 8 条新帖子
```

---

## 设置定时任务（自动更新）

```bash
# 编辑 crontab
crontab -e

# 添加这行（每5分钟执行一次）
*/5 * * * * cd $HOME/etfclaw-crawler && source venv/bin/activate && python3 crawler.py >> logs/crawler.log 2>&1

# 保存退出
```

---

## 查看结果

```bash
# 查看生成的页面
cat data/index.html

# 查看日志
tail -f logs/crawler.log

# 或者用 Python 启动简单 HTTP 服务器预览
cd data
python3 -m http.server 8080
# 然后浏览器访问 http://你的服务器IP:8080
```

---

## 文件说明

```
etfclaw-crawler/
├── crawler.py      # 爬虫主程序
├── setup.sh        # 安装脚本
├── data/           # 数据目录
│   ├── xueqiu_posts.json   # 雪球帖子数据
│   ├── weibo_posts.json    # 微博帖子数据
│   └── index.html          # 生成的网页
└── logs/           # 日志目录
    └── crawler.log
```

---

## 常见问题

### Q: 抓取失败，提示 Cookie 无效？
A: Cookie 过期了，需要重新获取。Cookie 通常几天到几周有效。

### Q: 雪球/微博需要登录吗？
A: 是的，必须登录状态才能抓取用户数据。

### Q: 没有 Groq API 能用吗？
A: 可以！代码内置了基于规则的备用标签系统，准确率约 70-80%。

### Q: 怎么增加更多用户？
A: 在配置里修改 `xueqiu_users` 和 `weibo_users` 列表。

---

## 部署到 GitHub Pages（可选）

1. 把 `data/index.html` 推送到 GitHub 仓库
2. 开启 GitHub Pages
3. 就可以用域名访问了

---

## 技术支持

遇到问题可以截图发给我帮你看。
