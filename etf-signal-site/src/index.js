/**
 * ETF 择时信号 - Cloudflare Worker
 * 数据来源: HKEx CCASS 公开数据 (https://www3.hkexnews.hk/sdw/search/searchsdw_c.aspx)
 * 策略: 基于港股杠反ETF份额变化的择时策略（开源证券）
 * 架构: KV缓存 + 后台抓取，避免Worker超时
 */

const TARGET_ETFS = [
  { code: '07226', name: '南方2倍做多恒生科技', type: '2x_long',  index: '恒生科技' },
  { code: '07552', name: '南方2倍做空恒生科技', type: '2x_short', index: '恒生科技' },
  { code: '03033', name: '南方恒生科技',          type: 'normal',   index: '恒生科技' },
  { code: '07200', name: '南方2倍做多恒指',       type: '2x_long',  index: '恒生指数' },
  { code: '07500', name: '南方2倍做空恒指',       type: '2x_short', index: '恒生指数' },
  { code: '03037', name: '南方恒生指数',           type: 'normal',   index: '恒生指数' },
];

const STRATEGY = {
  '恒生科技': { N: 20, lambda1: 1.2, lambda2: 1.0 },
  '恒生指数': { N: 20, lambda1: 1.0, lambda2: 1.0 },
};

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

// ============================================================
// HKEx CCASS 爬虫
// ============================================================
async function fetchCCASSFromHKEx(etfCode, dateStr) {
  const baseUrl = 'https://www3.hkexnews.hk/sdw/search/searchsdw_c.aspx';
  const headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9',
  };

  // Step 1: 获取表单参数
  const pageResp = await fetch(baseUrl, { headers });
  const pageHtml = await pageResp.text();
  const vs  = extractField(pageHtml, '__VIEWSTATE');
  const vsg = extractField(pageHtml, '__VIEWSTATEGENERATOR');
  const ev  = extractField(pageHtml, '__EVENTVALIDATION') || '';
  const today = extractField(pageHtml, 'today') || '';

  // Step 2: POST 查询
  const body = new URLSearchParams({
    '__EVENTTARGET': 'btnSearch',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': vs,
    '__VIEWSTATEGENERATOR': vsg,
    '__EVENTVALIDATION': ev,
    'today': today,
    'sortBy': 'shareholding',
    'sortDirection': 'desc',
    'originalShareholdingDate': dateStr,
    'alertMsg': '',
    'txtShareholdingDate': dateStr,
    'txtStockCode': etfCode,
    'txtStockName': '',
    'txtParticipantID': '',
    'txtParticipantName': '',
    'txtSelPartID': '',
  }).toString();

  const postResp = await fetch(baseUrl, {
    method: 'POST',
    headers: { ...headers, 'Content-Type': 'application/x-www-form-urlencoded', 'Referer': baseUrl },
    body,
  });
  const resultHtml = await postResp.text();
  return parseCCASSHtml(resultHtml);
}

function extractField(html, name) {
  const m = html.match(new RegExp('<input[^>]*name="' + name + '"[^>]*value="([^"]*)"', 'i'));
  return m ? m[1] : '';
}

function parseCCASSHtml(html) {
  const result = { futuTotal: 0, totalShares: 0, futuPercent: '0.00', rows: [] };
  // 匹配每行: participant-id | name | address | shareholding | percent
  const rowRe = /<tr>([\s\S]*?)<\/tr>/g;
  let row;
  while ((row = rowRe.exec(html)) !== null) {
    const tr = row[1];
    const idMatch  = tr.match(/col-participant-id[\s\S]*?mobile-list-body[^>]*>([^<]+)</);
    const nameMatch = tr.match(/col-participant-name[\s\S]*?mobile-list-body[^>]*>([^<]+)</);
    const shareMatch = tr.match(/col-shareholding["\s][^>]*>[\s\S]*?mobile-list-body[^>]*>([\d,]+)</);
    const pctMatch  = tr.match(/col-shareholding-percent["\s][^>]*>[\s\S]*?mobile-list-body[^>]*>([\d.]+%?)</);
    if (idMatch && nameMatch && shareMatch) {
      const id    = idMatch[1].trim();
      const name = nameMatch[1].replace(/<[^>]+>/g, '').trim();
      const shares = parseInt(shareMatch[1].replace(/,/g, ''), 10);
      const pct   = pctMatch ? pctMatch[1] : '';
      result.rows.push({ id, name, shares, pct });
      result.totalShares += shares;
      if (name.includes('富途') || /FUTU/i.test(name)) {
        result.futuTotal = shares;
        result.futuPercent = pct;
      }
    }
  }
  return result;
}

// ============================================================
// 策略信号计算
// ============================================================
function calculateSignal(historyByType, indexName) {
  const { N, lambda1, lambda2 } = STRATEGY[indexName] || { N: 20, lambda1: 1.0, lambda2: 1.0 };
  const long  = historyByType.filter(d => d.type === '2x_long');
  const short = historyByType.filter(d => d.type === '2x_short');
  if (long.length < 2 || short.length < 2) return { signal: '观望', reason: '数据不足(N<2)' };

  const curL  = long[long.length - 1]?.futuShareholding  || 0;
  const curS  = short[short.length - 1]?.futuShareholding || 0;
  const prevL = long[Math.max(0, long.length - 1 - N)]?.futuShareholding  || 0;
  const prevS = short[Math.max(0, short.length - 1 - N)]?.futuShareholding || 0;

  const deltaL = prevL > 0 ? ((curL - prevL) / prevL * 100) : 0;
  const deltaS = prevS > 0 ? ((curS - prevS) / prevS * 100) : 0;

  if (deltaL < -lambda1 || deltaS > lambda1)
    return { signal: '买入', deltaL, deltaS, reason: '散户多头离场或空头进场' };
  if (deltaL > lambda2 || deltaS < -lambda2)
    return { signal: '卖出', deltaL, deltaS, reason: '散户多头进场或空头离场' };
  return { signal: '观望', deltaL, deltaS, reason: '无明确信号' };
}

// ============================================================
// 后台抓取（被 waitUntil 和 cron 调用）
// ============================================================
async function refreshAllData(env) {
  const dateStr = fmtDate(new Date());
  console.log(`[refresh] Starting for ${dateStr}`);

  for (const etf of TARGET_ETFS) {
    try {
      let history = [];
      if (env.ETF_DATA) {
        const cached = await env.ETF_DATA.get(`etf:${etf.code}`);
        if (cached) history = JSON.parse(cached);
      }
      const data = await fetchCCASSFromHKEx(etf.code, dateStr);
      history.push({ date: dateStr, futuShareholding: data.futuTotal, totalShareholding: data.totalShares });
      if (history.length > 365) history = history.slice(-365);
      if (env.ETF_DATA) await env.ETF_DATA.put(`etf:${etf.code}`, JSON.stringify(history));
      console.log(`[refresh] ${etf.code}: futu=${data.futuTotal}, total=${data.totalShares}, pct=${data.futuPercent}`);
    } catch (e) {
      console.error(`[refresh] Failed ${etf.code}: ${e.message}`);
    }
  }

  // 计算并缓存信号
  const signals = await computeSignals(dateStr, env);
  if (env.ETF_DATA) {
    await env.ETF_DATA.put(`signals:${dateStr}`, JSON.stringify(signals), { expirationTtl: 86400 * 7 });
  }
  console.log(`[refresh] Done: ${dateStr}`);
}

async function computeSignals(dateStr, env) {
  const etfResults = {};
  for (const etf of TARGET_ETFS) {
    let history = [];
    if (env.ETF_DATA) {
      const cached = await env.ETF_DATA.get(`etf:${etf.code}`);
      if (cached) history = JSON.parse(cached);
    }
    const latest = history[history.length - 1] || {};
    const pct = latest.totalShareholding > 0
      ? (latest.futuShareholding / latest.totalShareholding * 100).toFixed(2)
      : '0.00';
    etfResults[etf.code] = { ...etf, futuTotal: latest.futuShareholding || 0, totalShares: latest.totalShareholding || 0, futuPercent: pct, history: history };
  }

  // 按指数分组计算信号
  const { N, lambda1, lambda2 } = STRATEGY['恒生科技'];
  const hstHist = { '2x_long': [], '2x_short': [], 'normal': [] };
  const hsiHist = { '2x_long': [], '2x_short': [], 'normal': [] };
  for (const [code, result] of Object.entries(etfResults)) {
    const hist = result.history || [];
    const h = hist.map(r => ({ type: result.type, futuShareholding: r.futuShareholding || 0, date: r.date }));
    if (result.index === '恒生科技') {
      hstHist[result.type].push(...h);
    } else {
      hsiHist[result.type].push(...h);
    }
  }
  // 每类取公共日期
  function intersectHist(histMap) {
    const allDates = new Set();
    for (const arr of Object.values(histMap)) {
      for (const h of arr) allDates.add(h.date);
    }
    const sorted = [...allDates].sort();
    return sorted;
  }
  const hstDates = intersectHist(hstHist);
  const hsiDates = intersectHist(hsiHist);

  function calcFromHist(dates, histMap, idxName) {
    const { N, lambda1, lambda2 } = STRATEGY[idxName];
    if (dates.length < 2) return { signal: '观望', reason: '数据不足' };
    const today = dates[dates.length - 1];
    const Nidx = Math.max(0, dates.length - 1 - N);
    const Nday = dates[Nidx];
    function sumType(type) {
      return (histMap[type] || [])
        .filter(h => h.date === today)
        .reduce((s, h) => s + h.futuShareholding, 0);
    }
    function sumTypePrev(type) {
      return (histMap[type] || [])
        .filter(h => h.date === Nday)
        .reduce((s, h) => s + h.futuShareholding, 0);
    }
    const curL = sumType('2x_long'), curS = sumType('2x_short');
    const prevL = sumTypePrev('2x_long'), prevS = sumTypePrev('2x_short');
    const dL = prevL > 0 ? (curL - prevL) / prevL * 100 : 0;
    const dS = prevS > 0 ? (curS - prevS) / prevS * 100 : 0;
    if (dL < -lambda1 || dS > lambda1) return { signal: '买入', deltaL: +dL.toFixed(2), deltaS: +dS.toFixed(2), reason: '散户多头离场或空头进场' };
    if (dL > lambda2 || dS < -lambda2) return { signal: '卖出', deltaL: +dL.toFixed(2), deltaS: +dS.toFixed(2), reason: '散户多头进场或空头离场' };
    return { signal: '观望', deltaL: +dL.toFixed(2), deltaS: +dS.toFixed(2), reason: '无明确信号' };
  }

  const hst = calcFromHist(hstDates, hstHist, '恒生科技');
  const hsi = calcFromHist(hsiDates, hsiHist, '恒生指数');

  return { updateTime: new Date().toISOString(), date: dateStr, indexSignals: { '恒生科技': hst, '恒生指数': hsi }, etfs: etfResults };
}

function fmtDate(d) {
  return `${d.getFullYear()}/${String(d.getMonth()+1).padStart(2,'0')}/${String(d.getDate()).padStart(2,'0')}`;
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

// 回填单日数据（6只ETF并发抓取）
async function backfillDate(dateStr, env) {
  console.log(`[backfill] ${dateStr}`);
  
  // 并发抓6只ETF
  const results = await Promise.allSettled(
    TARGET_ETFS.map(async (etf) => {
      let history = [];
      if (env.ETF_DATA) {
        const cached = await env.ETF_DATA.get(`etf:${etf.code}`);
        if (cached) history = JSON.parse(cached);
      }
      const data = await fetchCCASSFromHKEx(etf.code, dateStr);
      // 检查是否已有该日期，避免重复
      if (!history.find(h => h.date === dateStr)) {
        history.push({ date: dateStr, futuShareholding: data.futuTotal, totalShareholding: data.totalShares });
      }
      if (history.length > 365) history = history.slice(-365);
      if (env.ETF_DATA) await env.ETF_DATA.put(`etf:${etf.code}`, JSON.stringify(history));
      return { code: etf.code, futuTotal: data.futuTotal };
    })
  );
  
  const errors = results.filter(r => r.status === 'rejected').map(r => r.reason?.message || r.reason);
  if (errors.length > 0) {
    console.warn(`[backfill] ${dateStr} 部分失败:`, errors);
  }
  console.log(`[backfill] ${dateStr} 完成`);
}

// ============================================================
// Worker 入口
// ============================================================
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS')
      return new Response(null, { headers: CORS });

    try {
      if (url.pathname === '/api/refresh') {
        ctx.waitUntil(refreshAllData(env));
        return new Response(JSON.stringify({ ok: true, message: '后台抓取已触发' }), { headers: { 'Content-Type': 'application/json', ...CORS } });
      }

      // 单日回填接口: /api/backfill?date=2025/04/18
      if (url.pathname === '/api/backfill') {
        const dateStr = url.searchParams.get('date') || fmtDate(new Date());
        await backfillDate(dateStr, env);
        return new Response(JSON.stringify({ ok: true, date: dateStr }), { headers: { 'Content-Type': 'application/json', ...CORS } });
      }

      // 批量回填接口: /api/batch?start=2025/04/18&days=30
      if (url.pathname === '/api/batch') {
        const start = url.searchParams.get('start') || fmtDate(new Date());
        const days = parseInt(url.searchParams.get('days') || '10', 10);
        const results = [];
        for (let i = 0; i < days; i++) {
          const d = new Date();
          d.setDate(d.getDate() - i);
          const ds = fmtDate(d);
          try { await backfillDate(ds, env); results.push({ date: ds, ok: true }); }
          catch (e) { results.push({ date: ds, ok: false, error: e.message }); }
          if (i < days - 1) await sleep(500);
        }
        return new Response(JSON.stringify({ ok: true, results }), { headers: { 'Content-Type': 'application/json', ...CORS } });
      }

      if (url.pathname === '/api/signals') {
        const dateStr = fmtDate(new Date());
        if (env.ETF_DATA) {
          const cached = await env.ETF_DATA.get(`signals:${dateStr}`);
          if (cached) return new Response(cached, { headers: { 'Content-Type': 'application/json', ...CORS } });
        }
        // 无缓存 → 实时从KV历史数据计算
        try {
          const data = await computeSignals(dateStr, env);
          return new Response(JSON.stringify(data), { headers: { 'Content-Type': 'application/json', ...CORS } });
        } catch(e) {
          return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...CORS } });
        }
      }

      if (url.pathname === '/api/history') {
        const code = url.searchParams.get('code') || '07226';
        let history = [];
        if (env.ETF_DATA) { const c = await env.ETF_DATA.get(`etf:${code}`); if (c) history = JSON.parse(c); }
        return new Response(JSON.stringify({ code, history }), { headers: { 'Content-Type': 'application/json', ...CORS } });
      }

      // 返回 HTML 页面
      return new Response(renderHTML(), { headers: { 'Content-Type': 'text/html; charset=utf-8', ...CORS } });
    } catch (e) {
      return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json', ...CORS } });
    }
  },

  // 每日 Cron 触发（北京时间 16:25，CCASS 更新后）
  async scheduled(event, env, ctx) {
    await refreshAllData(env);
  }
};

// ============================================================
// HTML 前端
// ============================================================
function renderHTML() {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>港股杠反ETF择时信号 | CCASS情绪观测</title>
<style>
:root{--bg:#f4f7fb;--panel:#fff;--text:#0f172a;--muted:#64748b;--line:#e2e8f0;--blue:#2563eb;--green:#059669;--red:#dc2626;--shadow:0 14px 40px rgba(15,23,42,.06)}
*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(180deg,#f6f8fc 0%,#eef3fb 100%);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;min-height:100vh}
.wrap{max-width:1120px;margin:0 auto;padding:32px 20px 64px}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px}
.logo{display:flex;align-items:center;gap:10px}
.logo-icon{width:42px;height:42px;background:linear-gradient(135deg,#2563eb,#7c3aed);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px}
.logo-text{font-size:20px;font-weight:800}
.logo-sub{font-size:12px;color:var(--muted)}
.live-badge{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border-radius:999px;background:#ecfdf5;color:#047857;font-size:12px;font-weight:600;border:1px solid #a7f3d0}
.live-dot{width:8px;height:8px;border-radius:50%;background:#047857;animation:pl 2s infinite}
@keyframes pl{0%,100%{opacity:1}50%{opacity:.3}}
.hero{background:var(--panel);border:1px solid var(--line);border-radius:28px;box-shadow:var(--shadow);padding:32px;margin-bottom:18px}
.eyebrow{display:inline-block;padding:7px 12px;border-radius:999px;background:#eef4ff;color:#1d4ed8;font-size:12px;font-weight:700;border:1px solid #cfe0ff;margin-bottom:12px}
.hero h1{font-size:36px;font-weight:800;line-height:1.15;margin-bottom:10px}
.hero p{font-size:15px;line-height:1.8;color:#475569;max-width:800px}
.update-time{font-size:12px;color:#94a3b8;margin-top:14px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:22px;box-shadow:var(--shadow);padding:22px;margin-bottom:18px}
.panel-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
.section-title{font-size:18px;font-weight:800}
.badge{display:inline-block;padding:4px 10px;border-radius:999px;font-size:11px;font-weight:600;border:1px solid}
.badge.green{background:#ecfdf5;color:#047857;border-color:#a7f3d0}
.badge.blue{background:#eff6ff;color:#1d4ed8;border-color:#cfe0ff}
.index-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.index-card{border:1px solid var(--line);border-radius:18px;padding:20px}
.index-name{font-size:13px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-bottom:8px}
.signal{font-size:34px;font-weight:800;margin-bottom:6px}
.signal.buy{color:#047857}.signal.sell{color:#b91c1c}.signal.watch{color:#64748b}
.reason{font-size:13px;color:#475569;margin-bottom:10px}
.delta{font-size:12px;color:#94a3b8}
.delta span{font-weight:700}
.etf-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.etf-card{border:1px solid var(--line);border-radius:16px;padding:16px}
.etf-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px}
.etf-name{font-size:13px;font-weight:700;line-height:1.4}
.etf-code{font-size:11px;color:#94a3b8;font-family:monospace}
.etf-badge{font-size:10px;padding:3px 8px;border-radius:6px;font-weight:700}
.etf-badge.l{background:#fef2f2;color:#b91c1c}
.etf-badge.s{background:#ecfdf5;color:#047857}
.etf-badge.n{background:#f8fafc;color:#475569}
.etf-stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:10px}
.etf-stat{text-align:center;padding:8px;border-radius:10px;background:#f8fafc}
.etf-stat-k{font-size:10px;color:#94a3b8;text-transform:uppercase;letter-spacing:.03em;margin-bottom:4px}
.etf-stat-v{font-size:15px;font-weight:800}
.etf-stat-v.h{color:#047857}.etf-stat-v.l{color:#b91c1c}
.logic-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.logic-card{border:1px solid var(--line);border-radius:16px;padding:18px;background:#f8fafc}
.logic-title{font-size:14px;font-weight:700;margin-bottom:12px}
.logic-row{display:flex;gap:10px;margin-bottom:10px;align-items:flex-start}
.logic-icon{width:32px;height:32px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0}
.logic-icon.b{background:#ecfdf5}.logic-icon.s{background:#fef2f2}.logic-icon.w{background:#eff6ff}
.logic-text{font-size:12px;color:#475569;line-height:1.7}
@media(max-width:768px){.wrap{padding:20px 16px}.hero h1{font-size:26px}.index-grid,.etf-grid,.logic-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <div class="logo">
      <div class="logo-icon">📊</div>
      <div><div class="logo-text">港股杠反ETF择时</div><div class="logo-sub">基于CCASS散户情绪的择时策略</div></div>
    </div>
    <div class="live-badge"><span class="live-dot"></span><span id="status">加载中</span></div>
  </div>
  <div class="hero">
    <div class="eyebrow">📌 基于港股杠反ETF份额变化的择时策略</div>
    <h1>港股择时信号 · 富途情绪观测</h1>
    <p>监控南方东英旗下6只杠反ETF的富途证券持仓变化率。当散户多头离场时暗示底部区域，触发买入信号；当散户多头进场时暗示顶部区域，触发卖出信号。</p>
    <p class="update-time">数据来源：港交所CCASS · 策略来源：开源证券金工研报 · 更新：<span id="update-t">-</span></p>
  </div>
  <div class="panel">
    <div class="panel-header">
      <div class="section-title">指数择时信号</div>
      <span class="badge blue">N=20 λ₁=1.2% λ₂=1.0%</span>
    </div>
    <div class="index-grid">
      <div class="index-card"><div class="index-name">恒生科技指数</div><div id="hst-sig" class="signal watch">-</div><div id="hst-reason" class="reason"></div><div id="hst-delta" class="delta"></div></div>
      <div class="index-card"><div class="index-name">恒生指数</div><div id="hsi-sig" class="signal watch">-</div><div id="hsi-reason" class="reason"></div><div id="hsi-delta" class="delta"></div></div>
    </div>
  </div>
  <div class="panel">
    <div class="panel-header"><div class="section-title">6只杠反ETF富途持仓</div><span class="badge green">富途占比参考 13%~17%</span></div>
    <div class="etf-grid" id="etf-grid"><div style="text-align:center;padding:40px;color:#94a3b8">加载中...</div></div>
  </div>
  <div class="panel">
    <div class="panel-header"><div class="section-title">策略逻辑</div></div>
    <div class="logic-grid">
      <div class="logic-card">
        <div class="logic-title">📈 信号规则</div>
        <div class="logic-row"><div class="logic-icon b">📉</div><div class="logic-text"><b>买入信号</b>：做多ETF富途份额下降&gt;1.2% 或 做空ETF份额上升&gt;1.2%<br>→ 散户多头离场/空头进场 → 市场底部</div></div>
        <div class="logic-row"><div class="logic-icon s">📈</div><div class="logic-text"><b>卖出信号</b>：做多ETF富途份额上升&gt;1.0% 或 做空ETF份额下降&gt;1.0%<br>→ 散户多头进场/空头离场 → 市场顶部</div></div>
      </div>
      <div class="logic-card">
        <div class="logic-title">🔬 核心逻辑</div>
        <div class="logic-row"><div class="logic-icon w">🔍</div><div class="logic-text">富途证券是典型<strong>散户经纪商</strong>，杠反ETF中平均占比<strong>15.4%</strong>（最高31.3%），与指数呈显著<strong>负相关</strong>（恒生科技-0.67，恒指-0.92），具有明确反向指示意义。</div></div>
        <div class="logic-row"><div class="logic-icon w">⚡</div><div class="logic-text">数据日度更新，领先财报与宏观数据。<strong>恒生科技策略年化超额22.27%</strong>（回测2021-2025），恒指策略年化超额10.41%。</div></div>
      </div>
    </div>
  </div>
</div>
<script>
const API = 'https://etf-signal-luclaw.lumeredith1996.workers.dev';
function cls(s){return s==='买入'?'buy':s==='卖出'?'sell':'watch';}
function fmt(n){return n==null?'-':(n>=0?'+':'')+n.toFixed(2)+'%';}
function w(n){return (n/10000).toFixed(0)+'万';}
async function load(){
  try{
    const r = await fetch(API+'/api/signals');
    if(!r.ok) throw new Error(r.status);
    const d = await r.json();
    if(d.error==='no_data'){
      document.getElementById('etf-grid').innerHTML='<div style="text-align:center;padding:40px;color:#f59e0b">今日数据尚未抓取 · <a href="'+API+'/api/refresh" target="_blank">点击此处触发抓取</a></div>';
      document.getElementById('status').textContent='待抓取';
      return;
    }
    render(d);
  } catch(e){
    document.getElementById('etf-grid').innerHTML='<div style="text-align:center;padding:40px;color:#b91c1c">数据加载失败: '+e.message+'</div>';
    document.getElementById('status').textContent='异常';
  }
}
function render(d){
  document.getElementById('status').textContent='实时';
  document.getElementById('update-t').textContent=new Date(d.updateTime).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai'});
  for(const[idx,info]of Object.entries(d.indexSignals||{})){
    const el=idx==='恒生科技'?'hst':'hsi';
    const s=document.getElementById(el+'-sig');
    s.textContent=info.signal||'观望';s.className='signal '+cls(info.signal);
    document.getElementById(el+'-reason').textContent=info.reason||'';
    document.getElementById(el+'-delta').innerHTML=info.deltaL!=null?'做多变化: <span>'+fmt(info.deltaL)+'</span> · 做空变化: <span>'+fmt(info.deltaS)+'</span>':'';
  }
  const grid=document.getElementById('etf-grid');grid.innerHTML='';
  for(const code of['07226','07552','03033','07200','07500','03037']){
    const e=d.etfs&&d.etfs[code];if(!e||!e.futuTotal)continue;
    const bc=e.type==='2x_long'?'l':e.type==='2x_short'?'s':'n';
    const bt=e.type==='2x_long'?'2x多':e.type==='2x_short'?'2x空':'普通';
    const pct=parseFloat(e.futuPercent||0),pc=pct>10?'h':pct<5?'l':'';
    grid.innerHTML+='<div class="etf-card"><div class="etf-top"><div><div class="etf-code">'+code+'</div><div class="etf-name">'+e.name+'</div></div><span class="etf-badge '+bc+'">'+bt+'</span></div><div class="etf-stats"><div class="etf-stat"><div class="etf-stat-k">富途持仓</div><div class="etf-stat-v">'+w(e.futuTotal)+'</div></div><div class="etf-stat"><div class="etf-stat-k">总持仓</div><div class="etf-stat-v">'+w(e.totalShares)+'</div></div><div class="etf-stat"><div class="etf-stat-k">富途占比</div><div class="etf-stat-v '+pc+'">'+pct.toFixed(1)+'%</div></div></div></div>';
  }
}
load();
</script>
</body>
</html>`;
}
