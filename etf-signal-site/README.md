# 港股杠反ETF择时信号网站

基于港交所 CCASS 公开数据，追踪南方东英旗下 6 只港股杠反 ETF 的富途证券持仓变化率，实现港股择时信号。

策略来源：开源证券金工研报《基于港股杠反ETF份额变化的择时策略》(2025.12)

## 架构

- **Cloudflare Workers** — 后端 API + 页面服务
- **Cloudflare KV** — 每日 CCASS 数据存储（滚动保留 1 年）
- **前端** — 纯 HTML/CSS/JS，无框架

## 部署步骤

### 1. 安装 Wrangler CLI

```bash
npm install -g wrangler
```

### 2. 登录 Cloudflare

```bash
wrangler login
```

### 3. 创建 KV Namespace

```bash
wrangler kv:namespace create ETF_DATA
```

会返回类似：
```
{ binding = "ETF_DATA", id = "xxxxxxxxxxxxxxxxxxxx" }
```

### 4. 更新 wrangler.toml

将上一步返回的 `id` 填入 `wrangler.toml` 的 `kv_namespaces.id`。

### 5. 部署

```bash
cd etf-signal-site
wrangler deploy
```

部署成功后会返回 worker URL，例如：
```
https://etf-signal-api.your-subdomain.workers.dev
```

### 6. 绑定自定义域名（可选）

在 Cloudflare Dashboard 中：
1. 进入 Workers & Pages → 你的 Worker
2. 设置 → 触发器 → 自定义域
3. 添加 `social.etfclaw.site`（或你想要的域名）

## 本地开发

```bash
wrangler dev
# 访问 http://localhost:8787
```

## 监控的 6 只 ETF

| 代码 | 名称 | 类型 | 对应指数 |
|------|------|------|---------|
| 07226 | 南方2倍做多恒生科技 | 2x_long | 恒生科技 |
| 07552 | 南方2倍做空恒生科技 | 2x_short | 恒生科技 |
| 03033 | 南方恒生科技 | normal | 恒生科技 |
| 07200 | 南方2倍做多恒指 | 2x_long | 恒生指数 |
| 07500 | 南方2倍做空恒指 | 2x_short | 恒生指数 |
| 03037 | 南方恒生指数 | normal | 恒生指数 |

## 数据说明

- **数据来源**：港交所 CCASS 公开数据（每日更新）
- **可获取范围**：港交所官网保留最近 12 个月
- **持仓占比**：富途证券在杠反ETF中平均占 15.4%（最高 31.3%）
- **信号参数**：N=20，λ₁=1.2%（恒生科技）/1.0%（恒生指数），λ₂=1.0%

## API 接口

- `GET /api/signals` — 返回当前择时信号和所有 ETF 数据
- `GET /api/etf?code=07226` — 返回指定 ETF 的历史数据
