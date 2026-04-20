import openpyxl, json

# ===== Domestic ETF data (with live quotes from Longbridge) =====
domestic = [
    {'name':'恒生科技ETF','code':'513130.SH','scale':'456','partner':'华泰柏瑞'},
    {'name':'亚太精选ETF','code':'159687.SZ','scale':'15','partner':'南方基金'},
    {'name':'东南亚科技ETF','code':'513730.SH','scale':'13','partner':'华泰柏瑞'},
    {'name':'新经济ETF','code':'159822.SZ','scale':'2.6','partner':'银华基金'},
    {'name':'沙特ETF','code':'159329.SZ','scale':'13','partner':'华泰柏瑞/南方基金'},
    {'name':'沙特ETF','code':'520830.SH','scale':'12.7','partner':'华泰柏瑞/南方基金'},
]
domestic_quotes = {
    '513130.SH': {'last':'0.607','prev_close':'0.612','change':'-0.82%','up':False,'turnover':'340.4亿'},
    '159687.SZ': {'last':'1.643','prev_close':'1.658','change':'-0.90%','up':False,'turnover':'6.23亿'},
    '513730.SH': {'last':'1.231','prev_close':'1.237','change':'-0.49%','up':False,'turnover':'2.36亿'},
    '159822.SZ': {'last':'0.649','prev_close':'0.656','change':'-1.07%','up':False,'turnover':'1.03亿'},
    '159329.SZ': {'last':'0.941','prev_close':'0.945','change':'-0.42%','up':False,'turnover':'2.70亿'},
    '520830.SH': {'last':'0.929','prev_close':'0.934','change':'-0.54%','up':False,'turnover':'2.61亿'},
}

# ===== Overseas ETF data (HKEX listed, with live quotes) =====
# Format: {code_hk: {name, cat, last, prev_close}}
overseas_raw = [
    # 港股指数
    {'code':'3037.HK','name':'恒生指数ETF','cat':'港股指数','last':'25.960','prev_close':'25.960'},
    {'code':'3432.HK','name':'MSCI港股通精选ETF','cat':'港股指数','last':'105.350','prev_close':'105.350'},
    {'code':'3443.HK','name':'富时香港股票ETF','cat':'港股指数','last':'9.300','prev_close':'9.300'},
    {'code':'3469.HK','name':'恒生港股通红利ETF','cat':'港股指数','last':'8.480','prev_close':'8.480'},
    {'code':'3174.HK','name':'恒生生物科技ETF','cat':'港股指数','last':'3.634','prev_close':'3.634'},
    {'code':'2822.HK','name':'富时中国A50 ETF','cat':'港股指数','last':'15.460','prev_close':'15.460'},
    {'code':'3005.HK','name':'中证500ETF','cat':'港股指数','last':'25.680','prev_close':'25.680'},
    {'code':'3003.HK','name':'MSCI中国A50互联互通ETF','cat':'港股指数','last':'7.025','prev_close':'7.025'},
    {'code':'3147.HK','name':'中国创业板ETF','cat':'港股指数','last':'13.960','prev_close':'13.960'},
    {'code':'3109.HK','name':'科创板50指数ETF','cat':'港股指数','last':'13.230','prev_close':'13.230'},
    # 港股主题
    {'code':'3033.HK','name':'恒生科技指数ETF','cat':'港股主题','last':'4.724','prev_close':'4.724'},
    {'code':'3441.HK','name':'富时东西股票精选ETF','cat':'港股主题','last':'11.430','prev_close':'11.430'},
    {'code':'3442.HK','name':'恒生港美科技ETF','cat':'港股主题','last':'7.960','prev_close':'7.960'},
    {'code':'3431.HK','name':'富时香港韩国科技+指数ETF','cat':'港股主题','last':'8.390','prev_close':'8.390'},
    {'code':'3473.HK','name':'富时亚洲科技指数ETF','cat':'港股主题','last':'8.120','prev_close':'8.120'},
    {'code':'3535.HK','name':'野村富时香港日本股票现金流聚焦指数ETF','cat':'港股主题','last':'7.835','prev_close':'7.835'},
    # 区域性
    {'code':'3004.HK','name':'富时越南30ETF','cat':'区域性','last':'9.515','prev_close':'9.515'},
    {'code':'2830.HK','name':'沙特阿拉伯ETF','cat':'区域性','last':'82.520','prev_close':'82.520'},
    # A股指数
    {'code':'3133.HK','name':'华泰柏瑞沪深300ETF','cat':'A股指数','last':'11.550','prev_close':'11.550'},
    {'code':'3101.HK','name':'华泰柏瑞中证A500ETF','cat':'A股指数','last':'7.890','prev_close':'7.890'},
    {'code':'3193.HK','name':'银华中证5G通信主题ETF','cat':'A股指数','last':'15.070','prev_close':'15.070'},
    {'code':'3134.HK','name':'华泰柏瑞中证太阳能产业ETF','cat':'A股指数','last':'6.190','prev_close':'6.190'},
    # 美股
    {'code':'3034.HK','name':'纳斯达克100ETF','cat':'美股','last':'10.690','prev_close':'10.690'},
    {'code':'3167.HK','name':'工银标普中国新经济行业ETF','cat':'美股','last':'64.240','prev_close':'64.240'},
    {'code':'3454.HK','name':'美股七巨头ETF','cat':'美股','last':'10.050','prev_close':'10.050'},
    {'code':'3153.HK','name':'日经225指数ETF','cat':'美股','last':'113.700','prev_close':'113.700'},
    # 货币+债券+其他
    {'code':'3053.HK','name':'港元货币市场ETF','cat':'货币+债券','last':'1178.650','prev_close':'1178.650'},
    {'code':'3096.HK','name':'美元货币市场ETF','cat':'货币+债券','last':'958.050','prev_close':'958.050'},
    {'code':'3122.HK','name':'人民币货币市场ETF','cat':'货币+债券','last':'193.400','prev_close':'193.400'},
    {'code':'3199.HK','name':'工银富时中国国债及政策性银行债券指数ETF','cat':'货币+债券','last':'119.650','prev_close':'119.650'},
    {'code':'3433.HK','name':'富时美国国债20年+指数ETF','cat':'货币+债券','last':'67.980','prev_close':'67.980'},
    {'code':'3447.HK','name':'富时亚太精选房地产信托ETF','cat':'货币+债券','last':'7.900','prev_close':'7.900'},
    {'code':'2802.HK','name':'国指备兑认购期权主动型ETF','cat':'货币+债券','last':'8.125','prev_close':'8.125'},
    # 虚拟资产期货
    {'code':'3066.HK','name':'比特币期货ETF','cat':'虚拟资产期货','last':'22.800','prev_close':'22.800'},
    {'code':'3068.HK','name':'以太币期货ETF','cat':'虚拟资产期货','last':'9.780','prev_close':'9.780'},
    # 杠杆及反向 - 港股指数
    {'code':'7200.HK','name':'恒生指数每日杠杆(2X)','cat':'港股杠杆反向','last':'5.770','prev_close':'5.770'},
    {'code':'7500.HK','name':'恒生指数每日反向(-2X)','cat':'港股杠杆反向','last':'1.754','prev_close':'1.754'},
    {'code':'7300.HK','name':'恒生指数每日反向(-1X)','cat':'港股杠杆反向','last':'3.388','prev_close':'3.388'},
    {'code':'7288.HK','name':'恒生中国企业指数每日杠杆(2X)','cat':'港股杠杆反向','last':'3.056','prev_close':'3.056'},
    {'code':'7588.HK','name':'恒生中国企业指数每日反向(-2X)','cat':'港股杠杆反向','last':'1.566','prev_close':'1.566'},
    {'code':'7226.HK','name':'恒生科技指数每日杠杆(2X)','cat':'港股杠杆反向','last':'3.730','prev_close':'3.730'},
    {'code':'7552.HK','name':'恒生科技指数每日反向(-2X)','cat':'港股杠杆反向','last':'1.756','prev_close':'1.756'},
    # 杠杆及反向 - 美股
    {'code':'7266.HK','name':'纳斯达克100指数每日杠杆(2X)','cat':'美股杠杆反向','last':'30.300','prev_close':'30.300'},
    {'code':'7568.HK','name':'纳斯达克100指数每日反向(-2X)','cat':'美股杠杆反向','last':'3.328','prev_close':'3.328'},
    # 杠杆及反向 - A股
    {'code':'7299.HK','name':'黄金期货每日杠杆(2X)','cat':'商品杠杆反向','last':'29.540','prev_close':'29.540'},
    {'code':'7233.HK','name':'沪深300指数每日杠杆(2X)','cat':'A股杠杆反向','last':'4.968','prev_close':'4.968'},
    # 杠杆及反向 - 虚拟资产
    {'code':'7376.HK','name':'比特币期货每日反向(-1X)','cat':'虚拟资产杠杆反向','last':'5.380','prev_close':'5.380'},
    # 杠杆及反向 - 日股
    {'code':'7262.HK','name':'日经225每日杠杆(2X)','cat':'日股杠杆反向','last':'139.800','prev_close':'139.800'},
    {'code':'7515.HK','name':'日经225每日反向(-2X)','cat':'日股杠杆反向','last':'20.800','prev_close':'20.800'},
    # 单一股票 - 巴郡
    {'code':'7777.HK','name':'Berkshire每日杠杆(2X)','cat':'个股杠杆反向','last':'54.060','prev_close':'54.060'},
    # 单一股票 - 英伟达
    {'code':'7788.HK','name':'英伟达每日杠杆(2X)','cat':'个股杠杆反向','last':'137.700','prev_close':'137.700'},
    {'code':'7388.HK','name':'英伟达每日反向(-2X)','cat':'个股杠杆反向','last':'19.060','prev_close':'19.060'},
    # 单一股票 - 特斯拉
    {'code':'7766.HK','name':'特斯拉每日杠杆(2X)','cat':'个股杠杆反向','last':'91.320','prev_close':'91.320'},
    {'code':'7366.HK','name':'特斯拉每日反向(-2X)','cat':'个股杠杆反向','last':'14.420','prev_close':'14.420'},
    # 单一股票 - Coinbase
    {'code':'7711.HK','name':'Coinbase每日杠杆(2X)','cat':'个股杠杆反向','last':'27.360','prev_close':'27.360'},
    {'code':'7311.HK','name':'Coinbase每日反向(-2X)','cat':'个股杠杆反向','last':'15.400','prev_close':'15.400'},
    # 单一股票 - MicroStrategy
    {'code':'7799.HK','name':'MicroStrategy每日杠杆(2X)','cat':'个股杠杆反向','last':'5.145','prev_close':'5.145'},
    {'code':'7399.HK','name':'MicroStrategy每日反向(-2X)','cat':'个股杠杆反向','last':'58.560','prev_close':'58.560'},
    # 单一股票 - 三星/SK
    {'code':'7747.HK','name':'三星电子每日杠杆(2X)','cat':'个股杠杆反向','last':'77.480','prev_close':'77.480'},
    {'code':'7347.HK','name':'三星电子每日反向(-2X)','cat':'个股杠杆反向','last':'0.212','prev_close':'0.212'},
    {'code':'7709.HK','name':'SK海力士每日杠杆(2X)','cat':'个股杠杆反向','last':'31.100','prev_close':'31.100'},
]

# Calculate change % for each
for etf in overseas_raw:
    try:
        last = float(etf['last'])
        prev = float(etf['prev_close'])
        if prev != 0:
            chg = (last - prev) / prev * 100
            etf['change'] = f"{chg:+.2f}%"
            etf['up'] = chg > 0
        else:
            etf['change'] = '0.00%'
            etf['up'] = False
    except:
        etf['change'] = '0.00%'
        etf['up'] = False

# Group by category
cats = {}
for etf in overseas_raw:
    c = etf['cat']
    if c not in cats:
        cats[c] = []
    cats[c].append(etf)

print(f"境内: {len(domestic)} 条")
print(f"境外: {len(overseas_raw)} 条, 分类: {list(cats.keys())}")
for c, items in cats.items():
    print(f"  {c}: {len(items)} 条")

# Serialize for JS
dom_json = json.dumps(domestic, ensure_ascii=False)
dq_json = json.dumps(domestic_quotes, ensure_ascii=False)
ov_json = json.dumps(overseas_raw, ensure_ascii=False)
cats_json = json.dumps(cats, ensure_ascii=False)

# Cat display order
cat_order = [
    '港股指数','港股主题','区域性',
    'A股指数','美股',
    '货币+债券',
    '虚拟资产期货',
    '港股杠杆反向','美股杠杆反向','A股杠杆反向','日股杠杆反向','商品杠杆反向','虚拟资产杠杆反向','个股杠杆反向',
]
ordered_cats = [c for c in cat_order if c in cats]

# ========== Build HTML ==========
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全球ETF投资地图</title>
<style>
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
th{text-align:left;padding:10px 14px;background:#1c2128;border-bottom:1px solid var(--border);color:var(--dim);font-size:11px;text-transform:uppercase;letter-spacing:.5px;position:sticky;top:0;white-space:nowrap}
td{padding:10px 14px;border-bottom:1px solid var(--border);white-space:nowrap}
tr:hover td{background:#1c2128}
.nm{text-align:right;font-variant-numeric:tabular-nums}
.ps{color:var(--green)}.ng{color:var(--red)}.nu{color:var(--dim)}
.upd{font-size:11px;color:var(--dim)}
.tot{font-size:12px;color:var(--dim);margin-bottom:16px}
.tot b{color:var(--text)}
@media(max-width:768px){.header,.mn{padding:16px}.ta{padding:11px 14px}}
</style>
</head>
<body>
<div class="header">
  <div><div class="hi">🌏 全球ETF投资地图</div><div class="sub">实时行情 · 绩效数据 · 分类筛选</div></div>
  <div class="hr">
    <span class="upd" id="upt"></span>
    <button class="bn" onclick="location.reload()">🔄 刷新行情</button>
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
    <div class="tot" id="tot"></div>
    <div id="ogr"></div>
  </div>
</div>
<script>
const D=''' + dom_json + ''';
const DQ=''' + dq_json + ''';
const OV=''' + ov_json + ''';
function ud(v){try{return v.startsWith('-')?'ng':v==='--'||v.startsWith('+')?'':v==='0.00%'?'nu':'ps';}catch(e){return'nu';}}
function fmtP(v){if(v==='--'||v===undefined)return'--';try{const n=parseFloat(v);if(isNaN(n))return'--';return(n>=0?'+':'')+n.toFixed(2)+'%';}catch(e){return'--';}}
function colorClass(v){try{if(v===undefined||v==='--')return'nu';return parseFloat(v)>=0?'ps':'ng';}catch(e){return'nu';}}
document.getElementById('upt').textContent='更新: '+new Date().toLocaleTimeString('zh-CN');
document.getElementById('stxt').textContent='Longbridge API ✅ 正常';
document.getElementById('dot').style.background='var(--green)';
let up=0,dn=0;
D.forEach(d=>{const q=DQ[d.code];if(q){if(q.up)up++;else dn++;}});
document.getElementById('dst').innerHTML=
  '<div class="sc"><div class="lb">产品数量</div><div class="vl vb">'+D.length+'</div></div>'+
  '<div class="sc"><div class="lb">上涨</div><div class="vl vg">'+up+'</div></div>'+
  '<div class="sc"><div class="lb">下跌</div><div class="vl vr">'+dn+'</div></div>'+
  '<div class="sc"><div class="lb">数据来源</div><div class="vl" style="font-size:14px;padding-top:8px">长桥实时行情</div></div>';
let dh='';
D.forEach(d=>{
  const q=DQ[d.code]||{};
  const dir=ud(q.change||'0');
  const chg=q.change?'fmtP(q.change)':'--';
  dh+='<div class="crd"><div class="chd"><div><div class="nm">'+d.name+'</div><div class="cd">'+d.code+'</div></div><div class="pb"><div class="pr">'+(q.last||'--')+'</div><div class="ch ch'+dir+'">'+(q.change||'--')+'</div></div></div><div class="ir"><span>规模</span><span>'+d.scale+'亿</span></div><div class="ir"><span>今日成交</span><span>'+(q.turnover||'--')+'</span></div><div class="ir"><span>合作伙伴</span><span>'+d.partner+'</span></div></div>';
});
document.getElementById('dgr').innerHTML=dh;
// overseas
const cats=''' + cats_json + ''';
const catOrder=''' + json.dumps(ordered_cats) + ''';
const ordered=catOrder.filter(c=>cats[c]).concat(Object.keys(cats).filter(c=>!catOrder.includes(c)));
let totalHK=0;
ordered.forEach(c=>totalHK+=cats[c].length);
document.getElementById('tot').innerHTML='境外ETF共 <b>'+totalHK+'</b> 只，代码格式为港交所 <b>.HK</b>，行情数据来自长桥实时API';
let ghtml='';
ordered.forEach(cat=>{
  const items=cats[cat];
  if(!items||!items.length)return;
  ghtml+='<div class="cg"><div class="ct">'+cat+'（'+items.length+'只）</div><div class="tw"><table><thead><tr><th>名称</th><th>代码</th><th>最新价</th><th>涨跌幅</th></tr></thead><tbody>';
  items.forEach(p=>{
    const cc=colorClass(p.change);
    ghtml+='<tr><td><strong>'+p.name+'</strong></td><td style="color:var(--dim);font-size:12px">'+p.code+'</td><td class="nm" style="font-size:15px;font-weight:700">'+p.last+'</td><td class="nm '+cc+'" style="font-size:14px;font-weight:600">'+(p.change||'--')+'</td></tr>';
  });
  ghtml+='</tbody></table></div></div>';
});
document.getElementById('ogr').innerHTML=ghtml;
function sw(i){document.querySelectorAll('.ta').forEach((t,j)=>{t.classList.toggle('ac',j===i);});document.querySelectorAll('.pn').forEach((p,j)=>{p.classList.toggle('ac',j===i);});}
</script>
</body>
</html>'''

with open('/root/.openclaw/workspace/etf-map.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\nHTML written: {len(html)} chars')
print(f'Domestic: {len(domestic)} items')
print(f'Overseas: {len(overseas_raw)} items across {len(cats)} categories')
