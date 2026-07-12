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

当前处于 **Phase 3：真实使用验证与数据更新完善**。

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

1. 在真实墨水屏设备上确认 detail 三列的可读性，再决定保持三列、使用
   compact mode，还是轮换 detail widget。
2. 将已完成的 Codex quota 本地读取与展示发布到 live，并确认当前 Codex 版本能
   持续产生带有效窗口的 `rate_limits` 事件。

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

最近一次只读核验：**2026-07-12**

- HTTP 返回 HTTPS redirect。
- 未认证 HTTPS 返回 `401`，安全响应头存在。
- Caddy 为 active + enabled。
- weather timer 为 active + enabled，最近一次执行成功。
- live weather 更新时间为 `2026-07-12T22:17:07+08:00`，`stale=false`。
- TLS 证书已自动续期，SAN 为 `IP Address:112.74.73.134`。
- live `index.html` 和 `favicon.svg` 与本地一致；`styles.css`、`app.js` 尚未包含
  Codex quota UI，等待本轮改动完成后显式发布。
- live `ai-status` / `ai-tasks` 仍是 2026-06-01 smoke 数据，尚无 `quota` 字段。

注意：以上是带日期的运行快照，不替代下一次 live gate。

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

状态：**进行中**

已完成：

- role-based 六 widget 布局。
- weather 自动更新和失败隔离。
- 五类低敏 updater 及其测试。
- Codex quota 本地 rollout parser、5h/7d 窗口归一化和 `ai-status` 展示。
- 2026-07-12 本地 Browser gate：`758x1024` 下页面无滚动，六个 widget 无内部
  overflow，`5h` / `7d` quota 均显示，console 无错误。
- 本地和 live `758x1024` Browser gate。
- focus、todo、calendar 低敏 smoke 发布。

剩余 gate：

1. 在真实墨水屏设备记录实际 `window.innerWidth` / `window.innerHeight`。
2. 检查 detail 三列的字号、截断、残影和 30-50cm 阅读体验。
3. 基于实测只选择一种布局：
   - 保持三列；
   - 增加 compact mode；
   - 轮换 detail widget。
4. 选择后更新 CSS、静态 contract 测试和 Browser gate。
5. 将 Codex quota 的本地读取接入真实 Codex 工作流，并验证没有额度事件、旧文件、
   malformed JSONL 和窗口字段变化时的 stale/unavailable 行为。
   2026-07-12 真实 smoke 已验证：parser 会跨文件按事件时间选择最新有效窗口，
   不会被修改时间较新的旧 rollout 遮蔽。当前最近有效事件为
   `2026-07-12T10:40:34.256Z`，5h/7d 剩余均为 0%；之后的新事件窗口为空，
   因此脚本正确标记 stale。在恢复新鲜窗口前不得把该数值当当前额度。
6. 明确哪些 manual-only 数据值得进一步自动化；没有稳定来源就继续手动更新，
   不为了“自动化”引入原始隐私数据。

### Phase 4：设备稳定运行

状态：**基础部署完成，设备 gate 未完成**

完成条件：

- 真实设备可通过固定 URL 稳定访问。
- 浏览器重启或设备重启后仍可恢复页面。
- 自动刷新周期在设备上稳定。
- 短期证书续期后设备仍能正常建立 TLS 连接。
- 连续使用期间无不可接受的滚动、截断、闪烁或残影。

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

下一步不是继续增加 widget 或后端，而是完成真实设备 gate：

1. 在设备上打开当前 live 页面并记录真实 viewport。
2. 拍摄或记录 detail row 的实际阅读问题。
3. 根据证据选择三列、compact 或轮换中的一种。
4. 做最小 CSS 修改并重新执行本地测试、Browser gate 和 live gate。
5. 将本机生成的低敏 Codex quota 摘要显式发布到 live；不得把本机 rollout 文件或
   OAuth 凭据同步到服务器。

在真实设备反馈出现前，不进行推测性的布局重构。
