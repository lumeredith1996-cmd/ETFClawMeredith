#!/usr/bin/env python3
"""HTTP server + Longbridge quote API on port 3000 — batched non-blocking."""
import subprocess, json, os, time, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PORT = 3000
WORKDIR = "/root/.openclaw/workspace"
QC = {'data': {}, '_ts': 0}
LOCKED = False

BATCHES = [
    ['513130.SH','3033.HK','3441.HK','3442.HK','02830.HK','2830.HK'],
    ['159687.SZ','513730.SH','SQQ.SP','LCU.SP','7376.HK','3473.HK'],
    ['3535.HK','CYB.SP','S500.SP','07552.HK','07709.HK','03433.HK'],
    ['3167.HK','3432.HK','3037.HK','3431.HK','3443.HK','3469.HK'],
]

# --- Snowball cache ---
SNOWBALL_CACHE = None
SNOWBALL_LOCKED = False

def fetch_all():
    results = {}
    for batch in BATCHES:
        try:
            r = subprocess.run(
                ['longbridge','quote','--format','json'] + batch,
                capture_output=True, text=True, timeout=25
            )
            data = json.loads(r.stdout)
            for item in data:
                sym = item.get('symbol','')
                last = float(item.get('last',0) or 0)
                prev = float(item.get('prev_close',0) or 0)
                chg = round((last-prev)/prev*100,2) if prev else 0
                results[sym] = {'last':last,'prev':prev,'chg':chg,
                                'turnover':item.get('turnover','0')}
        except Exception:
            pass
    global QC, LOCKED
    QC = {'data': results, '_ts': time.time()}
    LOCKED = False

def ensure():
    global LOCKED
    if not QC['data'] or (time.time() - QC['_ts']) > 8:
        if not LOCKED:
            LOCKED = True
            threading.Thread(target=fetch_all, daemon=True).start()

# --- Snowball scraper ---
def scrape_snowball_sync():
    global SNOWBALL_CACHE, SNOWBALL_LOCKED
    try:
        result = subprocess.run(
            ['node', '/root/.openclaw/workspace/snowball-scraper.js'],
            capture_output=True, text=True, timeout=90
        )
        output = result.stdout.strip()
        lines = output.split('\n')
        json_start = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('{') or line.strip().startswith('['):
                json_start = i
        if json_start >= 0:
            json_text = '\n'.join(lines[json_start:])
            data = json.loads(json_text)
            SNOWBALL_CACHE = data
            print(f"Snowball scrape OK: {len(data) if isinstance(data, list) else 1} users")
        else:
            print(f"Snowball scraper output: {output[:300]}")
    except Exception as e:
        print(f"Snowball scrape error: {e}")
    finally:
        SNOWBALL_LOCKED = False

def ensure_snowball():
    global SNOWBALL_LOCKED, SNOWBALL_CACHE
    if SNOWBALL_CACHE is None and not SNOWBALL_LOCKED:
        SNOWBALL_LOCKED = True
        scrape_snowball_sync()

# --- Trump scraper ---
TRUMP_CACHE = None
TRUMP_LOCKED = False

def scrape_trump_sync():
    global TRUMP_CACHE, TRUMP_LOCKED
    try:
        result = subprocess.run(
            ['node', '/root/.openclaw/workspace/trump-scraper.js'],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout.strip()
        lines = output.split('\n')
        json_start = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('{') or line.strip().startswith('['):
                json_start = i
        if json_start >= 0:
            json_text = '\n'.join(lines[json_start:])
            data = json.loads(json_text)
            TRUMP_CACHE = data
            print(f"Trump scrape OK: {data.get('total', '?')} posts")
        else:
            print(f"Trump scraper output: {output[:300]}")
    except Exception as e:
        print(f"Trump scrape error: {e}")
    finally:
        TRUMP_LOCKED = False

def ensure_trump():
    global TRUMP_LOCKED, TRUMP_CACHE
    if TRUMP_CACHE is None and not TRUMP_LOCKED:
        TRUMP_LOCKED = True
        scrape_trump_sync()

# --- Weibo scraper ---
WEIBO_CACHE = None
WEIBO_LOCKED = False
WEIBO_LAST_FETCH = 0

def scrape_weibo_sync():
    global WEIBO_CACHE, WEIBO_LOCKED, WEIBO_LAST_FETCH
    try:
        result = subprocess.run(
            ['node', '/root/.openclaw/workspace/weibo-scraper.js'],
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout.strip()
        lines = output.split('\n')
        json_start = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('[{') or line.strip().startswith('[{'):
                json_start = i
                break
        if json_start < 0:
            for i, line in enumerate(lines):
                if line.strip().startswith('{'):
                    json_start = i
                    break
        if json_start >= 0:
            json_text = '\n'.join(lines[json_start:])
            data = json.loads(json_text)
            WEIBO_CACHE = data
            WEIBO_LAST_FETCH = time.time()
            total = sum(len(u.get('posts',[])) for u in data)
            print(f"Weibo scrape OK: {len(data)} users, {total} total posts")
        else:
            print(f"Weibo scraper output: {output[:300]}")
    except Exception as e:
        print(f"Weibo scrape error: {e}")
    finally:
        WEIBO_LOCKED = False

def ensure_weibo():
    global WEIBO_LOCKED, WEIBO_CACHE, WEIBO_LAST_FETCH
    if WEIBO_CACHE is None or (time.time() - WEIBO_LAST_FETCH) > 600:
        if not WEIBO_LOCKED:
            WEIBO_LOCKED = True
            threading.Thread(target=scrape_weibo_sync, daemon=True).start()

class H(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/quote'):
            ensure()
            d = QC.get('data', {})
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Access-Control-Allow-Origin','*')
            self.end_headers()
            self.wfile.write(json.dumps(d, ensure_ascii=False).encode())
        elif self.path.startswith('/api/snowball'):
            ensure_snowball()
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Access-Control-Allow-Origin','*')
            self.end_headers()
            self.wfile.write(json.dumps(SNOWBALL_CACHE or [], ensure_ascii=False).encode())
        elif self.path.startswith('/api/trump'):
            ensure_trump()
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Access-Control-Allow-Origin','*')
            self.end_headers()
            self.wfile.write(json.dumps(TRUMP_CACHE or {}, ensure_ascii=False).encode())
        elif self.path.startswith('/api/weibo'):
            ensure_weibo()
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Access-Control-Allow-Origin','*')
            self.end_headers()
            self.wfile.write(json.dumps(WEIBO_CACHE or [], ensure_ascii=False).encode())
        elif self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-Type','text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            super().do_GET()
    def log_message(self, *args): pass

os.chdir(WORKDIR)
ThreadingHTTPServer(('0.0.0.0', PORT), H).serve_forever()
