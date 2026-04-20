#!/usr/bin/env python3
"""
南方东英产品行情获取脚本
通过 HTTP API 获取行情数据（轮询方式，非WebSocket）
"""
import json
import urllib.request
import time
from datetime import datetime

# 南方东英产品代码 (境内ETF - HK交易所)
SYMBOLS = [
    ('513130.HK', '恒生科技ETF'),
    ('159687.HK', '亚太精选ETF'),
    ('513730.HK', '东南亚科技ETF'),
    ('159822.HK', '新经济ETF'),
    ('159329.HK', '沙特ETF'),
    ('520830.HK', '沙特ETF(场外)'),
]

# 境外产品 (美股)
US_SYMBOLS = [
    ('AAPL.US', '苹果'),
    ('NVDA.US', '英伟达'),
    ('MSFT.US', '微软'),
    ('GOOGL.US', '谷歌'),
    ('AMZN.US', '亚马逊'),
    ('META.US', 'Meta'),
    ('TSLA.US', '特斯拉'),
]

def get_access_token():
    """返回有效的 access token"""
    return "eyJhbGciOiJSUzI1NiIsImtpZCI6ImViNzNlNDQxNTI4NzQzNzMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL29wZW5hcGkubG9uZ2JyaWRnZS5jb20iLCJzdWIiOiJ7XCJjbGllbnRfaWRcIjpcImZkNTJmYmM1LTAyYTktNDdmNS1hZDMwLTA4NDJjODQxYWFlOVwiLFwibWVtYmVyX2lkXCI6MTQ3ODIyMjEsXCJhcHBfaWRcIjpcImxvbmdicmlkZ2VcIixcImFjY291bnRfY2hhbm5lbFwiOlwibGJcIixcInRhcmdldF9hYWlkXCI6XCIyMDQzMTA3NFwiLFwibXNfaWRcIjpcImxvbmdicmlkZ2VcIixcImJhc2VfbGV2ZWxcIjozfSIsImF1ZCI6WyIxNyIsIjc4IiwiNzkiLCI4MCIsIjEzNyIsIjE3OSIsIjE4MCIsIjMiLCI0IiwiNSIsIjYiLCIyMTciLCIyMjIiLCIyMjMiLCIxMyIsIjE0IiwiMTUiLCIxNiIsIjE5IiwiMjkiLCIzMCIsIjEwIiwiMTEiLCIxMiJdLCJleHAiOjE3NzYxMDIzNTYsImlhdCI6MTc3NjA5ODc1NiwianRpIjoiZ3IxQXEyZDdUWlIycXZVSy9VTWRUZz09Iiwic2NvcGVfaWRzIjpbNCw1LDYsNywxMCwxMV0sInRva2VuX3R5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.k7Gksfj1_OLgLot5jYGNVc-YlOHtyAqH7z8BuSNnMBTBefeDnmEOERQQ28IYJExXln9BjbevLgOrEkK6US8Sf_A-za0bdHEsDxmzCMS9fbjUmxA3akv4k28la4OZ9GWsFhgtSFrKg8G02vY3lrvca6SdgEtgRPmciNVzgjsZtb9vyAeZ6njnk1yKILP9fpEAdjliifr9c5-3a8aM79i8FXLoOTRgPc22RJGgHYqG84X07Cou7B-UZc2RjRj3TKr3uKvUWGJxpy7wwVJ0An8H543_SA3IDysI3WhJqThYBPqrwxi6Hmf2SasqAmiJId2tz1htaWpG4b6rQgtTj32KMw"

def get_quotes(symbols):
    """获取行情数据"""
    token = get_access_token()
    
    # Get OTP first
    req = urllib.request.Request(
        'https://openapi.longbridge.com/v1/socket/token',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json; charset=utf-8'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            otp_data = json.loads(resp.read())
            if otp_data['code'] != 0:
                return {'error': otp_data['message']}
            otp = otp_data['data']['otp']
    except Exception as e:
        return {'error': f'获取OTP失败: {e}'}
    
    # Return OTP for WebSocket connection (for now, we return the OTP info)
    return {
        'otp': otp,
        'symbols': symbols,
        'timestamp': datetime.now().isoformat(),
        'info': '需要通过WebSocket获取实时行情，此脚本仅提供OTP'
    }

def generate_html(quotes_data):
    """生成HTML页面"""
    html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>南方东英产品行情 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .update-time {{ color: #666; font-size: 14px; }}
        table {{ border-collapse: collapse; width: 100%; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background: #0066cc; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .up {{ color: red; }}
        .down {{ color: green; }}
        .error {{ color: orange; background: #fff3cd; padding: 10px; border-radius: 4px; }}
    </style>
</head>
<body>
    <h1>📈 南方东英产品行情</h1>
    <p class="update-time">数据更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    
    <div class="error">
        <strong>注意：</strong>当前通过轮询方式获取数据，有一定延迟。实时行情需要WebSocket连接。
        <br>当前OTP: {quotes_data.get('otp', 'N/A')[:50]}...
    </div>
    
    <h2>产品列表</h2>
    <table>
        <thead>
            <tr>
                <th>代码</th>
                <th>名称</th>
                <th>最新价</th>
                <th>涨跌额</th>
                <th>涨跌幅</th>
            </tr>
        </thead>
        <tbody>
'''
    for code, name in SYMBOLS:
        html += f'            <tr><td>{code}</td><td>{name}</td><td colspan="3">需要WebSocket实时数据</td></tr>\n'
    
    html += '''        </tbody>
    </table>
    
    <p style="margin-top: 20px; color: #666;">
        如需实时行情，请通过支持WebSocket的方式访问。
    </p>
</body>
</html>'''
    return html

if __name__ == '__main__':
    print("正在获取行情数据...")
    data = get_quotes([s[0] for s in SYMBOLS])
    print(json.dumps(data, indent=2, ensure_ascii=False))
