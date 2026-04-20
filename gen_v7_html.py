#!/usr/bin/env python3
"""Generate etf-map-v7.html - complete rebuild"""
import re, json

code = open('/root/.openclaw/workspace/etf-map-v6.html').read()

def parse_deep_array(block, item_pat_inner):
    result = {}; i = 0; n = len(block)
    while i < n:
        km = re.search(r"'([^']+)':\s*", block[i:])
        if not km: break
        key = km.group(1); i += km.end(); depth = 0; start = None
        for j, c in enumerate(block[i:], i):
            if c == '[':
                if depth == 0: start = j; depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0 and start is not None:
                    inner = block[start:j+1]
                    items = re.findall(item_pat_inner, inner)
                    if items: result[key] = [[a, float(b), float(c)] for a, b, c in items]
                    i = j + 1; break
        i += 1
    return result

def parse_hold_array(block):
    result = {}; i = 0; n = len(block)
    while i < n:
        km = re.search(r"'([^']+)':\s*", block[i:])
        if not km: break
        key = km.group(1); i += km.end(); depth = 0; start = None
        for j, c in enumerate(block[i:], i):
            if c == '[':
                if depth == 0: start = j; depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0 and start is not None:
                    inner = block[start:j+1]
                    items = re.findall(r"'([^']*)','([^']*)','([^']*)',([\d.]+)", inner)
                    if items: result[key] = [[a, b, c, float(d)] for a, b, c, d in items]
                    i = j + 1; break
        i += 1
    return result

def parse_str_array(block):
    result = {}; i = 0; n = len(block)
    while i < n:
        km = re.search(r"'([^']+)':\s*", block[i:])
        if not km: break
        key = km.group(1); i += km.end(); depth = 0; start = None
        for j, c in enumerate(block[i:], i):
            if c == '[':
                if depth == 0: start = j; depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0 and start is not None:
                    inner = block[start:j+1]
                    result[key] = re.findall(r"'([^']*)'", inner)
                    i = j + 1; break
        i += 1
    return result

# PRODUCTS
arr_start = code.find('const ALL_PRODUCTS=[') + len('const ALL_PRODUCTS=')
arr_end = code.find('];const HOLD', arr_start)
prod_block = code[arr_start:arr_end+1]
pattern = re.findall(r"\['([^']+)','([^']+)','([^']+)','([^']+)','([^']+)',([\d.]+),([\d.]+),(-?[\d.]+),(true|false),'([^']*)',(-?[\d.]+|'[^']*'),'([^']*)'\]", prod_block)
NOTES = {
    '513130.SH':'T+0申赎，QDII额度紧张，关注溢价风险',
    '159687.SZ':'亚太低碳精选，台湾+韩国+东南亚分散配置',
    '513730.SH':'新交所泛东南亚科技指数，印度+新加坡+印尼上市龙头',
    '159822.SZ':'新经济主题，中概科技+电商+生物医药',
    '159329.SZ':'沙特阿美+金融为主，油价与汇率双敏感',
    '520830.SH':'费率较低，与159329同为沙特ETF',
    '03441.HK':'东西股票精选，港+A股+美股ADR离岸上市',
    '03442.HK':'恒生港美科技指数，腾讯/阿里/亚马逊/英伟达',
    '03174.HK':'恒生生物科技指数，CXO/创新药为主',
    '03443.HK':'香港股票指数，港铁/友邦/汇丰等本地股',
    '03469.HK':'高股息策略，港股通红利主题',
    '02830.HK':'沙特主权基金持仓，油价+利差双敏感',
    '03454.HK':'美股七巨头指数，苹果/微软/英伟达/谷歌/Meta/亚马逊',
    '03153.HK':'日经225指数，东京证券交易所上市',
    '03147.HK':'中国创业板，A股科技成长风格',
    '03134.HK':'中证太阳能指数，A股光伏产业链',
    '03133.HK':'沪深300，A股大盘蓝筹',
    '03109.HK':'科创板50，科创板核心资产',
    '03101.HK':'中证A500，A股中盘+大盘均衡配置',
    '03034.HK':'纳斯达克100，美股科技旗舰指数',
    '03033.HK':'恒生科技指数，港股科技旗舰',
    '03004.HK':'富时越南30指数，胡志明交易所上市',
    '02822.HK':'富时中国A50，A股大盘蓝筹',
    '03068.HK':'以太币期货，合约展期成本注意',
    '03066.HK':'比特币期货，高波动加密货币',
    '03433.HK':'美国国债20年+，美债长端利率敏感',
    '03199.HK':'富时中国国债，人民币债券配置',
    '09096.HK':'美元货币市场，稳定收益美元资产管理',
    '03096.HK':'美元货币市场（子份额），美元现金管理',
    '03122.HK':'人民币货币ETF，人民币现金管理',
    '03053.HK':'港元货币ETF，港元储蓄替代',
    '03447.HK':'亚太房地产信托，租金收益型',
    '02802.HK':'国指备兑认购期权，机构衍生品策略',
    '03167.HK':'中证500指数，A股中盘代表',
    '03193.HK':'中证5G指数，A股通信设备',
    '03005.HK':'中证500，A股中盘均衡',
    '03003.HK':'MSCI中国A50，A股大盘+港股配置',
    '03431.HK':'港韩科技，港股+韩国科技股',
    '03432.HK':'港股通精选，港股通核心标的',
    '03037.HK':'恒生指数，港股大盘基准',
    '09167.HK':'工银标普中国，标普中国指数QDII',
}
products = []
for p in pattern:
    products.append({'name':p[0],'code':p[1],'region':p[2],'cat':p[3],'type':p[4],
          'last':float(p[5]),'prev':float(p[6]),'chg':float(p[7]),'up':p[8]=='true',
          'turnover':p[9],'premium':float(p[10]) if p[10].replace('.','').replace('-','').isdigit() else 0,
          'index':p[11],'note':NOTES.get(p[1],'')})

# OTHER DATA
h_s = code.find("const HOLD={") + len("const HOLD={")
HOLD = parse_hold_array(code[h_s:code.find("};const HOLIDAYS", h_s)])
hd_s = code.find("const HOLIDAYS={") + len("const HOLIDAYS={")
HOLIDAYS = parse_str_array(code[hd_s:code.find("};const IDATA", hd_s)])
id_s = code.find("const IDATA={") + len("const IDATA={")
IDATA = parse_deep_array(code[id_s:code.find("};const REPORTS", id_s)], r'"([^"]+)",\s*([-\d.]+),\s*([-\d.]+)\]')
fi_s = code.find("const FLOW_IN=[") + len("const FLOW_IN=[")
FLOW_IN = re.findall(r"\['([^']*)','([^']*)','([^']*)'\]", code[fi_s:code.find("];const FLOW_OUT", fi_s)])
fo_s = code.find("const FLOW_OUT=[") + len("const FLOW_OUT=[")
FLOW_OUT = re.findall(r"\['([^']*)','([^']*)','([^']*)'\]", code[fo_s:code.find("];// ───", fo_s)])
hsi_s = code.find("var HSI_INTRADAY=") + len("var HSI_INTRADAY=")
hsi_idx = code.find("MARKET_TEMP", hsi_s)
hsi_last2 = code.rfind("]]", hsi_s, hsi_idx)
raw_hsi = code[hsi_s:hsi_s+hsi_last2+2]
HSI = [[a,float(b),float(c)] for a,b,c in re.findall(r'"([^"]+)",\s*([-\d.]+),\s*([-\d.]+)\]', raw_hsi)]
hkf_s = code.find("var HK_FLOW_DATA=") + len("var HK_FLOW_DATA=")
hkf_idx = code.find("MARKET_VAL", hkf_s)
hkf_last2 = code.rfind("]]", hkf_s, hkf_idx)
raw_hkf = code[hkf_s:hkf_s+hkf_last2+2]
HK_FLOW = [[a,b,int(c)] for a,b,c in re.findall(r'\["([^"]+)",\s*"([^"]+)",\s*(-?\d+)\]', raw_hkf)]
rep_s = code.find("const REPORTS=[")
rep_e = code.find("];const FLOW_IN", rep_s)
REPORTS = re.findall(r"\{title:'([^']*)',date:'([^']*)',market:'([^']*)',sentiment:'([^']*)',tag1:'([^']*)',tag2:'([^']*)',tag3:'([^']*)',summary:'([^']*)'\}",code[rep_s:rep_e])
mkt_temp = int(re.search(r"var MARKET_TEMP=(\d+)", code).group(1))
mkt_val = int(re.search(r"var MARKET_VAL=(\d+)", code).group(1))
mkt_sent = int(re.search(r"var MARKET_SENT=(\d+)", code).group(1))
mkt_desc = re.search(r"var MARKET_DESC='([^']*)'", code).group(1)

# Serialize JSON
ALL_PRODUCTS_JSON = json.dumps(products, ensure_ascii=False)
HOLD_JSON = json.dumps(HOLD, ensure_ascii=False)
HOLIDAYS_JSON = json.dumps(HOLIDAYS, ensure_ascii=False)
IDATA_JSON = json.dumps(IDATA, ensure_ascii=False)
REPORTS_JSON = json.dumps(REPORTS, ensure_ascii=False)
FLOW_IN_JSON = json.dumps(FLOW_IN, ensure_ascii=False)
FLOW_OUT_JSON = json.dumps(FLOW_OUT, ensure_ascii=False)
HK_FLOW_JSON = json.dumps(HK_FLOW, ensure_ascii=False)
HSI_JSON = json.dumps(HSI, ensure_ascii=False)

print(f"Data: {len(products)} products, HSI={len(HSI)} points, HK_FLOW={len(HK_FLOW)}, HOLD={len(HOLD)}")

# Build HTML
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全球ETF投资地图</title>
<style>
:root{{--bg:#f5f6fa;--card:#fff;--card2:#f0f2f8;--border:#e2e5ef;--text:#1a1d2e;--text2:#6b7280;--dim:#9ca3af;--red:#dc2626;--green:#16a34a;--orange:#ea580c;--blue:#2563eb;--gold:#d97706;}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:"PingFang SC","Microsoft YaHei",-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}}
.header{{background:var(--card);border-bottom:2px solid var(--border);padding:0 32px;display:flex;justify-content:space-between;align-items:center;height:58px;position:sticky;top:0;z-index:100}}
.logo{{font-size:16px;font-weight:800;display:flex;align-items:center;gap:8px}}
.logo .beta{{background:var(--orange);color:#fff;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px}}
.hdr-right{{display:flex;align-items:center;gap:14px}}
.upd{{font-size:12px;color:var(--dim)}}
.lt{{width:8px;height:8px;border-radius:50%;background:var(--green);animation:pl 2s infinite}}
@keyframes pl{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.live{{font-size:12px;color:var(--dim);display:flex;align-items:center;gap:5px}}
.tabs{{background:var(--card);padding:0 32px;display:flex;border-bottom:1px solid var(--border)}}
.ta{{padding:12px 22px;font-size:14px;color:var(--dim);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px;font-weight:600;transition:.15s}}
.ta:hover{{color:var(--orange)}}
.ta.ac{{color:var(--orange);border-bottom-color:var(--orange)}}
.mn{{padding:20px 32px;max-width:1280px;margin:0 auto}}
.pn{{display:none}}.pn.ac{{display:block}}
.sec-title{{font-size:14px;font-weight:800;color:var(--text);margin-bottom:12px;padding-left:10px;border-left:4px solid var(--orange);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}}
.sec-title .sub{{font-size:12px;color:var(--dim);font-weight:400}}
.info-box{{background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;padding:11px 14px;font-size:12px;color:#92400e;margin-bottom:16px;line-height:1.65}}
.fbar{{display:flex;gap:5px;margin-bottom:8px;flex-wrap:wrap}}
.fsub{{display:flex;gap:4px;margin-bottom:12px;padding-left:4px;flex-wrap:wrap}}
.fbtn{{padding:5px 14px;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid var(--border);color:var(--dim);background:var(--card);transition:.15s;white-space:nowrap;user-select:none}}
.fbtn.ac,.fbtn:hover{{background:var(--orange);color:#fff;border-color:var(--orange)}}
.fsub-item{{padding:4px 11px;border-radius:6px;font-size:11px;font-weight:600;cursor:pointer;border:1px solid var(--border);color:var(--dim);background:var(--card);transition:.15s;user-select:none}}
.fsub-item.ac,.fsub-item:hover{{background:var(--blue);color:#fff;border-color:var(--blue)}}
.search-box{{margin-bottom:12px;display:flex;align-items:center;gap:10px}}
.search-in{{flex:1;max-width:300px;padding:7px 12px;border:1px solid var(--border);border-radius:8px;font-size:13px;background:var(--card);color:var(--text);outline:none;transition:border-color .15s}}
.search-in:focus{{border-color:var(--orange)}}
.search-in::placeholder{{color:var(--dim)}}
.search-count{{font-size:11px;color:var(--dim)}}
.tbl{{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.04);margin-bottom:18px}}
.tbl table{{width:100%;border-collapse:collapse;font-size:12.5px}}
.tbl th{{background:#fafbfc;padding:9px 11px;text-align:left;font-size:10.5px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;font-weight:700;border-bottom:1px solid var(--border);white-space:nowrap;cursor:pointer;user-select:none}}
.tbl th:hover{{color:var(--orange)}}
.th-sort::after{{content:" \\2195";font-size:9px;opacity:.3;margin-left:3px}}
.th-sort.asc::after{{content:" \\2191";opacity:1;color:var(--orange)}}
.th-sort.desc::after{{content:" \\2193";opacity:1;color:var(--orange)}}
.tbl td{{padding:9px 11px;border-bottom:1px solid #f5f5f5;vertical-align:middle}}
.tbl tr:last-child td{{border-bottom:none}}
.tbl tr:hover td{{background:#fafafa}}
.tbl .nm{{text-align:right;font-variant-numeric:tabular-nums}}
/* RED=DOWN, GREEN=UP - Chinese style */
.up{{color:var(--red);font-weight:700}}
.down{{color:var(--green);font-weight:700}}
.tag-o{{background:#fff7ed;color:#ea580c;font-size:10px;padding:2px 7px;border-radius:20px;font-weight:700}}
.tag-b{{background:#dbeafe;color:#1d4ed8;font-size:10px;padding:2px 7px;border-radius:20px;font-weight:700}}
.tag-d{{background:#f3f4f6;color:#6b7280;font-size:10px;padding:2px 7px;border-radius:20px}}
.tag-g{{background:#dcfce7;color:#16a34a;font-size:10px;padding:2px 7px;border-radius:20px;font-weight:700}}
.tag-r{{background:#fee2e2;color:#dc2626;font-size:10px;padding:2px 7px;border-radius:20px;font-weight:700}}
.tag-note{{background:#fef3c7;color:#92400e;font-size:10px;padding:1px 6px;border-radius:4px;cursor:help}}
.row-note{{font-size:10.5px;color:var(--text2);line-height:1.4;margin-top:3px}}
.modal{{position:fixed;inset:0;background:rgba(0,0,0,.45);backdrop-filter:blur(3px);display:none;align-items:center;justify-content:center;z-index:1000;padding:16px}}
.modal.open{{display:flex}}
.mbox{{background:var(--card);border-radius:14px;width:100%;max-width:920px;max-height:88vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.18)}}
.mhead{{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--card);border-radius:14px 14px 0 0;z-index:2}}
.mtitle{{font-size:14px;font-weight:800}}
.mclose{{width:28px;height:28px;border-radius:7px;border:1px solid var(--border);background:var(--card);color:var(--dim);cursor:pointer;font-size:13px;display:flex;align-items:center;justify-content:center}}
.mbody{{padding:16px 20px}}
.mprice-row{{display:flex;align-items:flex-end;gap:16px;margin-bottom:12px;flex-wrap:wrap}}
.mprice-block{{text-align:right}}
.mnav{{font-size:28px;font-weight:900}}
.mchg{{font-size:14px;font-weight:700;margin-top:3px}}
.mmeta{{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}}
.mmeta span{{font-size:11px;color:var(--dim);background:var(--card2);padding:3px 9px;border-radius:20px}}
.chart-wrap{{margin:12px 0;background:var(--card2);border-radius:10px;padding:12px}}
.chart-title{{font-size:10.5px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;font-weight:600}}
canvas#kchart{{max-width:100%;height:150px;background:var(--card);border-radius:8px;border:1px solid var(--border)}}
.chart-legend{{display:flex;gap:14px;margin-top:6px;font-size:10.5px;color:var(--dim)}}
.chart-legend span{{display:flex;align-items:center;gap:3px}}
.cline{{width:12px;height:2px;display:inline-block}}
.cline-p{{background:#2563eb}}.cline-v{{background:#ea580c}}
.hsec{{margin-top:16px}}
.hsec h4{{font-size:10.5px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;padding-bottom:7px;border-bottom:1px solid var(--border);margin-bottom:9px;font-weight:600}}
.mtbl{{width:100%;border-collapse:collapse;font-size:12px;overflow-x:auto;display:block}}
.mtbl table{{min-width:500px;width:100%}}
.mtbl th{{background:#fafbfc;padding:7px 9px;text-align:left;font-size:10px;color:var(--dim);text-transform:uppercase;border-bottom:1px solid var(--border);white-space:nowrap}}
.mtbl td{{padding:7px 9px;border-bottom:1px solid #f8f8f8;vertical-align:middle;white-space:nowrap}}
.mtbl tr:last-child td{{border-bottom:none}}
.mtbl tr:hover td{{background:#fafafa}}
.rank{{font-weight:800;color:var(--dim);width:24px;font-size:11px}}
.rgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:12px}}
.rcard{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:15px;transition:.2s;box-shadow:0 1px 4px rgba(0,0,0,.03)}}
.rcard:hover{{border-color:var(--orange);transform:translateY(-2px);box-shadow:0 4px 14px rgba(0,0,0,.07)}}
.rtop{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}}
.rtag{{font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px}}
.rtag-g{{background:#dcfce7;color:#16a34a}}.rtag-r{{background:#fee2e2;color:#dc2626}}.rtag-b{{background:#dbeafe;color:#1d4ed8}}.rtag-o{{background:#ffedd5;color:#ea580c}}
.rdate{{font-size:10.5px;color:var(--dim)}}
.rtitle{{font-size:13.5px;font-weight:700;line-height:1.45;margin-bottom:7px}}
.rsummary{{font-size:11.5px;color:var(--text2);line-height:1.65}}
.rfooter{{margin-top:10px;padding-top:9px;border-top:1px solid #f5f5f5;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px}}
.rsrc{{font-size:10.5px;color:var(--dim)}}
.rtags{{display:flex;gap:4px;flex-wrap:wrap}}
.rtags span{{font-size:10px;background:#f3f4f6;color:#6b7280;padding:2px 6px;border-radius:10px}}
.flow-tabs{{display:flex;gap:7px;margin-bottom:12px}}
.ftab{{padding:5px 13px;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;border:1px solid var(--border);color:var(--dim);background:var(--card);transition:.15s}}
.ftab.ac,.ftab:hover{{background:var(--orange);color:#fff;border-color:var(--orange)}}
.fsection{{display:none}}.fsection.ac{{display:block}}
.ftbl{{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:14px;box-shadow:0 1px 4px rgba(0,0,0,.03)}}
.ftbl table{{width:100%;border-collapse:collapse;font-size:12.5px}}
.ftbl th{{background:#fafbfc;padding:9px 12px;text-align:left;font-size:10.5px;color:var(--dim);text-transform:uppercase;border-bottom:1px solid var(--border)}}
.ftbl td{{padding:9px 12px;border-bottom:1px solid #f5f5f5}}
.ftbl tr:last-child td{{border-bottom:none}}
.rnum{{font-weight:900;color:var(--dim);width:30px;font-size:14px}}
.fname{{font-weight:600}}.fcode{{font-size:10.5px;color:var(--dim);margin-top:1px}}
.famt{{font-weight:800;font-size:13px;text-align:right;white-space:nowrap}}
.mkt-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;margin-bottom:16px}}
.mkt-row{{display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap}}
.mkt-hsi{{flex:0 0 auto}}
.mkt-label{{font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;font-weight:600}}
.mkt-big{{font-size:36px;font-weight:900;line-height:1}}
.mkt-chg{{font-size:14px;font-weight:700;margin-top:4px}}
.mkt-raw{{font-size:10.5px;color:var(--dim);margin-top:2px}}
.mkt-temps{{flex:1;min-width:200px}}
.temp-gauge{{height:8px;background:#f3f4f6;border-radius:4px;overflow:hidden;margin:8px 0 4px}}
.temp-fill{{height:100%;border-radius:4px;transition:width .5s}}
.mkt-meta{{font-size:11px;color:var(--text2);margin-top:4px}}
.mkt-hsi-chart{{background:#fafbfc;border-radius:8px;border:1px solid var(--border);margin-top:10px;padding:4px 4px 0}}
canvas#hsicanvas{{max-width:100%;height:90px;display:block}}
.flow-sub-title{{font-size:11px;font-weight:700;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;margin:16px 0 8px;padding-left:4px;border-left:3px solid var(--orange)}}
.flow-src{{font-weight:400;text-transform:none;letter-spacing:0;color:var(--dim);font-size:10.5px;margin-left:6px}}
.flow-2col{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.flow-col{{background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden}}
.flow-col-title{{font-size:10px;font-weight:700;text-transform:uppercase;padding:7px 11px}}
.flow-col-title.in{{background:#f0fdf4;color:#16a34a}}.flow-col-title.out{{background:#fef2f2;color:#dc2626}}
.flow-row{{display:flex;align-items:center;padding:6px 11px;border-bottom:1px solid #f9f9f9;gap:8px}}
.flow-row:last-child{{border-bottom:none}}
.flow-name{{flex:1;font-size:11.5px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.flow-bar-wrap{{flex:0 0 60px;height:4px;background:#f3f4f6;border-radius:2px;overflow:hidden}}
.flow-bar{{height:100%;border-radius:2px}}
.flow-bar.in{{background:#16a34a}}.flow-bar.out{{background:#dc2626}}
.flow-amt{{font-size:11px;font-weight:700;min-width:50px;text-align:right}}
.flow-amt.in{{color:#16a34a}}.flow-amt.out{{color:#dc2626}}
.flow-section{{background:var(--card2);border-radius:12px;padding:12px}}
.edu-tbl{{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:16px;box-shadow:0 1px 4px rgba(0,0,0,.04)}}
.edu-tbl table{{width:100%;border-collapse:collapse;font-size:11.5px}}
.edu-tbl th{{background:#fafbfc;padding:9px 12px;text-align:left;font-size:10px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px;font-weight:700;border-bottom:1px solid var(--border)}}
.edu-tbl td{{padding:9px 12px;border-bottom:1px solid #f5f5f5;vertical-align:top;line-height:1.65}}
.edu-tbl tr:last-child td{{border-bottom:none}}
@media(max-width:768px){{.header,.tabs{{padding:0 14px}}.mn{{padding:14px}}.tbl{{overflow-x:auto}}.tbl table{{min-width:900px}}.flow-2col{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="header">
  <div class="logo">🌍 全球ETF投资地图 <span class="beta">BETA</span></div>
  <div class="hdr-right">
    <span class="upd" id="upt"></span>
    <div class="live"><span class="lt"></span>实时行情</div>
  </div>
</div>
<div class="tabs">
  <div class="ta ac" id="tab0" onclick="sw(0)">📊 ETF产品大全</div>
  <div class="ta" id="tab1" onclick="sw(1)">📋 海外机构观点</div>
  <div class="ta" id="tab2" onclick="sw(2)">💰 海外聪明钱</div>
</div>
<div class="mn">
  <div class="pn ac" id="pn0">
    <div class="sec-title" id="sec-title">全部产品 <span class="sub" id="prod-count"></span></div>
    <div class="fbar" id="fbar"></div>
    <div class="fsub" id="fsub"></div>
    <div class="search-box">
      <input class="search-in" id="searchIn" placeholder="🔍 搜索产品名称或代码..." oninput="onSearch(this.value)">
      <span class="search-count" id="searchCount"></span>
    </div>
    <div class="tbl">
      <table id="etftbl">
        <thead id="etfthead"></thead>
        <tbody id="etftbody"></tbody>
      </table>
    </div>
    <div id="edu-section"></div>
  </div>
  <div class="pn" id="pn1">
    <div class="sec-title">海外机构最新观点 <span class="sub">宏观策略 &middot; 行业配置 &middot; 产品分析</span></div>
    <div class="rgrid" id="rgrid"></div>
  </div>
  <div class="pn" id="pn2">
    <div class="sec-title">香港ETF资金流 <span class="sub">2026-04-15 &middot; CSOP + Longbridge</span></div>
    <div class="flow-tabs">
      <div class="ftab ac" id="ftabin" onclick="sf('in')">⬆ 资金流入</div>
      <div class="ftab" id="ftabout" onclick="sf('out')">⬇ 资金流出</div>
    </div>
    <div id="mkt-section"></div>
    <div id="finsec" class="fsection ac">
      <div class="ftbl"><table><thead><tr><th style="width:38px">#</th><th>基金</th><th style="text-align:right">净流入（USD）</th></tr></thead><tbody id="flowintable"></tbody></table></div>
    </div>
    <div id="foutsec" class="fsection">
      <div class="ftbl"><table><thead><tr><th style="width:38px">#</th><th>基金</th><th style="text-align:right">净流出（USD）</th></tr></thead><tbody id="flowouttable"></tbody></table></div>
    </div>
  </div>
</div>
<div class="modal" id="modal" onclick="if(event.target===this)cm()">
  <div class="mbox">
    <div class="mhead">
      <div class="mtitle" id="mtitle"></div>
      <button class="mclose" onclick="cm()">✕</button>
    </div>
    <div class="mbody" id="mbody"></div>
  </div>
</div>
<script>
const ALL_PRODUCTS = {ALL_PRODUCTS_JSON};
const HOLD = {HOLD_JSON};
const HOLIDAYS = {HOLIDAYS_JSON};
const IDATA = {IDATA_JSON};
const REPORTS = {REPORTS_JSON};
const FLOW_IN = {FLOW_IN_JSON};
const FLOW_OUT = {FLOW_OUT_JSON};
const HK_FLOW = {HK_FLOW_JSON};
const HSI_INTRADAY = {HSI_JSON};
const MARKET_TEMP = {mkt_temp};
const MARKET_VAL = {mkt_val};
const MARKET_SENT = {mkt_sent};
const MARKET_DESC = '{mkt_desc}';

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
function sw(i){{document.querySelectorAll('.ta').forEach(function(t,j){{t.classList.toggle('ac',j===i);}});document.querySelectorAll('.pn').forEach(function