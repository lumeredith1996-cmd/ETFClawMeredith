#!/usr/bin/env python3
"""Build etf-map-v8.html using all产品.xlsx as authoritative source"""
import openpyxl, json

# ─── Load new product list ───────────────────────────────────────────────────
wb = openpyxl.load_workbook('/root/.openclaw/media/inbound/alläº_å---39b53832-0c03-4f14-a52d-76a6d053448a.xlsx')
ws = wb['products_all']
new_prods = []
for row in ws.iter_rows(min_row=2, values_only=True):
    if row[0]:
        new_prods.append({'region': row[0], 'cat': row[1], 'code': row[2], 'name': row[3], 'note': row[4] or ''})

# ─── Load v7 market data ────────────────────────────────────────────────────
v7 = json.load(open('/tmp/v7_data.json'))
old_map = {p['code']: p for p in v7['products']}

def try_match(code):
    if code in old_map: return old_map[code]
    if '.HK' in code or '.SP' in code:
        s = code.lstrip('0')
        if s in old_map: return old_map[s]
        if '.HK' in code:
            parts = code.split('.')
            p = parts[0].zfill(5) + '.' + parts[1]
            if p in old_map: return old_map[p]
    return None

# ─── Build final product list ───────────────────────────────────────────────
products = []
for np in new_prods:
    old = try_match(np['code'])
    p = {
        'name': np['name'],
        'code': np['code'],
        'region': np['region'],
        'cat': np['cat'],
        'note': np['note'],
    }
    if old:
        p.update({'last': old['last'], 'prev': old['prev'], 'chg': old['chg'],
                  'up': old['up'], 'turnover': old['turnover'],
                  'premium': old['premium'], 'index': old['index']})
    else:
        p.update({'last': 0, 'prev': 0, 'chg': 0, 'up': True,
                  'turnover': '-', 'premium': 0, 'index': ''})
    products.append(p)

# Keep other data
HOLD = v7['HOLD']
HOLIDAYS = v7['HOLIDAYS']
IDATA = v7['IDATA']
REPORTS = v7['REPORTS']
FLOW_IN = v7['FLOW_IN']
FLOW_OUT = v7['FLOW_OUT']
HK_FLOW = v7['HK_FLOW']
HSI = v7['HSI']
MT = v7['mkt_temp']
MV = v7['mkt_val']
MS = v7['mkt_sent']
MD = v7['mkt_desc']

AP = json.dumps(products, ensure_ascii=False)
HD = json.dumps(HOLD, ensure_ascii=False)
HD2 = json.dumps(HOLIDAYS, ensure_ascii=False)
ID = json.dumps(IDATA, ensure_ascii=False)
RP = json.dumps(REPORTS, ensure_ascii=False)
FI = json.dumps(FLOW_IN, ensure_ascii=False)
FO = json.dumps(FLOW_OUT, ensure_ascii=False)
KF = json.dumps(HK_FLOW, ensure_ascii=False)
HS = json.dumps(HSI, ensure_ascii=False)

# Count by region
in_count = sum(1 for p in products if p['region'] == '内地可买')
out_count = sum(1 for p in products if p['region'] == '境外可买')
print(f"Products: {len(products)} total | 内地可买 {in_count} | 境外可买 {out_count}")

# ─── CSS ────────────────────────────────────────────────────────────────────
CSS = """
:root{--bg:#f5f6fa;--card:#fff;--card2:#f0f2f8;--border:#e2e5ef;--text:#1a1d2e;--text2:#6b7280;--dim:#9ca3af;--red:#dc2626;--green:#16a34a;--orange:#ea580c;--blue:#2563eb;--gold:#d97706;}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"PingFang SC","Microsoft YaHei",-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
a{color:inherit;text-decoration:none}
.header{background:var(--card);border-bottom:2px solid var(--border);padding:0 32px;display:flex;justify-content:space-between;align-items:center;height:58px;position:sticky;top:0;z-index:100}
.logo{font-size:16px;font-weight:800;display:flex;align-items:center;gap:8px}
.logo .beta{background:var(--orange);color:#fff;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px}
.hdr-right{display:flex;align-items:center;gap:14px}
.upd{font-size:12px;color:var(--dim)}
.lt{width:8px;height:8px;border-radius:50%;background:var(--green);animation:pl 2s infinite}
@keyframes pl{0%,100%{opacity:1}50%{opacity:.3}}
.live{font-size:12px;color:var(--dim);display:flex;align-items:center;gap:5px}
.tabs{background:var(--card);padding:0 32px;display:flex;border-bottom:1px solid var(--border)}
.ta{padding:12px 22px;font-size:14px;color:var(--dim);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px;font-weight:600;transition:.15s}
.ta:hover{color:var(--orange)}
.ta.ac{color:var(--orange);border-bottom-color:var(--orange)}
.mn{padding:20px 32px;max-width:1280px;margin:0 auto}
.pn{display:none}.pn.ac{display:block}
.sec-title{font-size:14px;font-weight:800;color:var(--text);margin-bottom:12px;padding-left:10px;border-left:4px solid var(--orange);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.sec-title .sub{font-size:12px;color:var(--dim);font-weight:400}
.info-box{background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;padding:11px 14px;font-size:12px;color:#92400e;margin-bottom:16px;line-height:1.65}
.fbar{display:flex;gap:5px;margin-bottom:8px;flex-wrap:wrap}
.fsub{display:flex;gap:4px;margin-bottom:12px;padding-left:4px;flex-wrap:wrap}
.fbtn{padding:5px 14px;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid var(--border);color:var(--dim);background:var(--card);transition:.15s;white-space:nowrap;user-select:none}
.fbtn.ac,.fbtn:hover{background:var(--orange);color:#fff;border-color:var(--orange)}
.fsub-item{padding:4px 11px;border-radius:6px;font-size:11px;font-weight:600;cursor:pointer;border:1px solid var(--border);color:var(--dim);background:var(--card);transition:.15s;user-select:none}
.fsub-item.ac,.fsub-item:hover{background:var(--blue);color:#fff;border-color:var(--blue)}
.search-box{margin-bottom:12px;display:flex;align-items:center;gap:10px}
.search-in{flex:1;max-width:300px;padding:7px 12px;border:1px solid var(--border);border-radius:8px;font-size:13px;background:var(--card);color:var(--text);outline:none;transition:border-color .15s}
.search-in:focus{border-color:var(--orange)}
.search-in::placeholder{color:var(--dim)}
.search-count{font-size:11px;color:var(--dim)}
.tbl{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.04);margin-bottom:18px}
.tbl table{width:100%;border-collapse:collapse;font-size:12.5px}
.tbl th{background:#fafbfc;padding:9px 11px;text-align:left;font-size:10.5px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;font-weight:700;border-bottom:1px solid var(--border);white-space:nowrap;cursor:pointer;user-select:none}
.tbl th:hover{color:var(--orange)}
.th-sort::after{content:" \\2195";font-size:9px;opacity:.3;margin-left:3px}
.th-sort.asc::after{content:" \\2191";opacity:1;color:var(--orange)}
.th-sort.desc::after{content:" \\2193";opacity:1;color:var(--orange)}
.tbl td{padding:9px 11px;border-bottom:1px solid #f5f5f5;vertical-align:middle}
.tbl tr:last-child td{border-bottom:none}
.tbl tr:hover td{background:#fafafa}
.tbl tr.no-data td{opacity:0.55}
.tbl tr.no-data:hover td{background:#fafafa}
.tbl .nm{text-align:right;font-variant-numeric:tabular-nums}
/* RED=DOWN, GREEN=UP */
.up{color:var(--red);font-weight:700}
.down{color:var(--green);font-weight:700}
.tag-o{background:#fff7ed;color:#ea580c;font-size:10px;padding:2px 7px;border-radius:20px;font-weight:700}
.tag-b{background:#dbeafe;color:#1d4ed8;font-size:10px;padding:2px 7px;border-radius:20px;font-weight:700}
.tag-d{background:#f3f4f6;color:#6b7280;font-size:10px;padding:2px 7px;border-radius:20px}
.tag-g{background:#dcfce7;color:#16a34a;font-size:10px;padding:2px 7px;border-radius:20px;font-weight:700}
.tag-r{background:#fee2e2;color:#dc2626;font-size:10px;padding:2px 7px;border-radius:20px;font-weight:700}
.tag-note{background:#fef3c7;color:#92400e;font-size:10px;padding:1px 6px;border-radius:4px;cursor:help}
.row-note{font-size:10.5px;color:var(--text2);line-height:1.4;margin-top:3px}
.modal{position:fixed;inset:0;background:rgba(0,0,0,.45);backdrop-filter:blur(3px);display:none;align-items:center;justify-content:center;z-index:1000;padding:16px}
.modal.open{display:flex}
.mbox{background:var(--card);border-radius:14px;width:100%;max-width:920px;max-height:88vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.18)}
.mhead{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--card);border-radius:14px 14px 0 0;z-index:2}
.mtitle{font-size:14px;font-weight:800}
.mclose{width:28px;height:28px;border-radius:7px;border:1px solid var(--border);background:var(--card);color:var(--dim);cursor:pointer;font-size:13px;display:flex;align-items:center;justify-content:center}
.mbody{padding:16px 20px}
.mprice-row{display:flex;align-items:flex-end;gap:16px;margin-bottom:12px;flex-wrap:wrap}
.mprice-block{text-align:right}
.mnav{font-size:28px;font-weight:900}
.mchg{font-size:14px;font-weight:700;margin-top:3px}
.mmeta{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.mmeta span{font-size:11px;color:var(--dim);background:var(--card2);padding:3px 9px;border-radius:20px}
.chart-wrap{margin:12px 0;background:var(--card2);border-radius:10px;padding:12px}
.chart-title{font-size:10.5px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;font-weight:600}
canvas#kchart{max-width:100%;height:150px;background:var(--card);border-radius:8px;border:1px solid var(--border)}
.chart-legend{display:flex;gap:14px;margin-top:6px;font-size:10.5px;color:var(--dim)}
.chart-legend span{display:flex;align-items:center;gap:3px}
.cline{width:12px;height:2px;display:inline-block}
.cline-p{background:#2563eb}.cline-v{background:#ea580c}
.hsec{margin-top:16px}
.hsec h4{font-size:10.5px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;padding-bottom:7px;border-bottom:1px solid var(--border);margin-bottom:9px;font-weight:600}
.mtbl{width:100%;border-collapse:collapse;font-size:12px;overflow-x:auto;display:block}
.mtbl table{min-width:500px;width:100%}
.mtbl th{background:#fafbfc;padding:7px 9px;text-align:left;font-size:10px;color:var(--dim);text-transform:uppercase;border-bottom:1px solid var(--border);white-space:nowrap}
.mtbl td{padding:7px 9px;border-bottom:1px solid #f8f8f8;vertical-align:middle;white-space:nowrap}
.mtbl tr:last-child td{border-bottom:none}
.mtbl tr:hover td{background:#fafafa}
.rank{font-weight:800;color:var(--dim);width:24px;font-size:11px}
.rgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:12px}
.rcard{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:15px;transition:.2s;box-shadow:0 1px 4px rgba(0,0,0,.03)}
.rcard:hover{border-color:var(--orange);transform:translateY(-2px);box-shadow:0 4px 14px rgba(0,0,0,.07)}
.rtop{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
.rtag{font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px}
.rtag-g{background:#dcfce7;color:#16a34a}.rtag-r{background:#fee2e2;color:#dc2626}.rtag-b{background:#dbeafe;color:#1d4ed8}.rtag-o{background:#ffedd5;color:#ea580c}
.rdate{font-size:10.5px;color:var(--dim)}
.rtitle{font-size:13.5px;font-weight:700;line-height:1.45;margin-bottom:7px}
.rsummary{font-size:11.5px;color:var(--text2);line-height:1.65}
.rfooter{margin-top:10px;padding-top:9px;border-top:1px solid #f5f5f5;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px}
.rsrc{font-size:10.5px;color:var(--dim)}
.rtags{display:flex;gap:4px;flex-wrap:wrap}
.rtags span{font-size:10px;background:#f3f4f6;color:#6b7280;padding:2px 6px;border-radius:10px}
.flow-tabs{display:flex;gap:7px;margin-bottom:12px}
.ftab{padding:5px 13px;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid var(--border);color:var(--dim);background:var(--card);transition:.15s}
.ftab.ac,.ftab:hover{background:var(--orange);color:#fff;border-color:var(--orange)}
.fsection{display:none}.fsection.ac{display:block}
.ftbl{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:14px;box-shadow:0 1px 4px rgba(0,0,0,.03)}
.ftbl table{width:100%;border-collapse:collapse;font-size:12.5px}
.ftbl th{background:#fafbfc;padding:9px 12px;text-align:left;font-size:10.5px;color:var(--dim);text-transform:uppercase;border-bottom:1px solid var(--border)}
.ftbl td{padding:9px 12px;border-bottom:1px solid #f5f5f5}
.ftbl tr:last-child td{border-bottom:none}
.rnum{font-weight:900;color:var(--dim);width:30px;font-size:14px}
.fname{font-weight:600}.fcode{font-size:10.5px;color:var(--dim);margin-top:1px}
.famt{font-weight:800;font-size:13px;text-align:right;white-space:nowrap}
.mkt-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;margin-bottom:16px}
.mkt-row{display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap}
.mkt-hsi{flex:0 0 auto}
.mkt-label{font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;font-weight:600}
.mkt-big{font-size:36px;font-weight:900;line-height:1}
.mkt-chg{font-size:14px;font-weight:700;margin-top:4px}
.mkt-raw{font-size:10.5px;color:var(--dim);margin-top:2px}
.mkt-temps{flex:1;min-width:200px}
.temp-gauge{height:8px;background:#f3f4f6;border-radius:4px;overflow:hidden;margin:8px 0 4px}
.temp-fill{height:100%;border-radius:4px;transition:width .5s}
.mkt-meta{font-size:11px;color:var(--text2);margin-top:4px}
.mkt-hsi-chart{background:#fafbfc;border-radius:8px;border:1px solid var(--border);margin-top:10px;padding:4px 4px 0}
canvas#hsicanvas{max-width:100%;height:90px;display:block}
.flow-sub-title{font-size:11px;font-weight:700;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;margin:16px 0 8px;padding-left:4px;border-left:3px solid var(--orange)}
.flow-src{font-weight:400;text-transform:none;letter-spacing:0;color:var(--dim);font-size:10.5px;margin-left:6px}
.flow-2col{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.flow-col{background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden}
.flow-col-title{font-size:10px;font-weight:700;text-transform:uppercase;padding:7px 11px}
.flow-col-title.in{background:#f0fdf4;color:#16a34a}.flow-col-title.out{background:#fef2f2;color:#dc2626}
.flow-row{display:flex;align-items:center;padding:6px 11px;border-bottom:1px solid #f9f9f9;gap:8px}
.flow-row:last-child{border-bottom:none}
.flow-name{flex:1;font-size:11.5px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.flow-bar-wrap{flex:0 0 60px;height:4px;background:#f3f4f6;border-radius:2px;overflow:hidden}
.flow-bar{height:100%;border-radius:2px}
.flow-bar.in{background:#16a34a}.flow-bar.out{background:#dc2626}
.flow-amt{font-size:11px;font-weight:700;min-width:50px;text-align:right}
.flow-amt.in{color:#16a34a}.flow-amt.out{color:#dc2626}
.flow-section{background:var(--card2);border-radius:12px;padding:12px}
.edu-tbl{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,.04)}
.edu-tbl table{width:100%;border-collapse:collapse;font-size:11.5px}
.edu-tbl th{background:#fafbfc;padding:9px 12px;text-align:left;font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;font-weight:700;border-bottom:1px solid var(--border)}
.edu-tbl td{padding:9px 12px;border-bottom:1px solid #f5f5f5;vertical-align:top;line-height:1.65}
.edu-tbl tr:last-child td{border-bottom:none}
.no-mkt{font-size:11px;color:var(--dim);background:#fafafa;padding:2px 7px;border-radius:10px;margin-left:6px}
@media(max-width:768px){.header,.tabs{padding:0 14px}.mn{padding:14px}.tbl{overflow-x:auto}.tbl table{min-width:900px}.flow-2col{grid-template-columns:1fr}}}
""".strip()

# ─── JavaScript ──────────────────────────────────────────────────────────────
JS = f"""
const ALL_PRODUCTS = {AP};
const HOLD = {HD};
const HOLIDAYS = {HD2};
const IDATA = {ID};
const REPORTS = {RP};
const FLOW_IN = {FI};
const FLOW_OUT = {FO};
const HK_FLOW = {KF};
const HSI_INTRADAY = {HS};
const MARKET_TEMP = {MT};
const MARKET_VAL = {MV};
const MARKET_SENT = {MS};
const MARKET_DESC = '{MD}';

var curMain='内地可买',curSub=null,curSort='chg',curDir='desc',curSearch='';

function renderFilters(){{
  var mains=['内地可买','境外可买'];
  document.getElementById('fbar').innerHTML=mains.map(function(m){{
    return '<span class="fbtn'+(curMain===m?' ac':'')+'" data-m="'+m+'">'+m+'</span>';
  }}).join('');
  var subs=getSubs(curMain);
  document.getElementById('fsub').innerHTML=subs.map(function(s){{
    return '<span class="fsub-item'+(curSub===s?' ac':'')+'" data-s="'+s+'">'+s+'</span>';
  }}).join('');
  document.getElementById('sec-title').innerHTML=(curMain==='内地可买'?'境内':'境外')+'产品 <span class="sub" style="font-size:12px;color:var(--dim);font-weight:400" id="prod-count"></span>';
}}

function getSubs(m){{
  if(m==='内地可买')return ['全部','QDII ETF','QDII 联接基金','港股通ETF','跨境理财通-权益','跨境理财通-货币','跨境理财通-固收','跨境理财通-基金互认'];
  return ['全部','香港','美国','A股','日本','新兴市场','个股杠反ETF','指数杠反ETF','债券ETF','货币市场ETF','REITs ETF','加密货币期货ETF'];
}}

function setMain(m){{curMain=m;curSub=null;renderFilters();renderTable();}}
function setSub(s){{curSub=s;renderTable();}}
document.getElementById('fbar').addEventListener('click',function(e){{var b=e.target.closest('.fbtn');if(b)setMain(b.textContent.trim());}});
document.getElementById('fsub').addEventListener('click',function(e){{var b=e.target.closest('.fsub-item');if(b)setSub(b.textContent.trim());}});
function sw(i){{document.querySelectorAll('.ta').forEach(function(t,j){{t.classList.toggle('ac',j===i);}});document.querySelectorAll('.pn').forEach(function(p,j){{p.classList.toggle('ac',j===i);}});}}
function cm(){{document.getElementById('modal').classList.remove('open');}}
function sf(d){{document.getElementById('ftabin').classList.toggle('ac',d==='in');document.getElementById('ftabout').classList.toggle('ac',d==='out');document.getElementById('finsec').classList.toggle('ac',d==='in');document.getElementById('foutsec').classList.toggle('ac',d==='out');}}
function fmt(v){{try{{var n=parseFloat(v);return isNaN(n)?v:(n>=0?'+':'')+n.toFixed(2);}}catch(e){{return v;}}}}
function onSearch(v){{curSearch=v.toLowerCase();renderTable();}}

function tagCat(cat){{
  if(cat.indexOf('杠反')>=0||cat.indexOf('杠杆')>=0){{
    if(cat.indexOf('2倍做多')>=0||cat.indexOf('2倍做空')>=0){{
      var dir=cat.indexOf('做多')>=0?'up':'down';
      var label=cat.replace('ETF','').replace('2倍','');
      return '<span class="tag-'+(dir==='up'?'r':'b')+'">'+cat+'</span>';
    }}
    return '<span class="tag-d">'+cat+'</span>';
  }}
  if(cat.indexOf('联接')>=0)return '<span class="tag-o">QDII联接</span>';
  if(cat.indexOf('理财通')>=0||cat.indexOf('跨境')>=0)return '<span class="tag-o">理财通</span>';
  if(cat.indexOf('港股通')>=0)return '<span class="tag-g">港股通</span>';
  if(cat.indexOf('债券')>=0)return '<span class="tag-d">债券</span>';
  if(cat.indexOf('货币')>=0||cat.indexOf('Money')>=0)return '<span class="tag-d">货币</span>';
  if(cat.indexOf('REITs')>=0)return '<span class="tag-g">REITs</span>';
  if(cat.indexOf('加密货币')>=0)return '<span class="tag-r">加密</span>';
  return '<span class="tag-d">'+cat+'</span>';
}}

function renderTable(){{
  var rows=ALL_PRODUCTS.filter(function(r){{
    if(r.region!==curMain)return false;
    if(curSub&&r.cat!==curSub)return false;
    if(curSearch){{
      var s=curSearch;
      if(r.name.toLowerCase().indexOf(s)===-1&&r.code.toLowerCase().indexOf(s)===-1&&r.cat.toLowerCase().indexOf(s)===-1)return false;
    }}
    return true;
  }});

  var si={{name:0,chg:5,last:3,turnover:7,premium:8}}[curSort];
  rows.sort(function(a,b){{
    var av=si!==undefined?Object.values(a)[si]:undefined;
    var bv=si!==undefined?Object.values(b)[si]:undefined;
    if(av===undefined||bv===undefined)return 0;
    if(typeof av==='string'){{av=av.toLowerCase();bv=(bv||'').toLowerCase();}}
    if(av<bv)return curDir==='asc'?1:-1;
    if(av>bv)return curDir==='asc'?-1:1;
    return 0;
  }});

  var thClass=function(s){{return 'th-sort'+(curSort===s?' '+curDir:'');}};
  document.getElementById('etfthead').innerHTML=
    '<tr>'+
    '<th class="'+thClass('name')+'" data-sort="name">产品</th>'+
    '<th>分类</th>'+
    '<th class="'+thClass('chg')+'" data-sort="chg">涨跌幅</th>'+
    '<th class="'+thClass('last')+'" data-sort="last">最新价</th>'+
    '<th class="'+thClass('turnover')+'" data-sort="turnover">成交额</th>'+
    '<th class="'+thClass('premium')+'" data-sort="premium">折溢价</th>'+
    '</tr>';
  var tbody='';
  rows.forEach(function(r){{
    var hasM=r.last>0;
    var pclass=r.up?'up':'down';
    var note=r.note;
    var noteTag=note?'<span class="tag-note" title="'+note+'">*</span>':'';
    var noteRow=note?'<div class="row-note">'+note+'</div>':'';
    var rowClass=hasM?'':'no-data';

    var prStr=hasM?'<b class="'+pclass+'">'+fmt(r.chg)+'%</b>':'<span class="no-mkt">暂无行情</span>';
    var lastStr=hasM?'<b class="'+pclass+'">'+r.last+'</b>':'-';
    var turnStr=hasM&&r.turnover?r.turnover:'-';
    var pm=r.premium;
    var pmStr=(pm||pm===0)&&pm!='-'?'<span class="'+(pm>=0?'down':'up')+'">'+fmt(pm)+'%</span>':'-';

    var onclick=hasM?"openM('"+r.code+"')":'';
    tbody+='<tr class="'+rowClass+'"'+(hasM?' onclick="'+onclick+'" style="cursor:pointer"':'')+'>'+
      '<td><div style="font-weight:700">'+r.name+noteTag+'</div><div style="font-size:10.5px;color:var(--dim);margin-top:2px">'+r.code+'</div>'+noteRow+'</td>'+
      '<td>'+tagCat(r.cat)+'<div style="font-size:10px;color:var(--dim);margin-top:2px;max-width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+r.index+'</div></td>'+
      '<td class="nm" style="font-size:14px">'+prStr+'</td>'+
      '<td class="nm">'+lastStr+'</td>'+
      '<td class="nm" style="color:var(--text2)">'+turnStr+'</td>'+
      '<td class="nm">'+pmStr+'</td>'+
      '</tr>';
  }});
  document.getElementById('etftbody').innerHTML=tbody;
  document.getElementById('prod-count').textContent=rows.length+'只';
  document.getElementById('searchCount').textContent=curSearch?'筛选'+rows.length+'只':'';
}}

// Sort click with stopPropagation
document.getElementById('etftbl').addEventListener('click',function(e){{
  e.stopPropagation();
  var th=e.target.closest('th');
  if(!th||!th.classList.contains('th-sort'))return;
  var s=th.dataset.sort;if(!s)return;
  if(s===curSort){{curDir=curDir==='desc'?'asc':'desc';}}else{{curSort=s;curDir='desc';}}
  renderTable();
}});

function openM(code){{
  var d=ALL_PRODUCTS.find(function(r){{return r.code===code;}});if(!d)return;
  var pclass=d.up?'up':'down',pmp=d.premium>=0?'down':'up';
  document.getElementById('mtitle').textContent=d.name+' ('+d.code+')';
  var html='<div class="mprice-row">'+
    '<div><div class="mnav '+pclass+'">'+(d.last>0?d.last:'-')+'</div><div class="mchg '+pclass+'">'+(d.last>0?fmt(d.chg)+'%':'-')+'</div></div>'+
    '<div class="mprice-block"><div style="font-size:11px;color:var(--dim)">昨收</div><div style="font-size:17px;font-weight:800">'+(d.prev>0?d.prev:'-')+'</div></div>'+
    '<div class="mprice-block"><div style="font-size:11px;color:var(--dim)">折溢价</div><div style="font-size:17px;font-weight:800 '+pmp+'">'+(d.premium||d.premium===0)?fmt(d.premium)+'%':'-'+'</div></div></div>'+
    '<div class="mmeta"><span>跟踪指数：'+(d.index||'暂无')+'</span>'+tagCat(d.cat)+'<span>'+d.region+'</span></div>';
  if(IDATA[code]){{html+='<div class="chart-wrap"><div class="chart-title">分时走势</div><canvas id="kchart"></canvas><div class="chart-legend"><span><span class="cline cline-p"></span>实时价格</span><span><span class="cline cline-v"></span>昨收参考</span></div></div>';}}
  if(HOLD[code]){{var h=HOLD[code];html+='<div class="hsec"><h4>前十大持仓</h4><div class="mtbl"><table><thead><tr><th>#</th><th>代码</th><th>名称</th><th>权重</th></tr></thead><tbody>';h.forEach(function(item,idx){{html+='<tr><td class="rank">'+(idx+1)+'</td><td style="color:var(--dim)">'+item[0]+'</td><td>'+item[1]+'</td><td><b>'+item[3].toFixed(2)+'%</b></td></tr>';}});html+='</tbody></table></div></div>';}}
  if(HOLIDAYS[code]){{html+='<div class="hsec"><h4>重要日期（202