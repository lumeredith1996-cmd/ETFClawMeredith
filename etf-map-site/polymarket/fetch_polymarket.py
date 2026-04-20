#!/usr/bin/env python3
"""
Polymarket Dashboard Generator
Fetches hot prediction markets and generates a static dashboard HTML.
Run via cron: 0 */6 * * * cd /root/.openclaw/workspace/polymarket-dashboard && python3 fetch_polymarket.py
"""

import json
import re
import time
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

CATEGORIES = {
    "ai": "🤖 AI与科技",
    "tech": "💻 科技",
    "finance": "💰 金融",
    "breaking": "🔥 热门",
    "iran": "🌍 中东/伊朗",
}

FETCH_CATEGORIES = ["ai", "tech", "finance", "breaking", "iran"]

def fetch_url(url, timeout=15):
    """Fetch URL with custom User-Agent to avoid 403."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, Exception) as e:
        print(f"  ❌ Fetch error for {url}: {e}")
        return None

def parse_markets_from_html(html):
    """Parse market cards from Polymarket HTML (raw-html extractor output)."""
    markets = []
    if not html:
        return markets

    # Pattern: market question text followed by outcome probabilities
    # Each market appears as: <a href="/event/SLUG">Question text</a>
    # Then probability values like 94% near Yes/No links

    # Find all event blocks - each has question + probability pairs
    # The HTML from raw-html extractor has text content interleaved with links

    # Split by event links
    event_pattern = re.compile(r'/event/([^"]+)"[^>]*>([^<]+)</a>')
    outcomes = re.findall(event_pattern, html)

    # Find all probability percentages that follow outcome links
    pct_pattern = re.compile(r'>([\d]+)%\s*<[^>]*Yes|No')

    # The raw HTML has duplicate entries (each outcome appears twice)
    # Let's use a smarter approach: group by (slug, question) then find pcts
    lines = html.replace('</a>', '\n</a>').split('\n')

    current_market = None
    current_slug = None
    current_outcomes = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Check if this is an event link (question title)
        ev_match = re.search(r'/event/([^"]+)"[^>]*>([^<]+)</a>', line)
        if ev_match:
            slug = ev_match.group(1)
            question = ev_match.group(2).strip()

            # Deduplicate by slug (same market appears twice in output)
            if current_market and current_slug and current_slug != slug:
                if current_market and current_outcomes:
                    markets.append({
                        "question": current_market,
                        "slug": current_slug,
                        "url": f"https://polymarket.com/event/{current_slug}",
                        "outcomes": current_outcomes[:]
                    })
                current_outcomes = []

            current_market = question
            current_slug = slug

        # Look for percentage values
        pct_matches = re.findall(r'(\d+)%', line)
        for pct_str in pct_matches:
            pct = int(pct_str)
            if 1 <= pct <= 99:
                # This is likely an outcome probability
                # Determine if it's Yes or No based on context
                is_yes = 'Yes' in line or 'yes' in line.lower()
                outcome_label = None

                # Try to find the outcome label nearby
                label_match = re.search(r'>(Will |)([^<]{3,50})(?:</a>|</span>)', line)
                if label_match:
                    outcome_label = label_match.group(2).strip()
                else:
                    outcome_label = "Yes" if pct > 50 else "No"

                # Avoid duplicates in same market
                if not any(o.get('pct') == pct for o in current_outcomes):
                    current_outcomes.append({
                        "label": outcome_label,
                        "pct": pct
                    })

        i += 1

    # Don't forget last market
    if current_market and current_outcomes:
        markets.append({
            "question": current_market,
            "slug": current_slug,
            "url": f"https://polymarket.com/event/{current_slug}",
            "outcomes": current_outcomes
        })

    return markets

def parse_breaking_page(html):
    """Parse breaking news page with more detail - shows Yes% vs No% for each market."""
    markets = []
    if not html:
        return markets

    # Pattern from breaking page:
    # Question text, then Yes% (in green/blue), then No% (in red/gray)
    # Format: "Will X happen? 100%  84%" -> Yes=100%, No=84%
    # Or: "Event? Yes% No%"
    # Some have multi-outcome with named options

    # Split into lines for processing
    lines = html.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for event link
        ev_match = re.search(r'/event/([^"]+)"[^>]*>([^<]+)</a>', line)
        if ev_match:
            slug = ev_match.group(1)
            question = ev_match.group(2).strip()

            # Skip non-question links (like navigation)
            skip_words = ['Trending', 'Breaking', 'New', 'Politics', 'Sports', 'Crypto',
                         'Culture', 'Tech', 'Finance', 'Economy', 'Weather', 'All',
                         'Politics', 'World', 'Elections', 'Iran', 'Esports']
            if any(q.lower() == line.lower() or line.lower() in q.lower()
                   for q in skip_words if len(q) > 5):
                i += 1
                continue

            if len(question) < 10:
                i += 1
                continue

            # Look ahead for probabilities
            outcomes = []
            seen_pcts = set()

            for j in range(i+1, min(i+15, len(lines))):
                next_line = lines[j].strip()

                # Find percentage values
                pct_found = re.findall(r'(\d+)%', next_line)
                for pct_str in pct_found:
                    pct = int(pct_str)
                    if pct not in seen_pcts and 1 <= pct <= 99:
                        seen_pcts.add(pct)
                        # Determine label from surrounding context
                        label = "Yes" if len(outcomes) == 0 else f"Option{len(outcomes)+1}"

                        # Try to find named outcome
                        # Look for span or link text near this pct
                        context_before = ' '.join(lines[max(j-3,0):j])
                        context_after = ' '.join(lines[j:min(j+3,len(lines))])

                        label_match = re.search(r'<span[^>]*>([^<]{2,40})</span>', next_line)
                        if label_match:
                            potential_label = label_match.group(1).strip()
                            if len(potential_label) > 2 and potential_label not in ['Yes', 'No', '100%', '0%']:
                                label = potential_label

                        outcomes.append({"label": label, "pct": pct})

                # Stop if we've gone too far without finding the market
                if len(outcomes) >= 4:
                    break

                # If we hit another event link, stop
                if re.search(r'/event/', next_line) and j > i + 2:
                    break

            if outcomes:
                markets.append({
                    "question": question,
                    "slug": slug,
                    "url": f"https://polymarket.com/event/{slug}",
                    "outcomes": outcomes[:4]  # max 4 outcomes
                })

        i += 1

    # Deduplicate by slug
    seen_slugs = set()
    unique = []
    for m in markets:
        if m['slug'] not in seen_slugs:
            seen_slugs.add(m['slug'])
            unique.append(m)
    return unique

def get_category_markets(category):
    """Fetch and parse markets for a category."""
    print(f"Fetching /events/{category}...")
    url = f"https://polymarket.com/events/{category}"
    html = fetch_url(url)
    if not html:
        return []

    if category == "breaking":
        return parse_breaking_page(html)
    else:
        return parse_markets_from_html(html)

def get_market_detail(url):
    """Get detailed outcomes for a specific market."""
    print(f"  Fetching detail: {url}")
    html = fetch_url(url)
    if not html:
        return None

    outcomes = []
    # Look for outcome prices
    price_matches = re.findall(r'"outcome":\s*"([^"]+)"[^}]*"price":\s*([\d.]+)', html)
    for label, price in price_matches:
        pct = round(float(price) * 100, 0)
        if pct > 0:
            outcomes.append({"label": label, "pct": int(pct)})

    if not outcomes:
        # Fallback: parse from HTML
        pct_found = re.findall(r'([\d]+)%', html[:3000])
        for pct_str in pct_found[:4]:
            pct = int(pct_str)
            if 1 <= pct <= 99:
                outcomes.append({"label": "Yes" if pct > 50 else "No", "pct": pct})

    return {"outcomes": outcomes} if outcomes else None

def generate_dashboard(all_markets):
    """Generate the HTML dashboard."""
    import datetime

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Group markets by category
    ai_markets = [m for m in all_markets if '/ai' in m.get('_category', '') or
                  any(kw in m['question'].lower() for kw in ['ai ', 'model', 'anthropic', 'openai', 'nvidia', 'tech', 'largest company'])]
    breaking_markets = [m for m in all_markets if m.get('_category') == 'breaking']
    finance_markets = [m for m in all_markets if m.get('_category') in ('finance', 'tech') and
                       any(kw in m['question'].lower() for kw in ['fed', 'rate', 'oil', 'crude', 'wti', '降息', '原油', 'ipo', 'spacex', 'anthropic'])]

    # Filter for interesting markets
    interesting_slugs = {
        'ai': ['ai-model', 'anthropic', 'openai', 'nvidia', 'largest-company', 'best-ai'],
        'iran': ['iran', 'hormuz', 'trump', 'ceasefire', 'diplomatic', 'embargo', 'nuclear'],
        'finance': ['fed', 'rate', 'oil', 'crude', 'wti', 'ipo', 'anthropic', 'spacex'],
        'hormuz': ['hormuz', 'shipping', 'transit', 'ships'],
    }

    filtered = {}
    for cat, keywords in interesting_slugs.items():
        filtered[cat] = [
            m for m in all_markets
            if any(kw in m['question'].lower() for kw in keywords)
            or any(kw in (m.get('slug') or '').lower() for kw in keywords)
        ]
        # Deduplicate
        seen = set()
        filtered[cat] = [m for m in filtered[cat]
                        if m['slug'] not in seen and not seen.add(m['slug'])]

    # Limit to top 8 per category
    for cat in filtered:
        filtered[cat] = filtered[cat][:8]

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Polymarket 热门预测看板</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;background:#0f1117;color:#e2e8f0;min-height:100vh;padding-bottom:60px}}
.header{{background:linear-gradient(135deg,#1a1d2e 0%,#2d1b4e 100%);padding:24px 20px 20px;color:#fff}}
.header h1{{font-size:20px;font-weight:700;margin-bottom:4px;display:flex;align-items:center;gap:8px}}
.header p{{font-size:12px;opacity:0.6}}
.header .updated{{font-size:11px;opacity:0.5;margin-top:4px}}
.cat-tabs{{display:flex;gap:8px;padding:16px 20px;background:#1a1d2e;flex-wrap:wrap}}
.cat-tab{{padding:8px 16px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;background:#2d2d3d;color:#9ca3af;border:none;transition:all 0.15s}}
.cat-tab:hover{{background:#3d3d4d;color:#fff}}
.cat-tab.active{{background:#6366f1;color:#fff}}
.content{{padding:20px;max-width:1200px;margin:0 auto}}
.cat-section{{margin-bottom:40px}}
.cat-title{{font-size:16px;font-weight:700;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid #2d2d3d;display:flex;align-items:center;gap:8px}}
.market-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}}
.market-card{{background:#1a1d2e;border:1px solid #2d2d3d;border-radius:12px;padding:16px;transition:all 0.15s}}
.market-card:hover{{border-color:#6366f1;transform:translateY(-1px)}}
.market-question{{font-size:13px;font-weight:600;color:#fff;margin-bottom:12px;line-height:1.5}}
.market-link{{display:inline-block;font-size:11px;color:#6366f1;text-decoration:none;margin-bottom:10px}}
.market-link:hover{{text-decoration:underline}}
.outcome-bar{{margin-bottom:6px}}
.outcome-label{{font-size:12px;color:#9ca3af;margin-bottom:3px;display:flex;justify-content:space-between}}
.outcome-track{{height:6px;background:#2d2d3d;border-radius:3px;overflow:hidden}}
.outcome-fill{{height:100%;border-radius:3px;transition:width 0.3s}}
.outcome-fill.yes{{background:linear-gradient(90deg,#22c55e,#4ade80)}}
.outcome-fill.no{{background:linear-gradient(90deg,#ef4444,#f87171)}}
.outcome-fill.neutral{{background:linear-gradient(90deg,#6366f1,#818cf8)}}
.pct-badge{{font-size:12px;font-weight:700;min-width:36px;text-align:right}}
.yes-pct{{color:#22c55e}}
.no-pct{{color:#ef4444}}
.footer{{text-align:center;padding:20px;font-size:11px;color:#4b5563}}
.no-data{{text-align:center;padding:40px;color:#6b7280;font-size:13px}}
.vol-tag{{font-size:10px;color:#6b7280;margin-left:6px}}
.disclaimer{{font-size:10px;color:#6b7280;padding:12px 20px;text-align:center;line-height:1.6}}
@media(max-width:600px){{
  .market-grid{{grid-template-columns:1fr}}
  .cat-tabs{{padding:12px 16px}}
  .content{{padding:16px}}
}}
</style>
</head>
<body>

<header class="header">
  <h1>🔮 Polymarket 热门预测看板</h1>
  <p>实时抓取 Polymarket 全球预测市场数据 · 真金白银的市场情绪</p>
  <div class="updated">数据更新时间：{now} (每6小时自动更新)</div>
</header>

<div class="cat-tabs">
  <button class="cat-tab active" onclick="showSection('all')">📊 全热门</button>
  <button class="cat-tab" onclick="showSection('ai')">🤖 AI</button>
  <button class="cat-tab" onclick="showSection('iran')">🌍 中东/伊朗</button>
  <button class="cat-tab" onclick="showSection('finance')">💰 金融</button>
  <button class="cat-tab" onclick="showSection('hormuz')">⚓ 霍尔木兹</button>
</div>

<div class="content">
'''

    # Add sections for each category
    sections = [
        ("all", "📊 全热门预测", [m for m in all_markets if m.get('_category') == 'breaking'][:12]),
        ("ai", "🤖 AI与最强模型", filtered.get('ai', [])),
        ("iran", "🌍 美伊/中东局势", filtered.get('iran', [])),
        ("finance", "💰 金融与宏观", filtered.get('finance', [])),
        ("hormuz", "⚓ 霍尔木兹海峡", filtered.get('hormuz', [])),
    ]

    for sec_id, sec_title, sec_markets in sections:
        html += f'<div id="sec-{sec_id}" class="cat-section">\n'
        html += f'<div class="cat-title">{sec_title}</div>\n'
        if not sec_markets:
            html += '<div class="no-data">暂无数据</div>\n'
        else:
            html += '<div class="market-grid">\n'
            for m in sec_markets:
                html += market_card(m)
            html += '</div>\n'
        html += '</div>\n'

    html += f'''
</div>

<div class="disclaimer">
  ⚠️ 数据来源：Polymarket.com · 概率仅供参考，不构成投资建议 · 市场有风险，入市需谨慎
</div>

<script>
function showSection(id) {{
  // Update tabs
  document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
  event.target.classList.add('active');
  // Show/hide sections
  document.querySelectorAll('.cat-section').forEach(s => {{
    s.style.display = id === 'all' ? 'block' : 'none';
  }});
  if (id !== 'all') {{
    const target = document.getElementById('sec-' + id);
    if (target) target.style.display = 'block';
  }}
}}

// Auto-switch to AI tab on load (or keep on all)
const hash = window.location.hash.replace('#', '');
if (hash && document.getElementById('sec-' + hash)) {{
  document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.cat-section').forEach(s => s.style.display = 'none');
  const target = document.getElementById('sec-' + hash);
  if (target) target.style.display = 'block';
  // Find and activate the right tab button
  document.querySelectorAll('.cat-tab').forEach(t => {{
    if (t.textContent.includes(hash === 'ai' ? 'AI' : hash === 'iran' ? '中东' : hash === 'finance' ? '金融' : hash === 'hormuz' ? '霍尔木兹' : '')) {{
      t.classList.add('active');
    }}
  }});
}}
</script>
</body>
</html>'''

    return html

def market_card(m):
    """Generate HTML for a single market card."""
    outcomes = m.get('outcomes', [])
    if not outcomes:
        return ''

    question = m['question']
    slug = m['slug']
    url = m['url']

    # Truncate long questions
    if len(question) > 100:
        question = question[:97] + '...'

    # Build outcome bars
    outcome_html = ''
    for o in outcomes[:4]:  # max 4 outcomes
        label = o['label']
        pct = o['pct']
        if pct > 50:
            css_class = 'yes' if label.lower() in ('yes', 'true', 'no') and pct > 50 else 'neutral'
            css_class = 'yes' if label.lower() == 'yes' else ('no' if label.lower() == 'no' else 'neutral')
        else:
            css_class = 'no' if label.lower() == 'no' else 'neutral'

        pct_disp = f"{pct}%"

        outcome_html += f'''<div class="outcome-bar">
  <div class="outcome-label">
    <span>{label}</span>
    <span class="pct-badge {'yes-pct' if pct > 50 else 'no-pct'}">{pct_disp}</span>
  </div>
  <div class="outcome-track">
    <div class="outcome-fill {css_class}" style="width:{pct}%"></div>
  </div>
</div>'''

    return f'''<div class="market-card">
  <a href="{url}" target="_blank" class="market-link">🔗 {slug[:50]}</a>
  <div class="market-question">{question}</div>
  {outcome_html}
</div>'''

def main():
    print("🚀 Polymarket Dashboard Fetcher")
    print("=" * 50)

    all_markets = []

    # Fetch each category
    for cat in FETCH_CATEGORIES:
        markets = get_category_markets(cat)
        for m in markets:
            m['_category'] = cat
        all_markets.extend(markets)
        print(f"  → Found {len(markets)} markets in {cat}")
        time.sleep(1)  # Be polite

    # Deduplicate by slug
    seen = {}
    unique = []
    for m in all_markets:
        slug = m['slug']
        if slug not in seen:
            seen[slug] = m
            unique.append(m)
    all_markets = unique
    print(f"\n✅ Total unique markets: {len(all_markets)}")

    # Save raw data
    import os
    os.makedirs('/root/.openclaw/workspace/polymarket-dashboard', exist_ok=True)
    with open('/root/.openclaw/workspace/polymarket-dashboard/markets_raw.json', 'w') as f:
        json.dump(all_markets, f, ensure_ascii=False, indent=2)

    # Generate HTML
    html = generate_dashboard(all_markets)
    out_path = '/root/.openclaw/workspace/polymarket-dashboard/index.html'
    with open(out_path, 'w') as f:
        f.write(html)
    print(f"✅ Dashboard generated: {out_path}")
    print(f"   Size: {len(html)} bytes")

    return all_markets

if __name__ == '__main__':
    main()
