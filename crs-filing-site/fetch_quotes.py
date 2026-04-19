#!/usr/bin/env python3
"""Fetch Longbridge market data for all 110 ETF products and save to JSON"""
import subprocess, json, time, sys

def lb_cmd(args):
    """Run longbridge CLI and return JSON output"""
    cmd = ['longbridge'] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None
        # Parse JSON from output
        lines = result.stdout.strip().split('\n')
        for line in lines:
            try:
                return json.loads(line)
            except:
                pass
        return None
    except Exception as e:
        return None

def batch_quotes(codes, batch_size=10):
    """Fetch quotes in batches"""
    results = {}
    for i in range(0, len(codes), batch_size):
        batch = codes[i:i+batch_size]
        cmd = ['longbridge'] + ['quote', '--format', 'json'] + batch
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            for line in result.stdout.strip().split('\n'):
                if line.startswith('[') or line.startswith('{'):
                    try:
                        data = json.loads(line)
                        if isinstance(data, list):
                            for item in data:
                                if item.get('symbol'):
                                    results[item['symbol']] = item
                        elif data.get('symbol'):
                            results[data['symbol']] = data
                    except:
                        pass
        except Exception as e:
            print(f"Error on batch {i}: {e}")
        time.sleep(0.3)  # Rate limit
    return results

# Read product codes
import openpyxl
wb = openpyxl.load_workbook('/root/.openclaw/media/inbound/all产品_20260419.xlsx')
ws = wb['products_all']
products = []
seen = set()
for row in ws.iter_rows(values_only=True):
    if row[0] is None or row[0] == '一级分类': continue
    code = str(row[2]).strip() if row[2] else ''
    name = str(row[3]).strip() if row[3] else ''
    if code and code not in seen:
        seen.add(code)
        products.append({'code': code, 'name': name})

def to_longbridge(code):
    if code.endswith('.OF') and '.' not in code[:-3]:
        return code[:-2] + '.OF'
    return code

# Get unique codes for fetching
lb_codes = [to_longbridge(p['code']) for p in products]
print(f"Fetching quotes for {len(lb_codes)} products...")

quotes = batch_quotes(lb_codes, batch_size=10)
print(f"Got {len(quotes)} quotes")

# Fetch calc-index for a few key ETFs
key_etfs = [c for c in lb_codes if not c.endswith('.OF')]
index_data = {}
print(f"Fetching calc-index for {len(key_etfs[:30])} ETFs...")
for i in range(0, min(30, len(key_etfs)), 5):
    batch = key_etfs[i:i+5]
    cmd = ['longbridge', 'calc-index', '--format', 'json'] + batch
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        for line in result.stdout.strip().split('\n'):
            if line.startswith('[') or line.startswith('{'):
                try:
                    data = json.loads(line)
                    if isinstance(data, list):
                        for item in data:
                            if item.get('symbol'):
                                index_data[item['symbol']] = item
                    elif data.get('symbol'):
                        index_data[data['symbol']] = data
                except:
                    pass
    except:
        pass
    time.sleep(0.3)

# Fetch kline for a few key ETFs to compute performance
def get_kline(symbol, period='1mo'):
    cmd = ['longbridge', 'kline', '--format', 'json', '--period', period, '--count', '30', symbol]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        for line in result.stdout.strip().split('\n'):
            if line.startswith('['):
                data = json.loads(line)
                return data
    except:
        return None
    return None

# Save results
output = {
    'quotes': quotes,
    'calc_index': index_data,
}
with open('/root/.openclaw/workspace/etf-map-site/quotes_data.json', 'w') as f:
    json.dump(output, f, ensure_ascii=False)

print(f"Saved {len(quotes)} quotes and {len(index_data)} calc-index entries")
print("Quote samples:", list(quotes.items())[:3])
