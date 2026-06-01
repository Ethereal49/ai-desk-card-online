# AI Desk Card Web Plan

> 目标：复用 `/Users/ethereal/Documents/Code/ai-desk-card` 的产品想法和 widget 协议，但放弃固件推帧路线，改成一个适配 `758x1024` 墨水屏浏览器的简单网页。设备只需要访问网页即可显示卡片。

## 0. 结论

这条路线应该从一个极简网页 MVP 开始：

```
web/widgets.json -> web app -> e-ink browser
```

不要先做固件、daemon、BLE、USB、raw frame、partial refresh。它们是原 M5Paper 路线的必要复杂度，但不是浏览器墨水屏路线的必要复杂度。

当前路线已经进入 Phase 3：静态网页、IP HTTPS + Basic Auth、Agent/cron 写入链路和 Shenzhen weather 自动更新已完成。本地和 live runtime 已把页面信息架构校正为原仓库的 widget 角色模型：glance / headline / detail / status，并加入 `ai-status` 和 `ai-tasks` demo slice。显式低敏写入脚本和 focus/todo/calendar smoke 发布链路已通过 live 验收。下一步是根据真实设备观感决定 detail 三列是否需要 compact mode 或轮换显示。

## 1. 假设

- 设备面板分辨率为 `758x1024`（`width x height`，竖向屏）。
- 实际浏览器可视区域先不提前定死；先做 MVP，再用设备浏览器或 Codex 内置 Browser 确认 `window.innerWidth` / `window.innerHeight`。
- 设备有可用浏览器，能访问局域网或公网 URL。
- 首版只展示信息，不做复杂触屏交互。
- 刷新频率低频即可，目标是 `5m-30m` 级别，不支持实时行情、动画、视频。
- 首版数据载体继续使用静态 `web/widgets.json`；Phase 3 真实数据源先通过脚本/cron 写入裁剪后的展示字段。
- 部署目标优先考虑用户自有服务器，首版仍保持静态文件可部署。

## 2. 成功标准

MVP 完成必须同时满足：

- 在 `758x1024` 视口下首屏无滚动、无缩放依赖、无文字重叠。
- 页面能从 `widgets.json` 渲染一组临时展示 widget，用来判断视觉和信息密度。
- 不把最终展示 widget 固定为首版 demo 的选择；当前竖排布局是 MVP/fallback，不是最终信息架构。
- 页面在墨水屏上高对比、低信息密度、无动画闪烁。
- 刷新策略明确：浏览器自动刷新页面或前端定时重新拉取 JSON。
- 不依赖原项目固件、PlatformIO、BLE、USB、M5Paper daemon。
- 保留后续接入 Agent 更新数据的接口边界。

不能把“本地浏览器看起来差不多”当完成；必须用 Codex 内置 Browser 在 `758x1024` 视口截图或检查布局。

公网部署写入真实数据前还必须满足：

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

原仓库共 16 类。Phase 1 demo 已临时展示 4 个：

- `weather`
- `calendar`
- `todo`
- `focus`

原因：这四个覆盖“环境、时间、任务、当前专注”，足够验证基础布局。但它们不是最终选择。进入 Phase 3 后，默认集合应向原仓库的角色化布局收敛。本地 role-based slice 已补 `ai-status` 和 `ai-tasks`，当前静态资产使用 `weather`、`ai-status`、`focus`、`ai-tasks`、`calendar`、`todo` 六个 widget。

### 3.3 复用 schema 思路

保留 `/Users/ethereal/Documents/Code/ai-desk-card/plugin/skills/card-widget/schemas/*.schema.json` 的字段约束思想，但首版不必引入完整 JSON Schema 校验。

当前数据格式保持稳定：

```json
{
  "updated_at": "2026-05-29T14:00:00+08:00",
  "layout": "dashboard",
  "widgets": [
    {
      "slot": "headline",
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

schema 校验先不做，MVP、Phase 2 写入阶段和 Phase 3 weather slice 都只保持字段命名兼容。等接入更多私密数据源或后端 API 后，再补 JSON Schema 校验，避免首版被工程化拖慢。

当前 role-based slot 命名：

- `glance-left`: `weather` 或 `git-status`。
- `glance-right`: `ai-status`。
- `headline`: `focus` / `calendar` / `next-meeting` 中的主信息。
- `detail-left`: `ai-tasks` 计数。
- `detail-middle` / `detail-right`: `calendar`、`todo`、`inbox`、`notes` 等细节信息。

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
https://<server-or-ip>/
```

前端流程：

1. 页面加载。
2. `fetch("./widgets.json")`。
3. 根据 `widgets[]` 渲染固定布局。
4. 每 `5m` 重新 fetch 一次。
5. fetch 失败时保留旧内容，并显示 stale 状态。

### 5.2 后续架构

当前 Phase 2/3 仍使用文件写入；当需要网页内登录、账号体系、用户级数据权限或服务端聚合多个私密数据源时，再升级为后端服务：

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

仍不需要后端时的替代方案是继续使用纯静态 JSON 文件。

当前推荐继续保持静态 JSON 写入；后端服务是后续升级项，不是接入 weather 和单机自动更新的前置条件。

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
│ status rail: date / time / updated / stale │ 64
├────────────────────────────────────────────┤
│ weather / git-status   │ ai-status         │ 210
│ glance                 │ glance            │
├────────────────────────────────────────────┤
│ headline: focus / calendar / next-meeting  │ 320
├────────────────────────────────────────────┤
│ detail: todo / ai-tasks / inbox / notes    │ 278
├────────────────────────────────────────────┤
│ footer: source / refresh cadence / status  │ 56
└────────────────────────────────────────────┘
```

CSS 尺寸建议：

- viewport shell: `width: 758px; height: 1024px`
- padding: `24px`
- gap: `12px`
- status rail: `64px`
- top glance row: `210px`, two equal columns with a `12px` gap
- headline: `320px`
- detail: `278px`
- footer: `56px`

布局决策：

- 复用原仓库的四槽语义：top-left/top-right 是 glance，middle 是 headline，bottom 是 detail，status/footer 始终可见。
- 不照搬原仓库 `540x960` 的像素尺寸；只复用信息架构。
- `ai-status` 是 AI 会话状态，默认属于顶部 glance；不要把 AI 状态塞进 `focus`。
- `focus` 是用户当前专注任务，默认属于 headline。
- `ai-tasks` 是多个 AI 任务计数，默认属于 detail。
- 历史竖排 `focus -> weather -> calendar -> todo` 只作为 Phase 1 MVP 记录和 fallback 思路；当前本地默认页面已改为 role-based CSS grid。

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

- `ai-status`: 会话名、模型、当前 AI 任务、context 进度；不展示长日志。
- `focus`: 一个当前任务 + 一个大倒计时/状态 + 一行说明。
- `weather`: 当前温度最大，预测最多 2 天。
- `calendar`: 最多 4 个事件。
- `todo`: 最多 5 个任务。
- `ai-tasks`: running / waiting / blocked / completed_today 四个计数。

超过数量时由数据生成端裁剪，不在 UI 里滚动。

## 8. 数据更新策略

### 8.1 首版

使用静态 `widgets.json`：

- 手动编辑也能工作。
- Agent 可以直接改这个文件。
- cron 可以定时生成这个文件。
- 网页每 `300s` 拉取一次。
- Phase 1 先用示例数据判断展示效果；Phase 3 已开始接入真实数据源。

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

状态：已完成。Phase 1 原始实现位于 `web/`，使用静态 `widgets.json` 渲染 `focus`、`weather`、`calendar`、`todo` 四个 demo widget。Phase 3 本地代码已在该基础上升级为 role-based layout，并新增 `ai-status`。

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
- 复用现有 schema 字段命名。当前已完成，保留 `updated_at`、`layout`、`refresh_seconds`、`widgets`，并在 Phase 3 本地资产中加入 `ai-status` 和 role-based slot 命名。
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
- 2026-06-01 更新：Codex 内置 Browser 会生成 `.playwright-mcp/` 本地 QA 快照；该目录不属于项目状态，已加入 `.gitignore` 和 plan freshness hook ignore 列表。

### Phase 3 — 数据源接入

目标：让页面显示真实日常数据，并把最终展示集合从 Phase 1 demo widget 校正到原仓库的角色化 widget 模型。

状态：进行中；weather slice 已完成。第一个真实数据源为 Shenzhen weather，使用公开 `wttr.in` JSON 接口；自动更新由服务器 systemd timer 执行。`ai-status`、`ai-tasks` + role-based layout slice 已在本地代码落地并同步到 live runtime：`web/index.html` 增加 AI Status 和 AI Tasks slot，`web/app.js` 支持 `renderAiStatus()` / `renderAiTasks()`，`web/styles.css` 使用 role-based grid，`web/widgets.example.json` / `web/widgets.json` 已加入 `ai-status` 和 `ai-tasks` 示例。显式低敏写入入口 `scripts/update_ai_session.py`、`scripts/update_focus.py`、`scripts/update_todo.py`、`scripts/update_calendar.py` 已完成本地实现。当前 live HTTPS Basic Auth gate 和 authenticated live Browser layout gate 已通过。

当前设计判断：

- 原仓库的布局理念优于历史竖排布局：glance / headline / detail / status 分工更清楚。
- 历史竖排布局已完成 MVP 验证，继续作为 fallback 思路；不要在它上面继续堆最终信息架构。
- 本地新版布局已复用原仓库四槽语义，并按 `758x1024` 重新分配 CSS 尺寸。
- `focus` 继续表示用户当前专注任务；`ai-status` 表示 AI 当前会话状态；`ai-tasks` 表示多个 AI 任务计数。

优先级：

1. `weather`: `wttr.in` Shenzhen 公开接口，先跑通自动更新流程。
2. `ai-status`: 当前 Codex/AI 会话信息。本地 demo 字段已接入；真实写入方式应由 Codex 工作流显式生成裁剪后的低敏字段，不由 weather/timer refresh 自动采集。
3. `focus`: 当前用户专注任务，显式写入裁剪后的 `task`、`big_text`、`subtitle`。
4. `ai-tasks`: running / waiting / blocked / completed_today 计数。
5. `todo`: 显式写入裁剪后的 `title` 和最多 5 条 `{text, tag}`，暂不接 Reminders / Notion 原始记录。
6. `calendar`: 显式写入裁剪后的最多 4 条 `{start, title, end}`，暂不接系统日历 / Google Calendar 原始记录。

验收：

- 每个数据源失败时只影响对应 widget。
- 失败 widget 显示 stale，不影响整页。
- `ai-status` 和 `focus` 语义不能混用。
- 新布局必须继续满足 `758x1024` 无滚动、无重叠，并默认使用 Codex 内置 Browser 验收。
- 静态 contract 必须保证 `ai-status` 存在于 `widgets.example.json`，slot 为 `glance-right`，并且前端存在 `widget-ai-status` 和 `renderAiStatus()`。
- 静态 contract 必须保证 `ai-tasks` 存在于 `widgets.example.json`，slot 为 `detail-left`，字段为 `running` / `waiting` / `blocked` / `completed_today` 四个低敏计数，并且前端存在 `widget-ai-tasks` 和 `renderAiTasks()`。

当前 Phase 3 weather 验收：

- `scripts/update_weather.py` 只更新 `weather` widget，并保留其他 widget，包括 `ai-status`、`focus`、`ai-tasks`、`calendar`、`todo`。
- 如果文档缺少 weather widget，`scripts/update_weather.py` 会按 role-based layout 在 `glance-left` 插入 weather，而不是旧 slot `top-right`。
- 成功时 weather widget 写入 `location=Shenzhen`、`source=wttr.in`、`updated_at`、`current`、`forecast`、`stale=false`。
- 失败时保留上一份 weather 值，设置 `stale=true`，不清空页面。
- 服务器自动更新由 `ai-desk-card-weather.timer` 触发，每 30 分钟运行一次。
- live 验收：`ai-desk-card-weather.service` 已成功运行，`widgets.json` 显示 Shenzhen weather，Codex 内置 Browser 认证访问页面显示 `Shenzhen · wttr.in` 和当前温度。
- 修复记录：weather service 作为 root 原子写入时必须保持 `widgets.json` 为 `0644`，否则 Caddy 会对 `/widgets.json` 返回 `403`。
- 部署文档已记录 weather timer、失败隔离和 `0644` 权限要求。

当前本地 role-based / ai-status / ai-tasks 验收:

- `scripts/web_update.py` 生成 `weather`、`ai-status`、`focus`、`ai-tasks`、`calendar`、`todo`，slot 分别为 `glance-left`、`glance-right`、`headline`、`detail-left`、`detail-middle`、`detail-right`。
- `scripts/test_web_update.py` 已覆盖 `ai-status` 与 `focus` 语义分离。
- `scripts/test_web_update.py` 已覆盖 `ai-tasks` 四个低敏计数字段。
- `scripts/update_ai_session.py` 只更新 `ai-status` 和 `ai-tasks`，保留 weather/focus/calendar/todo；输入字段限制为 `session_name`、`model`、`task`、`context.used`、`context.limit`、`elapsed_seconds` 和四个任务计数。
- `scripts/update_ai_session.py` 的调用约定已固化为 manual only：只在有意义的 Codex 工作回合结束或阶段节点显式运行；脚本只写指定 `widgets.json`，不发布 live，不从 cron/hook 自动采集 session state。
- `scripts/test_update_ai_session.py` 已覆盖低敏字段、非 AI widget 保留、CLI manual-only help 文案、CLI 原子写入和 `0644` 权限。
- 2026-06-01 本地 smoke：`scripts/update_ai_session.py --widgets web/widgets.json ...` 成功更新 `ai-status` / `ai-tasks`，保留 weather/focus/calendar/todo，并写入 `0644` 的完整 JSON。
- `scripts/update_focus.py` 只更新 `focus`，保留 weather/ai-status/ai-tasks/calendar/todo；输入字段限制为 `task`、`big_text`、`subtitle`。
- `scripts/test_update_focus.py` 已覆盖 focus 裁剪字段、非 focus widget 保留、CLI 原子写入和 `0644` 权限。
- 2026-06-01 本地 smoke：`scripts/update_focus.py --widgets web/widgets.json ...` 成功更新 `focus`，保留 weather/ai-status/ai-tasks/calendar/todo，并写入 `0644` 的完整 JSON。
- `scripts/update_todo.py` 只更新 `todo`，保留 weather/ai-status/focus/ai-tasks/calendar；输入字段限制为 `title` 和最多 5 条 `{text, tag}`。
- `scripts/test_update_todo.py` 已覆盖 todo 裁剪字段、最多 5 条、非 todo widget 保留、CLI manual-only help 文案、CLI 原子写入和 `0644` 权限。
- 2026-06-01 本地 smoke：`scripts/update_todo.py --widgets web/widgets.json ...` 成功更新 `todo`，保留 weather/ai-status/focus/ai-tasks/calendar，并写入 `0644` 的完整 JSON。
- 2026-06-01 本地 Browser 验收：todo 更新为 3 条 `{text, tag}` 后，Codex 内置 Browser `758x1024` 下 `scrollHeight=1024`、`clientHeight=1024`，六个 widget 均渲染，检查范围内无内部 overflow。
- `scripts/update_calendar.py` 只更新 `calendar`，保留 weather/ai-status/focus/ai-tasks/todo；输入字段限制为最多 4 条 `START|TITLE|END`，输出为 `{start, title, end}`。
- `scripts/test_update_calendar.py` 已覆盖 calendar 裁剪字段、最多 4 条、非 calendar widget 保留、malformed event 拒绝、CLI manual-only help 文案、CLI 原子写入和 `0644` 权限。
- 2026-06-01 本地 smoke：`scripts/update_calendar.py --widgets web/widgets.json ...` 成功更新 `calendar`，保留 weather/ai-status/focus/ai-tasks/todo，并写入 `0644` 的完整 JSON。
- 2026-06-01 本地 Browser 验收：calendar 更新为 3 条 `{start, title, end}` 后，Codex 内置 Browser `758x1024` 下 `scrollHeight=1024`、`clientHeight=1024`，六个 widget 均渲染，检查范围内无内部 overflow。
- 2026-06-01 本地 Browser 验收：focus 更新为 `Define focus update boundary` 后，Codex 内置 Browser `758x1024` 下 `scrollHeight=1024`、`clientHeight=1024`，六个 widget 均渲染，检查范围内无内部 overflow。
- `scripts/test_web_static_contract.py` 已覆盖静态资产中的 `ai-status` / `ai-tasks` contract 和 role-based grid。
- `web/styles.css` 当前 role-based grid 为 `64px 210px 320px 278px 56px`，对应 status、glance、headline、detail、footer 五段。
- `web/styles.css` 当前 detail row 为三列：`180px minmax(0, 1fr) minmax(0, 1fr)`，用于同时显示 `ai-tasks`、`calendar`、`todo`。
- 2026-06-01 本地测试通过：`python3 -m unittest discover -s scripts -p 'test_*.py'`。
- 2026-06-01 Codex 内置 Browser 本地验收通过：`758x1024` 下 `scrollHeight=1024`、`clientHeight=1024`，`Weather`、`AI Status`、`Focus`、`AI Tasks`、`Calendar`、`Todo` 均渲染，检查范围内无内部 overflow。
- 2026-06-01 fetch 失败隔离通过：请求缺失 `widgets.json` 时页面保留已渲染内容，`status-label` 显示 `status: offline`。
- 2026-06-01 `web/README.md` 已同步为 role-based layout 检查说明，默认检查 widget 改为 `weather`、`ai-status`、`focus`、`ai-tasks`、`calendar`、`todo`。
- 2026-06-01 live sync 已执行：`index.html`、`styles.css`、`app.js`、`favicon.svg`、`widgets.json` 同步到 `/srv/ai-desk-card-online/`，备份为 `/srv/ai-desk-card-online.backups/web-before-role-20260601220821.tgz`。
- 2026-06-01 live SSH 内容校验通过：`widgets.json` 为 `weather`、`ai-status`、`focus`、`ai-tasks`、`calendar`、`todo`，`ai-status` slot 为 `glance-right`，`ai-tasks` slot 为 `detail-left`。
- 2026-06-01 live HTTPS Basic Auth gate 通过：`http://112.74.73.134/` 返回 HTTPS redirect；未认证 `https://112.74.73.134/`、`/widgets.json`、非运行文件和路径穿越探测返回 `401`；认证后 `/` 和 `/widgets.json` 返回 `200`，`/README.md`、`/widgets.example.json` 和路径穿越探测返回 `404`；响应包含 `Cache-Control`、CSP、`Referrer-Policy`、HSTS、`X-Content-Type-Options`。
- 2026-06-01 live TLS gate 通过：`openssl s_client` 显示 `Verification: OK`，证书 SAN 包含 `IP Address:112.74.73.134`。
- 2026-06-01 authenticated live Browser layout gate 通过：通过本地临时 Basic Auth proxy 读取 live HTTPS runtime assets，Codex 内置 Browser `758x1024` 下 `scrollHeight=1024`、`clientHeight=1024`，`Weather`、`AI Status`、`Focus`、`AI Tasks`、`Calendar`、`Todo` 均渲染，检查范围内无内部 overflow。
- 2026-06-01 `deploy/README.md` 已同步 role-based live 发布、HTTPS Basic Auth gate、authenticated live Browser layout gate、远程备份路径、`update_ai_session.py` manual-only live update 边界、`update_focus.py` live update 边界、`update_todo.py` live update 边界和 `update_calendar.py` live update 边界。
- 2026-06-01 `web/README.md` 已同步 `update_ai_session.py` manual-only 调用约定、`update_focus.py` 裁剪字段边界、`update_todo.py` 裁剪字段边界和 `update_calendar.py` 裁剪字段边界。
- 2026-06-01 live low-sensitive smoke 发布完成：本地 `web/widgets.json` 中的 focus/todo/calendar smoke 字段经人工边界检查后同步到 `/srv/ai-desk-card-online/widgets.json`；发布前远端备份为 `/srv/ai-desk-card-online.backups/widgets-before-smoke-20260601224034.json`。
- 2026-06-01 live smoke 字段校验通过：远端 `widgets.json` 只包含 `weather`、`ai-status`、`focus`、`ai-tasks`、`calendar`、`todo` 的裁剪展示字段；不含 raw logs、source IDs、meeting links、attendees、transcripts、tokens 或密钥。
- 2026-06-01 live smoke HTTPS Basic Auth gate 通过：`deploy/scripts/verify_ip_https.sh` 确认 HTTP 跳转 HTTPS，未认证 runtime / 非 runtime 路径返回 `401`，认证后 `/` 和 `/widgets.json` 返回 `200`，认证后非 runtime 文件和路径穿越探测返回 `404`。
- 2026-06-01 live smoke authenticated Browser gate 通过：通过本地临时 Basic Auth proxy 读取 live HTTPS runtime，Codex 内置 Browser `758x1024` 下 `scrollHeight=1024`、`clientHeight=1024`、`scrollWidth=758`、`clientWidth=758`，六个 widget label 均存在，检查范围内无内部 overflow；截图存于 `output/browser/live-smoke-2026-06-01-2240.png`。
- 2026-06-01 `deploy/README.md` 已补充 post-smoke live 快照，记录 JSON-only sync 的备份路径、字段边界、HTTPS Basic Auth gate 和 authenticated Browser gate。

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

当前 live 入口已使用 IP HTTPS + Caddy Basic Auth。它适合先保护整个静态站点和 `widgets.json`，不需要立刻引入后端账号系统。

如果内容涉及日程、消息、todo、focus 等隐私信息，优先级如下：

1. 部署层 Basic Auth：由 Caddy 要求输入用户名和密码。当前已采用，适合自有服务器和单用户设备。
2. 服务端登录：后端校验 session/cookie 后再返回 `widgets.json`。当需要账号、细粒度权限、网页内登录状态或多个用户时再做。
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

- 静态部署设置 `Cache-Control: no-store` 或等价策略。
- URL 加时间戳。

## 13. 下一步

Phase 1、Phase 1.5、Phase 2 和 Phase 2.1 已完成；Phase 3 已开始。weather slice 已完成并已部署自动更新。本地 `ai-status` / `ai-tasks` + role-based layout slice 已实现并同步到 live runtime，显式低敏写入脚本已实现，并通过静态/生成器测试、本地 Codex 内置 Browser `758x1024` 验收、live HTTPS Basic Auth gate 和 authenticated live Browser layout gate。focus/todo/calendar 的低敏 smoke 数据已同步到 live 并完成同一套 gate。

不要把 token 或原始私密数据写入 `widgets.json`。Phase 3 只能写入页面渲染所需的裁剪后字段。

建议顺序：

1. 根据真实设备观感决定是否把 detail 三列改为 compact mode 或轮换 detail widget。
2. 若真实设备 detail 区显得拥挤，优先在 `web/styles.css` 做最小 compact 调整，不引入新框架或后端。
3. 每次 Codex 工作结束前，让 `.codex/hooks/ensure_plan_updated.py` 检查 `PLAN_web.md` 是否已更新。
