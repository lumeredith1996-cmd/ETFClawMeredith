# MEMORY.md - Long-Term Memory

_最后更新：2026-04-20_

## 👤 陆至慧

- 飞书: `ou_9431fbacba2b2f0faf13928f0f147f6c`
- 时区: Asia/Shanghai (GMT+8)
- 第一次上线：2026-04-20 早上7点多

## 📂 核心项目

### 1. 全球ETF投资地图 (`etf-map-v11.html`)
- **文件**: `/root/.openclaw/workspace/etf-map-v11.html`
- **URL**: `https://lowest-sim-wood-altered.trycloudflare.com/etf-map-v11.html`
- **备ur**: `https://etf-map-lu.loca.lt/etf-map-v11.html` (localtunnel)
- **服务器**: `quoteserver.py` 监听端口3000
- **数据**: 110个产品，内地可买64个（含QDII ETF/港股通ETF/跨境理财通等），境外可买46个
- **行情**: Longbridge API，`fd52fbc5-02a9-47f5-ad30-0842c841aae9`
- **持仓数据**: 仅9个产品有成分股数据，其他显示"暂无数据"
- **颜色**: 红涨绿跌

### 2. KOL时间轴 (`kol-timeline.html`)
- **文件**: `/root/.openclaw/workspace/kol-timeline.html`
- **数据源**: 飞书Bitable `ZKTqb1BQBaPbubsay3rcyydvnko`, 表 `tblteGKNZ6ZoRofB`
- **Wiki**: `NaCTwa59qiEPKrkwNpLc0mVonOe`
- **Space ID**: `7616689702317444033`
- 124条KOL记录，含咖位评级和平台ID

### 3. CSOP资金流数据
- 每晚7点录入
- 用户发来CSV，需录入更新聪明钱Tab

## 🔧 技术配置

- **Longbridge token**: `fd52fbc5-02a9-47f5-ad30-0842c841aae9`
- **quoteserver.py**: `/root/.openclaw/workspace/quoteserver.py` 端口3000
- **Cloudflare隧道**: session名含`node-local-website`或`kol-timeline`

## 📌 待办

- [ ] 每晚7点录入CSOP新数据
- [ ] 飞书wiki `WR79wyYtkin7I3kbQescM2RznPd` (All产品) 新Tab
- [ ] 成分股数据源扩充
- [ ] 市场情绪Tab验证
- [ ] KOL时间轴接入真实数据源

## 📅 历史

- **2026-04-15**: ETF地图v6发布，KOL时间轴项目启动
- **2026-04-16**: ETF地图升至v9/v11，解决多个bug（curSub初始化、ISIN换行、60/40粉标签等）
- **2026-04-20**: 第一次上线，整理记忆文件
