// Worker export for Cloudflare Pages - serves API
export async function onRequest(context) {
  const url = new URL(context.request.url);
  
  // Proxy API requests to the existing Worker
  if (url.pathname.startsWith('/api/')) {
    const apiUrl = `https://etf-signal-luclaw.lumeredith1996.workers.dev${url.pathname}${url.search}`;
    const response = await fetch(apiUrl, {
      headers: { ...Object.fromEntries(context.request.headers) }
    });
    return new Response(response.body, {
      status: response.status,
      headers: response.headers
    });
  }
  
  return context.next();
}
