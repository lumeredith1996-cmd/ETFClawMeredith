const puppeteer = require('puppeteer');

const USERS = {
  '1247347556': '大道无形我有型',
  '7708198303': '星辰大海的边界',
  '3559889031': '张翼轸',
  '5806714603': '薇薇庄主的宏观策略',
  '7528829663': '且涨海外投',
  '9887656769': '梁宏',
};

async function scrapeUser(uid, name) {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-blink-features=AutomationControlled',
      '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ],
    executablePath: '/usr/bin/chromium-browser',
  });

  const page = await browser.newPage();
  
  // Set cookie before navigating
  await page.setCookie({
    name: 'xq_a_token',
    value: '5747552fd6cfb540bcec8da911a6d04586ec6385',
    domain: '.xueqiu.com',
    path: '/',
    httpOnly: true,
    secure: true,
  });

  try {
    // Navigate to xueqiu.com first to establish session
    await page.goto('https://xueqiu.com', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await new Promise(r => setTimeout(r, 2000));
    
    console.log(`Scraping: ${name} (uid: ${uid})`);
    
    // Use fetch API to get user timeline (more realistic than direct navigation)
    const timelineData = await page.evaluate(async (userId) => {
      const timestamp = Date.now();
      const url = `https://xueqiu.com/v4/statuses/user_timeline.json?user_id=${userId}&type=10&source=&_=${timestamp}`;
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Referer': `https://xueqiu.com/u/${userId}`,
          'X-Requested-With': 'XMLHttpRequest',
        },
        credentials: 'include'
      });
      
      if (!response.ok) {
        return { error: `HTTP ${response.status}`, text: await response.text() };
      }
      
      return await response.json();
    }, uid);
    
    if (timelineData.error) {
      console.log(`  -> Error: ${timelineData.error}`);
      return { uid, name, error: timelineData.error };
    }
    
    if (!timelineData.statuses || timelineData.statuses.length === 0) {
      console.log(`  -> No statuses found (may need fresh cookie)`);
      return { uid, name, error: 'No statuses', count: 0 };
    }
    
    const count = timelineData.statuses.length;
    console.log(`  -> Got ${count} posts`);
    
    return {
      uid,
      name,
      count,
      posts: timelineData.statuses.slice(0, 10).map(s => ({
        id: s.id,
        title: s.title || '',
        text: s.description || '',
        created: new Date(s.created_at).toISOString(),
        link: `https://xueqiu.com${s.target}`
      }))
    };
  } catch (e) {
    console.error(`  -> Exception: ${e.message}`);
    return { uid, name, error: e.message };
  } finally {
    await browser.close();
  }
}

async function main() {
  const results = [];
  
  console.log('Starting Snowball scraper...\n');
  
  for (const [uid, name] of Object.entries(USERS)) {
    const result = await scrapeUser(uid, name);
    results.push(result);
    
    // Delay between users
    await new Promise(r => setTimeout(r, 3000));
  }
  
  console.log('\n=== FINAL RESULTS ===');
  results.forEach(r => {
    console.log(`\n${r.name} (${r.uid}):`);
    if (r.error) {
      console.log(`  ERROR: ${r.error}`);
    } else {
      console.log(`  ${r.count} posts`);
      r.posts?.forEach((p, i) => {
        console.log(`  [${i+1}] ${p.text.substring(0, 80)}...`);
      });
    }
  });
  // Output raw JSON for programmatic consumption
  console.log('\n---JSON---');
  console.log(JSON.stringify(results));
}

main().catch(console.error);
