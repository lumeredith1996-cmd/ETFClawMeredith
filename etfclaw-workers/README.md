# ETFClaw Workers 部署指南

## 功能

- `etfclaw.site/social` → 跳转到 GitHub Pages
- 雪球/微博内容代理加速
- 全球CDN加速

## 部署步骤

### 1. GitHub 仓库创建

1. 登录 https://github.com
2. 点击 **+** → **New repository**
3. 填写：
   - Name: `etfclaw-workers`
   - Private: 可选
   - ✅ Add a README file

### 2. 本地初始化（在你的电脑或服务器上）

```bash
# 克隆仓库（替换为你的仓库地址）
git clone https://github.com/lumeredith1996-cmd/etfclaw-workers.git
cd etfclaw-workers

# 复制项目文件到这里（跳过这步，如果仓库是空的）
# 把 src/index.js 和 wrangler.toml 放入此目录

# 添加所有文件
git add .
git commit -m "feat: initial etfclaw workers"
git push origin main
```

### 3. Cloudflare 部署

**方式一：GitHub 集成（推荐，自动部署）**

1. 登录 https://dash.cloudflare.com
2. 进入 **Workers & Pages** → **Create Application** → **Create Worker**
3. 选择 **Connect to Git**
4. 授权 GitHub，选择 `etfclaw-workers` 仓库
5. 构建命令留空，直接部署

**方式二：wrangler CLI 手动部署**

```bash
# 安装 wrangler
npm install -g wrangler

# 登录 Cloudflare
wrangler login

# 部署
wrangler deploy
```

### 4. 配置自定义域名

1. 在 Cloudflare Dashboard → Workers → 你的 Worker
2. **Triggers** → **Custom Domains**
3. 点击 **Add Custom Domain**
4. 输入 `etfclaw.site` 或子域名如 `social.etfclaw.site`

### 5. 腾讯云 DNS 配置（域名不转出的情况）

**方案A：DNS 托管转 Cloudflare（推荐）**

1. 在腾讯云 DNSPod 把域名 NS 记录改成 Cloudflare 的：
   - `ns1.cloudflare.com`
   - `ns2.cloudflare.com`
2. 在 Cloudflare 添加域名，配置 DNS 和路由规则

**方案B：CNAME 转发**

1. 在腾讯云 DNSPod 添加 CNAME：
   - 主机记录：`social`
   - 记录值：`etfclaw-workers.workers.dev`
   - 设置为"Proxy"模式

## 使用示例

```
# 跳转
https://etfclaw.site/social

# 代理雪球
https://etfclaw.site/xueqiu/u/123456

# 代理微博
https://etfclaw.site/weibo/u/123456
```
