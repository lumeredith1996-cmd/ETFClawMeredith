#!/usr/bin/env python3
"""Build etf-map-v7.html"""
import json

d = json.load(open('/tmp/v7_data.json'))
P = d['products']
HOLD = d['HOLD']
HOLIDAYS = d['HOLIDAYS']
IDATA = d['IDATA']
REPORTS = d['REPORTS']
FLOW_IN = d['FLOW_IN']
FLOW_OUT = d['FLOW_OUT']
HK_FLOW = d['HK_FLOW']
HSI = d['HSI']
MT = d['mkt_temp']
MV = d['mkt_val']
MS = d['mkt_sent']
MD = d['mkt_desc']

AP = json.dumps(P, ensure_ascii=False)
HD = json.dumps(HOLD, ensure_ascii=False)
HD2 = json.dumps(HOLIDAYS, ensure_ascii=False)
ID = json.dumps(IDATA, ensure_ascii=False)
RP = json.dumps(REPORTS, ensure_ascii=False)
FI = json.dumps(FLOW_IN, ensure_ascii=False)
FO = json.dumps(FLOW_OUT, ensure_ascii=False)
KF = json.dumps(HK_FLOW, ensure_ascii=False)
HS = json.dumps(HSI, ensure_ascii=False)

CSS = """
:root{--bg:#f5f6fa;--card:#fff;--card2:#f0f2f8;--border:#e2e5ef;--text:#1a1d2e;--text2:#6b7280;--dim:#9ca3af;--red:#dc2626;--green:#16a34a;--orange:#ea580c;--blue:#2563eb;--gold:#d97706;}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"PingFang SC","Microsoft YaHei",-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
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
@media(max-width:768px){.header,.tabs{padding:0 14px}.mn{padding:14px}.tbl{overflow-x:auto}.tbl table{min-width:900px}.flow-2col{grid-template-columns:1fr}}}
""".strip()

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

var curMain='内地可买',curSub='QDII-ETF',curSort='chg',curDir='desc',curSearch='';

function renderFilters(){{
  var mains=['内地可买','境外可买'];
  document.getElementById('fbar').innerHTML=mains.map(function(m){{
    return '<span class="fbtn'+(curMain===m?' ac':'')+'" data-m="'+m+'">'+m+'</span>';
  }}).join('');
  var subs=curMain==='内地可买'
    ?['QDII-ETF','QDII-联接基金','港股通','5月入通','跨境理财通']
    :['权益ETF','债券ETF','货币ETF','杠反ETF','其他ETF'];
  document.getElementById('fsub').innerHTML=subs.map(function(s){{
    return '<span class="fsub-item'+(curSub===s?' ac':'')+'" data-s="'+s+'">'+s+'</span>';
  }}).join('');
  document.getElementById('sec-title').innerHTML=(curMain==='内地可买'?'境内产品':'境外产品')+' <span class="sub" id="prod-count"></span>';
}}
function setMain(m){{curMain=m;curSub=curMain==='内地可买'?'QDII-ETF':'权益ETF';renderFilters();renderTable();}}
function setSub(s){{curSub=s;renderTable();}}
document.getElementById('fbar').addEventListener('click',function(e){{var b=e.target.closest('.fbtn');if(b)setMain(b.textContent.trim());}});
document.getElementById('fsub').addEventListener('click',function(e){{var b=e.target.closest('.fsub-item');if(b)setSub(b.textContent.trim());}});
function sw(i){{document.querySelectorAll('.ta').forEach(function(t,j){{t.classList.toggle('ac',j===i);}});document.querySelectorAll('.pn').forEach(function(p,j){{p.classList.toggle('ac',j===i);}});}}
function cm(){{document.getElementById('modal').classList.remove('open');}}
function sf(d){{document.getElementById('ftabin').classList.toggle('ac',d==='in');document.getElementById('ftabout').classList.toggle('ac',d==='out');document.getElementById('finsec').classList.toggle('ac',d==='in');document.getElementById('foutsec').classList.toggle('ac',d==='out');}}
function fmt(v){{try{{var n=parseFloat(v);return isNaN(n)?v:(n>=0?'+':'')+n.toFixed(2);}}catch(e){{return v;}}}}

function onSearch(v){{curSearch=v.toLowerCase();renderTable();}}

function renderTable(){{
  var isMainland=curMain==='内地可买';
  var rows=ALL_PRODUCTS.filter(function(r){{
    var region=r.region,cat=r.cat,type=r.type;
    var isHK=type==='hk';
    if(isMainland){{
      if(curSub==='QDII-ETF')return cat==='QDII';
      if(curSub==='QDII-联接基金')return cat==='QDII联接';
      if(curSub==='港股通')return cat==='港股通';
      if(curSub==='5月入通')return cat==='5月入通';
      if(curSub==='跨境理财通')return cat==='跨境理财通';
      return false;
    }}else{{
      if(curSub==='权益ETF')return isHK&&(cat==='普通ETF'||cat==='权益ETF');
      if(curSub==='债券ETF')return isHK&&(cat==='债券ETF'||cat==='美国国债'||cat.indexOf('债券')===0);
      if(curSub==='货币ETF')return isHK&&(cat==='货币ETF');
      if(curSub==='杠反ETF')return cat.indexOf('2倍做')===0;
      if(curSub==='其他ETF')return isHK&&cat.indexOf('2倍做')!==0&&cat!=='普通ETF'&&cat!=='权益ETF';
      return false;
    }}
  }});
  
  // Search filter
  if(curSearch){{
    rows=rows.filter(function(r){{
      return r.name.toLowerCase().indexOf(curSearch)!==-1||r.code.toLowerCase().indexOf(curSearch)!==-1;
    }});
  }}

  var si={{name:0,chg:6,last:5,turnover:9,premium:10}}[curSort];
  rows.sort(function(a,b){{
    var av=si!==undefined?a[si]:undefined,bv=si!==undefined?b[si]:undefined;
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
    var n=r.name,code=r.code,cat=r.cat,type=r.type,last=r.last,chg=r.chg,up=r.up,turnover=r.turnover,premium=r.premium,index=r.index,note=r.note;
    var pclass=up?'up':'down';
    var hasQ=last>0;
    var isHK=type==='hk';
    var typeTag;
    if(type==='link'||type==='qdii-link')typeTag='<span class="tag-o">联接</span>';
    else if(type==='wealth'||type==='wealth-link')typeTag='<span class="tag-o">理财通</span>';
    else if(isHK){{
      if(cat.indexOf('2倍做')===0)typeTag='<span class="tag-d">'+cat.replace('2倍做','2x')+'</span>';
      else if(cat.indexOf('债券')>=0||cat==='美国国债')typeTag='<span class="tag-d">债券ETF</span>';
      else if(cat==='货币ETF')typeTag='<span class="tag-d">货币ETF</span>';
      else typeTag='<span class="tag-d">权益ETF</span>';
    }}else typeTag='<span class="tag-d">'+cat+'</span>';

    var prStr=hasQ?'<b class="'+pclass+'">'+fmt(chg)+'%</b>':'<span style="color:var(--dim)">-</span>';
    var lastStr=hasQ?'<b class="'+pclass+'">'+last+'</b>':'<span style="color:var(--dim)">-</span>';
    var turnStr=hasQ?turnover:'<span style="color:var(--dim)">-</span>';
    var pmStr=(premium||premium===0)&&premium!='-'?'<span class="'+(premium>=0?'down':'up')+'">'+fmt(premium)+'%</span>':'<span style="color:var(--dim)">-</span>';
    var noteTag=note?'<span class="tag-note" title="'+note+'">备注</span>':'';
    var noteRow=note?'<div class="row-note">'+note+'</div>':'';
    var rowStyle=hasQ?'cursor:pointer':'cursor:default;opacity:0.6';
    var oc=hasQ?"openM('"+code+"')":'';
    tbody+='<tr'+(hasQ?' onclick="'+oc+'"':'')+' style="'+rowStyle+'">'+
      '<td><div style="font-weight:700">'+n+noteTag+'</div><div style="font-size:10.5px;color:var(--dim);margin-top:2px">'+code+'</div>'+noteRow+'</td>'+
      '<td>'+typeTag+'</td>'+
      '<td class="nm" style="font-size:14px">'+prStr+'</td>'+
      '<td class="nm">'+lastStr+'</td>'+
      '<td class="nm" style="color:var(--text2)">'+turnStr+'</td>'+
      '<td class="nm">'+pmStr+'</td>'+
      '</tr>';
  }});
  document.getElementById('etftbody').innerHTML=tbody;
  document.getElementById('prod-count').textContent=rows.length+'只产品';
  document.getElementById('searchCount').textContent=curSearch?'筛选'+rows.length+'只':'';
  var edu='';
  if(curSub==='跨境理财通')edu=getEduTables();
  document.getElementById('edu-section').innerHTML=edu;
}}

function getEduTables(){{
  return '<div class="sec-title" style="margin-top:8px">跨境理财通科普</div>'+
    '<div class="edu-tbl"><table><thead><tr><th>渠道</th><th>基金设立地</th><th>可参与地区</th><th>投资者类型</th><th>参与门槛</th><th>资金投向</th><th>额度限制</th></tr></thead><tbody>'+
    '<tr><td style="font-weight:700">QDII</td><td>境内</td><td>全国</td><td>个人+机构</td><td>低</td><td>境外股票和债券市场</td><td>总额度1677.89亿美元，审批放缓</td></tr>'+
    '<tr><td style="font-weight:700">QDLP</td><td>境外机构境内试点设立</td><td>全国</td><td>个人合格投资者+机构</td><td>高</td><td>境外股票和债券市场，包括一级市场</td><td>各试点合计或超600亿美元</td></tr>'+
    '<tr><td style="font-weight:700">TRS</td><td>-</td><td>全国</td><td>个人合格投资者+机构</td><td>高</td><td>挂钩境外资产现货期货</td><td>额度未披露</td></tr>'+
    '<tr><td style="font-weight:700">跨境理财通（南向通）</td><td>港澳</td><td>粤港澳大湾区</td><td>个人（满足资产或收入要求）</td><td>中高</td><td>境外存款、债券、投资于大中华市场的基金</td><td>总额度1500亿元人民币</td></tr>'+
    '<tr><td style="font-weight:700">香港互认基金</td><td>香港</td><td>全国</td><td>个人+机构</td><td>低</td><td>境外股票和债券市场，以全球、亚太为主</td><td>总额度3000亿元人民币，近期获政策增量额度支持</td></tr>'+
    '</tbody></table></div>'+
    '<div class="edu-tbl"><table><thead><tr><th>方式</th><th>投资范围</th><th>额度限制</th><th>汇率风险</th></tr></thead><tbody>'+
    '<tr><td style="font-weight:700">QDII基金</td><td>投资范围广，不局限于港股通标的，可参与港股打新，同时可投资于境外市场</td><td>受基金公司获配的外汇额度限制；多数除QDII外也可通过港股通投资港股</td><td>有</td></tr>'+
    '<tr><td style="font-weight:700">港股通基金</td><td>仅限于港股通标的</td><td>港股通南向每日额度为每个市场人民币420亿</td><td>有</td></tr>'+
    '<tr><td style="font-weight:700">互认基金</td><td>投资范围广，跨区域、跨资产，多以亚太地区为主</td><td>内地与香港公募基金互认投资额度为资金净汇出各3000亿元人民币；在内地销售规模占基金总资产比例不得高于50%</td><td>部分产品设有对冲份额</td></tr>'+
    '<tr><td style="font-weight:700">互联互通ETF</td><td>跟踪标的指数，可包含非港股通标的</td><td>港股通南向每日额度为每个市场人民币420亿元</td><td>有</td></tr>'+
    '</tbody></table></div>'+
    '<div style="font-size:10.5px;color:var(--dim);text-align:right;padding:4px 0 8px">数据来源：中信建投证券 / 公开资料整理</div>';
}}

// SORT: stopPropagation fix
document.getElementById('etftbl').addEventListener('click',function(e){{
  e.stopPropagation(); // FIX: prevent row onclick from firing
  var th=e.target.closest('th');
  if(!th||!th.classList.contains('th-sort'))return;
  var s=th.dataset.sort;if(!s)return;
  if(s===curSort){{curDir=curDir==='desc'?'asc':'desc';}}else{{curSort=s;curDir='desc';}}
  renderTable();
}});

function openM(code){{
  var d=ALL_PRODUCTS.find(function(r){{return r.code===code;}});if(!d)return;
  var name=d.name,cat=d.cat,last=d.last,prev=d.prev,chg=d.chg,up=d.up,premium=d.premium,index=d.index;
  var pclass=up?'up':'down',pmp=premium>=0?'down':'up';
  document.getElementById('mtitle').textContent=name+' ('+code+')';
  var html='<div class="mprice-row">'+
    '<div><div class="mnav '+pclass+'">'+(last>0?last:'-')+'</div><div class="mchg '+pclass+'">'+(last>0?fmt(chg)+'%':'-')+'</div></div>'+
    '<div class="mprice-block"><div style="font-size:11px;color:var(--dim)">昨收</div><div style="font-size:17px;font-weight:800">'+(prev>0?prev:'-')+'</div></div>'+
    '<div class="mprice-block"><div style="font-size:11px;color:var(--dim)">折溢价</div><div style="font-size:17px;font-weight:800 '+pmp+'">'+(premium||premium===0)?fmt(premium)+'%':'-'+'</div></div></div>'+
    '<div class="mmeta"><span>跟踪指数：'+(index||'暂无')+'</span><span class="tag-d">'+cat+'</span></div>';
  if(IDATA[code]){{html+='<div class="chart-wrap"><div class="chart-title">分时走势 vs 昨收参考线</div><canvas id="kchart"></canvas><div class="chart-legend"><span><span class="cline cline-p"></span>实时价格</span><span><span class="cline cline-v"></span>昨收参考</span