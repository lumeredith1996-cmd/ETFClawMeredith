#!/usr/bin/env python3
"""Generate etf-map-v7.html"""
import re, json

# ── Extract product data ──────────────────────────────────────────────────────
code = open('/root/.openclaw/workspace/etf-map-v6.html').read()
arr_start = code.find('const ALL_PRODUCTS=[') + len('const ALL_PRODUCTS=')
arr_end = code.find('];const HOLD', arr_start)
prod_block = code[arr_start:arr_end+1]

pattern = re.findall(
    r"\['([^']+)','([^']+)','([^']+)','([^']+)','([^']+)',([\d.]+),([\d.]+),(-?[\d.]+),(true|false),'([^']*)',(-?[\d.]+|'[^']*'),'([^']*)'\]",
    prod_block
)
products = []
for p in pattern:
    products.append({
        'name': p[0], 'code': p[1], 'region': p[2], 'cat': p[3],
        'type': p[4], 'last': float(p[5]), 'prev': float(p[6]),
        'chg': float(p[7]), 'up': p[8] == 'true',
        'turnover': p[9],
        'premium': float(p[10]) if p[10].replace('.','').replace('-','').isdigit() else 0,
        'index': p[11],
    })

# ── Notes ────────────────────────────────────────────────────────────────────
NOTES = {
    '513130.SH': 'T+0申赎，QDII额度紧张，关注溢价风险',
    '159687.SZ': '亚太低碳精选，台湾+韩国+东南亚分散配置',
    '513730.SH': '新交所泛东南亚科技指数，印度+新加坡+印尼上市龙头',
    '159822.SZ': '新经济主题，中概科技+电商+生物医药',
    '159329.SZ': '沙特阿美+金融为主，油价与汇率双敏感',
    '520830.SH': '费率较低，与159329同为沙特ETF',
    '03441.HK': '东西股票精选，港+A股+美股ADR离岸上市',
    '03442.HK': '恒生港美科技指数，腾讯/阿里/亚马逊/英伟达',
    '03174.HK': '恒生生物科技指数，CXO/创新药为主',
    '03443.HK': '香港股票指数，港铁/友邦/汇丰等本地股',
    '03469.HK': '高股息策略，港股通红利主题',
    '02830.HK': '沙特主权基金持仓，油价+利差双敏感',
    '03454.HK': '美股七巨头指数，苹果/微软/英伟达/谷歌/Meta/亚马逊',
    '03153.HK': '日经225指数，东京证券交易所上市',
    '03147.HK': '中国创业板，A股科技成长风格',
    '03134.HK': '中证太阳能指数，A股光伏产业链',
    '03133.HK': '沪深300，A股大盘蓝筹',
    '03109.HK': '科创板50，科创板核心资产',
    '03101.HK': '中证A500，A股中盘+大盘均衡配置',
    '03034.HK': '纳斯达克100，美股科技旗舰指数',
    '03033.HK': '恒生科技指数，港股科技旗舰',
    '03004.HK': '富时越南30指数，胡志明交易所上市',
    '02822.HK': '富时中国A50，A股大盘蓝筹',
    '03068.HK': '以太币期货，合约展期成本注意',
    '03066.HK': '比特币期货，高波动加密货币',
    '03433.HK': '美国国债20年+，美债长端利率敏感',
    '03199.HK': '富时中国国债，人民币债券配置',
    '09096.HK': '美元货币市场，稳定收益美元资产管理',
    '03096.HK': '美元货币市场（子份额），美元现金管理',
    '03122.HK': '人民币货币ETF，人民币现金管理',
    '03053.HK': '港元货币ETF，港元储蓄替代',
    '03447.HK': '亚太房地产信托，租金收益型',
    '02802.HK': '国指备兑认购期权，机构衍生品策略',
    '03167.HK': '中证500指数，A股中盘代表',
    '03193.HK': '中证5G指数，A股通信设备',
    '03005.HK': '中证500，A股中盘均衡',
    '03003.HK': 'MSCI中国A50，A股大盘+港股配置',
    '03431.HK': '港韩科技，港股+韩国科技股',
    '03432.HK': '港股通精选，港股通核心标的',
    '03037.HK': '恒生指数，港股大盘基准',
    '09167.HK': '工银标普中国，标普中国指数QDII',
    '03441.HK': '东西精选，港股+A股+美股ADR',
    'N1005': '南方东英发行，跨境理财通南向通可投',
    'N1002': '南方东英日经指数，跨境理财通渠道',
    'N1077': '南方东英恒生科技，跨境理财通渠道',
}
for p in products:
    p['note'] = NOTES.get(p['code'], '')

# ── Extract other data ────────────────────────────────────────────────────────
def extract_js_block(start_str, end_str, code):
    s = code.find(start_str)
    if s == -1: return ''
    s += len(start_str)
    depth = 0
    in_str = False
    for i, c in enumerate(code[s:], s):
        if not in_str:
            if c in "'\"\"":
                in_str = True
            elif c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == -1:
                    return code[s:i]
        else:
            if c == "'" and code[i-1] != '\\':
                in_str = False
    return ''

def parse_hold(block):
    result = {}
    for m in re.finditer(r"'([^']+)':\[\[(.+?)\]\]", block, re.DOTALL):
        code_key, items_str = m.group(1), m.group(2)
        items = re.findall(r"\['([^']*)','([^']*)','([^']*)',([\d.]+)\]", items_str)
        result[code_key] = [[a, b, c, float(d)] for a, b, c, d in items]
    return result

def parse_holdays(block):
    result = {}
    for m in re.finditer(r"'([^']+)':\[(.+?)\]", block, re.DOTALL):
        result[m.group(1)] = re.findall(r"'([^']*)'", m.group(2))
    return result

def parse_idata(block):
    result = {}
    for m in re.finditer(r"'([^']+)':\[\[(.+?)\]\]", block, re.DOTALL):
        items = re.findall(r"\['([^']*)',([\d.]+),([\d.]+)\]", m.group(2))
        result[m.group(1)] = [[a, float(b), float(c)] for a, b, c in items]
    return result

# HOLD
h_s = code.find("const HOLD={") + len("const HOLD={")
h_e = code.find("};const HOLIDAYS", h_s)
HOLD = parse_hold(code[h_s:h_e])

# HOLIDAYS
hd_s = code.find("const HOLIDAYS={") + len("const HOLIDAYS={")
hd_e = code.find("};const IDATA", hd_s)
HOLIDAYS = parse_holdays(code[hd_s:hd_e])

# IDATA
id_s = code.find("const IDATA={") + len("const IDATA={")
id_e = code.find("};const REPORTS", id_s)
IDATA = parse_idata(code[id_s:id_e])

# FLOW_IN/OUT
fi_s = code.find("const FLOW_IN=[") + len("const FLOW_IN=[")
fi_e = code.find("];const FLOW_OUT", fi_s)
FLOW_IN = re.findall(r"\['([^']*)','([^']*)','([^']*)'\]", code[fi_s:fi_e])

fo_s = code.find("const FLOW_OUT=[") + len("const FLOW_OUT=[")
fo_e = code.find("];// ───", fo_s)
FLOW_OUT = re.findall(r"\['([^']*)','([^']*)','([^']*)'\]", code[fo_s:fo_e])

# HSI_INTRADAY
hsi_s = code.find("var HSI_INTRADAY=") + len("var HSI_INTRADAY=")
hsi_e_match = re.search(r"\]\];var MARKET_TEMP", code[hsi_s:])
HSI_INTRADAY = []
if hsi_e_match:
    raw = code[hsi_s:hsi_s + hsi_e_match.end()-1]
    HSI_INTRADAY = [[a, float(b), float(c)] for a, b, c in re.findall(r"\['([^']*)',([\d.]+),([\d.]+)\]", raw)]

# HK_FLOW_DATA
hkf_s = code.find("var HK_FLOW_DATA=") + len("var HK_FLOW_DATA=")
hkf_e_m = re.search(r"\];var MARKET_VAL", code[hkf_s:])
HK_FLOW = []
if hkf_e_m:
    raw = code[hkf_s:hkf_s + hkf_e_m.end()-1]
    HK_FLOW = [[a, b, int(c)] for a, b, c in re.findall(r"\['([^']*)',\s*'([^']*)',\s*(-?\d+)\]", raw)]

# MARKET vars
mkt_temp = int(re.search(r"var MARKET_TEMP=(\d+)", code).group(1))
mkt_val = int(re.search(r"var MARKET_VAL=(\d+)", code).group(1))
mkt_sent = int(re.search(r"var MARKET_SENT=(\d+)", code).group(1))
mkt_desc = re.search(r"var MARKET_DESC='([^']*)'", code).group(1)

# REPORTS
rep_s = code.find("const REPORTS=[")
rep_e = code.find("];const FLOW_IN", rep_s)
rep_block = code[rep_s:rep_e]
REPORTS = re.findall(
    r"\{title:'([^']*)',date:'([^']*)',market:'([^']*)',sentiment:'([^']*)',tag1:'([^']*)',tag2:'([^']*)',tag3:'([^']*)',summary:'([^']*)'\}",
    rep_block
)

# Serialize all data to JSON for HTML embedding
data = {
    'products': products,
    'HOLD': HOLD,
    'HOLIDAYS': HOLIDAYS,
    'IDATA': IDATA,
    'FLOW_IN': FLOW_IN,
    'FLOW_OUT': FLOW_OUT,
    'HK_FLOW': HK_FLOW,
    'HSI_INTRADAY': HSI_INTRADAY,
    'MARKET_TEMP': mkt_temp,
    'MARKET_VAL': mkt_val,
    'MARKET_SENT': mkt_sent,
    'MARKET_DESC': mkt_desc,
    'REPORTS': REPORTS,
}

with open('/tmp/v7_data.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Products: {len(products)}")
print(f"HOLD: {len(HOLD)}, HOLIDAYS: {len(HOLIDAYS)}, IDATA: {len(IDATA)}")
print(f"FlowIn: {len(FLOW_IN)}, FlowOut: {len(FLOW_OUT)}")
print(f"HK_FLOW: {len(HK_FLOW)}")
print(f"HSI: {len(HSI_INTRADAY)} points")
print(f"Reports: {len(REPORTS)}")
print("Data saved.")
