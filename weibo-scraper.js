const puppeteer = require('puppeteer');

const WEIBO_USERS = {
  '8454894899': '山基说',
  '7820112672': '表舅是养基大户',
  '5818642214': 'GMF_Light',
};

const WEIBO_COOKIES = [
  {name:'SUB',value:'_2A25E5jAfDeRhGedH7lYS-SvJzDmIHXVnms3XrDV8PUNbmtAbLWTskW9NUKXd-DLqijsslqB9cITKEgyUDLgmRswi',domain:'.weibo.com',path:'/',secure:true,httpOnly:true},
  {name:'SUBP',value:'0033WrSXqPxfM725Ws9jqgMF55529P9D9WFL8n_zHZN7UMzcnZpC_lXi5JpX5KzhUgL.Fo24SKB01K-fS0-2dJLoIpQLxKMLBo-LB--LxK-LB-BL1KWkKsLLIc_yM7tt',domain:'.weibo.com',path:'/',secure:true,httpOnly:true},
  {name:'XSRF-TOKEN',value:'R7flxpfMTWy2-gyGcuJ3aPCI',domain:'.weibo.com',path:'/',secure:true},
  {name:'WBPSESS',value:'SDojhWSwLyj_iZRH9wnYNWhaXy47z8teFI5tgSO55dsV-xhiZnJhqnOEPhI6S6Cw1L8T5pEqW-ARIiBuNQUwccGApzNUOhk9x9fF-xLjE2ya7FfYxukKlzgKPgxRZrijlUcdJwTOYZk2g7Iu1NwvUQ==',domain:'.weibo.com',path:'/',secure:true},
];

function parseWeiboTime(dateStr) {
  if (!dateStr) return new Date().toISOString();
  try { return new Date(dateStr).toISOString(); } catch(e) {}
  const now = new Date();
  if (dateStr.includes('秒前')) return now.toISOString();
  if (dateStr.includes('分钟前')) {
    const m = parseInt(dateStr) || 0;
    return new Date(now - m * 60000).toISOString();
  }
  if (dateStr.includes('小时前')) {
    const h = parseInt(dateStr) || 0;
    return new Date(now - h * 3600000).toISOString();
  }
  if (dateStr.includes('昨天')) {
    const t = dateStr.replace('昨天', '').trim();
    const [hh, mm] = t.split(':').map(Number);
    const d = new Date(now);
    d.setDate(d.getDate() - 1);
    d.setHours(hh || 0, mm || 0, 0, 0);
    return d.toISOString();
  }
  // Try parsing as date
  const d = new Date(dateStr);
  if (!isNaN(d)) return d.toISOString();
  return now.toISOString();
}

function stripHtml(html) {
  return (html || '').replace(/<br\s*\/?>/gi, '\n').replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/\n+/g, '\n').replace(/^\s+|\s+$/g, '').trim();
}

async function scrapeUser(uid, name) {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage'],
    executablePath: '/usr/bin/chromium-browser',
  });

  const page = await browser.newPage();
  await page.setRequestInterception(true);
  page.on('request', req => {
    const url = req.url();
    if (url.match(/\.(jpg|png|gif|webp|css|font|media|analytics)/)) req.abort();
    else req.continue();
  });

  try {
    for (const c of WEIBO_COOKIES) {
      try { await page.setCookie(c); } catch(e) {}
    }

    // Navigate first to establish session
    await page.goto(`https://weibo.com/u/${uid}`, { waitUntil: 'networkidle0', timeout: 25000 });
    await new Promise(r => setTimeout(r, 3000));

    // Call the PC API from within page context
    const apiData = await page.evaluate(async (userId) => {
      const ts = Date.now();
      const resp = await fetch(
        `https://weibo.com/ajax/statuses/mymblog?uid=${userId}&page=1&feature=0&__rnd=${ts}`,
        {
          method: 'GET',
          headers: {
            'Referer': `https://weibo.com/u/${userId}`,
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json, text/plain, */*',
          }
        }
      );
      return await resp.json();
    }, uid);

    if (!apiData.ok || !apiData.data?.list?.length) {
      console.log(`${name}: no posts (ok=${apiData.ok}, list=${apiData.data?.list?.length})`);
      return { uid, name, error: 'No posts', count: 0, posts: [] };
    }

    const posts = apiData.data.list.map(item => ({
      id: String(item.id),
      text: stripHtml(item.text || item.rawText || ''),
      created: new Date(item.created_at).toISOString(),
      link: `https://weibo.com/${uid}/status/${item.id}`,
      author: name,
    }));

    console.log(`${name}: ${posts.length} posts`);
    if (posts.length > 0) console.log(`  Latest: ${posts[0].text.substring(0, 80)}...`);

    return { uid, name, count: posts.length, posts };
  } catch (e) {
    console.error(`${name}: Error - ${e.message}`);
    return { uid, name, error: e.message, count: 0, posts: [] };
  } finally {
    await browser.close();
  }
}

async function main() {
  const results = [];
  
  console.log('Weibo scraper starting...\n');
  
  for (const [uid, name] of Object.entries(WEIBO_USERS)) {
    const result = await scrapeUser(uid, name);
    results.push(result);
    await new Promise(r => setTimeout(r, 5000));
  }
  
  console.log('\n=== FINAL RESULTS ===');
  results.forEach(r => {
    console.log(`\n${r.name} (${r.uid}): ${r.error || r.count+' posts'}`);
    if (r.posts?.length) {
      r.posts.slice(0, 2).forEach((p, i) => console.log(`  [${i+1}] ${p.text.substring(0, 80)}...`));
    }
  });
  
  console.log('\n---JSON---');
  console.log(JSON.stringify(results));
}

main().catch(console.error);
