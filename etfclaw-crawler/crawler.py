#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETFClaw 爬虫 - 雪球/微博内容抓取 + AI 自动打标签
作者: OpenClaw
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os
from datetime import datetime, timedelta
import hashlib

# ========== 配置区 ==========
CONFIG = {
    # 你的雪球 Cookie（需要登录雪球后从浏览器复制）
    'xueqiu_cookie': 'your_xueqiu_cookie_here',
    
    # 你的微博 Cookie（需要登录微博后从浏览器复制）  
    'weibo_cookie': 'your_weibo_cookie_here',
    
    # 要抓取的用户 ID
    'xueqiu_users': ['2780816299'],
    'weibo_users': ['1954395575'],
    
    # AI API 配置（使用 Groq 免费 API，速度快）
    'groq_api_key': 'your_groq_api_key_here',  # 去 https://console.groq.com 免费申请
    
    # 数据存储目录
    'data_dir': './data',
    
    # 抓取间隔（秒）
    'request_interval': 2
}

# ========== 雪球爬虫 ==========
class XueqiuCrawler:
    BASE_URL = 'https://xueqiu.com'
    
    def __init__(self, cookie, user_id):
        self.cookie = cookie
        self.user_id = user_id
        self.session = requests.Session()
        self.session.headers.update({
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': f'https://xueqiu.com/u/{user_id}'
        })
    
    def get_user_tweets(self, page=1, count=10):
        """获取用户最新帖子"""
        url = f'{self.BASE_URL}/statuses/user_timeline.json'
        params = {
            'user_id': self.user_id,
            'page': page,
            'count': count
        }
        
        try:
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            
            if data.get('statuses'):
                return [{
                    'id': str(t['id']),
                    'platform': 'xueqiu',
                    'user_id': self.user_id,
                    'username': t['user']['screen_name'],
                    'content': self._clean_html(t.get('text', '')),
                    'created_at': t.get('created_at', ''),
                    'time_ago': self._time_ago(t.get('created_at', '')),
                    'like_count': t.get('like_count', 0),
                    'retweet_count': t.get('retweet_count', 0),
                    'comment_count': t.get('comments_count', 0),
                    'url': f"https://xueqiu.com/{self.user_id}/{t['id']}"
                } for t in data['statuses']]
            return []
        except Exception as e:
            print(f"❌ 雪球抓取失败: {e}")
            return []
    
    def _clean_html(self, html):
        """清理 HTML 标签"""
        soup = BeautifulSoup(html, 'html.parser')
        return soup.get_text(strip=True)
    
    def _time_ago(self, timestamp):
        """时间戳转相对时间"""
        if not timestamp:
            return ''
        try:
            dt = datetime.fromtimestamp(int(timestamp) / 1000)
            delta = datetime.now() - dt
            if delta < timedelta(minutes=1):
                return '刚刚'
            elif delta < timedelta(hours=1):
                return f'{int(delta.total_seconds() / 60)}分钟前'
            elif delta < timedelta(days=1):
                return f'{int(delta.total_seconds() / 3600)}小时前'
            elif delta < timedelta(days=7):
                return f'{int(delta.days)}天前'
            else:
                return dt.strftime('%m-%d')
        except:
            return ''


# ========== 微博爬虫 ==========
class WeiboCrawler:
    BASE_URL = 'https://weibo.com'
    
    def __init__(self, cookie, user_id):
        self.cookie = cookie
        self.user_id = user_id
        self.session = requests.Session()
        self.session.headers.update({
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': f'https://weibo.com/u/{user_id}'
        })
    
    def get_user_tweets(self, page=1):
        """获取用户最新帖子"""
        url = f'{self.BASE_URL}/ajax/profile/getUserInfo'
        params = {
            'uid': self.user_id,
            'page': page
        }
        
        try:
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            
            if data.get('ok') == 1:
                user_info = data.get('data', {})
                # 微博需要更复杂的 API，这里用简化的 mblog 接口
                mblog_url = f'{self.BASE_URL}/ajax/statuses/mymblog'
                mblog_params = {
                    'uid': self.user_id,
                    'page': page,
                    'feature': 0
                }
                mblog_resp = self.session.get(mblog_url, params=mblog_params, timeout=10)
                mblog_data = mblog_resp.json()
                
                if mblog_data.get('ok') == 1:
                    posts = mblog_data.get('data', {}).get('list', [])
                    return [{
                        'id': str(p['id']),
                        'platform': 'weibo',
                        'user_id': self.user_id,
                        'username': user_info.get('screen_name', ''),
                        'content': p.get('text_raw', p.get('text', '')),
                        'created_at': p.get('created_at', ''),
                        'time_ago': self._time_ago(p.get('created_at', '')),
                        'like_count': p.get('attitudes_count', 0),
                        'retweet_count': p.get('reposts_count', 0),
                        'comment_count': p.get('comments_count', 0),
                        'url': f"https://weibo.com/{self.user_id}/{p['id']}"
                    } for p in posts]
            return []
        except Exception as e:
            print(f"❌ 微博抓取失败: {e}")
            return []
    
    def _time_ago(self, time_str):
        """时间字符串转相对时间"""
        if not time_str:
            return ''
        try:
            # 微博格式: Thu Apr 18 21:00:00 +0800 2024
            dt = datetime.strptime(time_str, '%a %b %d %H:%M:%S +0800 %Y')
            delta = datetime.now() - dt
            if delta < timedelta(minutes=1):
                return '刚刚'
            elif delta < timedelta(hours=1):
                return f'{int(delta.total_seconds() / 60)}分钟前'
            elif delta < timedelta(days=1):
                return f'{int(delta.total_seconds() / 3600)}小时前'
            elif delta < timedelta(days=7):
                return f'{int(delta.days)}天前'
            else:
                return dt.strftime('%m-%d')
        except:
            return time_str


# ========== AI 标签服务 ==========
class AITagger:
    """使用 Groq API 进行内容分类和情绪分析（免费，速度快）"""
    
    SYSTEM_PROMPT = """你是一个投资内容分析助手。请分析每条帖子并返回以下信息：
1. category: 市场分析/基金选择/宏观策略/板块解读/风险提示/理财知识/其他
2. importance: high(重要)/mid(一般)/low(参考)
3. sentiment: bullish(看多)/bearish(看空)/neutral(中性)
4. summary: 一句话总结（不超过20字）

请直接返回JSON格式，不要其他内容。"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = 'https://api.groq.com/openai/v1/chat/completions'
        self.model = 'llama-3.1-8b-instant'  # 免费模型，速度快
    
    def tag(self, content):
        """对内容进行 AI 标签分析"""
        if not self.api_key or self.api_key == 'your_groq_api_key_here':
            # 没有 API key 时使用规则匹配
            return self._rule_based_tag(content)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': self.SYSTEM_PROMPT},
                    {'role': 'user', 'content': content[:500]}  # 限制内容长度
                ],
                'temperature': 0.3
            }
            
            resp = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            result = resp.json()
            
            if 'choices' in result:
                text = result['choices'][0]['message']['content']
                # 尝试解析 JSON
                try:
                    return json.loads(text)
                except:
                    return self._parse_ai_response(text)
            return self._rule_based_tag(content)
                
        except Exception as e:
            print(f"⚠️ AI 标签失败，使用规则匹配: {e}")
            return self._rule_based_tag(content)
    
    def _rule_based_tag(self, content):
        """基于规则的简单标签（无 API 时备用）"""
        content_lower = content.lower()
        
        # 情绪判断
        bullish_words = ['看好', '买入', '做多', '增持', '机会', '涨', '牛市', '配置', '布局', '价值', '低估', '增长']
        bearish_words = ['看空', '卖出', '做空', '减持', '风险', '跌', '熊市', '止损', '高估', '谨慎', '警惕', '减持']
        
        sentiment = 'neutral'
        bullish_count = sum(1 for w in bullish_words if w in content)
        bearish_count = sum(1 for w in bearish_words if w in content)
        if bullish_count > bearish_count and bullish_count >= 2:
            sentiment = 'bullish'
        elif bearish_count > bullish_count and bearish_count >= 2:
            sentiment = 'bearish'
        
        # 分类判断
        category_keywords = {
            'market': ['市场', '大盘', '指数', '行情', '走势', 'A股', '港股', '美股'],
            'fund': ['基金', 'ETF', '净值', '定投', '持仓', '基金经理'],
            'macro': ['宏观', '经济', 'CPI', 'GDP', '政策', '央行', '美联储', '利率'],
            'sector': ['板块', '行业', '半导体', '新能源', '消费', '医药', '金融', '地产'],
            'risk': ['风险', '止损', '仓位', '回撤', '波动', '黑天鹅'],
            'edu': ['学习', '知识', '科普', '理财', '入门', '基础']
        }
        
        category = 'other'
        for cat, keywords in category_keywords.items():
            if any(kw in content for kw in keywords):
                category = cat
                break
        
        # 重要程度（根据内容长度和互动数大致判断）
        importance = 'mid' if len(content) > 100 else 'low'
        
        return {
            'category': category,
            'categoryName': {'market': '市场分析', 'fund': '基金选择', 'macro': '宏观策略', 
                           'sector': '板块解读', 'risk': '风险提示', 'edu': '理财知识', 
                           'other': '其他'}[category],
            'importance': importance,
            'sentiment': sentiment,
            'summary': content[:20] + '...' if len(content) > 20 else content
        }
    
    def _parse_ai_response(self, text):
        """解析 AI 返回的文本"""
        try:
            # 尝试提取 JSON
            import re
            match = re.search(r'\{[^}]+\}', text)
            if match:
                return json.loads(match.group())
        except:
            pass
        return self._rule_based_tag(text)


# ========== 数据存储 ==========
class DataStore:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_posts(self, posts, platform):
        """保存帖子到 JSON 文件"""
        filename = os.path.join(self.data_dir, f'{platform}_posts.json')
        
        # 读取现有数据
        existing = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except:
                existing = []
        
        # 合并去重
        existing_ids = {p['id'] for p in existing}
        new_posts = [p for p in posts if p['id'] not in existing_ids]
        
        # 合并（新的在前）
        updated = new_posts + existing
        # 保留最多 500 条
        updated = updated[:500]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(updated, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {platform}: 保存了 {len(new_posts)} 条新帖子，共 {len(updated)} 条")
        return new_posts
    
    def load_all_posts(self):
        """加载所有帖子"""
        all_posts = []
        
        for platform in ['xueqiu', 'weibo']:
            filename = os.path.join(self.data_dir, f'{platform}_posts.json')
            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        posts = json.load(f)
                        all_posts.extend(posts)
                except:
                    pass
        
        # 按时间排序
        all_posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return all_posts
    
    def generate_index(self, posts):
        """生成 index.html"""
        html_path = os.path.join(self.data_dir, 'index.html')
        
        # 为每个帖子添加标签
        for post in posts:
            post['categoryName'] = post.get('categoryName', '其他')
            post['importance'] = post.get('importance', 'mid')
            post['sentiment'] = post.get('sentiment', 'neutral')
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_html(posts))
        
        print(f"✅ 生成 index.html，共 {len(posts)} 条帖子")
        return html_path
    
    def _generate_html(self, posts):
        """生成 HTML 页面"""
        posts_json = json.dumps(posts, ensure_ascii=False)
        
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>投资大V观点追踪</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    :root {{
      --primary: #1a73e8;
      --success: #34a853;
      --danger: #ea4335;
      --warning: #fbbc04;
      --bg: #f8f9fa;
      --card-bg: #ffffff;
      --text: #202124;
      --text-secondary: #5f6368;
      --border: #e8eaed;
    }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; min-height: 100vh; }}
    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
    .header h1 {{ font-size: 1.5rem; margin-bottom: 8px; }}
    .header .subtitle {{ font-size: 0.85rem; opacity: 0.9; }}
    .controls {{ background: var(--card-bg); padding: 15px 20px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; }}
    .filter-btn {{ padding: 6px 12px; border: 1px solid var(--border); border-radius: 20px; background: white; cursor: pointer; font-size: 0.8rem; transition: all 0.2s; }}
    .filter-btn:hover {{ border-color: var(--primary); color: var(--primary); }}
    .filter-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); }}
    .refresh-btn {{ margin-left: auto; padding: 8px 16px; background: var(--primary); color: white; border: none; border-radius: 20px; cursor: pointer; font-size: 0.85rem; }}
    .stats {{ display: flex; gap: 20px; padding: 12px 20px; background: #e8f0fe; font-size: 0.8rem; color: var(--text-secondary); }}
    .main {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
    .card {{ background: var(--card-bg); border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
    .card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.12); }}
    .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }}
    .source-badge {{ display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 16px; font-size: 0.75rem; font-weight: 500; }}
    .source-xueqiu {{ background: #ffeced; color: #e53131; }}
    .source-weibo {{ background: #fff5e6; color: #eb6841; }}
    .time-ago {{ font-size: 0.75rem; color: var(--text-secondary); }}
    .tags {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }}
    .tag {{ padding: 3px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 500; }}
    .tag-category {{ background: #e3f2fd; color: #1565c0; }}
    .tag-importance-high {{ background: #ffebee; color: #c62828; }}
    .tag-importance-mid {{ background: #fff3e0; color: #ef6c00; }}
    .tag-importance-low {{ background: #f5f5f5; color: #616161; }}
    .tag-bullish {{ background: #e8f5e9; color: #2e7d32; }}
    .tag-bearish {{ background: #ffebee; color: #c62828; }}
    .tag-neutral {{ background: #f5f5f5; color: #616161; }}
    .card-content {{ font-size: 0.9rem; line-height: 1.7; color: var(--text); margin-bottom: 12px; }}
    .card-content.collapsed {{ max-height: 120px; overflow: hidden; position: relative; }}
    .card-content.collapsed::after {{ content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 40px; background: linear-gradient(transparent, var(--card-bg)); }}
    .expand-btn {{ color: var(--primary); cursor: pointer; font-size: 0.8rem; background: none; border: none; padding: 0; }}
    .card-footer {{ display: flex; gap: 12px; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border); }}
    .action-btn {{ display: flex; align-items: center; gap: 4px; font-size: 0.75rem; color: var(--text-secondary); text-decoration: none; }}
    .action-btn:hover {{ color: var(--primary); }}
    @media (max-width: 768px) {{ .header h1 {{ font-size: 1.2rem; }} .controls {{ padding: 12px; }} .card {{ padding: 14px; }} }}
  </style>
</head>
<body>
  <header class="header">
    <h1>📊 投资大V观点追踪</h1>
    <p class="subtitle">雪球 · 微博 · 🔄 自动更新</p>
  </header>
  <div class="controls">
    <button class="filter-btn active" data-filter="category" data-value="all">全部</button>
    <button class="filter-btn" data-filter="category" data-value="market">市场分析</button>
    <button class="filter-btn" data-filter="category" data-value="fund">基金选择</button>
    <button class="filter-btn" data-filter="category" data-value="macro">宏观策略</button>
    <button class="filter-btn" data-filter="category" data-value="sector">板块解读</button>
    <button class="filter-btn" data-filter="category" data-value="risk">风险提示</button>
    <button class="filter-btn" data-filter="sentiment" data-value="bullish">📈 看多</button>
    <button class="filter-btn" data-filter="sentiment" data-value="bearish">📉 看空</button>
    <button class="refresh-btn" onclick="location.reload()">🔄 刷新</button>
  </div>
  <div class="stats">
    <span>📌 共 <strong id="total-count">0</strong> 条</span>
    <span>📈 看多 <strong id="bullish-count">0</strong></span>
    <span>📉 看空 <strong id="bearish-count">0</strong></span>
    <span>🕐 <span id="update-time">--</span></span>
  </div>
  <main class="main" id="posts-container"></main>
<script>
const posts = {posts_json};
const categoryNames = {{ market: '市场分析', fund: '基金选择', macro: '宏观策略', sector: '板块解读', risk: '风险提示', edu: '理财知识', other: '其他' }};
const sentimentNames = {{ bullish: '看多', bearish: '看空', neutral: '中性' }};
const importanceEmoji = {{ high: '🔥', mid: '⚡', low: '💤' }};
const sentimentEmoji = {{ bullish: '📈', bearish: '📉', neutral: '➡️' }};
const platformIcon = {{ xueqiu: '❄️', weibo: '📮' }};

let filtered = [...posts];
let filters = {{ category: 'all', sentiment: 'all' }};

function render() {{
  filtered = posts.filter(p => {{
    if (filters.category !== 'all' && p.category !== filters.category) return false;
    if (filters.sentiment !== 'all' && p.sentiment !== filters.sentiment) return false;
    return true;
  }});
  
  document.getElementById('total-count').textContent = posts.length;
  document.getElementById('bullish-count').textContent = posts.filter(p => p.sentiment === 'bullish').length;
  document.getElementById('bearish-count').textContent = posts.filter(p => p.sentiment === 'bearish').length;
  document.getElementById('update-time').textContent = new Date().toLocaleString('zh-CN');
  
  const container = document.getElementById('posts-container');
  if (filtered.length === 0) {{
    container.innerHTML = '<div style="text-align:center;padding:60px;color:#666;">暂无符合条件的内容</div>';
    return;
  }}
  
  container.innerHTML = filtered.map(p => `
    <article class="card">
      <div class="card-header">
        <span class="source-badge source-${{p.platform}}">${{platformIcon[p.platform] || '📎'}} ${{p.username || p.user_id}}</span>
        <span class="time-ago">${{p.time_ago || ''}}</span>
      </div>
      <div class="tags">
        <span class="tag tag-category">📂 ${{categoryNames[p.category] || '其他'}}</span>
        <span class="tag tag-importance-${{p.importance || 'mid'}}">${{importanceEmoji[p.importance] || '📌'}} ${{p.importance === 'high' ? '重要' : p.importance === 'low' ? '参考' : '一般'}}</span>
        <span class="tag tag-${{p.sentiment}}">${{sentimentEmoji[p.sentiment] || '📌'}} ${{sentimentNames[p.sentiment] || '中性'}}</span>
      </div>
      <div class="card-content collapsed" onclick="this.classList.toggle('collapsed')">${{p.content}}</div>
      <button class="expand-btn" onclick="this.previousElementSibling.classList.toggle('collapsed')">展开/收起</button>
      <div class="card-footer">
        <a href="${{p.url}}" target="_blank" class="action-btn">🔗 查看原文</a>
        <span class="action-btn">👍 ${{p.like_count || 0}}</span>
        <span class="action-btn">🔁 ${{p.retweet_count || 0}}</span>
        <span class="action-btn">💬 ${{p.comment_count || 0}}</span>
      </div>
    </article>
  `).join('');
}}

document.querySelectorAll('.filter-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    const filter = btn.dataset.filter;
    const value = btn.dataset.value;
    document.querySelectorAll(`[data-filter="${{filter}}"]`).forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    filters[filter] = value;
    render();
  }});
}});

render();
</script>
</body>
</html>'''


# ========== 主程序 ==========
def main():
    print(f"🚀 ETFClaw 爬虫启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 初始化
    os.makedirs(CONFIG['data_dir'], exist_ok=True)
    store = DataStore(CONFIG['data_dir'])
    tagger = AITagger(CONFIG.get('groq_api_key', ''))
    
    all_new_posts = []
    
    # 抓取雪球
    print("\\n📡 抓取雪球...")
    for user_id in CONFIG['xueqiu_users']:
        if not CONFIG['xueqiu_cookie'] or CONFIG['xueqiu_cookie'] == 'your_xueqiu_cookie_here':
            print(f"⚠️ 雪球 Cookie 未配置，跳过用户 {user_id}")
            continue
            
        crawler = XueqiuCrawler(CONFIG['xueqiu_cookie'], user_id)
        posts = crawler.get_user_tweets(count=20)
        
        if posts:
            # AI 打标签
            for post in posts:
                print(f"   🤖 AI 标签: {post['content'][:30]}...")
                tags = tagger.tag(post['content'])
                post.update(tags)
                time.sleep(0.5)  # 避免 API 限流
            
            new_posts = store.save_posts(posts, 'xueqiu')
            all_new_posts.extend(new_posts)
        
        time.sleep(CONFIG['request_interval'])
    
    # 抓取微博
    print("\\n📡 抓取微博...")
    for user_id in CONFIG['weibo_users']:
        if not CONFIG['weibo_cookie'] or CONFIG['weibo_cookie'] == 'your_weibo_cookie_here':
            print(f"⚠️ 微博 Cookie 未配置，跳过用户 {user_id}")
            continue
            
        crawler = WeiboCrawler(CONFIG['weibo_cookie'], user_id)
        posts = crawler.get_user_tweets()
        
        if posts:
            for post in posts:
                print(f"   🤖 AI 标签: {post['content'][:30]}...")
                tags = tagger.tag(post['content'])
                post.update(tags)
                time.sleep(0.5)
            
            new_posts = store.save_posts(posts, 'weibo')
            all_new_posts.extend(new_posts)
        
        time.sleep(CONFIG['request_interval'])
    
    # 生成 HTML
    print("\\n📄 生成页面...")
    all_posts = store.load_all_posts()
    
    # 重新生成所有帖子的标签（确保一致性）
    for post in all_posts:
        if not post.get('category'):
            tags = tagger.tag(post['content'])
            post.update(tags)
            time.sleep(0.3)
    
    store.generate_index(all_posts)
    
    print(f"\\n✅ 完成！抓取了 {len(all_new_posts)} 条新帖子")


if __name__ == '__main__':
    main()
