const https = require('https');

const TRUMP_API = 'https://hketf-lab.pages.dev/api/pulse/trump-truth-archive';

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0' } }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch(e) { reject(new Error('JSON parse error')); }
      });
    }).on('error', reject);
  });
}

function stripHtml(html) {
  return html ? html.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').trim() : '';
}

function timeAgo(isoString) {
  const now = new Date();
  const then = new Date(isoString);
  const diffMs = now - then;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays < 7) return `${diffDays}天前`;
  return then.toLocaleDateString('zh-CN');
}

async function scrape() {
  try {
    const data = await fetchJson(TRUMP_API);
    if (!data.ok || !data.posts) return { posts: [], source: 'trump' };

    const posts = data.posts.slice(0, 20).map(p => {
      const content = p.content_zh_cn || stripHtml(p.content_html) || p.content || '';
      const hasMedia = p.media && p.media.length > 0;
      const mediaType = hasMedia ? (p.media[0].type === 'image' ? 'image' : 'video') : null;
      const mediaUrl = hasMedia ? p.media[0].url : null;

      return {
        id: p.status_url,
        author: '特朗普 @realDonaldTrump',
        authorAvatar: p.avatar || 'https://hketf-lab.pages.dev/assets/home/trump-home.jpg',
        text: content,
        originalText: stripHtml(p.content_html) || p.content || '',
        created: p.created_at,
        timeAgo: timeAgo(p.created_at),
        link: p.url,
        source: 'truth',
        hasMedia,
        mediaType,
        mediaUrl,
        platform: 'truthsocial'
      };
    });

    return {
      posts,
      source: 'trump',
      fetchedAt: new Date().toISOString(),
      total: data.count,
      windowHours: data.windowHours
    };
  } catch (e) {
    return { posts: [], source: 'trump', error: e.message };
  }
}

// Run as CLI: print JSON to stdout
if (require.main === module) {
  scrape().then(r => {
    console.log(JSON.stringify(r));
    process.exit(0);
  }).catch(e => {
    console.error('Trump scraper error:', e.message);
    process.exit(1);
  });
} else {
  module.exports = scrape;
}
