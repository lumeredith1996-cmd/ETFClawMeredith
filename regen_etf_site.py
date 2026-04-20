#!/usr/bin/env python3
"""Regenerate ETF map site according to 2026-04-20 requirements:
1. index.html: Keep only 四大渠道对比表，点击跳转products.html?chan=QDII
2. Remove all ⚠️ symbols from products
3. Remove duplicate type filters in sub-bar
4. 内地可买: keep only QDII ETF / QDII联接基金 / 港股通ETF (with 60/40 note)
"""

import openpyxl
from collections import defaultdict
import json

# ===== 读取数据 =====
wb = openpyxl.load_workbook('/root/.openclaw/media/inbound/all产品_20260419.xlsx')
ws = wb['products_all']

products = []
for row in ws.iter_rows(values_only=True):
    if row[0] is None or row[0] == '一级分类':
        continue
    products.append({
        'cat1': str(row[0]).strip(),
        'cat2': str(row[1]).strip(),
        'code': str(row[2]).strip() if row[2] else '',
        'name': str(row[3]).strip() if row[3] else '',
        'note': str(row[4]).strip() if row[4] else ''
    })

print(f"总产品数: {len(products)}")

# ===== 四大渠道对比 =====
CHANNELS = [
    {
        'id': 'qdsii', 'name': 'QDII ETF', 'icon': '🌏', 'color': '#3b82f6',
        'desc': '境内投资者直投境外ETF，额度需抢',
        'quota': '有额度限制', 'quota_color': '#ef4444',
        'product_count': 6,
        'link': 'products.html?chan=mainland&cat2=QDII%20ETF',
        'examples': '恒生科技ETF / 亚太精选ETF / 东南亚科技ETF / 沙特ETF',
        'how': '场内证券账户购买，T+2交收',
        'risk': '净值波动，汇率风险',
    },
    {
        'id': 'link', 'name': 'QDII 联接基金', 'icon': '📋', 'color': '#6366f1',
        'desc': '布局境外ETF的基金代销',
        'quota': '部分限额', 'quota_color': '#f59e0b',
        'product_count': 7,
        'link': 'products.html?chan=mainland&cat2=QDII%20%E8%81%94%E6%8E%A5%E5%9F%BA%E9%87%91',
        'examples': '恒生科技ETF联接A/C / 亚太精选ETF联接 / 东南亚科技ETF联接',
        'how': '场外基金账户申赎，限额各渠道不同',
        'risk': '申赎费率，净值波动',
    },
    {
        'id': 'hgt', 'name': '港股通ETF', 'icon': '🇭🇰', 'color': '#10b981',
        'desc': '互联互通ETF，可直接买卖',
        'quota': '无额度限制', 'quota_color': '#10b981',
        'product_count': 7,
        'link': 'products.html?chan=mainland&cat2=%E6%B8%AF%E8%82%A1%E9%80%9AETF',
        'examples': '南方恒生科技ETF / 恒生生物科技ETF / 港股通精选ETF',
        'how': 'A股账户买入，人民币结算',
        'risk': '汇率风险，跨境价差',
    },
    {
        'id': 'xfinance', 'name': '跨境理财通', 'icon': '💱', 'color': '#f59e0b',
        'desc': '大湾区居民可买港澳金融产品',
        'quota': '个人额度100万/年', 'quota_color': '#f59e0b',
        'product_count': 8,
        'link': 'products.html?chan=mainland&cat2=%E8%B7%A8%E5%A2%83%E7%90%86%E8%B4%8F%E9%80%9A',
        'examples': '恒生科技指数ETF(非上市类别) / 港元货币ETF / 美债20年+指数ETF',
        'how': '必须临柜办理，大湾区9市试点',
        'risk': '产品复杂度，非上市类别',
    },
]

# ===== 生成 index.html — 四大渠道对比 =====
def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

channel_rows = ''
for ch in CHANNELS:
    examples_short = ch['examples'].split('/')[0].strip()
    channel_rows += f'''
        <tr onclick="location.href='{ch['link']}'" style="cursor:pointer">
          <td style="padding:16px">
            <div style="display:flex;align-items:center;gap:10px">
              <span style="font-size:28px">{ch['icon']}</span>
              <div>
                <div style="font-weight:700;font-size:15px">{ch['name']}</div>
                <div style="font-size:12px;color:#6b7280;margin-top:2px">{ch['desc']}</div>
              </div>
            </div>
          </td>
          <td style="padding:16px;text-align:center">
            <span style="font-size:13px;font-weight:600;color:{ch['quota_color']}">{ch['quota']}</span>
          </td>
          <td style="padding:16px;text-align:center">
            <span style="background:{ch['color']}22;color:{ch['color']};border:1px solid {ch['color']}44;border-radius:20px;padding:4px 12px;font-size:13px;font-weight:600">{ch['product_count']} 只</span>
          </td>
          <td style="padding:16px;font-size:13px;color:#6b7280">{ch['how']}</td>
          <td style="padding:16px;font-size:13px;color:#6b7280">{ch['risk']}</td>
          <td style="padding:16px">
            <button style="background:{ch['color']};color:#fff;border:none;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:600;cursor:pointer">
              查看产品 →
            </button>
          </td>
        </tr>'''

index_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全球ETF投资地图 — 投资工具箱</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#f5f6fa;--card:#fff;--card2:#f0f2f8;--border:#e2e5ef;--text:#1a1d2e;--text2:#6b7280;--dim:#9ca3af}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}}
.header{{background:var(--text);color:#fff;padding:20px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}}
.header h1{{font-size:20px;font-weight:700;display:flex;align-items:center;gap:8px}}
.header-right{{font-size:13px;opacity:0.6}}
.nav{{display:flex;gap:8px;padding:12px 24px;background:#fff;border-bottom:1px solid var(--border);flex-wrap:wrap}}
.nav a{{color:var(--text2);text-decoration:none;font-size:14px;padding:6px 14px;border-radius:6px;transition:all 0.15s;display:inline-block}}
.nav a:hover{{background:var(--card2);color:var(--text)}}
.nav a.active{{background:var(--text);color:#fff}}
.hero{{padding:24px;background:linear-gradient(135deg,#1a1d2e 0%,#2d3154 100%);color:#fff}}
.hero h2{{font-size:22px;font-weight:700;margin-bottom:8px}}
.hero p{{font-size:14px;line-height:1.7;opacity:0.8;max-width:640px}}
.section{{padding:24px}}
.section-title{{font-size:18px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px}}
.ch-table{{width:100%;border-collapse:collapse;background:var(--card);border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,0.06);border:1px solid var(--border)}}
.ch-table thead th{{background:#1a1d2e;color:#fff;font-size:11px;font-weight:600;padding:12px 16px;text-align:left;text-transform:uppercase;letter-spacing:0.06em}}
.ch-table td{{padding:14px 16px;font-size:14px;border-bottom:1px solid var(--border);vertical-align:middle}}
.ch-table tr:last-child td{{border-bottom:none}}
.ch-table tr:hover{{background:#f8fbff}}
.footer{{text-align:center;padding:24px;font-size:12px;color:var(--dim)}}
@media(max-width:768px){{
  .ch-table{{font-size:12px}}
  .ch-table td{{padding:10px 8px}}
}}
</style>
</head>
<body>
<header class="header">
  <h1>🌏 全球ETF投资地图</h1>
  <div class="header-right">数据更新: 2026-04-19</div>
</header>
<nav class="nav">
  <a href="index.html" class="active">🗺️ 全球ETF地图</a>
  <a href="products.html">🔎 产品筛选</a>
</nav>
<div class="hero">
  <h2>四大跨境投资渠道</h2>
  <p>内地投资者可通过QDII、港股通、跨境理财通等四大渠道配置海外资产，点击下方对应渠道查看具体产品列表</p>
</div>
<div class="section">
  <div class="section-title">📊 渠道对比</div>
  <table class="ch-table">
    <thead>
      <tr>
        <th>投资渠道</th>
        <th style="width:100px;text-align:center">额度</th>
        <th style="width:100px;text-align:center">产品数量</th>
        <th style="width:180px">如何购买</th>
        <th style="width:140px">主要风险</th>
        <th style="width:120px">操作</th>
      </tr>
    </thead>
    <tbody>
      {channel_rows}
    </tbody>
  </table>
</div>
<div class="footer">
  数据来源: 产品清单 2026-04-19 · 共 110 只ETF产品
</div>
</body>
</html>'''

with open('/root/.openclaw/workspace/etf-map-site/index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)
print("✅ index.html 已生成（四大渠道对比表）")

# ===== 生成 products.html =====
# 内地可买：只保留 QDII ETF / QDII联接基金 / 港股通ETF
# 港股通ETF 下的 60/40 产品用特殊底色标记

# 先筛选内地可买产品
mainland_products = [p for p in products if p['cat1'] == '内地可买']

# 定义允许的子分类
ALLOWED_MAINLAND_CAT2 = ['QDII ETF', 'QDII 联接基金', '港股通ETF']
# 60/40 产品代码
HGT_6040_CODES = {'3441.HK', '3442.HK', '3431.HK'}  # 东西精选/港美科技/港韩科技

def badge(cat2):
    colors = {
        'QDII ETF': '#3b82f6',
        'QDII 联接基金': '#6366f1',
        '港股通ETF': '#10b981',
    }
    c = colors.get(cat2, '#6b7280')
    return f'<span style="background:{c}22;color:{c};border:1px solid {c}44;border-radius:4px;padding:2px 8px;font-size:12px;white-space:nowrap;display:inline-block">{esc(cat2)}</span>'

def is_6040(p):
    """判断是否为60/40产品"""
    return p['cat2'] == '港股通ETF-60/40产品' or p['code'] in HGT_6040_CODES

rows_html = ''
for p in mainland_products:
    if p['cat2'] not in ALLOWED_MAINLAND_CAT2:
        continue
    code_disp = esc(p['code']) if p['code'] else '—'
    name_disp = esc(p['name'])
    note_str = ''
    is_6040_flag = is_6040(p)
    row_class = 'is-6040' if is_6040_flag else ''
    rows_html += f"""<tr class="product-row {row_class}" data-cat2="{esc(p['cat2'])}" data-code="{esc(p['code'])}" data-name="{name_disp}" data-is6040="{'1' if is_6040_flag else '0'}">
  <td style="padding:10px 16px"><code style="color:#3b82f6;font-size:13px">{code_disp}</code></td>
  <td style="padding:10px 16px"><strong>{name_disp}</strong>{note_str}</td>
  <td style="padding:10px 16px">{badge(p['cat2'])}{'<span style="background:#fce7f3;color:#be185d;border:1px solid #fce7f366;border-radius:4px;padding:2px 8px;font-size:12px;white-space:nowrap;margin-left:6px;display:inline-block">60/40</span>' if is_6040_flag else ''}</td>
</tr>"""

# 境外产品
overseas_products = [p for p in products if p['cat1'] == '境外可买']
overseas_rows_html = ''
for p in overseas_products:
    code_disp = esc(p['code']) if p['code'] else '—'
    name_disp = esc(p['name'])
    cat2 = p['cat2']
    colors2 = {
        '香港': '#ef4444', '香港-美元份额': '#dc2626',
        '美国': '#3b82f6', 'A股': '#8b5cf6',
        '日本': '#ec4899', '新兴市场': '#f59e0b',
        '跨市场': '#14b8a6', '个股杠反ETF': '#ef4444',
        '个股杠反ETF-美元份额': '#dc2626', '指数杠反ETF': '#f97316',
        '加密货币期货ETF': '#fbbf24', '加密货币期货杠反ETF': '#f59e0b',
        '商品期货杠反ETF': '#eab308', '债券ETF-中国': '#6366f1',
        '债券ETF-美国': '#3b82f6', '货币市场ETF': '#10b981',
        '货币市场ETF-美元份额': '#14b8a6', 'REITs ETF': '#8b5cf6',
        '港股通ETF-60/40产品': '#14b8a6',
    }
    c = colors2.get(cat2, '#6b7280')
    overseas_rows_html += f"""<tr class="product-row" data-cat2="{esc(cat2)}" data-code="{esc(p['code'])}" data-name="{name_disp}">
  <td style="padding:10px 16px"><code style="color:#3b82f6;font-size:13px">{code_disp}</code></td>
  <td style="padding:10px 16px"><strong>{name_disp}</strong></td>
  <td style="padding:10px 16px"><span style="background:{c}22;color:{c};border:1px solid {c}44;border-radius:4px;padding:2px 8px;font-size:12px;white-space:nowrap;display:inline-block">{esc(cat2)}</span></td>
</tr>"""

# URL参数解析
parse_url = '''
function getUrlParam(key) {
  const params = new URLSearchParams(location.search);
  return params.get(key);
}
function applyUrlFilter() {
  const chan = getUrlParam('chan');
  const cat2 = getUrlParam('cat2');
  if (chan === 'mainland') switchChannel('mainland');
  else if (chan === 'overseas') switchChannel('overseas');
  if (cat2) {
    document.querySelectorAll('.sub-btn').forEach(b => {
      if (b.dataset.cat2 === cat2) b.click();
    });
  }
}
'''

products_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>产品筛选 — 全球ETF投资工具箱</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f6fa;color:#1a1d2e;min-height:100vh}}
.header{{background:#1a1d2e;color:#fff;padding:18px 24px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}}
.header h1{{font-size:20px;font-weight:700}}
.header p{{font-size:13px;opacity:0.65}}
.nav{{display:flex;gap:8px;padding:12px 24px;background:#fff;border-bottom:1px solid #e2e5ef;flex-wrap:wrap}}
.nav a{{color:#6b7280;text-decoration:none;font-size:14px;padding:6px 14px;border-radius:6px;transition:all 0.15s}}
.nav a:hover{{background:#f0f2f8;color:#1a1d2e}}
.nav a.active{{background:#1a1d2e;color:#fff}}

.channel-bar{{padding:20px 24px 0;background:#fff;border-bottom:2px solid #e2e5ef}}
.channel-label{{font-size:11px;color:#9ca3af;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px}}
.channel-tabs{{display:flex;gap:8px;flex-wrap:wrap}}
.chan-btn{{flex:1;min-width:160px;max-width:260px;padding:12px 16px;border:2px solid #e2e5ef;border-bottom:none;border-radius:10px 10px 0 0;font-size:13px;font-weight:700;cursor:pointer;background:#f8f9fc;color:#6b7280;transition:all 0.15s;text-align:center}}
.chan-btn:hover{{background:#f0f2f8;color:#1a1d2e}}
.chan-btn.active{{background:#1a1d2e;color:#fff;border-color:#1a1d2e}}

.sub-bar{{padding:12px 24px;background:#fff;display:flex;gap:8px;flex-wrap:wrap;align-items:center;border-bottom:1px solid #f0f2f8;min-height:52px}}
.sub-bar-label{{font-size:12px;color:#9ca3af;font-weight:600;margin-right:4px;flex-shrink:0}}
.sub-btn{{padding:6px 14px;border:1px solid #e2e5ef;border-radius:20px;font-size:13px;cursor:pointer;background:#fff;color:#6b7280;transition:all 0.15s;flex-shrink:0}}
.sub-btn:hover{{border-color:#3b82f6;color:#3b82f6}}
.sub-btn.active{{background:#1a1d2e;color:#fff;border-color:#1a1d2e}}

.search-bar{{padding:12px 24px;background:#fff;border-bottom:1px solid #f0f2f8;display:flex;gap:12px;align-items:center}}
.search-input{{flex:1;padding:10px 14px;border:1px solid #e2e5ef;border-radius:8px;font-size:14px;outline:none;max-width:400px;transition:border 0.15s}}
.search-input:focus{{border-color:#3b82f6}}

.stats{{padding:8px 24px;font-size:12px;color:#6b7280;background:#f8f9fc}}

table{{width:100%;border-collapse:collapse}}
thead{{background:#f0f2f8;position:sticky;top:0;z-index:10}}
th{{text-align:left;padding:10px 16px;font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.06em;border-bottom:2px solid #e2e5ef}}
td{{padding:10px 16px;font-size:14px;border-bottom:1px solid #f0f2f8;vertical-align:middle}}
tr.product-row:hover{{background:#f8fbff}}
.product-row{{cursor:pointer}}
.product-row.is-6040{{background:#fce7f3}}
.product-row.is-6040:hover{{background:#fde7f6}}

.no-result{{text-align:center;padding:60px;color:#9ca3af}}
.no-result div{{font-size:40px;margin-bottom:12px}}

#popup{{display:none;position:fixed;inset:0;z-index:1000;background:rgba(0,0,0,0.5);backdrop-filter:blur(4px);justify-content:center;align-items:center;padding:20px}}
#popup.show{{display:flex}}
.popup-box{{background:#fff;border-radius:16px;max-width:720px;width:100%;max-height:85vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,0.3);position:relative}}
.popup-header{{padding:16px 20px;border-bottom:1px solid #f0f2f8;display:flex;align-items:center;justify-content:space-between}}
.popup-header h3{{font-size:16px;font-weight:700}}
.popup-close{{width:32px;height:32px;border-radius:50%;border:none;background:#f0f2f8;cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center;color:#6b7280;transition:all 0.15s;flex-shrink:0}}
.popup-close:hover{{background:#e2e5ef;color:#1a1d2e}}
.popup-body{{padding:20px}}
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>🔎 产品筛选</h1>
    <p>共 {len(mainland_products)} 只内地可买产品 · 共 {len(overseas_products)} 只境外可买产品</p>
  </div>
</div>
<nav class="nav">
  <a href="index.html">🗺️ 全球ETF地图</a>
  <a href="products.html" class="active">🔎 产品筛选</a>
</nav>

<div class="channel-bar">
  <div class="channel-label">投资渠道</div>
  <div class="channel-tabs">
    <button class="chan-btn active" id="chan-mainland" onclick="switchChannel('mainland')">
      🇹🇨 内地可买 <span style="opacity:0.65;font-size:11px;font-weight:400">({len(mainland_products)})</span>
    </button>
    <button class="chan-btn" id="chan-overseas" onclick="switchChannel('overseas')">
      🌍 境外可买 <span style="opacity:0.65;font-size:11px;font-weight:400">({len(overseas_products)})</span>
    </button>
  </div>
</div>

<div id="mainlandPanel">
  <div class="sub-bar" id="mainlandSubBar">
    <span class="sub-bar-label">类型筛选:</span>
    <button class="sub-btn active" data-cat2="全部" onclick="toggleCat2('全部', this)">全部</button>
    <button class="sub-btn" data-cat2="QDII ETF" onclick="toggleCat2('QDII ETF', this)">QDII ETF</button>
    <button class="sub-btn" data-cat2="QDII 联接基金" onclick="toggleCat2('QDII 联接基金', this)">QDII 联接基金</button>
    <button class="sub-btn" data-cat2="港股通ETF" onclick="toggleCat2('港股通ETF', this)">港股通ETF</button>
  </div>
  <div class="search-bar">
    <input type="text" class="search-input" id="searchInput" placeholder="🔍  搜索产品名称或代码..." oninput="applyFilters()">
  </div>
  <div class="stats" id="statsBar">显示全部 {len(mainland_products)} 只产品</div>
  <div style="overflow-x:auto">
    <table>
    <thead>
      <tr>
        <th style="width:120px">代码</th>
        <th>产品名称</th>
        <th style="width:220px">类型</th>
      </tr>
    </thead>
    <tbody id="mainlandTableBody">
    {rows_html}
    </tbody>
    </table>
  </div>
</div>

<div id="overseasPanel" style="display:none">
  <div class="sub-bar" id="overseasSubBar">
    <span class="sub-bar-label">类型筛选:</span>
  </div>
  <div class="search-bar">
    <input type="text" class="search-input" id="searchInput2" placeholder="🔍  搜索产品名称或代码..." oninput="applyFilters()">
  </div>
  <div class="stats" id="statsBar2">显示全部 {len(overseas_products)} 只产品</div>
  <div style="overflow-x:auto">
    <table>
    <thead>
      <tr>
        <th style="width:120px">代码</th>
        <th>产品名称</th>
        <th style="width:220px">分类</th>
      </tr>
    </thead>
    <tbody id="overseasTableBody">
    {overseas_rows_html}
    </tbody>
    </table>
  </div>
</div>

<div id="noResult" class="no-result" style="display:none">
  <div>🔍</div>
  <div>没有找到匹配的产品</div>
</div>

<div id="popup">
  <div class="popup-box">
    <div class="popup-header">
      <h3 id="popupTitle">产品详情</h3>
      <button class="popup-close" onclick="closePopup()">×</button>
    </div>
    <div class="popup-body" id="popupBody"></div>
  </div>
</div>

<script>
{parse_url}

let curChannel = 'mainland';
let curCat2 = '全部';
let searchQuery = '';

function switchChannel(chan) {{
  curChannel = chan;
  document.getElementById('chan-mainland').classList.toggle('active', chan === 'mainland');
  document.getElementById('chan-overseas').classList.toggle('active', chan === 'overseas');
  document.getElementById('mainlandPanel').style.display = chan === 'mainland' ? 'block' : 'none';
  document.getElementById('overseasPanel').style.display = chan === 'overseas' ? 'block' : 'none';
  applyFilters();
}}

function toggleCat2(cat2, btn) {{
  if (curCat2 === cat2) {{
    curCat2 = '全部';
    document.querySelectorAll('.sub-btn[data-cat2]').forEach(b => b.classList.remove('active'));
    document.querySelector('.sub-btn[data-cat2="全部"]').classList.add('active');
  }} else {{
    curCat2 = cat2;
    document.querySelectorAll('.sub-btn[data-cat2]').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }}
  applyFilters();
}}

function applyFilters() {{
  const q1 = document.getElementById('searchInput').value.trim().toLowerCase();
  const q2 = document.getElementById('searchInput2').value.trim().toLowerCase();
  const query = q1 || q2;

  if (curChannel === 'mainland') {{
    const rows = document.querySelectorAll('#mainlandTableBody tr');
    let visible = 0;
    rows.forEach(row => {{
      const rowCat2 = row.dataset.cat2;
      const code = row.dataset.code.toLowerCase();
      const name = row.dataset.name.toLowerCase();
      const is6040 = row.dataset.is6040 === '1';
      const cat2Ok = curCat2 === '全部' || rowCat2 === curCat2;
      const searchOk = !query || code.includes(query) || name.includes(query);
      const show = cat2Ok && searchOk;
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    }});
    document.getElementById('statsBar').textContent = `显示 ${{visible}} / {len(mainland_products)} 只产品`;
  }} else {{
    const rows = document.querySelectorAll('#overseasTableBody tr');
    let visible = 0;
    rows.forEach(row => {{
      const cat2 = row.dataset.cat2;
      const code = row.dataset.code.toLowerCase();
      const name = row.dataset.name.toLowerCase();
      const cat2Ok = curCat2 === '全部' || cat2 === curCat2;
      const searchOk = !query || code.includes(query) || name.includes(query);
      const show = cat2Ok && searchOk;
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    }});
    document.getElementById('statsBar2').textContent = `显示 ${{visible}} / {len(overseas_products)} 只产品`;
  }}
}}

// 渲染境外筛选按钮
const overseasCat2Set = new Set();
document.querySelectorAll('#overseasTableBody tr').forEach(r => overseasCat2Set.add(r.dataset.cat2));
const overseasSubBar = document.getElementById('overseasSubBar');
const cat2Labels = {{'香港':'香港股票','美国':'美国股票','A股':'A股ETF','日本':'日本股票','新兴市场':'新兴市场','跨市场':'跨市场','个股杠反ETF':'个股杠反','个股杠反ETF-美元份额':'个股杠反$','指数杠反ETF':'指数杠反','加密货币期货ETF':'加密期货','加密货币期货杠反ETF':'加密杠反','商品期货杠反ETF':'商品杠反','债券ETF-中国':'中国债券','债券ETF-美国':'美国债券','货币市场ETF':'货币市场','货币市场ETF-美元份额':'货币$','REITs ETF':'REITs','港股通ETF-60/40产品':'港股通60/40'}};

['全部'].concat([...overseasCat2Set]).forEach(cat2 => {{
  const btn = document.createElement('button');
  btn.className = 'sub-btn' + (cat2 === '全部' ? ' active' : '');
  btn.dataset.cat2 = cat2;
  btn.textContent = cat2 === '全部' ? '全部' : (cat2Labels[cat2] || cat2);
  btn.onclick = () => toggleCat2(cat2, btn);
  overseasSubBar.appendChild(btn);
}});

// URL参数自动筛选
applyUrlFilter();

document.getElementById('searchInput').addEventListener('input', applyFilters);
document.getElementById('searchInput2').addEventListener('input', applyFilters);

function showPopup(code) {{
  document.getElementById('popupTitle').textContent = code;
  document.getElementById('popupBody').innerHTML = '<p style="color:#9ca3af;text-align:center;padding:40px">详情数据开发中...</p>';
  document.getElementById('popup').classList.add('show');
}}
function closePopup() {{
  document.getElementById('popup').classList.remove('show');
}}
document.querySelectorAll('.product-row').forEach(row => {{
  row.addEventListener('click', () => showPopup(row.dataset.code));
}});
</script>
</body>
</html>'''

with open('/root/.openclaw/workspace/etf-map-site/products.html', 'w', encoding='utf-8') as f:
    f.write(products_html)
print("✅ products.html 已生成")
print(f"   内地可买: {len(mainland_products)} 只 / 境外可买: {len(overseas_products)} 只")
