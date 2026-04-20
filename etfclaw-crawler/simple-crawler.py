#!/usr/bin/env python3
import requests, json, time, os
from datetime import datetime

# 配置
XUEQIU_COOKIE = 'xq_a_token=5747552fd6cfb540bcec8da911a6d04586ec6385; xq_r_token=3c66d5ca7a0f43cb7a47f4c18a1916495c404fac; u=2780816299; xq_is_login=1; xqat=5747552fd6cfb540bcec8da911a6d04586ec6385'
WEIBO_COOKIE = 'SUB=_2A25E5jAfDeRhGedH7lYS-SvJzDmIHXVnms3XrDV_PUJbkNAbLVKgkW9NUKXd-AdPRgxGTrHGxCY8lzLnHRmnuhgd; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFL8n_zHZN7UMzcnZpC_lXi5JpX5KzhUgL.Fo24SKB01K-fS0-2dJLoIpQLxKMLBo-LB--LxK-LB-BL1KWkKsLLIc_yM7tt; ULV=1776435290149:1:1:1:4977809397643.026.1776435290141; WBPSESS=SDojhWSwLyj_iZRH9wnYNWhaXy47z8teFI5tgSO55dsV-xhiZnJhqnOEPhI6S6CwvrPVX3VvjTEn_uV4_LGlabHS7e1iPjrAQ-Bn8g1QpWBhTO5RohyzCeoAlK6Fx2eCqUPCQRSShOzjvuDWTCBlvA==; XSRF-TOKEN=R7flxpfMTWy2-gyGcuJ3aPCI'
XUEQIU_UID = '2780816299'
WEIBO_UID = '1954395575'

def get_xueqiu():
    r = requests.get('https://xueqiu.com/statuses/user_timeline.json', params={'user_id': XUEQIU_UID, 'page': 1, 'count': 10}, headers={'Cookie': XUEQIU_COOKIE, 'User-Agent': 'Mozilla/5.0'})
    d = r.json()
    posts = []
    if d.get('statuses'):
        for t in d['statuses']:
            posts.append({'id': str(t['id']), 'platform': 'xueqiu', 'content': t.get('text',''), 'url': f'https://xueqiu.com/{XUEQIU_UID}/{t["id"]}', 'time': t.get('created_at', ''), 'like': t.get('like_count', 0), 'user': t['user']['screen_name']})
    return posts

def get_weibo():
    r = requests.get('https://weibo.com/ajax/statuses/mymblog', params={'uid': WEIBO_UID, 'page': 1, 'feature': 0}, headers={'Cookie': WEIBO_COOKIE, 'User-Agent': 'Mozilla/5.0'})
    d = r.json()
    posts = []
    if d.get('ok') == 1:
        for p in d.get('data', {}).get('list', []):
            posts.append({'id': str(p['id']), 'platform': 'weibo', 'content': p.get('text_raw',''), 'url': f'https://weibo.com/{WEIBO_UID}/{p["id"]}', 'time': p.get('created_at',''), 'like': p.get('attitudes_count', 0), 'user': p.get('user',{}).get('screen_name','')})
    return posts

def tag(p):
    bullish = ['看好','买入','做多','增持','机会','涨','牛市','配置','低估']
    bearish = ['看空','卖出','做空','减持','风险','跌','熊市','止损','高估']
    s = 'neutral'
    bc = sum(1 for w in bullish if w in p['content'])
    rc = sum(1 for w in bearish if w in p['content'])
    if bc >= 2 and bc > rc: s = 'bullish'
    elif rc >= 2 and rc > bc: s = 'bearish'
    cats = {'market':['市场','大盘'],'fund':['基金','ETF'],'macro':['宏观'],'sector':['板块'],'risk':['风险'],'edu':['知识']}
    c = 'other'
    for k,v in cats.items():
        if any(w in p['content'] for w in v): c = k; break
    cn = {'market':'市场分析','fund':'基金选择','macro':'宏观策略','sector':'板块解读','risk':'风险提示','edu':'理财知识','other':'其他'}
    p['cat'] = c; p['catName'] = cn[c]; p['sent'] = s
    return p

def save(posts, f):
    os.makedirs('data', exist_ok=True)
    ex = []
    if os.path.exists(f):
        try: ex = json.load(open(f))
        except: pass
    ids = {x['id'] for x in ex}
    new = [x for x in posts if x['id'] not in ids]
    json.dump(new+ex, open(f,'w'), ensure_ascii=False, indent=2)
    print(f'OK: {len(new)} new, total {len(ex)+len(new)}')
    return new

def main():
    print('ETFClaw Crawler Start')
    all_p = []
    print('Xueqiu...')
    p = get_xueqiu()
    for x in p: tag(x)
    all_p.extend(save(p, 'data/xueqiu.json'))
    time.sleep(1)
    print('Weibo...')
    p = get_weibo()
    for x in p: tag(x)
    all_p.extend(save(p, 'data/weibo.json'))
    print(f'Done! {len(all_p)} new posts')

if __name__ == '__main__':
    main()
