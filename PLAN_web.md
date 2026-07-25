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

**Phase 5：真实数据接入与安全发布已完成并归档。Phase 6：可配置 Focus 与视觉对齐已完成
并归档。Phase 7：可靠性与操作体验已完成规划，等待新会话按任务顺序实施。**

已完成：

- 静态网页和 role-based 六 widget 布局。
- `758x1024` 无滚动 Browser 验收。
- JSON 读取失败时保留旧内容并显示 offline。
- IP HTTPS、Caddy Basic Auth 和静态文件访问边界。
- Shenzhen weather 每 30 分钟自动更新。
- `ai-status`、`ai-tasks`、`focus`、`todo`、`calendar` 的低敏手动写入脚本。
- Codex quota 的本地 rollout JSONL 读取方案已确定，使用 agent-battery 的本地解析思路。
- 本地测试、plan freshness hook 和 live 发布流程。
- Linear、Apple Calendar、Codex metadata 的确定性只读 adapter。
- 共享 JSON/privacy contract、本地 preview/publish orchestrator、远端锁定 installer。
- Phase 5 曾实现完整换行与极端内容整行省略；Phase 6 已按用户新决策改为完整数据保留、
  展示层最多两行并显示 `...`，正常五条 todo 继续保留。
- credential-free LaunchAgent 模板与有界 latest-status wrapper。
- Phase 5 的 source/projection/privacy、退出码、双层锁、remote install/rollback、
  LaunchAgent 以及完整文本 overflow 规则已固化到 backend/frontend Trellis code-spec。

Phase 5 closeout：

1. 用户选择的两个 Calendar exact names 已写入本机 ignored `0600` 配置；macOS
   Calendar Full Access 已授予 Codex，permission preflight 已通过。
2. redacted preview 和一次真实 owned-widget publish 已完成，remote JSON、backup、权限
   和 weather preservation 已核验。
3. authenticated HTTPS gate 已在有界重试版脚本上完整通过；LaunchAgent 已安装，连续
   三次 status update 已完成，其中 `18:22:32` 与 `18:27:39` 两个自然 tick 相隔 307 秒；
   latest status `0600` 且无敏感字段，publish 与 weather service 通过共享锁串行成功。
   用户已确认物理底边、无重叠和无 ellipsis；sleep/wake 实机 gate 已由用户显式豁免。
   验证脚本只对连接错误做有界重试，不放宽 HTTP status 断言。
   后续一次 tick 出现 Linear 瞬时 stale 时按 last-known-good 正常发布，紧接的只读
   source-check 和 `18:38:07` 自然 tick 均恢复 `linear=ok`；该状态作为故障隔离与无人值守
   恢复证据记录，不误报为所有 tick 全 source fresh。当前 `pmset` 日志没有可关联的安装后
   sleep/wake 事件；用户已明确豁免该直接实机 gate，因此不把它记录为误导性的通过。

Code-spec checkpoint 已记录在 Phase 5 evidence；它不替代上述 authenticated HTTPS、
真实设备或 LaunchAgent gate。
后续只读复核仍显示 HTTP `301`、未认证 HTTPS `401`、Caddy/weather timer active、live
JSON `0644`、六个 widget 完整且无 stale widget；LaunchAgent 已安装并持续运行。

Phase 6 已确认调整：`todo` 的真实 source of truth 仍为 Linear；`focus` 改为最终投影层的
可配置 headline slot，不再由 Linear adapter 同时拥有。缺省配置仍取最终 todo 第一项，保持
现有生产行为；可选来源严格限定为 `todo.first`、`calendar.next`、`ai-status.task`、
`weather.current` 和 `manual`。配置位于本机
`~/.config/ai-desk-card-online/focus.json`，不传输到服务器；任意 selector、脚本或模型路由
均不允许，存在但无效的配置必须在 SSH/发布前 fail loud。
候选集为本人在 `CODE` / `LIFE` 中的 `started` / `unstarted` issue；排除 backlog、
completed、canceled 和 parent/container issue，但保留子任务及无 due date 的可执行 issue。
排序固定为 Linear priority、due date（逾期最早、今日、未来、无日期）、`started`、
`updatedAt`、稳定 identifier；第一项同步为 focus。
Linear 认证使用 `LINEAR_API_KEY`：优先读取进程环境，fallback 到仓库根目录
`.env.local`。该文件已确认 Git ignored、未跟踪且权限为 `0600`；任何日志不得输出值。
`calendar` 的真实来源确定为本机 Apple Calendar，通过只读 `osascript` adapter 获取；
只允许 title/start/end/all-day 投影，禁止 location、notes、UID、attendee 和 URL。
Calendar 必须配置显式 name allowlist；缺失或为空时 fail loud，不能回退到读取全部。
事件窗口为本地时间“现在到明天 `23:59`”；排除已结束/canceled，ongoing 优先，
all-day 与 timed event 共用最多四条。
`ai-status` / `ai-tasks` 覆盖全部本机 Codex task：组合只读 thread/goal metadata 与
rollout 生命周期事件，不读取 `logs_2.sqlite`、prompt、response、preview 或完整 transcript。
Codex state 规则已确认：unmatched `task_started` 只有在最近 30 分钟仍有 metadata 活动时
算 `running`；goal 的 blocked/limited 状态算 `blocked`；active/paused goal 或最近 24 小时
结束的 no-goal task 算 `waiting`；`completed_today` 按 distinct task 计数。

已核对旧仓库 `/Users/ethereal/Documents/Code/ai-desk-card` 的真实实现：可复用的是
per-widget schema、读取当前状态后更新、last-known-good cache、freshness/TTL 和可见调度
这些机制；不能直接复用的是 loopback daemon、Pillow/固件传输和 cron 唤起 headless AI
CLI 的刷新路线。旧仓库只有 Reminders 的确定性 todo adapter，Calendar 没有对应 adapter，
`ai-status` / `ai-tasks` 也只有 payload schema，定时 refresh 逻辑会明确跳过它们。因此本项目
采用纯 Python adapter + 单一本机 orchestrator + SSH locked atomic merge，不依赖模型判断。

原有的 contract drift（producer 允许 5 条、renderer 只渲染 4 条）已在 Phase 5 修正：
renderer、example、shared contract 和 Browser gate 统一为 5 条；正常 bounded fixture
显示 `5/5`，极端 fixture 只移除最低优先级整行并显示实际 `selected/total`。

Phase 6 将 Phase 5 的完整文字显示策略替换为两行视觉上限：Focus、AI 状态、weather、
forecast、calendar 和 todo 的用户/source 文本保留完整 JSON 与 DOM 值，但超过两行时在
展示层显示 `...`；短文本不得误加省略号。正常五条 todo 必须全部保留，整行移除只作为
整个 widget 仍溢出的最终保护。主信息与数值居中，calendar/todo/forecast 列表继续左对齐并
统一列宽；header、divider、AI 计数格和 footer 使用一致的 grid/flex 对齐规则。

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
| ai-status / ai-tasks | `scripts/source_codex_tasks.py` + orchestrator | 已实现，live preflight 通过 |
| Codex quota | `scripts/update_codex_usage.py` parser + orchestrator | 已实现；当前真实样本 stale |
| focus | `scripts/source_linear.py`，取最终 todo 第一项 | 已实现，live preflight 通过 |
| todo | `scripts/source_linear.py` | 已实现，live preflight 通过 |
| calendar | `scripts/source_apple_calendar.py` | 已实现，allowlist/preflight 通过 |
| 统一 preview/publish | `scripts/refresh_dashboard.py` | 已实现，真实 publish gate 通过 |
| 完整 demo | `scripts/web_update.py` | 仅用于重置 demo |

旧 manual-only updater 的含义：

- 只在有意义的工作回合结束或明确阶段节点调用。
- 脚本只修改指定的 `widgets.json`，不自动发布 live。
- live 发布仍通过显式 `scp` 和 `sudo install -m 0644` 完成。
- 不从 hook、cron 或本机进程自动抓取 AI session、todo 或 calendar 原始数据。

Phase 5 production 路径不再使用这些手工参数；统一入口只输出 source health 和 changed
widget type。配置错误在 SSH 前终止；可恢复 source failure 保留对应 last-known-good 并标记
stale。远端 installer 在 `/run/lock/ai-desk-card-widgets.lock` 内重新读取 live JSON，保留
weather，做 changed-only backup、`0644` 原子安装、验证和 rollback。weather systemd unit
通过 `/usr/bin/flock` 使用同一 lock。

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
- 唯一布局结果为保留 detail 三列；Phase 6 使用统一两行 ellipsis，主信息居中，
  forecast/calendar/todo 仍按稳定列左对齐，整行省略只保留为最终 overflow 保护。
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

### Phase 7：可靠性与操作体验

状态：**规划完成，尚未实施**

Trellis parent task：
`.trellis/tasks/07-25-phase7-reliability-operator-ergonomics/`。
规划通过 `agent/phase7-planning-handoff` 分支上的 draft PR 交接，目标分支为 `main`。
新会话不得直接启动 parent，必须按以下顺序逐个完成并归档 child task：

1. `07-25-phase7-codex-quota-freshness`：恢复可信的 Codex quota freshness；若不存在
   权威当前来源，则保留 stale 并记录 evidence-backed no-go，不能放宽 stale threshold。
2. `07-25-phase7-focus-config-cli`：为现有 allowlisted Focus 配置增加本机 `get`、`set`、
   `reset` CLI；只原子写入私有配置，不发布、不修改 `widgets.json`。
3. `07-25-phase7-certificate-docs`：使用只读 live evidence 修正文档，记录
   `snap.certbot.renew.timer` 和 deploy hook 机制，不固化证书到期日、不修改服务器状态。
4. `07-25-phase7-plan-current-state`：在前三项形成 durable outcome 后，将本计划压缩为
   单一 current-state source of truth，保留约束、风险和 archive links。

完整执行约束和新会话入口见 parent task 的 `handoff.md`；四个 child 均保持
`planning`，不得把本次规划发布误记为 Phase 7 实现完成。

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

当前最高优先级是 Phase 7 的 `07-25-phase7-codex-quota-freshness`。新会话从
`.trellis/tasks/07-25-phase7-reliability-operator-ergonomics/handoff.md` 开始，继续
`agent/phase7-planning-handoff`，只启动 quota child；Focus CLI、certificate docs 和
plan cleanup 按 Phase 7 章节所列顺序后续执行。

Phase 5 本地实现、source permission、live cutover 与 scheduler gate 均已关闭。生产路线保持
“真实 source adapter -> 隐私裁剪与失败隔离 -> 锁定发布 -> 可观察调度”，不再把
manual/smoke updater 当作生产 source。

Phase 6 closeout（completed and archived）：
`.trellis/tasks/archive/2026-07/07-23-phase6-configurable-focus-visual-alignment/`。范围仅包含两行 ellipsis、
allowlisted Focus 投影和现有六 widget 的排版对齐；不增加网页编辑器、后端 API、动态 widget、
source 写回或任意字段路由。完成门槛包括三种视口的短/长中文/英文/长 token Browser gate、
完整数据与 DOM 保留、五条 todo、无滚动/重叠/overflow、live publish/weather preservation、
LaunchAgent 后续 tick，以及真实设备确认或明确 waiver。

2026-07-23 Phase 6 本地实现 checkpoint：新增 strict bounded Focus config/resolver，缺省
`todo.first`，支持 `calendar.next`、`ai-status.task`、`weather.current`、`manual` 与短字段
override；Linear production adapter 只拥有 todo，Focus 在 source/LKG/quota merge 后生成。
两行 clamp、top/header/detail/footer alignment 和 flat equal AI metrics 已完成。内置 Browser
使用公开隔离 fixture 验证 `758x1024`、`740x951`、`467x600`：五条 todo、两条 forecast、
长中文/英文/无断点 token 均显示两行 `...`，完整 DOM 值保留，三列 header 同高，四个 AI
计数格等宽等高，page/widget 无 overflow，底边完整。短文本 fixture 保持普通 todo 标题和
Calendar 结束时间完整可见；临时 Browser server 已停止。

最终本地修订还将 Calendar 的结束时间固定在右侧列、Todo tag 保持内联，避免普通短标题被
过早省略；短文本五条 todo 和 Calendar 结束时间在截图中完整可见，长 fixture 仍仅在超过
两行时显示 `...`。最新全套测试为 `86 passed`，静态/compile/plist/shell/contract/privacy/
Trellis/plan/diff gate 均通过；live owned publish、静态 bundle hash、LaunchAgent 后续 tick、
weather preservation、远端权限、timer 和证书 transport 均已只读复核。2026-07-25 用户在
实体设备上确认两行省略可读、Focus/各模块对齐正常且底边完整；AC1-AC9 全部通过。
最终 Trellis closeout：实现 commit 为 `9753aba`，实体设备验收记录为 `7cf32a1`，task 由
`24af5bf` 归档，Session 5 journal 由 `8f7fde6` 记录；task status 为 `completed`，当前无
active task。

已归档 Trellis task：
`.trellis/tasks/archive/2026-07/07-23-phase6-configurable-focus-visual-alignment/`。
`.trellis/tasks/archive/2026-07/07-23-phase5-daily-publish-workflow/`。

1. Calendar exact-name allowlist、Full Access 和同一 Python/osascript permission
   preflight 已完成。
2. 完整 `--preview` 与一次真实 `--publish` 已完成；remote JSON、mode、backup 和
   weather preservation 已通过；authenticated HTTPS runtime/404/TLS/IP SAN gate 已通过。
3. `758x1024`、`740x951`、`467x600` 与真实设备的完整文字、五条正常 todo、极端
   `selected/total`、首次加载 fit 和物理底边均已复核。
4. LaunchAgent 已安装并通过连续 5 分钟 run、non-overlap、latest status 和共享锁 gate；
   直接 system sleep/wake 观察已由用户显式豁免，task 已 finish/archive。

暂不做：网页内编辑、后端 API、数据库、向来源系统写回、镜像完整第三方记录、或把
任何 source/Basic Auth/SSH 凭据写入仓库。

2026-07-23 本地 checkpoint：77 个 unittest、Python compile、JavaScript syntax、plist
lint 和 example contract 通过；真实 Linear 返回 5 个投影 todo，Codex metadata adapter
成功，quota 只有旧 weekly 样本并正确标记 stale；Calendar allowlist 与 Full Access 已
配置，bounded permission preflight 返回 ok（当前窗口 `0/0`）。Browser 已验证
`758x1024` 正常
example 可显示五条 todo 和两条
forecast，六 widget 无内部 overflow；`740x951` / `467x600` 自动 fit、无 page scroll、
normal URL 仍显示 `source: widgets.json`，底边完整。极端文本 gate 和 physical/live cutover
中，288 字符无断点 token 和长中文主标题已做到 widget/page 零 overflow、无 `...`；长
todo fixture 只保留最高优先级完整前缀并显示 `2/8`。physical/live cutover 已完成。
Forecast 的 `Today/Tomorrow` 也已改为完整单词布局，不再在词中间断开。
最近检查还修复了 quota last-known-good 保留、stale partial exit、Python 3.8 remote
syntax、严格 nested allowlist 和超限 Codex thread fail-loud 行为。

Live cutover checkpoint：Phase 5 静态 UI bundle 已备份并发布，local/live hash 一致且
mode 为 `0644`；weather service 已改用共享 lock，手动 oneshot `Result=success`、timer
仍 active、weather fresh；HTTP/HTTPS 未认证表面保持 `301/401`。远端 installer 也已在
Python 3.8 上针对 live JSON 临时副本通过 weather preservation、backup 和 mode gate。
证书 SAN 为 `IP Address:112.74.73.134`，当前有效期到 `2026-07-28T03:57:26Z`。真实
owned-widget publish、authenticated HTTPS 和 LaunchAgent 连续运行 gate 已完成；设备底边
已由用户确认，直接 system sleep/wake 观察由用户显式豁免。PRD completion audit 为
`24/24`，并在 Phase 5 evidence 中记录了该 waiver 及其证据边界。

最新质量检查：78 个 Python tests、静态 contract tests、`node --check`、
`git diff --check` 和 Trellis task validation 通过；本地 `--source-check` 在 allowlist
配置后返回 Calendar ok，一次 redacted preview 和真实 owned-widget publish 已完成；
in-app Browser 对 IP HTTPS 返回 `ERR_BLOCKED_BY_CLIENT`，不计作 authenticated live
Browser 通过；authenticated shell gate 已完整通过，物理设备作为最终 visual authority。
远端只读核验
确认五个静态资源和 `widgets.json` 为 `0644`、weather timer 为 enabled/active 且最近
service result 为 success，公网仍为 HTTP `301`、未认证 HTTPS `401`，证书 SAN 仍为该 IP。
最终 installer regression 还覆盖了原子替换完成后若目录同步报错的恢复路径：即使写函数
未正常返回，也会从本次 changed-only backup 恢复 live JSON，而不会跳过 rollback。
