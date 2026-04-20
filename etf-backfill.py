#!/usr/bin/env python3
"""
ETF 历史数据快速回填脚本 - 发现即写入版本
"""

import re, json, time, sys, os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

CF_ACCOUNT_ID = '52fca883b81b260936d4b8dcf7157053'
CF_API_TOKEN = os.environ.get('CF_API_TOKEN', '')
KV_NS_ID = 'e34fc986e75d4dada57d78aa84eeb150'

# 用于 KV 写入的独立 session
kv_session = requests.Session()
kv_session.headers['Authorization'] = f'Bearer {CF_API_TOKEN}'

TARGET_ETFS = [
    ('07226', '南方2倍做多恒生科技'),
    ('07552', '南方2倍做空恒生科技'),
    ('03033', '南方恒生科技'),
    ('07200', '南方2倍做多恒指'),
    ('07500', '南方2倍做空恒指'),
    ('03037', '南方恒生指数'),
]

BASE_URL = 'https://www3.hkexnews.hk/sdw/search/searchsdw_c.aspx'
CONCURRENCY = 4
FETCH_DELAY = 0.8

session = requests.Session()
session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=Retry(total=2, backoff_factor=0.5))
session.mount('https://', adapter)

def kv_read(key):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{KV_NS_ID}/values/{key}"
    try:
        r = kv_session.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, list) else ([data] if isinstance(data, dict) else [])
    except:
        return []

def kv_write(key, value):
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{KV_NS_ID}/values/{key}"
    try:
        r = kv_session.put(url, data=json.dumps(value).encode(), timeout=15,
                           headers={'Content-Type': 'application/json'})
        return r.json().get('success', False)
    except Exception as e:
        print(f"    KV write error: {e}")
        return False

def get_fields(html):
    fields = {}
    for name in ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION', 'today']:
        m = re.search(f'<input[^>]*name="{name}"[^>]*value="([^"]*)"', html)
        fields[name] = m.group(1) if m else ''
    return fields

def parse(html):
    futu_total, total_shares, futu_pct = 0, 0, '0'
    for row in re.findall(r'<tr>([\s\S]*?)</tr>', html):
        share_m = re.search(r'col-shareholding["\s][^>]*>[\s\S]*?mobile-list-body[^>]*>([\d,]+)<', row)
        pct_m = re.search(r'col-shareholding-percent["\s][^>]*>[\s\S]*?mobile-list-body[^>]*>([\d.]+%?)<', row)
        name_m = re.search(r'col-participant-name[\s\S]*?mobile-list-body[^>]*>([^<]+)<', row)
        if name_m and share_m:
            name = name_m.group(1).strip()
            shares = int(share_m.group(1).replace(',', ''))
            total_shares += shares
            if '富途' in name or 'FUTU' in name.upper():
                futu_total, futu_pct = shares, (pct_m.group(1) if pct_m else '0')
    return futu_total, total_shares, futu_pct

def fetch_one(etf_code, date_str):
    time.sleep(FETCH_DELAY)
    try:
        r1 = session.get(BASE_URL, timeout=25)
        fields = get_fields(r1.text)
        r2 = session.post(BASE_URL, data={
            '__EVENTTARGET': 'btnSearch', '__EVENTARGUMENT': '',
            '__VIEWSTATE': fields['__VIEWSTATE'],
            '__VIEWSTATEGENERATOR': fields['__VIEWSTATEGENERATOR'],
            '__EVENTVALIDATION': fields['__EVENTVALIDATION'],
            'today': fields['today'],
            'sortBy': 'shareholding', 'sortDirection': 'desc',
            'originalShareholdingDate': date_str, 'alertMsg': '',
            'txtShareholdingDate': date_str, 'txtStockCode': etf_code, 'txtStockName': '',
            'txtParticipantID': '', 'txtParticipantName': '', 'txtSelPartID': '',
        }, timeout=25)
        futu, total, pct = parse(r2.text)
        return {'code': etf_code, 'date': date_str, 'futu': futu, 'total': total, 'pct': pct}
    except Exception as e:
        return {'code': etf_code, 'date': date_str, 'error': str(e)}

def trading_days(start_str, end_str):
    s = datetime.strptime(start_str, '%Y/%m/%d')
    e = datetime.strptime(end_str, '%Y/%m/%d')
    d = s
    while d <= e:
        if d.weekday() < 5:
            yield d.strftime('%Y/%m/%d')
        d += timedelta(days=1)

def main():
    today = datetime.now()
    today_str = today.strftime('%Y/%m/%d')

    if len(sys.argv) >= 3:
        start_str, end_str = sys.argv[1], sys.argv[2]
    elif len(sys.argv) == 2:
        start_str, end_str = sys.argv[1], today_str
    else:
        end_str = today_str
        s = today; c = 0
        while c < 30:
            s -= timedelta(days=1)
            if s.weekday() < 5: c += 1
        start_str = s.strftime('%Y/%m/%d')

    dates = list(trading_days(start_str, end_str))
    total = len(dates) * len(TARGET_ETFS)
    print(f"📅 {start_str} → {end_str} ({len(dates)} 交易日 × {len(TARGET_ETFS)} ETF = {total} 任务)\n")

    tasks = [(code, date) for date in dates for code, _ in TARGET_ETFS]
    results = {}  # code -> {date: data}
    done = 0
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = {ex.submit(fetch_one, code, date): (code, date) for code, date in tasks}

        for future in as_completed(futures):
            code, date = futures[future]
            res = future.result()
            done += 1

            if 'error' not in res and res['futu'] > 0:
                if code not in results:
                    results[code] = {}
                results[code][date] = res

                # 立即写入 KV（不等最后）
                if code in results and date not in (kv_read(f'etf:{code}') or [{}])[0].get('date', '__none'):
                    history = kv_read(f'etf:{code}') or []
                    existing = {h['date'] for h in history}
                    if date not in existing:
                        history.append({'date': date, 'futuShareholding': res['futu'], 'totalShareholding': res['total']})
                    history.sort(key=lambda x: x['date'])
                    if len(history) > 365: history = history[-365:]
                    kw = kv_write(f'etf:{code}', history)
                    pct_d = f"{res['pct']}%" if res['pct'] else '-'
                    status = '✅' if kw else '❌KV'
                    print(f"{status} {date} {code}: futu={res['futu']:,}({pct_d}) [{done}/{total}]")
            else:
                err = res.get('error', 'futu=0')
                print(f"❌ {date} {code}: {err} [{done}/{total}]")

            elapsed = time.time() - t0
            rate = done / elapsed
            print(f"\r  进度 {done}/{total} ({done*100//total}%) 速度:{rate:.1f}/s 剩余:~{((total-done)/rate/60):.0f}min   ", end='', flush=True)

    print(f"\n\n⏱️  完成！耗时: {(time.time()-t0)/60:.1f}min")
    print(f"\n📈 07226 历史:")
    hist = kv_read('etf:07226') or []
    for r in hist[-7:]:
        pct = (r['futuShareholding']/r['totalShareholding']*100) if r.get('totalShareholding') else 0
        print(f"  {r['date']}: 富途={r['futuShareholding']:,} ({pct:.1f}%)")

if __name__ == '__main__':
    main()
