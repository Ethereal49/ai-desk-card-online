# AI Desk Card Web Plan

> 目标：复用 `/Users/ethereal/Documents/Code/ai-desk-card` 的产品想法和 widget 协议，但放弃固件推帧路线，改成一个适配 `758x1024` 墨水屏浏览器的简单网页。设备只需要访问网页即可显示卡片。

## 0. 结论

这条路线应该从一个极简网页 MVP 开始：

```
data/widgets.json -> web app -> e-ink browser
```

不要先做固件、daemon、BLE、USB、raw frame、partial refresh。它们是原 M5Paper 路线的必要复杂度，但不是浏览器墨水屏路线的必要复杂度。

## 1. 假设

- 设备面板分辨率为 `758x1024`（`width x height`，竖向屏）。
- 实际浏览器可视区域先不提前定死；先做 MVP，再用设备浏览器或 Codex 内置 Browser 确认 `window.innerWidth` / `window.innerHeight`。
- 设备有可用浏览器，能访问局域网或公网 URL。
- 首版只展示信息，不做复杂触屏交互。
- 刷新频率低频即可，目标是 `5m-30m` 级别，不支持实时行情、动画、视频。
- 首版数据源使用静态 JSON；真实数据来源在看过 MVP 效果后再定。
- 部署目标优先考虑用户自有服务器，首版仍保持静态文件可部署。

## 2. 成功标准

MVP 完成必须同时满足：

- 在 `758x1024` 视口下首屏无滚动、无缩放依赖、无文字重叠。
- 页面能从 `widgets.json` 渲染一组临时展示 widget，用来判断视觉和信息密度。
- 不把最终展示 widget 固定为首版 demo 的选择；最终展示哪几个在看过 MVP 后再定。
- 页面在墨水屏上高对比、低信息密度、无动画闪烁。
- 刷新策略明确：浏览器自动刷新页面或前端定时重新拉取 JSON。
- 不依赖原项目固件、PlatformIO、BLE、USB、M5Paper daemon。
- 保留后续接入 Agent 更新数据的接口边界。

不能把“本地浏览器看起来差不多”当完成；必须用 Codex 内置 Browser 在 `758x1024` 视口截图或检查布局。

公网部署进入真实数据前还必须满足：

- `widgets.json` 不在无认证、无加密的公网环境里暴露真实隐私数据。
- 服务器安全组只开放必要端口；数据库、内部应用、临时容器端口不得公网可连。
- 访问控制在 Caddy 或服务端完成，不能依赖前端隐藏内容。
- HTTPS 可用后再启用会传输密码的访问方式。

## 3. 从原项目复用什么

### 3.1 复用产品原则

保留：

- ambient 副屏，而不是第二块交互屏。
- glanceable，一眼看状态，不承载长阅读。
- 低频刷新，内容稳定，避免动态打扰。
- AI / 自动化系统决定显示什么，用户不手动维护复杂 dashboard。

### 3.2 复用 widget 类型

从 `/Users/ethereal/Documents/Code/ai-desk-card/plugin/skills/card-widget/schemas/` 直接参考：

- `ai-status`
- `ai-tasks`
- `break-reminder`
- `calendar`
- `deadlines`
- `focus`
- `git-status`
- `inbox`
- `messages`
- `next-meeting`
- `now-playing`
- `pr-queue`
- `scratch`
- `system`
- `todo`
- `weather`

原仓库共 16 类。首版 demo 可以先临时展示 4 个：

- `weather`
- `calendar`
- `todo`
- `focus`

原因：这四个覆盖“环境、时间、任务、当前专注”，足够验证基础布局。但它们不是最终选择，最终展示集合由用户看过 MVP 后再定。

### 3.3 复用 schema 思路

保留 `/Users/ethereal/Documents/Code/ai-desk-card/plugin/skills/card-widget/schemas/*.schema.json` 的字段约束思想，但首版不必引入完整 JSON Schema 校验。

首版数据格式：

```json
{
  "updated_at": "2026-05-29T14:00:00+08:00",
  "layout": "dashboard",
  "widgets": [
    {
      "slot": "hero",
      "type": "focus",
      "data": {
        "task": "Write PLAN_web.md",
        "big_text": "25:00",
        "subtitle": "current focus"
      }
    }
  ]
}
```

schema 校验先不做，MVP 和 JSON 写入阶段都只保持字段命名兼容。等真实数据源或 API 写入出现后，再补 JSON Schema 校验，避免首版被工程化拖慢。

### 3.4 复用墨水屏设计经验

保留：

- 大字体。
- 高对比。
- 少颜色。
- 少信息。
- 固定布局。
- 无动画。
- 宽松留白。

原项目的关键经验可以转成网页规则：

- 正文字号不低于 `26px`。
- 次要信息不低于 `20px`。
- 每个列表最多 `3-5` 项。
- 一个 widget 只表达一个核心问题。
- 颜色只用于状态区分，不做装饰。

## 4. 明确丢弃什么

网页路线不复用：

- `src/` 固件。
- `platformio.ini`。
- `daemon/card_daemon.py` 的传输层。
- raw `4bpp` / `RGB565` 帧编码。
- `/frame`、`/cmd`、BLE、USB serial、mDNS。
- M5Paper deep sleep / wake / battery 模式。
- Pillow renderer 的像素输出链路。

可以从 `/Users/ethereal/Documents/Code/ai-desk-card` 参考但不直接搬：

- `daemon/card_render.py`
- `daemon/card_render_color.py`

原因：浏览器已经有 HTML/CSS 渲染能力，继续用 Pillow 生成图片会降低可维护性，除非目标设备浏览器 CSS 支持极差。

## 5. 推荐架构

### 5.1 MVP 架构

```
web/
  index.html
  styles.css
  app.js
  widgets.json
```

浏览器打开：

```
http://<server>/index.html
```

前端流程：

1. 页面加载。
2. `fetch("./widgets.json")`。
3. 根据 `widgets[]` 渲染固定布局。
4. 每 `5m` 重新 fetch 一次。
5. fetch 失败时保留旧内容，并显示 stale 状态。

### 5.2 后续架构

当 MVP 验证后再升级：

```
Agent / cron / scripts
        |
        v
POST /api/widgets
        |
        v
widgets store
        |
        v
web dashboard
        |
        v
e-ink browser
```

后端可以是：

- Node.js + Express
- Python + FastAPI
- Cloudflare Worker
- Vercel serverless function
- 纯静态 JSON 文件

首版推荐纯静态 JSON 或极简 Node 服务。

## 6. `758x1024` 布局

### 6.1 约束

- 固定目标视口：`758x1024`。
- 不依赖用户缩放。
- 不做纵向滚动。
- 不做动画 transition。
- 不做 hover-only 信息。
- 所有信息在首次 paint 内可见。

### 6.2 推荐布局

```
┌────────────────────────────────────────────┐
│ top bar: date / time / updated / stale     │ 64
├────────────────────────────────────────────┤
│ focus                                      │
│ large current task                         │ 210
├────────────────────────────────────────────┤
│ weather                                    │
│ temp / condition / 2-day forecast          │ 160
├────────────────────────────────────────────┤
│ calendar / next meeting                    │ 190
├────────────────────────────────────────────┤
│ todo / inbox / notes                       │ 236
├────────────────────────────────────────────┤
│ footer: source / refresh cadence / status  │ 44
└────────────────────────────────────────────┘
```

CSS 尺寸建议：

- viewport shell: `width: 758px; height: 1024px`
- padding: `24px`
- gap: `12px`
- top bar: `64px`
- focus: `210px`
- weather: `160px`
- calendar: `190px`
- todo: `236px`
- footer: `44px`

如果实际浏览器有地址栏无法全屏，需要提供第二套 compact mode：

- shell 使用 `min-height: 100vh`
- 内容按 `1024px` 高度设计，但允许整体缩小到 `calc(100vh)`
- 不允许内容自然溢出。

## 7. 视觉规则

### 7.1 黑白墨水屏默认主题

默认只用：

- background: `#f8f8f2`
- ink: `#111`
- muted: `#666`
- border: `#111`
- stale/background accent: `#ddd`

不要用大面积渐变、阴影、半透明、细灰线。

### 7.2 字体

推荐：

```css
font-family:
  system-ui,
  -apple-system,
  BlinkMacSystemFont,
  "PingFang SC",
  "Noto Sans CJK SC",
  sans-serif;
```

字号建议：

- page title / current time: `34-42px`
- widget title: `22-26px`
- body: `26-32px`
- big number: `64-96px`
- footer/meta: `18-22px`

### 7.3 信息密度

- `focus`: 一个当前任务 + 一个大倒计时/状态 + 一行说明。
- `weather`: 当前温度最大，预测最多 2 天。
- `calendar`: 最多 4 个事件。
- `todo`: 最多 5 个任务。

超过数量时由数据生成端裁剪，不在 UI 里滚动。

## 8. 数据更新策略

### 8.1 首版

使用静态 `widgets.json`：

- 手动编辑也能工作。
- Agent 可以直接改这个文件。
- cron 可以定时生成这个文件。
- 网页每 `300s` 拉取一次。
- 真实数据源暂不接入；MVP 先用示例数据判断展示效果。

### 8.2 第二阶段

第二阶段先不做 API，继续使用文件写入：

```
Agent / cron / scripts -> web/widgets.json -> web dashboard
```

要求：

- 写入方直接生成完整 `web/widgets.json`。
- 每次写入必须更新 `updated_at`。
- 页面继续通过 `fetch("./widgets.json?t=" + Date.now())` 拉取，避免缓存。
- 数据写入失败不能破坏上一份可用 JSON。

API 是后续升级项，不属于 Phase 2：

```
POST /api/widgets
GET  /api/widgets
```

写入 body：

```json
{
  "widgets": [
    { "slot": "focus", "type": "focus", "data": {} }
  ]
}
```

### 8.3 stale 规则

页面必须显示数据新鲜度：

- `updated_at <= 15m`: normal
- `15m < updated_at <= 60m`: stale
- `updated_at > 60m`: old
- fetch 失败：保留旧数据，footer 显示 `offline`

不要因为请求失败清空屏幕。

## 9. 目录规划

新代码建议放在：

```
web/
  README.md
  index.html
  styles.css
  app.js
  widgets.example.json
  widgets.json
```

后续如果需要服务端：

```
web-server/
  package.json
  src/server.ts
  data/widgets.json
```

不要把网页 MVP 混进 `daemon/`。`daemon/` 属于原硬件推帧路线。

## 10. 实施阶段

### Phase 1 — 静态网页 MVP

目标：设备浏览器打开页面能稳定显示。

状态：已完成。当前实现位于 `web/`，使用静态 `widgets.json` 渲染 `focus`、`weather`、`calendar`、`todo` 四个 demo widget。

任务：

- 新建 `web/`。
- 写 `index.html`。
- 写 `styles.css`，固定适配 `758x1024`。
- 写 `app.js`，读取 `widgets.json`。
- 写 `widgets.example.json`。
- 支持 4 个 widget：`focus`、`weather`、`calendar`、`todo`。
- 页面每 `300s` 自动刷新数据。

验收：

- Codex 内置 Browser 模拟 `758x1024` 截图或检查无滚动、无重叠。
- 断网或 JSON 读取失败时不白屏。
- 所有文字在 30-50cm 阅读距离下足够大。

当前验收记录：

- 历史 `758x1024` viewport 验收：`scrollHeight=1024`，`clientHeight=1024`。后续 UI/layout 验收默认改用 Codex 内置 Browser。
- 正常路径 console：`0 errors, 0 warnings`。
- `widgets.json` 返回 500 时页面不白屏，保留内容并显示 `offline`。
- `widgets.json` 返回 `{}` 缺字段时页面不崩、不白屏。
- 旧截图产物已删除；后续 UI 检查如需产物，放入 `output/browser/`。

### Phase 1.5 — 公网部署安全加固

目标：当前页面已经能从公网访问，但在写入真实日程、todo、消息、focus 等私人数据前，先把公网边界收紧。

状态：已完成（IP HTTPS + Basic Auth）。仓库侧已补充 Caddy 部署安全模板和验收清单；用户确认当前不绑定域名、直接访问公网 IP。已验证 Let's Encrypt IP address certificate 方案，live Caddy 使用 `http://112.74.73.134/` 跳转到 `https://112.74.73.134/`，HTTPS 入口已启用 Basic Auth。Phase 3 开始条件已满足。

当前审计结论：

- `http://112.74.73.134/` 不再直接返回页面，而是跳转到 HTTPS。
- 未认证 `https://112.74.73.134/` 和 `/widgets.json` 返回 `401`，不能直接读取页面或 JSON。
- 认证后 `https://112.74.73.134/` 和 `/widgets.json` 返回 `200`，并带有 `Cache-Control: no-store`、CSP、`Referrer-Policy`、`Strict-Transport-Security`、`X-Content-Type-Options`。
- 当前 live Caddy `v2.11.3` 已应用 `deploy/caddy/Caddyfile.ip-https.example` 的 Basic Auth 形态；最近备份为 `/etc/caddy/Caddyfile.ai-desk-card-online.before-basic-auth.20260531232710.bak`。
- 当前 HTTPS 证书由 Let's Encrypt 签发，SAN 为 `IP Address:112.74.73.134`，有效期到 `2026-06-07`；Certbot `5.6.0` 使用 `--preferred-profile shortlived` 续期，并通过 deploy hook 同步证书到 Caddy。
- 当前 Caddy HTTPS server 使用 `:443` 加显式证书，而不是 `https://112.74.73.134` site label；原因是部分客户端访问 IP 时不发送 SNI。
- 认证后 `/README.md`、`/widgets.example.json` 和路径穿越探测返回 `404`。
- 公网 `758x1024` 浏览器验收：`scrollHeight=1024`、`clientHeight=1024`，`focus`、`weather`、`calendar`、`todo` 均渲染。
- 与本项目无关的公网端口本阶段不处理；用户已明确要求先不要管项目无关端口。该项不作为当前 Phase 1.5 验收条件。
- 前端代码没有第三方 CDN、cookie、localStorage 或后端接口；动态 JSON 内容已通过 `escapeHtml()` 渲染，当前 XSS 风险较低。

任务：

- 在仓库中保留可复用的 Caddy 安全配置模板和验收清单，避免服务器侧手工配置失真。
- 在 IP-only 模式下先做 demo 加固：屏蔽非运行文件、补安全响应头、保持 `Cache-Control: no-store`；不要在 HTTP 上启用 Basic Auth。
- 本项目入口保持公网 `80` 可访问；与本项目无关的安全组、Docker / 1Panel 端口本阶段明确 out of scope。
- HTTPS 和 Basic Auth 已作为 Phase 3 前置条件完成；后续真实数据源仍必须做最小字段裁剪，不能把 token 或原始私密数据写入前端可读内容。
- 禁止公网访问非运行必需文件，例如 `/README.md`、`/widgets.example.json`。当前 IP-only live 已完成。
- 增加静态站点安全响应头：`X-Content-Type-Options`、`Referrer-Policy`、`Content-Security-Policy`、`frame-ancestors`。当前 IP-only live 已完成。
- 保留 `Cache-Control: no-store` 或等价策略，避免设备和中间缓存长期保存私人数据。当前 IP-only live 已完成。

验收：

- `http://112.74.73.134/` 返回 HTTPS redirect。
- 未认证 `https://112.74.73.134/` 和 `/widgets.json` 返回 `401`。
- 认证后 `https://112.74.73.134/` 和 `/widgets.json` 返回 `200`。
- 认证后 `/README.md`、`/widgets.example.json`、不存在路径和路径穿越尝试不会泄露文件内容。
- 响应包含 `Cache-Control: no-store`、CSP、`Referrer-Policy`、`X-Content-Type-Options`。
- 公网 `758x1024` 浏览器验收无滚动：`scrollHeight=1024`、`clientHeight=1024`。
- `widgets.json` 放入真实私人数据前，访问控制 gate 必须保持通过；当前 gate 已通过。

IP-only 模式的边界：

- `http://112.74.73.134/` 只保留 ACME challenge 和 HTTPS redirect。
- `https://112.74.73.134/` 是当前正式入口。
- Basic Auth 只在 HTTPS 入口启用，不在 HTTP 上传输密码。
- 真实数据源 token 不得进入 `widgets.json` 或前端代码；Phase 3 只输出渲染所需的最小字段。

### Phase 2 — Agent 可写入数据

目标：让 AI Agent 或脚本更新页面内容。

状态：已完成（public demo write path）。已新增 `scripts/web_update.py`，支持生成完整公开 demo `web/widgets.json` 并原子写入；已同步一次公开 demo 数据到 live `/srv/ai-desk-card-online/widgets.json`，无需重启 Caddy。IP-only 模式仍不得写入真实私人数据。

任务：

- 使用最小写入方式：直接写 `web/widgets.json`。当前已完成。
- 增加数据生成脚本，例如 `scripts/web_update.py`。当前已完成。
- 复用现有 schema 字段命名。当前已完成，保留 `updated_at`、`layout`、`refresh_seconds`、`widgets` 和 Phase 1 widget 类型。
- 写入 `updated_at`。当前已完成。

验收：

- Agent/脚本能更新 widget：`scripts/web_update.py` 已生成新的 `focus`、`weather`、`calendar`、`todo` demo 数据。
- 页面在下一次刷新自动显示新内容：公网 `758x1024` 浏览器验收已看到 `Phase 2 public demo update`。
- 无需重启网页服务：仅同步 live `/srv/ai-desk-card-online/widgets.json` 后 Caddy 直接返回新 JSON。

### Phase 2.1 — Codex plan update hook

目标：每次 Codex 工作结束前自动检查 `PLAN_web.md` 是否跟随项目状态更新。

状态：已完成。已按官方 Codex hooks 机制添加项目级 `.codex/hooks.json`，在 `Stop` 事件运行 `.codex/hooks/ensure_plan_updated.py`。

任务：

- 使用项目级 `<repo>/.codex/hooks.json`，不是 git hook。
- 监听 Codex `Stop` 事件。
- 如果项目文件比 `PLAN_web.md` 更新，返回 `decision: block`，要求先更新 plan 再结束。
- 忽略 `.git/`、`output/` 和 Python cache 等非项目状态产物。

验收：

- `python3 scripts/test_plan_guard.py` 覆盖新旧 plan 和 output artifact ignore 行为。
- 运行 `.codex/hooks/ensure_plan_updated.py` 在当前仓库应返回 `{}`。
- 项目级 hook 需要在 Codex 中通过 `/hooks` review/trust 后自动执行；这是官方 Codex hook 信任机制。
- 2026-05-31 更新：UI/layout 验收规则已改为默认使用 Codex 内置 Browser；旧浏览器自动化产物和专用忽略项已删除，并同步忽略 Python cache。公网 IP HTTPS + Basic Auth 验收脚本和 Caddy 模板已补充。
- 2026-05-31 更新：Phase 3 ready gate 已通过：HTTP redirect、HTTPS 未认证 `401`、认证后 runtime `200`、认证后非运行文件 `404`。
- 2026-05-31 更新：Basic Auth 密码已轮换；明文密码不写入仓库。

### Phase 3 — 数据源接入

目标：让页面显示真实日常数据。

状态：进行中；weather slice 已完成。第一个真实数据源为 Shenzhen weather，使用公开 `wttr.in` JSON 接口；自动更新由服务器 systemd timer 执行。

数据源在 MVP 视觉效果确认后再选。

优先级：

1. `weather`: `wttr.in` Shenzhen 公开接口，先跑通自动更新流程。
2. `focus`: 当前手动指定任务，从 widgets 中可选。
3. `todo`: 本地 JSON / Reminders / Notion 任选一种。
4. `calendar`: 系统日历或 Google Calendar。

验收：

- 每个数据源失败时只影响对应 widget。
- 失败 widget 显示 stale，不影响整页。

当前 Phase 3 weather 验收：

- `scripts/update_weather.py` 只更新 `weather` widget，并保留 `focus`、`calendar`、`todo`。
- 成功时 weather widget 写入 `location=Shenzhen`、`source=wttr.in`、`updated_at`、`current`、`forecast`、`stale=false`。
- 失败时保留上一份 weather 值，设置 `stale=true`，不清空页面。
- 服务器自动更新由 `ai-desk-card-weather.timer` 触发，每 30 分钟运行一次。
- live 验收：`ai-desk-card-weather.service` 已成功运行，`widgets.json` 显示 Shenzhen weather，Codex 内置 Browser 认证访问页面显示 `Shenzhen · wttr.in` 和当前温度。
- 修复记录：weather service 作为 root 原子写入时必须保持 `widgets.json` 为 `0644`，否则 Caddy 会对 `/widgets.json` 返回 `403`。
- 部署文档已记录 weather timer、失败隔离和 `0644` 权限要求。

### Phase 4 — 部署

目标：墨水屏设备无需开发环境即可访问。

状态：基础部署和 IP HTTPS + Basic Auth 加固已完成。Caddy 已托管静态文件并可通过公网 IP 的 HTTPS 认证访问。它可以作为 Phase 3 真实数据源接入的开始边界，但仍不是完整生产系统。

首选部署：

- 用户自有服务器：Caddy 托管静态文件，必要时加 Basic Auth 或反向代理认证。

备选部署：

- 用户自有服务器：Nginx 托管静态文件。
- 局域网：本机 `python3 -m http.server` 或 Node 静态服务。
- 公网静态：GitHub Pages / Cloudflare Pages / Vercel。

验收：

- 设备能通过固定 URL 打开页面。
- 重启服务后 URL 不变。
- 刷新周期稳定。
- 如果内容包含隐私信息，访问控制必须在部署层或服务端完成，不能只靠前端隐藏。

## 10.5 隐私和解锁

MVP 先不做解锁。部署到服务器并确认页面效果后，如果内容涉及日程、消息、todo、focus 等隐私信息，优先使用 Caddy 的 Basic Auth：

1. 部署层 Basic Auth：由 Caddy 要求输入用户名和密码。实现最简单，适合自有服务器。
2. 服务端登录：后端校验 session/cookie 后再返回 `widgets.json`。更灵活，但需要服务端。
3. 前端密码解锁 + 加密数据：`widgets.json` 存加密内容，浏览器输入密码后本地解密。适合静态部署，但密码丢失无法恢复，数据生成流程也要负责加密。

不要使用“前端输入密码后仅隐藏/显示 DOM”的假解锁。如果 `widgets.json` 仍然公开可读，它只能防路人，不能保护数据。

## 11. 技术选择建议

首版不要上 React，除非后续确定要复杂组件化。

推荐首版：

- HTML
- CSS
- vanilla JavaScript
- JSON file

原因：

- 墨水屏页面状态少。
- 无复杂交互。
- 构建系统会增加部署摩擦。
- 静态文件最容易被任意设备访问。

后续需要组件化时再迁移到：

- Astro
- SvelteKit
- React + Vite

## 12. 风险和验证

### 风险 1：设备浏览器实际可视区域不是 `758x1024`

验证：

- 打开一个 viewport probe 页面，显示 `window.innerWidth` / `window.innerHeight`。
- 若有浏览器地址栏，记录真实 viewport。

处理：

- 保留 `758x1024` design target。
- CSS 使用固定比例布局 + compact mode。

### 风险 2：设备浏览器 CSS 支持差

验证：

- 测 CSS grid、fetch、localStorage、meta refresh。

处理：

- CSS grid 不支持时退回 block/flex。
- fetch 不支持时退回整页 meta refresh + inline JSON。

### 风险 3：墨水屏刷新残影

验证：

- 避免频繁变动大面积黑块。
- 避免动画。
- 保持布局位置稳定。

处理：

- 每次刷新只改变文本内容。
- 黑色块只用于边框和标题，不做整页反色。

### 风险 4：页面被缓存导致数据不更新

验证：

- `fetch("./widgets.json?t=" + Date.now())`。

处理：

- 静态部署设置 `Cache-Control: no-cache`。
- URL 加时间戳。

## 13. 下一步

Phase 1、Phase 1.5、Phase 2 和 Phase 2.1 已完成；当前下一阶段是 Phase 3：数据源接入。Phase 3 开始条件已经满足。

不要把 token 或原始私密数据写入 `widgets.json`。Phase 3 只能写入页面渲染所需的裁剪后字段。

建议顺序：

1. 基于实际观感决定最终展示哪几个 widget。
2. 进入 Phase 3，先接入风险最低的数据源，例如 weather 或手动 focus。
3. 接 todo/calendar 前先定义字段裁剪规则，避免把原始私密内容或 token 写入前端。
4. 每次 Codex 工作结束前，让 `.codex/hooks/ensure_plan_updated.py` 检查 `PLAN_web.md` 是否已更新。
