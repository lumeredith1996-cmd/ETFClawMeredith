#!/usr/bin/env python3
"""Surgically edit etf-map-v5.html → etf-map-v6.html"""
import sys

with open('/root/.openclaw/workspace/etf-map-v5.html', 'r', encoding='utf-8') as f:
    c = f.read()

orig_len = len(c)
print(f"Original: {orig_len} chars")

# ─── 1. CSS: Replace chan-bar/chan-btn with fbar/fbtn + add fsub/fsub-item + edu-tbl ──
old_css = ".chan-bar{display:flex;gap:6px;margin-bottom:14px;flex-wrap:wrap}\n.chan-btn{padding:5px 13px;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid var(--border);color:var(--dim);background:var(--card);transition:.15s;white-space:nowrap}\n.chan-btn.ac,.chan-btn:hover{background:var(--orange);color:#fff;border-color:var(--orange)}"
new_css = """.fbar{display:flex;gap:5px;margin-bottom:8px;flex-wrap:wrap}
.fsub{display:flex;gap:4px;margin-bottom:14px;padding-left:4px;flex-wrap:wrap}
.fbtn{padding:5px 14px;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid var(--border);color:var(--dim);background:var(--card);transition:.15s;white-space:nowrap;user-select:none}
.fbtn.ac,.fbtn:hover{background:var(--orange);color:#fff;border-color:var(--orange)}
.fsub-item{padding:4px 11px;border-radius:6px;font-size:11px;font-weight:600;cursor:pointer;border:1px solid var(--border);color:var(--dim);background:var(--card);transition:.15s;user-select:none}
.fsub-item.ac,.fsub-item:hover{background:var(--blue);color:#fff;border-color:var(--blue)}"""

if old_css in c:
    c = c.replace(old_css, new_css, 1)
    print("1. CSS: OK")
else:
    print("1. CSS: FAILED - pattern not found")

# ─── 2. HTML: section title with id and prod-count ─────────────────────────────
old_sec = '<div class="sec-title">全部产品 <span class="sub">共88只ETF &middot; 点击表头排序 &middot; 点击行查看详情</span></div>'
new_sec = '<div class="sec-title" id="sec-title">全部产品 <span class="sub" id="prod-count"></span></div>'
if old_sec in c:
    c = c.replace(old_sec, new_sec, 1)
    print("2. Section title: OK")
else:
    print("2. Section title: FAILED")

# ─── 3. HTML: chan-bar → fbar ─────────────────────────────────────────────────
if 'id="chanbar"' in c:
    c = c.replace('id="chanbar"', 'id="fbar"', 1)
    print("3. chanbar→fbar: OK")
else:
    print("3. chanbar→fbar: FAILED")

# ─── 4. HTML: add fsub div after fbar ──────────────────────────────────────────
if '<div class="fbar" id="fbar"></div>' in c:
    c = c.replace('<div class="fbar" id="fbar"></div>', '<div class="fbar" id="fbar"></div>\n    <div class="fsub" id="fsub"></div>', 1)
    print("4. Add fsub: OK")
else:
    print("4. Add fsub: FAILED")

# ─── 5. HTML: add edu-section after table ──────────────────────────────────────
if '    </div>\n\n   <div class="pn" id="pn1">' in c:
    c = c.replace('    </div>\n\n   <div class="pn" id="pn1">', '    </div>\n    <div id="edu-section"></div>\n\n   <div class="pn" id="pn1">', 1)
    print("5. Add edu-section: OK")
else:
    print("5. Add edu-section: FAILED")

# ─── 6. HTML: replace table thead/tbody structure ──────────────────────────────
old_tbl = """      <table id="etftbl">
        <thead>
          <tr>
            <th class="th-sort" data-sort="name">产品 <span class="sort-icon"></span></th>
            <th class="th-sort" data-sort="region">地域 <span class="sort-icon"></span></th>
            <th class="th-sort" data-sort="cat">分类 <span class="sort-icon"></span></th>
            <th class="th-sort desc" data-sort="chg">涨跌幅 <span class="sort-icon"></span></th>
            <th class="th-sort" data-sort="last">最新价 <span class="sort-icon"></span></th>
            <th class="th-sort" data-sort="turnover">成交额 <span class="sort-icon"></span></th>
            <th class="th-sort" data-sort="premium">折溢价 <span class="sort-icon"></span></th>
            <th>跟踪指数</th>
            <th>联接基金（QDII）</th>
          </tr>
        </thead>
        <tbody id="etftbody">
        </tbody>
      </table>"""
new_tbl = """      <table id="etftbl">
        <thead id="etfthead">
        </thead>
        <tbody id="etftbody">
        </tbody>
      </table>"""
if old_tbl in c:
    c = c.replace(old_tbl, new_tbl, 1)
    print("6. Table structure: OK")
else:
    print("6. Table structure: FAILED")
    # Try to find the actual table start
    idx = c.find('id="etftbl"')
    if idx >= 0:
        print("  Found etftbl at:", repr(c[idx:idx+600]))

# ─── 7. CSS: add edu-tbl styles ────────────────────────────────────────────────
old_tbl_css = ".tbl{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.04);margin-bottom:18px}\n.tbl table{width:100%;border-collapse:collapse;font-size:12.5px}"
new_tbl_css = """.tbl{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.04);margin-bottom:18px}
.tbl table{width:100%;border-collapse:collapse;font-size:12.5px}
.edu-tbl{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,.04)}
.edu-tbl table{width:100%;border-collapse:collapse;font-size:11.5px}
.edu-tbl th{background:#fafbfc;padding:9px 12px;text-align:left;font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;font-weight:700;border-bottom:1px solid var(--border)}
.edu-tbl td{padding:9px 12px;border-bottom:1px solid #f5f5f5;vertical-align:top;line-height:1.65}
.edu-tbl tr:last-child td{border-bottom:none}"""
if old_tbl_css in c:
    c = c.replace(old_tbl_css, new_tbl_css, 1)
    print("7. edu-tbl CSS: OK")
else:
    print("7. edu-tbl CSS: FAILED")

# ─── 8. JS: Replace FILTERS + remove renderChanBar/setFilter ───────────────────
old_filters = "const FILTERS=['全部','内地可买','境外可买','QDII','港股通','5月入通','普通ETF','QDII联接基金','2倍做多','2倍做空'];"
new_filters = """// ─── Two-level filter system ──────────────────────────────────────────────────
var curMain='内地可买',curSub='QDII-ETF',curSort='chg',curDir='desc';

function renderFilters(){
  var mains=['内地可买','境外可买'];
  var barHtml=mains.map(function(m){return '<span class="fbtn'+(curMain===m?' ac':'')+'" data-m="'+m+'">'+m+'</span>';}).join('');
  document.getElementById('fbar').innerHTML=barHtml;
  var subs=curMain==='内地可买'?['QDII-ETF','QDII-联接基金','港股通','5月入通','跨境理财通']:['权益ETF','债券ETF','货币ETF','杠反ETF','其他ETF'];
  var subHtml=subs.map(function(s){return '<span class="fsub-item'+(curSub===s?' ac':'')+'" data-s="'+s+'">'+s+'</span>';}).join('');
  document.getElementById('fsub').innerHTML=subHtml;
  var secLbl=curMain==='内地可买'?'境内产品':'境外产品';
  document.getElementById('sec-title').innerHTML=secLbl+' <span class="sub" id="prod-count"></span>';
}
function setMain(m){curMain=m;curSub=curMain==='内地可买'?'QDII-ETF':'权益ETF';renderFilters();renderTable();}
function setSub(s){curSub=s;renderTable();}
document.getElementById('fbar').addEventListener('click',function(e){var b=e.target.closest('.fbtn');if(b)setMain(b.textContent.trim());});
document.getElementById('fsub').addEventListener('click',function(e){var b=e.target.closest('.fsub-item');if(b)setSub(b.textContent.trim());});"""

if old_filters in c:
    c = c.replace(old_filters, new_filters, 1)
    print("8. FILTERS: OK")
else:
    print("8. FILTERS: FAILED")

# Remove renderChanBar
old_rcb = "function renderChanBar(){document.getElementById('chanbar').innerHTML=FILTERS.map(f=>`<div class=\"chan-btn${f===curFilter?' ac':''}\" onclick=\"setFilter('${f}')}\">${f}</div>`).join('');}"
if old_rcb in c:
    c = c.replace(old_rcb, "")
    print("  renderChanBar removed: OK")
else:
    print("  renderChanBar removal: FAILED")

# Remove setFilter
if "function setFilter(f){curFilter=f;renderChanBar();renderETFTbl();}" in c:
    c = c.replace("function setFilter(f){curFilter=f;renderChanBar();renderETFTbl();}\n", "")
    print("  setFilter removed: OK")
else:
    print("  setFilter removal: FAILED")

# Remove curFilter init
if "let curFilter='全部',curSort='chg',curDir='desc';" in c:
    c = c.replace("let curFilter='全部',curSort='chg',curDir='desc';", "")
    print("  curFilter init removed: OK")
else:
    print("  curFilter init removal: FAILED")

# ─── 9. Replace renderETFTbl ──────────────────────────────────────────────────
old_ret = "function renderETFTbl(){\n  let rows=ALL_PRODUCTS.filter(r=>{\n    if(curFilter==='全部')return true;\n    if(curFilter==='内地可买')return r[2]==='内地';\n    if(curFilter==='境外可买')return r[2]==='境外';\n    if(curFilter==='QDII')return r[3]==='QDII';\n    if(curFilter==='港股通')return r[3]==='港股通';\n    if(curFilter==='5月入通')return r[3]==='5月入通';\n    if(curFilter==='普通ETF')return r[3]==='普通ETF';\n    if(curFilter==='2倍做多')return r[3]==='2倍做多';\n    if(curFilter==='2倍做空')return r[3]==='2倍做空';\n    if(curFilter==='QDII联接基金')return r[3]==='QDII'&&(r[1]==='513130.SH'||r[1]==='159687.SZ'||r[1]==='513730.SH');\n    return true;\n  }).sort((a,b)=>{\n    const FIELDS={name:0,region:2,cat:3,chg:6,last:5,up:8,turnover:9,premium:10};\n    const f=FIELDS[curSort]??0;\n    const av=a[f],bv=b[f];\n    if(typeof av==='string')return curDir==='desc'?av.localeCompare(bv):bv.localeCompare(av);\n    if(av<bv)return curDir==='asc'?1:-1;\n    if(av>bv)return curDir==='asc'?-1:1;\n    return 0;\n  });"

if old_ret in c:
    c = c.replace(old_ret, "function renderTable(){\n  var isMainland=curMain==='内地可买';\n  var rows=ALL_PRODUCTS.filter(function(r){\n    var cat=r[3];\n    if(isMainland){\n      if(curSub==='QDII-ETF')return cat==='QDII';\n      if(curSub==='QDII-联接基金')return cat==='QDII联接';\n      if(curSub==='港股通')return cat==='港股通';\n      if(curSub==='5月入通')return cat==='5月入通';\n      if(curSub==='跨境理财通')return cat==='跨境理财通';\n      return false;\n    }else{\n      return cat===curSub;\n    }\n  });\n  var si={name:0,chg:6,last:5,turnover:9,premium:10}[curSort];\n  rows.sort(function(a,b){\n    var av=si!==undefined?a[si]:undefined,bv=si!==undefined?b[si]:undefined;\n    if(av===undefined||bv===undefined)return 0;\n    if(typeof av==='string'){av=av.toLowerCase();bv=(bv||'').toLowerCase();}\n    if(av<bv)return curDir==='asc'?1:-1;\n    if(av>bv)return curDir==='asc'?-1:1;\n    return 0;\n  });", 1)
    print("9. renderETFTbl→renderTable: OK")
else:
    print("9. renderETFTbl→renderTable: FAILED")
    # Find what the actual renderETFTbl starts with
    idx = c.find('function renderETFTbl()')
    print(f"  renderETFTbl at: {idx}")
    print(f"  Content: {repr(c[idx:idx+300])}")

# ─── 10. Replace renderETFTbl body (table header generation) ───────────────────
old_th_gen = """  document.getElementById('etftbl').innerHTML=`
    <thead>
      <tr>
        <th class="th-sort ${curSort==='name'?'desc':''}" data-sort="name">产品 <span class="sort-icon"></span></th>
        <th class="th-sort ${curSort==='region'?'desc':''}" data-sort="region">地域 <span class="sort-icon"></span></th>
        <th class="th-sort ${curSort==='cat'?'desc':''}" data-sort="cat">分类 <span class="sort-icon"></span></th>
        <th class="th-sort ${curSort==='chg'?'desc':''}" data-sort="chg">涨跌幅 <span class="sort-icon"></span></th>
        <th class="th-sort ${curSort==='last'?'desc':''}" data-sort="last">最新价 <span class="sort-icon"></span></th>
        <th class="th-sort ${curSort==='turnover'?'desc':''}" data-sort="turnover">成交额 <span class="sort-icon"></span></th>
        <th class="th-sort ${curSort==='premium'?'desc':''}" data-sort="premium">折溢价 <span class="sort-icon"></span></th>
        <th>跟踪指数</th>
        <th>联接基金（QDII）</th>
      </tr>
    </thead>
    <tbody>
      ${rows.map((r,i)=>{
        const [name,code,region,cat,type,last,prev,chg,up,turnoverStr,premium,index,linkFund]=r;
        const pclass=up?'up':'dn';"""

if old_th_gen in c:
    c = c.replace(old_th_gen, """  var thClass=function(s){return 'th-sort'+(curSort===s?' '+curDir:'');};
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
  rows.forEach(function(r){
    var n=r[0],code=r[1],region=r[2],cat=r[3],type=r[4],last=r[5],prev=r[6],chg=r[7],up=r[8],turnoverStr=r[9],premium=r[10],index=r[11];
    var pclass=up?'up':'dn';
    var hasQ=last>0;
    var typeTag;
    if(type==='link'||type==2)typeTag='<span class="tag-o">联接</span>';
    else if(type==='wealth'||type==3)typeTag='<span class="tag-y">理财通</span>';
    else typeTag='<span class="tag-d">'+cat+'</span>';
    var prStr=hasQ?'<b class="'+pclass+'">'+fmt(chg)+'%</b>':'<span style="color:var(--dim)">-</span>';
    var lastStr=hasQ?'<b class="'+pclass+'">'+last+'</b>':'<span style="color:var(--dim)">-</span>';
    var turnStr=hasQ?turnoverStr:'<span style="color:var(--dim)">-</span>';
    var pmStr=(premium||premium===0)&&premium!='-'?'<span class="'+(premium>=0?'up':'dn')+'">'+fmt(premium)+'%</span>':'<span style="color:var(--dim)">-</span>';
    var rowStyle=hasQ?'cursor:pointer':'cursor:default;opacity:0.6';
    var oc=hasQ?"openM('"+code+"')":'';
    tbody+='<tr'+(hasQ?' onclick="'+oc+'"':'')+' style="'+rowStyle+'">'+
      '<td><div style="font-weight:700">'+n+'</div><div style="font-size:10.5px;color:var(--dim);margin-top:2px">'+code+'</div></td>'+
      '<td>'+typeTag+'</td>'+
      '<td class="nm" style="font-size:14px">'+prStr+'</td>'+
      '<td class="nm">'+lastStr+'</td>'+
      '<td class="nm" style="color:var(--text2)">'+turnStr+'</td>'+
      '<td class="nm">'+pmStr+'</td>'+
      '</tr>';
  });
  document.getElementById('etftbody').innerHTML=tbody;
  document.getElementById('prod-count').textContent=rows.length+'只产品';
  var edu='';
  if(curSub==='跨境理财通')edu=getEduTables();
  document.getElementById('edu-section').innerHTML=edu;
}
function getEduTables(){return'<div class="sec-title" style="margin-top:8px">跨境理财通科普</div>'+'<div class="edu-tbl"><table><thead><tr><th>渠道</th><th>基金设立地</th><th>可参与地区</th><th>投资者类型</th><th>参与门槛</th><th>资金投向</th><th>额度限制</th></tr></thead><tbody>'+'<tr><td style="font-weight:700">QDII</td><td>境内</td><td>全国</td><td>个人+机构</td><td>低</td><td>境外股票和债券市场</td><td>总额度1677.89亿美元，审批放缓</td></tr>'+'<tr><td style="font-weight:700">QDLP</td><td>境外机构境内试点设立</td><td>全国</td><td>个人合格投资者+机构</td><td>高</td><td>境外股票和债券市场，包括一级市场</td><td>各试点合计或超600亿美元</td></tr>'+'<tr><td style="font-weight:700">TRS</td><td>-</td><td>全国</td><td>个人合格投资者+机构</td><td>高</td><td>挂钩境外资产现货期货</td><td>额度未披露</td></tr>'+'<tr><td style="font-weight:700">跨境理财通（南向通）</td><td>港澳</td><td>粤港澳大湾区</td><td>个人（满足资产或收入要求）</td><td>中高</td><td>境外存款、债券、投资于大中华市场的基金</td><td>总额度1500亿元人民币</td></tr>'+'<tr><td style="font-weight:700">香港互认基金</td><td>香港</td><td>全国</td><td>个人+机构</td><td>低</td><td>境外股票和债券市场，以全球、亚太为主</td><td>总额度3000亿元人民币，近期获政策增量额度支持</td></tr>'+'</tbody></table></div>'+'<div class="edu-tbl"><table><thead><tr><th>方式</th><th>投资范围</th><th>额度限制</th><th>汇率风险</th></tr></thead><tbody>'+'<tr><td style="font-weight:700">QDII基金</td><td>投资范围广，不局限于港股通标的，可参与港股打新，同时可投资于境外市场</td><td>受基金公司获配的外汇额度限制；多数除QDII外也可通过港股通投资港股</td><td>有</td></tr>'+'<tr><td style="font-weight:700">港股通基金</td><td>仅限于港股通标的</td><td>港股通南向每日额度为每个市场人民币420亿</td><td>有</td></tr>'+'<tr><td style="font-weight:700">互认基金</td><td>投资范围广，跨区域、跨资产，多以亚太地区为主</td><td>内地与香港公募基金互认投资额度为资金净汇出各3000亿元人民币；在内地销售规模占基金总资产比例不得高于50%</td><td>部分产品设有对冲份额</td></tr>'+'<tr><td style="font-weight:700">互联互通ETF</td><td>跟踪标的指数，可包含非港股通标的</td><td>港股通南向每日额度为每个市场人民币420亿元</td><td>有</td></tr>'+'</tbody></table></div>'+'<div style="font-size:10.5px;color:var(--dim);text-align:right;padding:4px 0 8px">数据来源：中信建投证券 / 公开资料整理</div>';}""", 1)
    print("10. Table body replacement: OK")
else:
    print("10. Table body replacement: FAILED")
    # Find the actual pattern
    idx = c.find("document.getElementById('etftbl').innerHTML=")
    if idx >= 0:
        print(f"  Found innerHTML at {idx}")
        print(repr(c[idx:idx+400]))

# ─── 11. Replace sort handler ──────────────────────────────────────────────────
old_sort = "document.getElementById('etftbl').querySelector('thead').addEventListener('click',e=>{e.stopPropagation();if(e.target.closest('.th-sort')){const th=e.target.closest('.th-sort');const s=th.dataset.sort;curDir=(s===curSort&&curDir==='desc')?'asc':'desc';curSort=s;renderETFTbl();}});"
new_sort = "document.getElementById('etftbl').addEventListener('click',function(e){var th=e.target.closest('th');if(!th||!th.classList.contains('th-sort'))return;var s=th.dataset.sort;if(!s)return;if(s===curSort){curDir=curDir==='desc'?'asc':'desc';}else{curSort=s;curDir='desc';}renderTable();});"
if old_sort in c:
    c = c.replace(old_sort, new_sort, 1)
    print("11. Sort handler: OK")
else:
    print("11. Sort handler: FAILED")

# ─── 12. Replace renderChanBar() call ──────────────────────────────────────────
if 'renderChanBar();' in c:
    c = c.replace('renderChanBar();', 'renderFilters();', 1)
    print("12. renderChanBar→renderFilters: OK")
else:
    print("12. renderChanBar→renderFilters: FAILED")

# ─── 13. Replace renderETFTbl() call ───────────────────────────────────────────
# Count occurrences
cnt = c.count('renderETFTbl()')
print(f"  renderETFTbl() occurrences: {cnt}")
if cnt > 0:
    c = c.replace('renderETFTbl()', 'renderTable()')
    print("13. renderETFTbl→renderTable (all): OK")
else:
    print("13. renderETFTbl→renderTable: FAILED")

# ─── 14. Add 跨境理财通 products to ALL_PRODUCTS ──────────────────────────────
old_arr_end = "  ['2倍做空恒生','07500.HK','境外','2倍做空','hk',1.714,1.726,-0.7,false,'2.3亿',0.0,'2倍做空恒生']\n];const HOLD={"
new_arr_end = """  ['2倍做空恒生','07500.HK','境外','2倍做空','hk',1.714,1.726,-0.7,false,'2.3亿',0.0,'2倍做空恒生']
  // 跨境理财通（南向通）
  ,['南方东英纳斯达克100ETF','N1005','内地','跨境理财通','wealth',0,0,0,false,'-','-','纳斯达克100指数']
  ,['南方东英日经225指数ETF','N1002','内地','跨境理财通','wealth',0,0,0,false,'-','-','日经225指数']
  ,['南方东英恒生科技指数ETF','N1077','内地','跨境理财通','wealth',0,0,0,false,'-','-','恒生科技指数']
  ,['南方东英港元货币市场ETF','N1048','内地','跨境理财通','wealth',0,0,0,false,'-','-','港元货币市场指数']
  ,['南方东英美元货币市场ETF','KO5038','内地','跨境理财通','wealth',0,0,0,false,'-','-','美元货币市场指数']
  ,['南方东英人民币货币市场ETF','N1059','内地','跨境理财通','wealth',0,0,0,false,'-','-','人民币货币市场指数']
  ,['南方东英美国国债20年+指数ETF','KO9810','内地','跨境理财通','wealth',0,0,0,false,'-','-','美国国债20年+指数']
  ,['南方东英精选美元债券基金','HKO000225927','内地','跨境理财通','wealth',0,0,0,false,'-','-','精选美元债券(美元)']
  ,['南方东英精选港元债券基金','HK0000225901','内地','跨境理财通','wealth',0,0,0,false,'-','-','精选港元债券(港元)']
  ,['南方东英精选人民币债券基金','HKO000225919','内地','跨境理财通','wealth',0,0,0,false,'-','-','精选人民币债券(人民币)']
];const HOLD={"""

if old_arr_end in c:
    c = c.replace(old_arr_end, new_arr_end, 1)
    print("14. Add 跨境理财通 products: OK")
else:
    print("14. Add 跨境理财通 products: FAILED")
    # Try to find the actual ending
    idx = c.find("['2倍做空恒生','07500.HK'")
    if idx >= 0:
        print(f"  Found at {idx}")
        print(repr(c[idx:idx+200]))

# ─── 15. Fix openM to use find (compatible with both string and numeric type) ──
# Replace the openM line that uses .find() - it already uses filter/find so should be fine
# Just need to update it to not use template literal

# Write result
with open('/root/.openclaw/workspace/etf-map-v6.html', 'w', encoding='utf-8') as f:
    f.write(c)

print(f"\nFinal: {len(c)} chars (delta: {len(c)-orig_len:+d})")
