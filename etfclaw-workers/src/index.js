/**
 * ETFClaw Cloudflare Workers
 * 功能：
 * 1. /social -> 重定向到 GitHub Pages
 * 2. /xueqiu/* -> 代理雪球内容（加速）
 * 3. /weibo/* -> 代理微博内容（加速）
 * 4. 静态资源缓存
 */

const GITHUB_PAGES_URL = 'https://lumeredith1996-cmd.github.io/ETFClawMeredith';
const SOCIAL_PATH = '/social-v1.html';

// 缓存配置
const CACHE_TTL = 300; // 5分钟缓存

async function fetchWithCache(url, cache, options = {}) {
  const cacheKey = url;
  
  // 尝试从缓存读取
  const cached = await cache.match(cacheKey);
  if (cached) {
    return cached;
  }
  
  // 请求原站
  const response = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (compatible; ETFClawProxy/1.0)',
      ...options.headers
    },
    ...options
  });
  
  if (response.ok) {
    // 仅缓存GET请求和成功响应
    if (options.method === 'GET' || !options.method) {
      const cloned = response.clone();
      const newRes = new Response(cloned.body, cloned);
      newRes.headers.set('Cache-Control', `public, max-age=${CACHE_TTL}`);
      newRes.headers.set('X-Proxy-By', 'ETFClaw-Workers');
      await cache.put(cacheKey, newRes);
    }
  }
  
  // 处理重定向，手动跟随
  if (response.status >= 300 && response.status < 400 && response.headers.get('Location')) {
    const location = response.headers.get('Location');
    return fetchWithCache(location, cache, options);
  }
  
  return response;
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    
    // 获取或创建缓存
    const cache = caches.default;
    
    // ========== 路由处理 ==========
    
    // 1. /social 或 /social/ -> 重定向到 GitHub Pages
    if (pathname === '/social' || pathname === '/social/') {
      return Response.redirect(`${GITHUB_PAGES_URL}${SOCIAL_PATH}`, 302);
    }
    
    // 2. /xueqiu/* -> 代理雪球内容
    if (pathname.startsWith('/xueqiu/')) {
      const targetPath = pathname.replace('/xueqiu/', '/');
      const targetUrl = `https://xueqiu.com${targetPath}${url.search}`;
      
      // 雪球需要Cookie，先尝试直接代理
      try {
        const response = await fetchWithCache(targetUrl, cache, {
          headers: {
            'Cookie': request.headers.get('Cookie') || '',
            'Referer': 'https://xueqiu.com',
          }
        });
        
        const newResponse = new Response(response.body, response);
        newResponse.headers.set('Access-Control-Allow-Origin', '*');
        newResponse.headers.set('X-Proxy-By', 'ETFClaw-Workers');
        return newResponse;
      } catch (e) {
        return new Response('Proxy error: ' + e.message, { status: 502 });
      }
    }
    
    // 3. /weibo/* -> 代理微博内容
    if (pathname.startsWith('/weibo/')) {
      const targetPath = pathname.replace('/weibo/', '/');
      const targetUrl = `https://weibo.com${targetPath}${url.search}`;
      
      try {
        const response = await fetchWithCache(targetUrl, cache, {
          headers: {
            'Cookie': request.headers.get('Cookie') || '',
            'Referer': 'https://weibo.com',
            'Accept-Language': 'zh-CN,zh;q=0.9',
          }
        });
        
        const newResponse = new Response(response.body, response);
        newResponse.headers.set('Access-Control-Allow-Origin', '*');
        newResponse.headers.set('X-Proxy-By', 'ETFClaw-Workers');
        return newResponse;
      } catch (e) {
        return new Response('Proxy error: ' + e.message, { status: 502 });
      }
    }
    
    // 4. 前端页面路由 -> 返回 GitHub Pages 内容
    // 匹配 /, /index, /social-v1.html 等
    if (pathname === '/' || pathname === '/index' || pathname === '/index.html' || pathname === '/social-v1.html') {
      try {
        const response = await fetchWithCache(`${GITHUB_PAGES_URL}${SOCIAL_PATH}`, cache);
        return new Response(response.body, {
          headers: {
            'Content-Type': 'text/html; charset=utf-8',
            'Cache-Control': 'public, max-age=60',
          }
        });
      } catch (e) {
        return new Response('Failed to load page', { status: 500 });
      }
    }
    
    // 5. 静态资源（CSS, JS, 图片等）
    if (pathname.match(/\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2)$/)) {
      const fullUrl = `${GITHUB_PAGES_URL}${pathname}`;
      try {
        const response = await fetchWithCache(fullUrl, cache);
        const contentType = pathname.endsWith('.css') ? 'text/css' :
                           pathname.endsWith('.js') ? 'application/javascript' :
                           pathname.endsWith('.png') ? 'image/png' :
                           pathname.endsWith('.svg') ? 'image/svg+xml' :
                           'application/octet-stream';
        return new Response(response.body, {
          headers: {
            'Content-Type': contentType,
            'Cache-Control': 'public, max-age=86400', // 静态资源缓存1天
          }
        });
      } catch (e) {
        return new Response('Resource not found', { status: 404 });
      }
    }
    
    // 默认：返回主页
    return Response.redirect(`${GITHUB_PAGES_URL}${SOCIAL_PATH}`, 302);
  }
};
