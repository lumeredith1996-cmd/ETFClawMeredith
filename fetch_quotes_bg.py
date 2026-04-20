#!/usr/bin/env python3
"""Background job to fetch Longbridge quotes - run with nohup"""
import subprocess, json, time

CODES = [
    "513730.SH","159687.SZ","513130.SH","03190.HK","02800.HK","02828.HK",
    "3033.HK","3037.HK","07226.HK","07552.HK","07200.HK","07500.HK",
    "03033.HK","03037.HK","3441.HK","3442.HK","3174.HK","3167.HK",
    "3432.HK","0700.HK","9988.HK","0941.HK","2318.HK","3690.HK",
    "9618.HK","1810.HK","1024.HK","603259.SH","600519.SH"
]

def fetch_quote(code):
    try:
        r = subprocess.run(
            ['timeout','6','longbridge','quote','--format','json',code],
            capture_output=True, text=True, timeout=8
        )
        for line in r.stdout.strip().split('\n'):
            if line.startswith('[{') or line.startswith('[  {'):
                data = json.loads(line)
                if isinstance(data, list) and len(data) > 0:
                    return data[0]
    except:
        pass
    return None

quotes = {}
for i, code in enumerate(CODES):
    q = fetch_quote(code)
    if q:
        quotes[code] = q
    time.sleep(1.2)
    if i % 5 == 0:
        print(f"Progress: {i+1}/{len(CODES)}", flush=True)

output = {
    "quotes": quotes,
    "updated": subprocess.run(['date','-Iseconds'], capture_output=True, text=True).stdout.strip()
}

with open('/root/.openclaw/workspace/etf-map-site/lb_quotes.json','w') as f:
    json.dump(output, f, ensure_ascii=False)

print(f"Done! Fetched {len(quotes)} quotes", flush=True)
