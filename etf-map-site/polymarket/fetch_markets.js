#!/usr/bin/env node
/**
 * Polymarket Fetcher using Puppeteer
 * Fetches JavaScript-rendered Polymarket pages and extracts market data.
 */

const puppeteer = require('puppeteer');

const CATEGORIES = [
  { id: 'ai', name: '🤖 AI与科技', url: 'https://polymarket.com/events/ai' },
  { id: 'tech', name: '💻 科技', url: 'https://polymarket.com/events/tech' },
  { id: 'finance', name: '💰 金融', url: 'https://polymarket.com/events/finance' },
  { id: 'breaking', name: '🔥 热门', url: 'https://polymarket.com/breaking' },
  { id: 'iran', name: '🌍 中东/伊朗', url: 'https://polymarket.com/events/iran' },
];

const HOT_KEYWORDS = {
  ai: ['ai', 'anthropic', 'openai', 'nvidia', 'gpt', 'model', 'largest company', 'best ai'],
  iran: ['iran', 'ceasefire', 'diplomatic', 'trump', 'nuclear', 'sanction', 'embargo', 'middle east'],
  finance: ['fed', 'rate cut', 'oil', 'wti', 'crude', 'ipo', 'spacex', 'anthropic', 'inflation', 'gdp'],
  hormuz: ['hormuz', 'shipping', 'transit', 'ships', 'straits'],
};

const KNOWN_HOT_MARKETS = [
  // AI markets
  { slug: 'which-company-has-the-best-ai-model-end-of-april', cat: 'ai' },
  { slug: 'which-company-has-the-best-ai-model-end-of-may', cat: 'ai' },
  { slug: 'which-company-has-best-ai-model-end-of-june', cat: 'ai' },
  { slug: 'largest-company-end-of-april-738', cat: 'ai' },
  { slug: 'largest-company-end-of-june-712', cat: 'ai' },
  { slug: '2nd-largest-company-end-of-april', cat: 'ai' },
  { slug: 'anthropic-ipo-closing-market-cap-119', cat: 'ai' },
  // Iran/Hormuz markets
  { slug: 'iran-agrees-to-unrestricted-shipping-through-hormuz-in-april', cat: 'hormuz' },
  { slug: 'will-ships-transit-the-strait-of-hormuz-on-any-day-by-end-of-april', cat: 'hormuz' },
  { slug: 'how-many-ships-will-iran-successfully-target-by-april-30', cat: 'iran' },
  { slug: 'us-x-iran-diplomatic-meeting-by-april-22-2026', cat: 'iran' },
  { slug: 'will-trump-announce-that-the-us-x-iran-ceasefire-has-been-broken-by-april-21-2026', cat: 'iran' },
  { slug: 'who-will-attend-the-next-us-x-iran-diplomatic-meeting', cat: 'iran' },
  { slug: 'what-will-the-us-agree-to', cat: 'iran' },
  { slug: 'iranian', cat: 'iran' },
  // Finance markets
  { slug: 'how-many-fed-rate-cuts-in-2026', cat: 'finance' },
  { slug: 'what-price-will-wti-hit-in-april-2026', cat: 'finance' },
  { slug: 'spacex-ipo-by', cat: 'finance' },
];

async function fetchWithPuppeteer(url) {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
  });
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36');
  await page.setExtraHTTPHeaders({ 'Accept-Language': 'en-US,en;q=0.9' });

  try {
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });
    // Wait a bit for dynamic content
    await page.waitForTimeout(3000);

    // Extract text content from the page
    const content = await page.evaluate(() => {
      // Try to find market cards
      const cards = document.querySelectorAll('[data-testid="market-card"], .market-card, .智能-\\:nth-child');
      const results = [];

      // Get all text content from main content area
      const main = document.querySelector('main') || document.body;
      const text = main.innerText || main.textContent || '';

      return {
        text: text.substring(0, 50000),
       html: document.body.innerHTML.substring(0, 200000)
      };
    });

    return { content, url };
  } finally {
    await browser.close();
  }
}

function parseProbabilities(text) {
  // Extract question + probability pairs from text
  const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
  const markets = [];
  let currentQuestion = null;
  let currentSlug = null;
  let currentOutcomes = [];

  for (const line of lines) {
    // Check if this looks like a question
    if (line.length > 15 && line.length < 300) {
      // Look for probability pattern nearby in next few lines
      const idx = lines.indexOf(line);
      let probs = [];
      for (let j = idx + 1; j < Math.min(idx + 10, lines.length); j++) {
        const matches = lines[j].match(/(\d+)%/g);
        if (matches) {
          probs = matches.map(m => parseInt(m));
          break;
        }
      }

      if (probs.length > 0 && !line.match(/^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$/)) {
        // Looks like a market question
        if (currentQuestion && currentOutcomes.length > 0) {
          markets.push({
            question: currentQuestion,
            slug: currentSlug || '',
            outcomes: currentOutcomes.slice(0, 4)
          });
        }
        currentQuestion = line;
        currentSlug = null;
        currentOutcomes = probs.map(pct => ({
          label: pct > 50 ? 'Yes' : 'No',
          pct: pct
        }));
      }
    }
  }

  // Don't forget last
  if (currentQuestion && currentOutcomes.length > 0) {
    markets.push({
      question: currentQuestion,
      slug: currentSlug || '',
      outcomes: currentOutcomes.slice(0, 4)
    });
  }

  return markets;
}

async function fetchMarketDetail(slug) {
  const url = `https://polymarket.com/event/${slug}`;
  try {
    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    });
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36');
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });
    await page.waitForTimeout(2000);

    const result = await page.evaluate(() => {
      const text = document.body.innerText || '';
      const html = document.body.innerHTML || '';

      // Extract probabilities
      const probMatches = text.match(/(\d+)%/g) || [];
      const uniqueProbs = [...new Set(probMatches.map(p => parseInt(p)))].filter(p => p > 0 && p < 100);

      // Extract question
      const h1 = document.querySelector('h1');
      const question = h1 ? h1.innerText : '';

      // Find Yes/No labels
      const outcomes = [];
      // Look for outcome labels and their prices
      const labels = [];
      const yesMatch = text.match(/Yes[\s\n]+(\d+)%/i);
      const noMatch = text.match(/No[\s\n]+(\d+)%/i);
      if (yesMatch) outcomes.push({ label: 'Yes', pct: parseInt(yesMatch[1]) });
      if (noMatch) outcomes.push({ label: 'No', pct: parseInt(noMatch[1]) });

      // Get URL
      const canonical = document.querySelector('link[rel="canonical"]');
      const pageUrl = canonical ? canonical.href : window.location.href;

      return {
        question: question.substring(0, 300),
        url: pageUrl,
        outcomes,
        rawText: text.substring(0, 3000),
        allProbs: uniqueProbs.slice(0, 8)
      };
    });

    await browser.close();
    return { slug, url, ...result };
  } catch (e) {
    console.error(`  Error fetching ${slug}: ${e.message}`);
    return { slug, url, outcomes: [], error: e.message };
  }
}

async function main() {
  console.log('🚀 Polymarket Fetcher (Puppeteer)')
  console.log('=' .repeat(50));

  const allMarkets = [];

  // Step 1: Fetch known hot markets (most reliable)
  console.log('\n📦 Fetching known hot markets...');
  for (const { slug, cat } of KNOWN_HOT_MARKETS) {
    process.stdout.write(`  Fetching ${slug}... `);
    const result = await fetchMarketDetail(slug);
    if (result.question && result.outcomes && result.outcomes.length > 0) {
      console.log(`✅ ${result.question.substring(0, 50)} - ${result.outcomes.map(o => `${o.label}:${o.pct}%`).join(', ')}`);
      allMarkets.push({
        ...result,
        _category: cat
      });
    } else if (result.allProbs && result.allProbs.length > 0) {
      // Fallback: use text probabilities
      const outcomes = result.allProbs.map(p => ({
        label: 'Yes',
        pct: p
      }));
      console.log(`⚠️ ${result.question?.substring(0, 50) || slug} - probs: ${result.allProbs.join(', ')}`);
      allMarkets.push({
        question: result.question || slug,
        url: result.url,
        slug,
        outcomes,
        _category: cat
      });
    } else {
      console.log(`❌ no data`);
    }
    await new Promise(r => setTimeout(r, 800));
  }

  console.log(`\n✅ Total markets collected: ${allMarkets.length}`);

  // Step 2: Save raw data
  const fs = require('fs');
  const path = require('path');
  const outDir = '/root/.openclaw/workspace/polymarket-dashboard';
  fs.mkdirSync(outDir, { recursive: true });
  fs.writeFileSync(`${outDir}/markets_raw.json`, JSON.stringify(allMarkets, null, 2));

  // Step 3: Generate dashboard HTML
  generateDashboard(allMarkets, outDir);

  console.log(`\n✨ Done! Dashboard generated.`);
}

function generateDashboard(markets, outDir) {
  const fs = require('fs');

  const now = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });

  // Build market sections
  const catNames = {
    ai: '🤖 AI与最强模型',
    iran: '🌍 美伊/中东局势',
    finance: '💰 金融与宏观',
    hormuz: '⚓ 霍尔木兹海峡',
  };

  let sectionsHtml = '';
  for (const [catId, catName] of Object.entries(catNames)) {
    const catMarkets = markets.filter(m => m._category === catId).slice(0, 10);
    if (catMarkets.length === 0) continue;

    sectionsHtml += `<div id="sec-${catId}" class="cat-section">
  <div class="cat-title">${catName} <span style="font-size:12px;font-weight:400;opacity:0.6">(${catMarkets.length}个市场)</span></div>
  <div class="market-grid">
`;

    for (const m of catMarkets) {
      const question = m.question.length > 90 ? m.question.substring(0, 87) + '...' : m.question;
      const outcomes = m.outcomes || [];

      let outcomesHtml = '';
      for (const o of outcomes.slice(0, 4)) {
        const pct = typeof o.pct === 'number' ? o.pct : parseFloat(o.pct);
        const label = o.label || 'Yes';
        const isYes = label.toLowerCase() === 'yes';
        const colorClass = isYes ? 'yes-pct' : 'no-pct';
        const barClass = isYes ? 'yes' : 'no';
        const barPct = pct > 0 && pct < 100 ? pct : (isYes ? pct : 100 - pct);

        outcomesHtml += `<div class="outcome-bar">
      <div class="outcome-label">
        <span>${label}</span>
        <span class="pct-badge ${colorClass}">${pct}%</span>
      </div>
      <div class="outcome-track">
        <div class="outcome-fill ${barClass}" style="width:${Math.min(100, Math.max(2, pct))}%"></div>
      </div>
    </div>`;
      }

      const slug = m.slug || m.url?.split('/event/')[1] || '';
      const marketUrl = m.url || `https://polymarket.com/event/${slug}`;

      sectionsHtml += `    <div class="market-card">
      <a href="${marketUrl}" target="_blank" class="market-link">🔗 查看详情 →</a>
      <div class="market-question">${question}</div>
      ${outcomes.length > 0 ? outcomesHtml : '<div style="color:#6b7280;font-size:12px">数据加载中...</div>'}
    </div>\n`;
    }

    sectionsHtml += `  </div>
</div>\n`;
  }

  const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Polymarket 热门预测看板</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;background:#0f1117;color:#e2e8f0;min-height:100vh;padding-bottom:80px}
.header{background:linear-gradient(135deg,#1a1d2e 0%,#2d1b4e 100%);padding:24px 20px 20px;color:#fff}
.header h1{font-size:22px;font-weight:700;margin-bottom:6px;display:flex;align-items:center;gap:8px}
.header p{font-size:12px;opacity:0.6}
.updated{font-size:11px;opacity:0.45;margin-top:6px}
.cat-tabs{display:flex;gap:8px;padding:14px 20px;background:#1a1d2e;flex-wrap:wrap;position:sticky;top:0;z-index:10}
.cat-tab{padding:7px 14px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;background:#252536;color:#9ca3af;border:1px solid #2d2d3d;transition:all 0.15s}
.cat-tab:hover{background:#2d2d4d;color:#fff}
.cat-tab.active{background:#6366f1;color:#fff;border-color:#6366f1}
.content{padding:20px;max-width:1200px;margin:0 auto}
.disclaimer{font-size:10px;color:#4b5563;padding:16px 20px;text-align:center;line-height:1.8;border-top:1px solid #1a1d2e;margin-top:20px}
.no-data{text-align:center;padding:40px 20px;color:#6b7280;font-size:13px}
.cat-section{margin-bottom:40px}
.cat-title{font-size:16px;font-weight:700;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #252536;display:flex;align-items:center;gap:8px}
.market-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:14px}
.market-card{background:#1a1d2e;border:1px solid #252536;border-radius:12px;padding:16px;transition:all 0.2s}
.market-card:hover{border-color:#6366f1;transform:translateY(-2px);box-shadow:0 4px 20px rgba(99,102,241,0.1)}
.market-link{display:inline-block;font-size:11px;color:#6366f1;text-decoration:none;margin-bottom:8px}
.market-link:hover{text-decoration:underline}
.market-question{font-size:13px;font-weight:600;color:#f1f5f9;margin-bottom:12px;line-height:1.5;min-height:40px}
.outcome-bar{margin-bottom:6px}
.outcome-label{font-size:12px;color:#9ca3af;margin-bottom:3px;display:flex;justify-content:space-between;align-items:center}
.pct-badge{font-size:13px;font-weight:700;min-width:36px;text-align:right}
.yes-pct{color:#22c55e}
.no-pct{color:#ef4444}
.outcome-track{height:5px;background:#252536;border-radius:3px;overflow:hidden}
.outcome-fill{height:100%;border-radius:3px;transition:width 0.5s ease}
.outcome-fill.yes{background:linear-gradient(90deg,#16a34a,#22c55e)}
.outcome-fill.no{background:linear-gradient(90deg,#dc2626,#ef4444)}
.outcome-fill.neutral{background:linear-gradient(90deg,#6366f1,#818cf8)}
.refresh-bar{text-align:center;padding:12px;background:#1a1d2e;border-bottom:1px solid #252536}
.refresh-bar button{background:#252536;color:#9ca3af;border:1px solid #2d2d3d;padding:8px 20px;border-radius:8px;cursor:pointer;font-size:12px;transition:all 0.15s}
.refresh-bar button:hover{background:#2d2d4d;color:#fff}
@media(max-width:600px){.market-grid{grid-template-columns:1fr}.content{padding:16px}.cat-tabs{padding:10px 16px}}
</style>
</head>
<body>

<div class="header">
  <h1>🔮 Polymarket 热门预测看板</h1>
  <p>实时抓取 Polymarket 全球预测市场 · 真金白银押注的市场共识</p>
  <div class="updated">数据更新时间：${now} · 每6小时自动刷新</div>
</div>

<div class="refresh-bar">
  <button onclick="location.reload()">🔄 刷新数据</button>
</div>

<div class="cat-tabs">
  <button class="cat-tab active" onclick="showSection('ai', this)">🤖 AI</button>
  <button class="cat-tab" onclick="showSection('hormuz', this)">⚓ 霍尔木兹</button>
  <button class="cat-tab" onclick="showSection('iran', this)">🌍 美伊局势</button>
  <button class="cat-tab" onclick="showSection('finance', this)">💰 金融</button>
</div>

<div class="content">
  ${sectionsHtml || '<div class="no-data">暂无数据，请刷新页面</div>'}
</div>

<div class="disclaimer">
  ⚠️ 数据来源：<a href="https://polymarket.com" style="color:#6366f1">Polymarket.com</a> · 概率仅供参考，不构成投资建议 · 市场有风险，入市需谨慎<br>
  本页面每6小时自动从Polymarket抓取最新数据 · 预测市场反映真金白银的市场情绪
</div>

<script>
function showSection(id, btn) {
  // Update tabs
  document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
  if (btn) btn.classList.add('active');
  
  // Show/hide sections
  document.querySelectorAll('.cat-section').forEach(s => {
    s.style.display = 'none';
  });
  const target = document.getElementById('sec-' + id);
  if (target) target.style.display = 'block';
}

// Show AI section by default on load
showSection('ai', document.querySelector('.cat-tab.active'));

// URL hash support
if (window.location.hash) {
  const cat = window.location.hash.replace('#', '');
  const btn = document.querySelector(\`.cat-tab[onclick*=\"\${cat}\"]\`);
  if (btn) showSection(cat, btn);
}
</script>

</body>
</html>`;

  fs.writeFileSync(`${outDir}/index.html`, html);
  console.log(`✅ Dashboard saved: ${outDir}/index.html (${html.length} bytes)`);
}

main().catch(console.error);
