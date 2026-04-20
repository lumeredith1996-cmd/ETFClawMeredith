/**
 * ETF 历史数据回填脚本
 * 向 Worker 的 /api/backfill 端点发送请求，后台抓取历史数据
 * 
 * 用法: node etf-backfill.js [起始日期 YYYY/MM/DD] [结束日期 YYYY/MM/DD]
 * 示例: node etf-backfill.js 2025/04/19 2026/04/18
 */

const WORKER_URL = 'https://etf-signal-luclaw.lumeredith1996.workers.dev';
const BATCH_SIZE = 10; // 每次并发请求数

const TARGET_ETFS = [
  { code: '07226', name: '南方2倍做多恒生科技' },
  { code: '07552', name: '南方2倍做空恒生科技' },
  { code: '03033', name: '南方恒生科技' },
  { code: '07200', name: '南方2倍做多恒指' },
  { code: '07500', name: '南方2倍做空恒指' },
  { code: '03037', name: '南方恒生指数' },
];

// 生成日期范围内的所有交易日（跳过周末）
function* tradingDays(start, end) {
  const startDate = parseDate(start);
  const endDate = parseDate(end);
  const current = new Date(startDate);
  
  while (current <= endDate) {
    const day = current.getDay();
    if (day !== 0 && day !== 6) { // 跳过周末
      yield formatDate(current);
    }
    current.setDate(current.getDate() + 1);
  }
}

function parseDate(str) {
  const [y, m, d] = str.split('/').map(Number);
  return new Date(y, m - 1, d);
}

function formatDate(d) {
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`;
}

// 并发限制器
async function throttledMap(items, fn, concurrency = BATCH_SIZE) {
  const results = [];
  for (let i = 0; i < items.length; i += concurrency) {
    const batch = items.slice(i, i + concurrency);
    const batchResults = await Promise.all(batch.map(fn));
    results.push(...batchResults);
    if (i + concurrency < items.length) {
      await new Promise(r => setTimeout(r, 300)); // 避免过快
    }
  }
  return results;
}

// 调用 Worker 后台回填接口
async function triggerBackfill(dateStr) {
  const url = `${WORKER_URL}/api/backfill?date=${dateStr}`;
  try {
    const resp = await fetch(url, { timeout: 15000 });
    const data = await resp.json();
    return { date: dateStr, ok: data.ok || false, error: data.error || null };
  } catch (e) {
    return { date: dateStr, ok: false, error: e.message };
  }
}

async function main() {
  const endDate = formatDate(new Date()); // 今天
  const startDate = process.argv[2] || '2025/04/19'; // 默认1年前
  
  console.log(`📅 回填范围: ${startDate} → ${endDate}`);
  console.log(`⚡ 并发数: ${BATCH_SIZE}`);
  console.log('');
  
  const dates = [...tradingDays(startDate, endDate)];
  console.log(`📊 共 ${dates.length} 个交易日待抓取\n`);
  
  let completed = 0;
  let succeeded = 0;
  let failed = 0;
  
  const startTime = Date.now();
  
  for (let i = 0; i < dates.length; i += BATCH_SIZE) {
    const batch = dates.slice(i, i + BATCH_SIZE);
    const dayLabel = `${i + 1}-${Math.min(i + BATCH_SIZE, dates.length)}/${dates.length}`;
    
    process.stdout.write(`\r[${dayLabel}] 抓取中... `);
    
    const results = await throttledMap(batch, triggerBackfill, BATCH_SIZE);
    
    for (const r of results) {
      completed++;
      if (r.ok) succeeded++;
      else {
        failed++;
        process.stdout.write(`\n  ⚠️  ${r.date}: ${r.error}`);
      }
    }
    
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    const rate = completed / elapsed;
    const remaining = dates.length - completed;
    const eta = (remaining / rate / 60).toFixed(1);
    
    process.stdout.write(`\r[${dayLabel}] ✅${succeeded} ⏳${remaining} 速度:${rate.toFixed(1)}/s 预计剩余:${eta}min   `);
  }
  
  console.log(`\n\n✅ 完成！共 ${dates.length} 天，成功 ${succeeded}，失败 ${failed}`);
  console.log(`⏱️  总耗时: ${((Date.now() - startTime) / 1000 / 60).toFixed(1)} 分钟`);
  
  if (failed > 0) {
    console.log('\n💡 提示: HKEx 对部分日期可能无数据（节假日），属正常');
  }
}

main().catch(console.error);
