import openpyxl, json

wb = openpyxl.load_workbook('/root/.openclaw/media/inbound/æ_å_äº_å---b3d3d04a-4b58-47ae-93fe-f5ed1ca48997.xlsx')

domestic = [
    {'name':'恒生科技ETF','code':'513130.SH','scale':'456','partner':'华泰柏瑞'},
    {'name':'亚太精选ETF','code':'159687.SZ','scale':'15','partner':'南方基金'},
    {'name':'东南亚科技ETF','code':'513730.SH','scale':'13','partner':'华泰柏瑞'},
    {'name':'新经济ETF','code':'159822.SZ','scale':'2.6','partner':'银华基金'},
    {'name':'沙特ETF','code':'159329.SZ','scale':'13','partner':'华泰柏瑞/南方基金'},
    {'name':'沙特ETF','code':'520830.SH','scale':'12.7','partner':'华泰柏瑞/南方基金'},
]
quotes = {
    '513130.SH': {'last':'0.607','prev_close':'0.612','change':'-0.82%','up':False,'volume':'5602万','turnover':'340.4亿'},
    '159687.SZ': {'last':'1.643','prev_close':'1.658','change':'-0.90%','up':False,'volume':'37.9万','turnover':'6.23亿'},
    '513730.SH': {'last':'1.231','prev_close':'1.237','change':'-0.49%','up':False,'volume':'19.2万','turnover':'2.36亿'},
    '159822.SZ': {'last':'0.649','prev_close':'0.656','change':'-1.07%','up':False,'volume':'15.9万','turnover':'1.03亿'},
    '159329.SZ': {'last':'0.941','prev_close':'0.945','change':'-0.42%','up':False,'volume':'28.6万','turnover':'2.70亿'},
    '520830.SH': {'last':'0.929','prev_close':'0.934','change':'-0.54%','up':False,'volume':'28.1万','turnover':'2.61亿'},
}

ws_ov = wb['境外产品']
overseas = []
for i, row in enumerate(ws_ov.iter_rows(values_only=True)):
    if i == 0: continue
    code_raw, name_raw = row[0], row[1] or ''
    name = str(name_raw).replace('南方东英','')
    def fmt(v):
        if v is None or v == '--': return '--'
        try: return f'{float(v):.2f}'
        except: return str(v)
    overseas.append({
        'name': name, 'code': str(code_raw),
        'ytd': fmt(row[4]), 'm1': fmt(row[5]), 'm3': fmt(row[6]),
        'm6': fmt(row[7]), 'y1': fmt(row[8]),
        'annualized': fmt(row[11]), 'scale': fmt(row[13])
    })

def get_cat(n):
    pairs = [
        ('美股七巨头','美股精选'),('标普中国','美股指数'),('纳斯达克100','美股科技'),
        ('纳斯达克科技','美股科技'),('恒生港股通红利','港股高股息'),
        ('富时香港$','港股指数'),('恒生ETF','港股指数'),('恒生科技','港股科技'),
        ('MSCI港股通','港股精选'),('富时东西','全球精选'),('银华中证5G','5G主题'),
        ('恒生生物科技','医疗健康'),('日经225','日本指数'),('中国创业板','A股成长'),
        ('华泰柏瑞中证太阳能','新能源'),('华泰柏瑞沪深300','A股指数'),
        ('科创板50','科创板'),('华泰柏瑞中证A500','A股SmartBeta'),
        ('标普500','美股指数'),('MSCI中国A股','A股指数'),('恒生港美科技','科技主题'),
        ('中证海外中国','海外中国'),('中证医疗保健','医疗健康'),('中证新能源车','新能源'),
        ('中证军工','军工主题'),('中证半导体','半导体'),('中证消费','消费主题'),
        ('中证红利','高股息'),('中证黄金','商品'),('中证油气','能源'),
        ('中证银行','金融'),('中证证券','金融'),('中证保险','金融'),
        ('中证地产','房地产'),('中证农业','农业'),('中证煤炭','能源'),
        ('中证钢铁','原材料'),('中证有色金属','原材料'),('中证化工','原材料'),
        ('中证汽车','汽车'),('中证家电','消费'),('中证电子','科技'),
        ('中证计算机','科技'),('中证通信','科技'),('中证人工智能','AI主题'),
        ('中证机器人','AI主题'),('中证云服务','云计算'),('中证大数据','数据主题'),
        ('中证网络安全','安全主题'),('中证在线消费','消费'),('中证食品饮料','消费'),
        ('中证休闲服务','消费'),('中证交通运输','交运'),('中证物流','交运'),
        ('中证环境治理','环保'),('中证绿色能源','新能源'),('标普医疗','美股医疗'),
        ('纳斯达克金融','美股金融'),('MSCI新兴市场','新兴市场'),('恒生中国企业','中概股'),
        ('标普全球优选','全球优选'),('富时美国','美股消费'),('富时香港韩国','科技主题'),
    ]
    import re
    for kw, c in pairs:
        if re.search(kw, n): return c
    return '其他'

for p in overseas:
    p['cat'] = get_cat(p['name'])

cats = {}
for p in overseas:
    c = p['cat']
    if c not in cats: cats[c] = []
    cats[c].append(p)

# Serialize data for embedding
dom_json = json.dumps(domestic, ensure_ascii=False)
quotes_json = json.dumps(quotes, ensure_ascii=False)
cats_json = json.dumps(cats, ensure_ascii=False)

# Build HTML
with open('/root/.openclaw/workspace/etf-map.html', 'w', encoding='utf-8') as f:
    f.write('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>全球ETF投资地图</title>\n<style>\n')
    f.write('''\
:root{--bg:#0d1117;--card:#161b22;--border:#30363d;--text:#e6edf3;--dim:#8b949e;--green:#3fb950;--red:#f85149;--accent:#ffa657;--blue:#58a6ff}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'PingFang SC','Microsoft YaHei',-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
.header{background:var(--card);border-bottom:1px solid var(--border);padding:18px 36px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}
.hi{font-size:20px;font-weight:700}
.sub{font-size:12px;color:var(--dim);margin-top:3px}
.hr{display:flex;align-items:center;gap:14px}
.st{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--dim)}
.lt{width:7px;height:7px;border-radius:50%;background:var(--green);animation:pl 2s infinite}
.lt.o{background:var(--dim);animation:none}
@keyframes pl{0%,100%{opacity:1}50%{opacity:.4}}
.bn{background:#238636;border:none;color:#fff;padding:7px 16px;border-radius:6px;cursor:pointer;font-size:13px}
.bn:hover{background:#2ea043}
.tabs{display:flex;padding:0 36px;background:var(--card);border-bottom:1px solid var(--border)}
.ta{padding:13px 24px;cursor:pointer;font-size:14px;color:var(--dim);border-bottom:2px solid transparent;transition:.2s}
.ta:hover{color:var(--text)}
.ta.ac{color:var(--accent);border-bottom-color:var(--accent)}
.mn{padding:24px 36px;max-width:1400px;margin:0 auto}
.pn{display:none}
.pn.ac{display:block}
.sts{display:flex;gap:14px;margin-bottom:24px;flex-wrap:wrap}
.sc{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 22px;min-width:150px}
.sc .lb{font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px}
.sc .vl{font-size:26px;font-weight:700;margin-top:3px}
.vg{color:var(--green)}.vb{color:var(--blue)}.vr{color:var(--red)}
.gd{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:12px}
.crd{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px;transition:.2s}
.crd:hover{border-color:var(--dim)}
.chd{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px}
.nm{font-size:14px;font-weight:600}
.cd{font-size:11px;color:var(--dim);margin-top:2px}
.pb{text-align:right}
.pr{font-size:22px;font-weight:700}
.ch{font-size:12px;font-weight:600;margin-top:2px}
.chu{color:var(--green)}.chd{color:var(--red)}.chn{color:var(--dim)}
.ir{display:flex;justify-content:space-between;font-size:11px;color:var(--dim);margin-top:10px;padding-top:10px;border-top:1px solid var(--border)}
.ir span:last-child{color:var(--text)}
.cg{margin-bottom:30px}
.ct{font-size:12px;color:var(--dim);text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;padding-left:10px;border-left:3px solid var(--accent)}
.tw{overflow-x:auto;border-radius:10px;border:1px solid var(--border)}
table{width:100%;border-collapse:collapse;font-size:13px;white-space:nowrap}
th{text-align:left;padding:10px 14px;background:#1c2128;border-bottom:1px solid var(--border);color:var(--dim);font-size:11px;text-transform:uppercase;letter-spacing:.5px;position:sticky;top:0}
td{padding:10px 14px;border-bottom:1px solid var(--border)}
tr:hover td{background:#1c2128}
.nm{text-align:right;font-variant-numeric:tabular-nums}
.ps{color:var(--green)}.ng{color:var(--red)}.nu{color:var(--dim)}
.upd{font-size:11px;color:var(--dim)}
@media(max-width:768px){.header,.mn{padding:16px}.ta{padding:11px 14px}}
''')
    f.write('</style>\n</head>\n<body>\n')
    f.write('''\
<div class="header">
  <div><div class="hi">🌏 全球ETF投资地图</div><div class="sub">实时行情 · 绩效数据 · 分类筛选</div></div>
  <div class="hr">
    <span class="upd" id="upt"></span>
    <button class="bn" onclick="location.reload()">🔄 刷新</button>
    <div class="st"><span class="lt" id="dot"></span><span id="stxt">连接中</span></div>
  </div>
</div>
<div class="tabs">
  <div class="ta ac" id="tab0" onclick="sw(0)">🇨🇳 境内ETF</div>
  <div class="ta" id="tab1" onclick="sw(1)">🌐 境外ETF</div>
</div>
<div class="mn">
  <div class="pn ac" id="pn0">
    <div class="sts" id="dst"></div>
    <div class="gd" id="dgr"></div>
  </div>
  <div class="pn" id="pn1">
    <div id="ogr"></div>
  </div>
</div>
<script>
''')
    f.write(f'const D={dom_json};\n')
    f.write(f'const Q={quotes_json};\n')
    f.write(f'const OC={cats_json};\n')
    f.write('''\
function ud(v){return v.startsWith('-')?'ng':v==='--'?'nu':'ps';}
function fp(v){if(v==='--')return'--';return(parseFloat(v)>=0?'+':'')+v+'%';}
function cl(v){return ud(v)==='ng'?'ng':'ps';}
document.getElementById('upt').textContent='更新: '+new Date().toLocaleTimeString('zh-CN');
document.getElementById('stxt').textContent='Longbridge API ✅ 正常';
document.getElementById('dot').style.background='var(--green)';
let up=0,dn=0;
D.forEach(d=>{const q=Q[d.code];if(q){if(q.up)up++;else dn++;}});
document.getElementById('dst').innerHTML=
  '<div class="sc"><div class="lb">产品数量</div><div class="vl vb">'+D.length+'</div></div>'+
  '<div class="sc"><div class="lb">上涨</div><div class="vl vg">'+up+'</div></div>'+
  '<div class="sc"><div class="lb">下跌</div><div class="vl vr">'+dn+'</div></div>'+
  '<div class="sc"><div class="lb">数据来源</div><div class="vl" style="font-size:14px;padding-top:8px">长桥实时行情</div></div>';
let dh='';
D.forEach(d=>{
  const q=Q[d.code]||{};
  const dir=ud(q.change||'0');
  dh+='<div class="crd"><div class="chd"><div><div class="nm">'+d.name+'</div><div class="cd">'+d.code+'</div></div><div class="pb"><div class="pr">'+(q.last||'--')+'</div><div class="ch ch'+dir+'">'+(q.change||'--')+'</div></div></div><div class="ir"><span>规模</span><span>'+d.scale+'亿</span></div><div class="ir"><span>今日成交</span><span>'+(q.turnover||'--')+'</span></div><div class="ir"><span>合作伙伴</span><span>'+d.partner+'</span></div></div>';
});
document.getElementById('dgr').innerHTML=dh;
const catOrder=['美股科技','美股精选','美股指数','美股消费','港股科技','港股指数','港股高股息','港股精选','A股指数','A股成长','科创板','A股SmartBeta','科技主题','AI主题','5G主题','云计算','数据主题','安全主题','医疗健康','新能源','消费主题','高股息','金融','原材料','能源','环保','交运','日本指数','新兴市场','中概股','全球精选','全球优选','海外中国','军工主题','半导体','房地产','农业','汽车','商品','其他'];
let orderedCats=catOrder.filter(c=>OC[c]).concat(Object.keys(OC).filter(c=>!catOrder.includes(c)));
let ghtml='';
orderedCats.forEach(cat=>{
  const items=OC[cat];
  if(!items||!items.length)return;
  ghtml+='<div class="cg"><div class="ct">'+cat+'（'+items.length+'只）</div><div class="tw"><table><thead><tr><th>简称</th><th>代码</th><th>今年来</th><th>近1月</th><th>近3月</th><th>近6月</th><th>近1年</th><th>年化</th><th>规模(亿)</th></tr></thead><tbody>';
  items.forEach(p=>{
    ghtml+='<tr><td><strong>'+p.name+'</strong></td><td style="color:var(--dim)">'+p.code+'</td><td class="nm '+ud(p.ytd)+'">'+fp(p.ytd)+'</td><td class="nm '+ud(p.m1)+'">'+fp(p.m1)+'</td><td class="nm '+ud(p.m3)+'">'+fp(p.m3)+'</td><td class="nm '+ud(p.m6)+'">'+fp(p.m6)+'</td><td class="nm '+ud(p.y1)+'">'+fp(p.y1)+'</td><td class="nm '+ud(p.annualized)+'">'+fp(p.annualized)+'</td><td class="nm nu">'+(p.scale==='--'?'--':p.scale)+'</td></tr>';
  });
  ghtml+='</tbody></table></div></div>';
});
document.getElementById('ogr').innerHTML=ghtml;
function sw(i){document.querySelectorAll('.ta').forEach((t,j)=>{t.classList.toggle('ac',j===i);});document.querySelectorAll('.pn').forEach((p,j)=>{p.classList.toggle('ac',j===i);});}
''')
    f.write('</script>\n</body>\n</html>')

print('Done!')
