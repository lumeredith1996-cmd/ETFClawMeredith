#!/usr/bin/env python3
"""Generate ETF Map page + Product Overview page from Excel data"""

import openpyxl
from collections import defaultdict
import json

# ===== 读取数据 =====
wb = openpyxl.load_workbook('/root/.openclaw/media/inbound/alläº_å_20260419---80d1ce18-9fe0-47d7-b4ae-c0e9043c3b7e.xlsx')
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

# ===== 按分类组织 =====
# 结构: { cat1: { cat2: [products...] } }
tree = defaultdict(lambda: defaultdict(list))
for p in products:
    tree[p['cat1']][p['cat2']].append(p)

# ===== 统计 =====
print("内地可买:")
for cat2, prods in sorted(tree['内地可买'].items()):
    print(f"  {cat2}: {len(prods)}个")
print("\n境外可买:")
for cat2, prods in sorted(tree['境外可买'].items()):
    print(f"  {cat2}: {len(prods)}个")

# ===== 生成 产品总览页面 =====
def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def badge(cat1, cat2):
    colors = {
        'QDII ETF': '#3b82f6', 'QDII 联接基金': '#6366f1',
        '港股通ETF': '#10b981', '港股通ETF-60/40产品': '#14b8a6',
        '跨境理财通（大湾区9市）-权益': '#f59e0b',
        '跨境理财通（大湾区9市）-货币': '#fbbf24',
        '跨境理财通（大湾区9市）-固定收益': '#f97316',
        '跨境理财通（大湾区9市）-基金互认': '#eab308',
        '香港': '#ef4444', '香港-美元份额': '#dc2626',
        '美国': '#3b82f6', 'A股': '#8b5cf6',
        '新兴市场': '#f59e0b', '日本': '#ec4899',
        '跨市场': '#14b8a6', '个股杠反ETF': '#ef4444',
        '个股杠反ETF-美元份额': '#dc2626', '指数杠反ETF': '#f97316',
        '加密货币期货ETF': '#fbbf24', '加密货币期货杠反ETF': '#f59e0b',
        '商品期货杠反ETF': '#eab308', '债券ETF-中国': '#6366f1',
        '债券ETF-美国': '#3b82f6', '货币市场ETF': '#10b981',
        '货币市场ETF-美元份额': '#14b8a6', 'REITs ETF': '#8b5cf6',
    }
    c = colors.get(cat2, '#6b7280')
    return f'<span style="background:{c}22;color:{c};border:1px solid {c}44;border-radius:4px;padding:2px 8px;font-size:12px;white-space:nowrap">{esc(cat2)}</span>'

def note_html(note):
    if not note or note == 'None':
        return ''
    return f'<span style="color:#f59e0b;font-size:11px;margin-left:6px">⚠️ {esc(note)}</span>'

rows_html = ''
for p in products:
    code_disp = esc(p['code']) if p['code'] else '—'
    name_disp = esc(p['name'])
    cat1_class = 'mainland' if p['cat1'] == '内地可买' else 'overseas'
    cat1_label = '🇨🇳 内地可买' if p['cat1'] == '内地可买' else '🌍 境外可买'
    row = f"""<tr data-cat1="{cat1_class}" data-cat2="{esc(p['cat2'])}" data-code="{esc(p['code'])}" data-name="{name_disp}">
  <td style="text-align:center"><span class="cat1-badge {cat1_class}">{cat1_label}</span></td>
  <td><code style="color:#3b82f6;font-size:13px">{code_disp}</code></td>
  <td><strong>{name_disp}</strong>{note_html(p['note'])}</td>
  <td>{badge(p['cat1'], p['cat2'])}</td>
</tr>"""
    rows_html += row

overview_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>产品筛选 — 全球ETF投资工具箱</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f6fa;color:#1a1d2e}}
.header{{background:#1a1d2e;color:#fff;padding:20px 24px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}}
.header h1{{font-size:20px;font-weight:700}}
.header p{{font-size:13px;opacity:0.7}}
.nav{{display:flex;gap:8px;padding:12px 24px;background:#fff;border-bottom:1px solid #e2e5ef;flex-wrap:wrap}}
.nav a{{color:#6b7280;text-decoration:none;font-size:14px;padding:6px 12px;border-radius:6px;transition:all 0.15s}}
.nav a:hover{{background:#f0f2f8;color:#1a1d2e}}
.nav a.active{{background:#1a1d2e;color:#fff}}
.toolbar{{padding:16px 24px;background:#fff;border-bottom:1px solid #e2e5ef;display:flex;gap:12px;flex-wrap:wrap;align-items:center}}
.search-box{{flex:1;min-width:200px;position:relative}}
.search-box input{{width:100%;padding:10px 14px 10px 38px;border:1px solid #e2e5ef;border-radius:8px;font-size:14px;outline:none;transition:border 0.15s}}
.search-box input:focus{{border-color:#3b82f6}}
.search-box::before{{content:"🔍";position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:14px}}
.filter-group{{display:flex;gap:8px;flex-wrap:wrap;align-items:center}}
.filter-label{{font-size:13px;color:#6b7280;font-weight:500}}
.filter-btn{{padding:8px 14px;border:1px solid #e2e5ef;border-radius:20px;font-size:13px;cursor:pointer;background:#fff;color:#6b7280;transition:all 0.15s}}
.filter-btn:hover{{border-color:#3b82f6;color:#3b82f6}}
.filter-btn.active{{background:#1a1d2e;color:#fff;border-color:#1a1d2e}}
.stats{{padding:10px 24px;font-size:13px;color:#6b7280;background:#f0f2f8}}
table{{width:100%;border-collapse:collapse}}
thead{{background:#f0f2f8;position:sticky;top:0;z-index:10}}
th{{text-align:left;padding:10px 16px;font-size:12px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.05em;border-bottom:2px solid #e2e5ef}}
td{{padding:12px 16px;font-size:14px;border-bottom:1px solid #f0f2f8;vertical-align:middle}}
tr:hover{{background:#f8f9ff}}
.cat1-badge{{font-size:12px;font-weight:600;padding:3px 8px;border-radius:4px;display:inline-block}}
.cat1-badge.mainland{{background:#dbeafe;color:#1d4ed8}}
.cat1-badge.overseas{{background:#d1fae5;color:#065f46}}
.badge-row{{display:flex;gap:4px;flex-wrap:wrap;margin-top:4px}}
.badge-row:first-child{{margin-top:0}}
.note-warn{{color:#d97706;font-size:11px;margin-left:6px}}
.no-result{{text-align:center;padding:60px;color:#9ca3af;font-size:15px}}
.no-result div{{font-size:40px;margin-bottom:12px}}
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>🔎 产品筛选</h1>
    <p>共 {len(products)} 只ETF产品 · 点击行查看详情（含成分股权重+休市日历）</p>
  </div>
</div>
<nav class="nav">
  <a href="index.html">🗺️ 全球ETF地图</a>
  <a href="products.html" class="active">🔎 产品筛选</a>
</nav>
<div class="toolbar">
  <div class="search-box">
    <input type="text" id="searchInput" placeholder="搜索产品名称或代码...">
  </div>
  <div class="filter-group">
    <span class="filter-label">渠道:</span>
    <button class="filter-btn active" data-filter="all" onclick="filterAll()">全部</button>
    <button class="filter-btn" data-filter="mainland" onclick="filterCat1('mainland')">🇨🇳 内地可买</button>
    <button class="filter-btn" data-filter="overseas" onclick="filterCat1('overseas')">🌍 境外可买</button>
  </div>
  <div class="filter-group" id="cat2Filters">
    <span class="filter-label">类型:</span>
  </div>
</div>
<div class="stats" id="statsBar">显示全部 {len(products)} 只产品</div>
<div style="overflow-x:auto">
<table>
<thead>
  <tr>
    <th style="width:100px">购买渠道</th>
    <th style="width:120px">代码</th>
    <th>产品名称</th>
    <th style="width:220px">分类</th>
  </tr>
</thead>
<tbody id="tableBody">
{rows_html}
</tbody>
</table>
</div>
<div id="noResult" class="no-result" style="display:none">
  <div>🔍</div>
  <div>没有找到匹配的产品</div>
</div>
<script>
// 获取所有二级分类
const allCat2 = [{', '.join(f"'{c}'" for c in sorted({'QDII ETF','QDII 联接基金','港股通ETF','港股通ETF-60/40产品','跨境理财通（大湾区9市）-权益','跨境理财通（大湾区9市）-货币','跨境理财通（大湾区9市）-固定收益','跨境理财通（大湾区9市）-基金互认','香港','香港-美元份额','美国','A股','新兴市场','日本','跨市场','个股杠反ETF','个股杠反ETF-美元份额','指数杠反ETF','加密货币期货ETF','加密货币期货杠反ETF','商品期货杠反ETF','债券ETF-中国','债券ETF-美国','货币市场ETF','货币市场ETF-美元份额','REITs ETF'}))}];
// 渲染二级分类按钮
const cat2Filters = document.getElementById('cat2Filters');
const cat2Labels = {{'QDII ETF':'QDII ETF','QDII 联接基金':'QDII 联接','港股通ETF':'港股通ETF','港股通ETF-60/40产品':'港股通60/40','跨境理财通（大湾区9市）-权益':'跨境权益','跨境理财通（大湾区9市）-货币':'跨境货币','跨境理财通（大湾区9市）-固定收益':'跨境固收','跨境理财通（大湾区9市）-基金互认':'基金互认','香港':'香港','香港-美元份额':'港-美元','美国':'美国','A股':'A股','新兴市场':'新兴市场','日本':'日本','跨市场':'跨市场','个股杠反ETF':'个股杠反','个股杠反ETF-美元份额':'个股杠反$','指数杠反ETF':'指数杠反','加密货币期货ETF':'加密期货','加密货币期货杠反ETF':'加密杠反','商品期货杠反ETF':'商品杠反','债券ETF-中国':'债券-中国','债券ETF-美国':'债券-美国','货币市场ETF':'货币','货币市场ETF-美元份额':'货币$','REITs ETF':'REITs'}};
Object.keys(cat2Labels).forEach(cat2 => {{
  const btn = document.createElement('button');
  btn.className = 'filter-btn';
  btn.dataset.cat2 = cat2;
  btn.textContent = cat2Labels[cat2];
  btn.onclick = () => toggleCat2(cat2);
  cat2Filters.appendChild(btn);
}});

let curCat1 = 'all';
let curCat2Set = new Set();
const rows = document.querySelectorAll('#tableBody tr');
const searchInput = document.getElementById('searchInput');
const statsBar = document.getElementById('statsBar');
const noResult = document.getElementById('noResult');

function applyFilters() {{
  const q = searchInput.value.trim().toLowerCase();
  let visible = 0;
  rows.forEach(row => {{
    const cat1 = row.dataset.cat1;
    const cat2 = row.dataset.cat2;
    const code = row.dataset.code.toLowerCase();
    const name = row.dataset.name.toLowerCase();
    const cat1Ok = curCat1 === 'all' || cat1 === curCat1;
    const cat2Ok = curCat2Set.size === 0 || curCat2Set.has(cat2);
    const searchOk = !q || code.includes(q) || name.includes(q);
    const show = cat1Ok && cat2Ok && searchOk;
    row.style.display = show ? '' : 'none';
    if (show) visible++;
  }});
  statsBar.textContent = `显示 ${{visible}} / {len(products)} 只产品`;
  noResult.style.display = visible === 0 ? 'block' : 'none';
}}

function filterCat1(cat) {{
  curCat1 = cat;
  document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.toggle('active', b.dataset.filter === cat));
  applyFilters();
}}

function filterAll() {{
  curCat1 = 'all';
  document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.toggle('active', b.dataset.filter === 'all'));
  applyFilters();
}}

function toggleCat2(cat2) {{
  if (curCat2Set.has(cat2)) curCat2Set.delete(cat2);
  else curCat2Set.add(cat2);
  document.querySelectorAll('[data-cat2]').forEach(b => {{
    if (b.dataset.cat2 === cat2) b.classList.toggle('active', curCat2Set.has(cat2));
  }});
  applyFilters();
}}

searchInput.addEventListener('input', applyFilters);
</script>
</body>
</html>'''

with open('/root/.openclaw/workspace/etf-map-site/products.html', 'w', encoding='utf-8') as f:
    f.write(overview_html)
print("\n✅ products.html 已生成")

# ===== 生成全球ETF地图页面 =====
# 按区域组织
regions = {
    '🇨🇳 内地': {
        'icon': '🇨🇳', 'color': '#ef4444',
        'desc': '内地投资者可通过QDII、港股通、跨境理财通等渠道购买',
        'subs': {
            'QDII ETF': {'code': '513130.SH', 'name': '恒生科技ETF', 'note': '不限额'},
            'QDII 联接基金': {'code': '015310.OF', 'name': '恒生科技ETF联接A', 'note': '无限额'},
            '港股通ETF': {'code': '3033.HK', 'name': '南方恒生科技ETF', 'note': ''},
            '港股通ETF-60/40产品': {'code': '3441.HK', 'name': '东西精选ETF', 'note': '跨港美'},
            '跨境理财通-权益': {'code': 'HK0000773892', 'name': '恒生科技指数ETF', 'note': '大湾区'},
            '跨境理财通-货币': {'code': 'HK0000489705', 'name': '港元货币ETF', 'note': '大湾区'},
            '跨境理财通-固收/基金互认': {'code': 'HK0000981032', 'name': '美债20年+指数ETF', 'note': '基金互认'},
        }
    },
    '🇭🇰 香港': {
        'icon': '🇭🇰', 'color': '#f59e0b',
        'desc': '香港本地上市，覆盖港股、A股、全球市场',
        'subs': {
            '香港股票ETF': {'code': '3033.HK', 'name': '恒生科技ETF', 'note': ''},
            'A股ETF': {'code': '3133.HK', 'name': '华泰柏瑞沪深300ETF', 'note': ''},
            '美国ETF': {'code': '3034.HK', 'name': '纳斯达克100ETF', 'note': ''},
            '日本ETF': {'code': '3153.HK', 'name': '日经225指数ETF', 'note': ''},
            '新兴市场ETF': {'code': '3004.HK', 'name': '富时越南30ETF', 'note': ''},
            '港股通精选ETF': {'code': '3432.HK', 'name': '港股通精选ETF', 'note': '跨市场'},
            '跨市场ETF': {'code': '3442.HK', 'name': '港美科技ETF', 'note': '跨港美'},
        }
    },
    '🌏 亚洲': {
        'icon': '🌏', 'color': '#14b8a6',
        'desc': '覆盖亚太及东南亚精选市场',
        'subs': {
            '港韩科技ETF': {'code': '3431.HK', 'name': '港韩科技ETF', 'note': '跨市场'},
            '亚太精选': {'code': '159687.SZ', 'name': '亚太精选ETF', 'note': 'QDII'},
            '东南亚科技': {'code': '513730.SH', 'name': '东南亚科技ETF', 'note': 'QDII'},
        }
    },
    '🇸🇦 中东': {
        'icon': '🇸🇦', 'color': '#fbbf24',
        'desc': '配置石油财富与新兴消费市场',
        'subs': {
            '沙特ETF': {'code': '2830.HK', 'name': '沙特阿拉伯ETF', 'note': ''},
            '沙特ETF(内地)': {'code': '159329.SZ', 'name': '沙特ETF南方', 'note': 'QDII'},
        }
    },
    '💱 债券·货币': {
        'icon': '💱', 'color': '#6366f1',
        'desc': '美元、人民币、港元货币与债券配置',
        'subs': {
            '美债20年+': {'code': '3433.HK', 'name': '美国国债20年+指数ETF', 'note': ''},
            '中国国债': {'code': '3199.HK', 'name': '工银富时中国国债ETF', 'note': ''},
            '货币ETF(港)': {'code': '3053.HK', 'name': '港元货币ETF', 'note': ''},
            '货币ETF(人民币)': {'code': '3122.HK', 'name': '人民币货币ETF', 'note': ''},
            '货币ETF(美元)': {'code': '3096.HK', 'name': '美元货币市场ETF', 'note': ''},
        }
    },
    '🏠 REITs': {
        'icon': '🏠', 'color': '#8b5cf6',
        'desc': '亚太房地产信托收益',
        'subs': {
            '亚太REITs': {'code': '3447.HK', 'name': '亚太房地产信托ETF', 'note': ''},
            '新加坡REITs': {'code': 'SRT.SP', 'name': '新加坡房地产信托ETF', 'note': ''},
        }
    },
    '₿ 加密货币': {
        'icon': '₿', 'color': '#f97316',
        'desc': '比特币、以太币期货及杠杆产品',
        'subs': {
            '比特币期货': {'code': '3066.HK', 'name': '比特币期货ETF', 'note': ''},
            '以太币期货': {'code': '3068.HK', 'name': '以太币期货ETF', 'note': ''},
            '做空比特币期货': {'code': '7376.HK', 'name': '1倍做空比特币期货', 'note': ''},
        }
    },
    '📈 指数杠反': {
        'icon': '📈', 'color': '#ef4444',
        'desc': '2倍/1倍做多或做空主要指数',
        'subs': {
            '2x做多恒生科技': {'code': '7226.HK', 'name': '南方2倍做多恒生科技', 'note': ''},
            '2x做空恒生科技': {'code': '7552.HK', 'name': '南方2倍做空恒生科技', 'note': ''},
            '2x做多恒指': {'code': '7200.HK', 'name': '南方2倍做多恒生', 'note': ''},
            '2x做空恒指': {'code': '7500.HK', 'name': '南方2倍做空恒生', 'note': ''},
            '2x做多恒企': {'code': '7288.HK', 'name': '南方2倍做多恒企', 'note': ''},
            '2x做空恒企': {'code': '7588.HK', 'name': '南方2倍做空恒企', 'note': ''},
            '2x做多纳指100': {'code': '7266.HK', 'name': '南方2倍做多纳指100', 'note': ''},
            '2x做空纳指100': {'code': '7568.HK', 'name': '南方2倍做空纳指100', 'note': ''},
            '2x做多日经225': {'code': '7262.HK', 'name': '南方2倍做多日经225', 'note': ''},
            '2x做空日经225': {'code': '7515.HK', 'name': '南方2倍做空日经225', 'note': ''},
            '2x做多沪深300': {'code': '7233.HK', 'name': '南方2倍做多沪深300', 'note': ''},
            '1x做空恒生': {'code': '7300.HK', 'name': '南方1倍做空恒生', 'note': ''},
        }
    },
    '🦄 个股杠反': {
        'icon': '🦄', 'color': '#ec4899',
        'desc': '2倍做多或做空明星科技股',
        'subs': {
            '2x做多MSTR': {'code': '7799.HK', 'name': '2倍做多MicroStrategy', 'note': ''},
            '2x做多英伟达': {'code': '7788.HK', 'name': '2倍做多英伟达', 'note': ''},
            '2x做多特斯拉': {'code': '7766.HK', 'name': '2倍做多特斯拉', 'note': ''},
            '2x做多三星': {'code': '7747.HK', 'name': '2倍做多三星电子', 'note': ''},
            '2x做多SK海力士': {'code': '7709.HK', 'name': '2倍做多SK海力士', 'note': ''},
            '2x做多Coinbase': {'code': '7711.HK', 'name': '2倍做多Coinbase', 'note': ''},
            '2x做多BRK': {'code': '7777.HK', 'name': '2倍做多Berkshire', 'note': ''},
            '2x做空MSTR': {'code': '7399.HK', 'name': '2倍做空MicroStrategy', 'note': ''},
            '2x做空英伟达': {'code': '7388.HK', 'name': '2倍做空英伟达', 'note': ''},
            '2x做空特斯拉': {'code': '7366.HK', 'name': '2倍做空特斯拉', 'note': ''},
            '2x做空三星': {'code': '7347.HK', 'name': '2倍做空三星电子', 'note': ''},
            '2x做空Coinbase': {'code': '7311.HK', 'name': '2倍做空Coinbase', 'note': ''},
        }
    },
    '💰 收息神器': {
        'icon': '💰', 'color': '#10b981',
        'desc': '月月派息/高股息ETF，稳健现金流',
        'subs': {
            '恒生高息股30': {'code': '3466.HK', 'name': '恒生高息股30指数ETF', 'note': '月派息'},
            '国指备兑认购(2802)': {'code': '2802.HK', 'name': '南方东英国指备兑ETF', 'note': '月派息~18%'},
            'GX国指备兑(3416)': {'code': '3416.HK', 'name': 'GX中国企指备兑ETF', 'note': '月派息~16%'},
            '富邦沪深港高股息': {'code': '03190.HK', 'name': '富邦沪深港高股息ETF', 'note': '年息~6%'},
            '港股通红利': {'code': '3469.HK', 'name': '南方港股通红利ETF', 'note': ''},
        }
    },
}

# 生成地图HTML
region_cards = ''
for region, data in regions.items():
    subs_html = ''
    for sub_name, sub_data in data['subs'].items():
        note_str = f'<span class="note-w">⚠️ {sub_data["note"]}</span>' if sub_data['note'] else ''
        subs_html += f'''<div class="p-row">
          <span class="p-name">{esc(sub_name)}</span>
          <span class="p-code">{esc(sub_data['code'])}</span>
          <span class="p-desc">{esc(sub_data['name'])}{note_str}</span>
        </div>'''
    
    region_cards += f'''<div class="region-card">
  <div class="region-header" style="border-left:4px solid {data['color']}">
    <span class="region-icon">{data['icon']}</span>
    <div>
      <div class="region-name">{region}</div>
      <div class="region-desc">{esc(data['desc'])}</div>
    </div>
  </div>
  <div class="region-products">
    {subs_html}
  </div>
</div>'''

map_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全球ETF投资地图 — 投资工具箱</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#f5f6fa;--card:#fff;--card2:#f0f2f8;--border:#e2e5ef;--text:#1a1d2e;--text2:#6b7280;--dim:#9ca3af;--green:#10b981;--blue:#3b82f6;--red:#ef4444;--yellow:#f59e0b;--purple:#8b5cf6}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}}
.header{{background:var(--text);color:#fff;padding:20px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}}
.header h1{{font-size:20px;font-weight:700;display:flex;align-items:center;gap:8px}}
.header-right{{font-size:13px;opacity:0.6}}
.nav{{display:flex;gap:8px;padding:12px 24px;background:#fff;border-bottom:1px solid var(--border);flex-wrap:wrap}}
.nav a{{color:var(--text2);text-decoration:none;font-size:14px;padding:6px 14px;border-radius:6px;transition:all 0.15s;display:inline-block}}
.nav a:hover{{background:var(--card2);color:var(--text)}}
.nav a.active{{background:var(--text);color:#fff}}
.intro{{padding:16px 24px;background:linear-gradient(135deg,#1a1d2e 0%,#2d3154 100%);color:#fff}}
.intro p{{font-size:13px;line-height:1.7;opacity:0.85;max-width:700px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px;padding:20px 24px}}
.region-card{{background:var(--card);border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,0.06);overflow:hidden;border:1px solid var(--border)}}
.region-header{{padding:14px 16px;display:flex;align-items:flex-start;gap:12px;background:var(--card2)}}
.region-icon{{font-size:24px;flex-shrink:0}}
.region-name{{font-size:15px;font-weight:700;color:var(--text)}}
.region-desc{{font-size:12px;color:var(--text2);margin-top:2px}}
.region-products{{padding:8px}}
.p-row{{display:grid;grid-template-columns:120px 95px 1fr;gap:8px;padding:8px 10px;border-radius:6px;align-items:center;transition:background 0.1s}}
.p-row:hover{{background:var(--card2)}}
.p-name{{font-size:13px;font-weight:600;color:var(--text)}}
.p-code{{font-size:12px;color:var(--blue);font-family:monospace}}
.p-desc{{font-size:12px;color:var(--text2)}}
.note-w{{color:var(--yellow);font-size:11px;margin-left:4px}}
.footer{{text-align:center;padding:24px;font-size:12px;color:var(--dim)}}
@media(max-width:600px){{
  .grid{{grid-template-columns:1fr}}
  .p-row{{grid-template-columns:1fr;gap:2px}}
  .p-code{{font-size:11px}}
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
<div class="intro">
  <p>📌 覆盖内地、香港、美国、日本、东南亚、中东等全球主要市场 · 共 {len(products)} 只ETF产品 · 点击下方分类查看各区域代表性产品</p>
</div>
<div class="grid">
{region_cards}
</div>
<div class="footer">
  数据来源: 产品列表 2026-04-19 · 分类依据: 招标产品清单
</div>
</body>
</html>'''

with open('/root/.openclaw/workspace/etf-map-site/index.html', 'w', encoding='utf-8') as f:
    f.write(map_html)
print("✅ index.html (全球ETF地图) 已生成")
print(f"   共 {len(products)} 只产品，{len(regions)} 个区域分类")
