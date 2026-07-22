# AI Desk Card Web Plan

## 1. 目标与当前结论

本项目把 `/Users/ethereal/Documents/Code/ai-desk-card` 的产品原则和 widget
语义迁移到浏览器路线，为 `758x1024` 竖向墨水屏提供一个低频、稳定、
可远程更新的信息卡片。

当前架构保持：

```text
Agent / cron / scripts
        |
        v
web/widgets.json
        |
        v
static web app
        |
        v
e-ink browser
```

当前处于 **Phase 5：日常更新工作流规划**。

已完成：

- 静态网页和 role-based 六 widget 布局。
- `758x1024` 无滚动 Browser 验收。
- JSON 读取失败时保留旧内容并显示 offline。
- IP HTTPS、Caddy Basic Auth 和静态文件访问边界。
- Shenzhen weather 每 30 分钟自动更新。
- `ai-status`、`ai-tasks`、`focus`、`todo`、`calendar` 的低敏手动写入脚本。
- Codex quota 的本地 rollout JSONL 读取方案已确定，使用 agent-battery 的本地解析思路。
- 本地测试、plan freshness hook 和 live 发布流程。

当前优先问题：

1. 把现有各 widget 的本地更新和手工 `scp` 发布收敛成一个可审计、可回滚的日常流程。
2. 在实现前明确自动化边界：默认保持显式低敏输入，不直接接入 Reminders、Calendar
   或原始 AI session。

2026-07-23 Phase 4 closeout：

- 浏览器重启、整机重启、自动 fit、六 widget 和 `T+65m` 物理恢复报告通过；
  设备专用 `viewport=1` 诊断仍显示 `source: widgets.json`，记录为非阻塞限制。
- `T0=2026-07-21T15:01:39+08:00` 后，服务器侧观察持续 `26h55m`：weather timer
  57 次执行、52 次 fresh、5 次受控 stale fallback、0 次 unit failure，最终恢复 fresh。
- 运行时 bundle hash、六 widget、quota contract、Caddy/timer 和证书 SAN/date 的
  服务器证据均保留；本地 43 个 Python tests、Trellis validate 和 diff check 也已通过。
- 用户要求停止后续检查，因此最终物理设备 reload、最新证书在设备上的再次接受、以及
  最终 authenticated HTTPS `200/404` gate 均标记为 **未验证**，不宣称 Phase 4 全部通过。

## 2. 不变约束

### 2.1 产品约束

- 目标设备视口为 `758x1024`（宽 x 高）。
- 页面是 ambient display，不是第二块交互屏。
- 首屏必须无纵向滚动、无缩放依赖、无文字重叠。
- 无动画、transition、hover-only 内容、渐变和装饰阴影。
- 保持高对比、大字体、固定布局和低信息密度。
- 刷新频率保持在 `5m-30m`，不承载实时行情、视频或持续动画。

### 2.2 技术约束

- MVP 继续使用 HTML、CSS、vanilla JavaScript 和 JSON。
- runtime 数据文件固定为 `web/widgets.json`。
- 不引入 React、Vite、Astro、后端 API 或构建步骤，除非先更新本计划。
- 不依赖原项目固件、PlatformIO、BLE、USB、raw frame、daemon 或 Pillow
  渲染链路。
- 服务端代码如有必要，放入 `web-server/`，不能混入 `web/`。
- 部署配置放入 `deploy/`，不得包含密码、token、私钥或服务器生成文件。

### 2.3 隐私约束

- `widgets.json` 只保存页面渲染需要的裁剪字段。
- 禁止写入 token、密钥、transcript、raw log、source ID、meeting link、
  attendee、私密备注或原始第三方记录。
- Codex quota 只写入 5h/7d 的剩余百分比、reset 时间、来源和更新时间；
  不写入 rollout 原文、session 路径、账户标识或 token 明细。
- 访问控制必须由 Caddy 或后端完成，不能使用仅隐藏 DOM 的前端假解锁。
- 数据源接入默认采用显式字段映射，不直接镜像 Reminders、Notion、
  Calendar 或 AI session 原始数据。

## 3. 当前信息架构

固定 slot 和默认 widget：

| Slot | Widget | 作用 |
| --- | --- | --- |
| `glance-left` | `weather` | 环境状态 |
| `glance-right` | `ai-status` | 当前 AI 会话摘要 |
| `headline` | `focus` | 用户当前专注任务 |
| `detail-left` | `ai-tasks` | AI 任务计数 |
| `detail-middle` | `calendar` | 近期日程 |
| `detail-right` | `todo` | 待办事项 |

语义边界：

- `ai-status` 表示 AI 会话状态，不得与 `focus` 混用。
- `focus` 只表示用户当前要做的事情。
- `ai-tasks` 只展示 `running`、`waiting`、`blocked`、
  `completed_today` 四个计数。
- `calendar` 最多 4 条事件。
- `todo` 最多 5 条事项。
- 列表裁剪由数据生成端完成，前端不提供滚动区域。

当前布局分区：

```text
status rail   64px
glance row   210px
headline     320px
detail row   278px
footer        56px
```

detail row 当前为三列：

```css
180px minmax(0, 1fr) minmax(0, 1fr)
```

该三列布局已通过模拟视口验收，但必须以真实设备观感决定是否保留。

## 4. 数据契约

顶层字段保持稳定：

```json
{
  "updated_at": "2026-06-13T15:30:00+08:00",
  "layout": "dashboard",
  "refresh_seconds": 300,
  "widgets": []
}
```

要求：

- 每次写入生成完整且合法的 JSON。
- 写入成功后更新顶层 `updated_at`。
- 使用原子替换，失败时不得破坏上一份可用文件。
- live `widgets.json` 文件权限保持 `0644`，确保 Caddy 可读。
- 页面使用 cache-busting fetch，并由部署层设置 `Cache-Control: no-store`。
- fetch 失败时保留最后一次成功渲染的数据并显示 offline。
- 单个数据源失败时只标记对应 widget stale，不清空其他 widget。

数据新鲜度：

- `<= 15m`：normal。
- `15m-60m`：stale。
- `> 60m`：old。
- fetch 失败：offline。

## 5. 更新入口

| 数据 | 更新方式 | 当前状态 |
| --- | --- | --- |
| weather | `scripts/update_weather.py` + systemd timer | 已自动化 |
| ai-status / ai-tasks | `scripts/update_ai_session.py` | manual only |
| Codex quota | `scripts/update_codex_usage.py` 读取本机 rollout JSONL | 本地自动读取，显式写入 JSON |
| focus | `scripts/update_focus.py` | manual only |
| todo | `scripts/update_todo.py` | manual only |
| calendar | `scripts/update_calendar.py` | manual only |
| 完整 demo | `scripts/web_update.py` | 仅用于重置 demo |

manual-only 的含义：

- 只在有意义的工作回合结束或明确阶段节点调用。
- 脚本只修改指定的 `widgets.json`，不自动发布 live。
- live 发布仍通过显式 `scp` 和 `sudo install -m 0644` 完成。
- 不从 hook、cron 或本机进程自动抓取 AI session、todo 或 calendar 原始数据。

Codex quota 使用本地文件方案，不使用 OAuth、`/wham/usage`、CLI RPC/PTY 或远程
usage API。`scripts/update_codex_usage.py` 的读取边界是：

- 扫描 `~/.codex/sessions/**/*.jsonl`，也支持 `--sessions` 指定目录。
- 按文件修改时间倒序，最多读取最近的有限数量文件。
- 每个文件按固定大小从尾部向前分块扫描，跳过较新的空 `rate_limits`，寻找最近的
  有效 `event_msg.token_count` 事件，避免一次性加载完整 rollout。
- 事件时间超过 10 分钟时保留数值但标记 stale，不能因成功解析旧文件而显示 fresh。
- 按窗口时长识别 5h 和 7d，不假设 `primary` 永远是 5h。
- 兼容 `used_percent` / `used_percentage`、`resets_at` / `reset_at` 和
  `window_minutes` / `limit_window_seconds` 的字段差异。
- 只更新 `ai-status` 的 `data.quota`，保留 session/task/context 等其他字段。
- 没有可用事件时保留旧 quota 并标记 stale，不清空页面。

暂不升级为后端 API。只有出现以下需求时才重新评估：

- 多用户和细粒度权限。
- 网页内登录或 session 管理。
- 多个私密数据源需要服务端聚合。
- 静态文件发布无法满足一致性或审计要求。

## 6. 部署边界

当前部署：

- 主机：`myecs`。
- 静态目录：`/srv/ai-desk-card-online`。
- 入口：公网 IP 的 HTTP 跳转 HTTPS。
- HTTPS：Caddy + Let's Encrypt IP short-lived certificate。
- 认证：Caddy Basic Auth。
- runtime 公开范围：认证后的 `/`、静态资源和 `/widgets.json`。
- `README.md`、`widgets.example.json`、路径穿越请求等非 runtime 内容必须返回
  `404`。

证书采用自动续期和 deploy hook 同步，不在计划中记录固定到期日。证书状态是
运行时事实，每次部署或状态检查都必须重新验证。

当前 durable deployment 结论：

- quota-aware role-3 bundle 已发布，运行时仍是静态 `index.html`、`app.js`、
  `styles.css` 和 `widgets.json`。
- 三列 detail layout、visual viewport 自动 fit、4px safe inset、offline fallback 和
  `?viewport=1` 诊断均保留；真实设备首次加载无需 pinch，底边完整。
- Phase 3 的 authenticated HTTPS allowlist 与 privacy gate 已通过；Phase 4 最终未在
  最新续期证书下复跑 authenticated gate，该 residual risk 记录在本计划顶部。
- Phase 3 详细发布、设备和验证证据位于已归档的
  `.trellis/tasks/archive/2026-07/07-12-phase3-real-use-gates/`，不在当前计划重复保存。

## 7. 阶段状态

### Phase 1：静态网页 MVP

状态：**完成**

完成条件：

- 页面读取 `widgets.json` 并渲染。
- `758x1024` 下无滚动和重叠。
- JSON 缺失、字段缺失或 fetch 失败时不白屏。
- 页面每 `refresh_seconds` 重新拉取数据。

### Phase 1.5：公网访问加固

状态：**完成**

完成条件：

- HTTP 跳转 HTTPS。
- 未认证请求不能读取页面和 JSON。
- 认证后 runtime 文件返回 `200`。
- 非 runtime 文件和路径穿越探测不泄露内容。
- 启用 `Cache-Control: no-store`、CSP、HSTS、`Referrer-Policy` 和
  `X-Content-Type-Options`。

### Phase 2：文件写入链路

状态：**完成**

完成条件：

- updater 原子写入完整 JSON。
- updater 保留非目标 widget。
- 写入失败不破坏上一份数据。
- live JSON 更新无需重启 Caddy。

### Phase 2.1：Trellis Codex hook

状态：**完成**

- `.codex/hooks.json` 只注册 Trellis `UserPromptSubmit` hook，运行
  `.codex/hooks/inject-workflow-state.py`。
- 旧 `Stop` plan freshness hook 已于 2026-07-12 从配置移除，避免与 Trellis
  生成配置拼接成无效 JSON。
- `.codex/hooks/ensure_plan_updated.py` 和 `scripts/test_plan_guard.py` 暂时保留为
  手动检查工具，不再由 Codex hook 自动执行。
- `.code-review-graph/`、`output/`、`.playwright-mcp/` 和 Python cache 是可重建的
  本地 QA/分析产物，不代表项目状态变化。
- 2026-07-12 完成 Trellis bootstrap guidelines：`.trellis/spec/backend/` 和
  `.trellis/spec/frontend/` 已按当前 static web、Python updater、JSON contract、
  Browser gate 和部署验证实践补齐，并引用仓库内真实代码示例。

### Phase 3：真实使用验证与数据更新

状态：**完成**

已完成：

- role-based 六 widget 布局。
- weather 自动更新和失败隔离。
- 五类低敏 updater 及其测试。
- Codex quota 本地 rollout parser、5h/7d 窗口归一化和 `ai-status` 展示。
- 2026-07-12 本地 Browser gate：`758x1024` 下页面无滚动，六个 widget 无内部
  overflow，`5h` / `7d` quota 均显示，console 无错误。
- 本地和 live `758x1024` Browser gate。
- focus、todo、calendar 低敏 smoke 发布。
- 真实设备确认 layout viewport `740x951`、visual viewport `467x600`；首次加载无需
  pinch，底边完整，30-50cm 可读且无重叠或明显残影。
- 唯一布局结果为保留 detail 三列；窄列 ellipsis 接受为明确裁剪行为。
- quota-aware assets 和裁剪 JSON 已发布，fresh/stale/unavailable 路径、privacy
  allowlist、authenticated HTTPS 和 physical-device rendering 均通过。
- `07-12-phase3-real-use-gates` 已归档；Phase 3 不再保留实现 gate。

### Phase 4：设备稳定运行

状态：**观察结束，部分验收；用户终止剩余 gate**

已验证：

- 真实设备可通过固定 URL 访问，浏览器重启和整机重启后均恢复。
- `T+65m` 物理报告正常，覆盖多次 5 分钟 refresh 和至少两次 weather update。
- 服务器侧连续观察超过 24 小时；weather 失败时保留 last-known-good，后续自动恢复。

未验证并保留为 residual risk：

- `T+24h` 后的最终物理视觉状态。
- 设备对观察窗口内最新续期证书的 reload 验证。
- 最新证书下的 authenticated HTTPS `200/404` closeout gate。

Phase 4 task 的归档仅表示观察工作按用户指示结束，不表示上述未验证项通过。

## 8. 验证命令

本地测试：

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 .codex/hooks/ensure_plan_updated.py
python3 -m json.tool .codex/hooks.json
```

本地 Browser gate：

```bash
cd web
python3 -m http.server 4173
```

使用 Codex 内置 Browser 在 `758x1024` 检查：

- `scrollHeight <= clientHeight`。
- `scrollWidth <= clientWidth`。
- 六个 widget 均存在。
- widget 内部无 overflow。
- fetch 失败后仍保留内容并显示 offline。

live HTTPS gate：

```bash
export AI_DESK_CARD_AUTH_USER=desk
export AI_DESK_CARD_AUTH_PASSWORD='<live-password>'
deploy/scripts/verify_ip_https.sh
```

live 状态检查还应包括：

```bash
systemctl status caddy
systemctl status ai-desk-card-weather.timer
systemctl status ai-desk-card-weather.service
openssl s_client -connect 112.74.73.134:443 -servername 112.74.73.134
```

不得仅依据配置文件宣布 live 验收通过。

## 9. 下一步

下一步是 **Phase 5：日常更新与安全发布工作流**。当前产品的主要摩擦不是页面能力，
而是 `focus`、`todo`、`calendar`、`ai-status` 和 quota 需要分别运行 updater，再手工
执行 `scp` / `sudo install`；这使桌卡容易长期显示旧信息。

推荐边界：先做一个本机、显式触发的单命令流程，不直接自动抓取第三方原始数据。

1. 复用现有 updater，接收明确的低敏字段；weather 继续由服务器 timer 独立维护。
2. 在临时文件中组合更新，执行 schema、widget allowlist、privacy allowlist 和 JSON
   完整性检查；任何一步失败都不得改动本地基线或 live 文件。
3. 发布前创建远端备份，再原子安装 `widgets.json`，最后只核验非敏感结构、
   `updated_at` 和 HTTP 状态；失败时给出明确错误与回滚路径。
4. 提供 `--dry-run`，默认只展示将变化的 widget/字段，不打印密码、原始 session、
   source ID、meeting link 或其他禁止字段。
5. 用单元测试覆盖无变化、部分 widget 更新、隐私字段拒绝、传输失败和远端安装失败。

暂不做：网页内编辑、后端 API、数据库、常驻本机 daemon、自动读取 Reminders/Calendar
全文、或把 Basic Auth/SSH 凭据写入仓库。

规划阶段唯一需要确认的产品决策是：Phase 5 只降低“显式更新 + 发布”的操作成本，
还是同时接入本机数据源自动采集。推荐前者；后者会显著扩大隐私和平台耦合范围。
