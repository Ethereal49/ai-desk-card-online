# AI Desk Card Web Plan

## 1. 产品目标与当前状态

本项目把 `/Users/ethereal/Documents/Code/ai-desk-card` 的产品原则和 widget
语义迁移到浏览器路线，为 `758x1024` 竖向墨水屏提供低频、稳定、可远程更新的信息卡片。

当前生产架构保持静态：没有 backend service、数据库或前端构建步骤。

```text
Mac deterministic sources
  -> privacy projection + last-known-good merge + Focus resolution
  -> locked SSH publish
  -> server widgets.json <- shared lock <- server weather timer
  -> Caddy HTTPS + Basic Auth
  -> static browser app
  -> e-ink display
```

当前状态：

- 静态六 widget 页面、真实 source adapters、locked publisher、LaunchAgent、server-owned
  weather、Caddy Basic Auth、IP certificate renewal 和实体设备布局均已实施。
- Phase 6 确立的现行 UI 是 visual viewport 自动 fit、三列 detail layout、完整 DOM 数据和
  最多两行可见 ellipsis；更早的文本处理方案已被替代。
- Phase 7 的四个 child 均已形成 durable outcome 并归档；parent integrated repository、
  redacted source/preview、read-only live、plan/path/privacy 和 code-spec convergence gates 已通过，
  当前只剩 branch/PR/archive/journal closeout，不再有 product implementation 缺口。
- Phase 4/5 的未完成观察或显式 waiver 不因后来任务归档而被反向记为通过；见第 8 节。

## 2. 不变约束

### 2.1 产品与界面

- 设计基准固定为 `758x1024`（宽 x 高），页面是 ambient display，不是交互式 dashboard。
- 首屏必须无需手动 pinch、无页面滚动、无文字重叠、无不可解释的内容丢失。
- 保持高对比、大字体、固定布局和低信息密度，适合 30-50 cm 距离阅读。
- 禁止动画、transition、hover-only 内容、渐变、装饰阴影和持续高频更新。
- 页面更新频率保持在 `5m-30m`；不承载实时行情、视频或持续动画。

### 2.2 技术与目录

- 继续使用 HTML、CSS、vanilla JavaScript 和 JSON；runtime truth 固定为
  `web/widgets.json`。
- 未先更新本计划，不引入 React、Vite、Astro、TypeScript build、backend API 或数据库。
- 不依赖原项目的 firmware、PlatformIO、BLE、USB、raw frame、daemon 或 Pillow 渲染链路。
- Web MVP 代码留在 `web/`；未来 server code 如有必要放入 `web-server/`；部署资产留在
  `deploy/`；生成 QA 产物留在 ignored `output/`。
- `.codex/hooks.json` 只保留 Trellis workflow-state injection。Plan freshness 通过
  `.codex/hooks/ensure_plan_updated.py` 手动 gate，不另加 project hook。

### 2.3 隐私与安全

- `widgets.json` 只允许页面渲染所需的 bounded display fields；最终 publication 必须通过
  `widget_contract.validate_document` 的完整 shape、slot、list、length 和 private-key 检查。
- 禁止发布 token、密钥、transcript、raw log、source ID/path、meeting link、attendee、
  私密 notes、prompt/response 或完整第三方记录。
- Field allowlist 不是语义敏感度分类器；真实 title/event/task 文本仍必须经过 source cropping，
  并由 Caddy Basic Auth 保护。
- Source access 保持只读。任何 source-system write、任意 selector/model routing、网页编辑器或
  浏览器端伪解锁均不在当前架构内。
- Repository 和 LaunchAgent 不保存 Basic Auth password、source credential、private key 或
  server-generated certificate material。

## 3. 六 Widget 与 Source Ownership

| Slot | Widget | 当前 owner/source | 显示边界 |
| --- | --- | --- | --- |
| `glance-left` | `weather` | server `update_weather.py` / wttr.in | current + 2 forecast |
| `glance-right` | `ai-status` | Mac Codex metadata + quota projection | session/task/context/quota summary |
| `headline` | `focus` | Mac final projection resolver | 1 allowlisted headline source |
| `detail-left` | `ai-tasks` | Mac Codex metadata | `running/waiting/blocked/completed_today` |
| `detail-middle` | `calendar` | allowlisted Apple Calendar | 最多 4 条 |
| `detail-right` | `todo` | assigned Linear `CODE`/`LIFE` issues | 最多 5 条 |

Source rules：

- Linear 只拥有 `todo`。候选为本人 assigned、`started`/`unstarted` 的可执行 issue；排除
  backlog、completed、canceled 和 parent/container，按 priority、due、state、updated time
  和稳定 identifier 确定顺序。
- Calendar 只拥有 `calendar`。必须配置 exact-name non-empty allowlist；窗口为本地时间现在到
  明天 `23:59`，排除已结束/canceled。All-day state 只用于生成 `ALL DAY` display label；public
  event 只包含 start/title/optional end，不读取 location、notes、UID、attendee 或 URL。
- Codex metadata 只投影低敏 title/model/timing/state/count；不读取 prompt、response、preview、
  transcript 或 `logs_2.sqlite` 内容。
- Focus 在 source、last-known-good 和 quota merge 后只解析一次，不由 Linear adapter 拥有。
  缺省为 `todo.first`；允许 `todo.first`、`calendar.next`、`ai-status.task`、
  `weather.current`、`manual` 及 bounded overrides。
- Quota 当前没有 authoritative fresh local window。保留 last-known-good、明确标记 stale，并让
  source-check/preview/publish 返回 partial exit `2`；禁止增加 600 秒阈值、用 mtime/token count
  伪造 freshness，或转向 UI scraping/非稳定 private API。

Focus 私有配置位于 `~/.config/ai-desk-card-online/focus.json`。使用：

```bash
scripts/configure_focus.py get
scripts/configure_focus.py set --source calendar.next
scripts/configure_focus.py set --source manual --task "Private local focus"
scripts/configure_focus.py reset
```

CLI 复用 production parser，目录为 `0700`、文件 atomic replace 为 `0600`，输出只含 source 和
field-presence flags；它不读 source、不写 `widgets.json`、不连接 SSH、不 preview/publish，也不
restart scheduler。有效配置由下一次正常 refresh 读取。

## 4. 数据与失败契约

Top-level contract 固定：

```text
updated_at: ISO-8601 string
layout: exactly "dashboard"
refresh_seconds: integer
widgets: exactly one validated object for each of the six unique type/slot pairs
```
```

- Producer 生成完整 JSON，成功后更新 `updated_at`，使用 atomic replacement；live 文件保持
  `0644` 供 Caddy 读取。
- `refresh_seconds` 合法范围为 `30..86400`；当前 deployment 使用 `300`。浏览器对非 300 值
  的 timer mismatch 记录在第 8 节。
- `web/widgets.example.json` 是公开示例，不是 runtime source；manual `update_*.py` 和
  `web_update.py` 仅用于 local demo、diagnosis 或 rollback，不是 production sources。
- Source failure 只保留该 owner 的 last-known-good，添加 `stale`、`last_attempt_at` 和低敏
  `error`；不能清空其他 widget。配置错误在 baseline SSH 前 fail loud，不能合并或发布。
- 页面 document freshness：`<=15m` normal、`15m-60m` stale、`>60m` old；fetch/parse/send
  failure 为 offline。
- Routine output 只包含 source health、changed widget types、publish result 或 bounded reason；
  不输出 task/event titles、calendar names、paths、raw JSON 或 credentials。

主要 exit contract：

| 情况 | Exit / 结果 |
| --- | --- |
| 所有 source fresh | `0` |
| 可恢复 source 或 quota stale | `2`，保留 LKG，可继续 preview/publish |
| credential/allowlist/Focus config invalid | `3`，SSH 前终止 |
| local refresh lock 已占用 | `4`，无重入 |
| SSH/install/contract/I/O fatal | `1`，不得留下 broken live file |
| scheduled refresh timeout | `124`，写 bounded fatal status |

## 5. 前端 Layout 与 Runtime 行为

固定 card：

```text
width 758px; height 1024px
rows  64px / 210px / 320px / 278px / 56px
glance columns  1fr / 1fr
detail columns  180px / 1fr / 1fr
```

- Primary headline/metrics 居中；forecast、calendar、todo 使用左对齐稳定列；AI counts 是 flat
  `2x2` grid；footer 是 left/center/right 三列。
- 所有 data-derived HTML 必须 escape。Source/user prose 保留完整 JSON/DOM/accessibility value；
  可见层最多两行，超限时显示 ellipsis，短文本不得误加 ellipsis。
- Normal fixture 保留 5 条 todo、4 条 calendar 和 2 条 forecast。若 clamp/compact 后 widget
  仍 overflow，renderer 才从尾部移除整行，并保持 truthful `selected/total`；primary widget
  依次 compact/hide secondary content，不能无声截断主信息。
- `applyViewportScale()` 优先使用 `visualViewport`，小于目标时预留 4px inset，优先 CSS
  `zoom`，否则 transform fallback；scale 不超过 1，并在 window/visual viewport resize 时重算。
- `?viewport=1` 只替换 footer diagnostic；普通 URL 保持 `source: widgets.json`。
- 启动先渲染完整 fallback，再用 cache-busting `XMLHttpRequest` 加载 JSON。只有成功 parse 才替换
  `lastData`；HTTP/parse/send failure 保留 LKG 并显示 offline，不白屏。
- 真实设备是最终视觉 authority；static contract test 不能替代 Browser geometry 或 physical
  bottom-border/readability check。

## 6. Publication、Scheduler 与 Deployment

Production local entrypoint：

```bash
scripts/refresh_dashboard.py --source-check
scripts/refresh_dashboard.py --preview
scripts/refresh_dashboard.py --publish
```

- `--source-check` 只收集/投影 sources，不连接 publish host。
- `--preview` 通过 SSH 读取 live baseline，完成 merge/Focus/strict validation，只打印 redacted
  health 和 changed types，不写 live。
- `--publish` 在 local non-blocking lock 下只传五个 Mac-owned widgets 到 unique remote temp；
  installer 在 `/run/lock/ai-desk-card-widgets.lock` 下重读 live JSON、保留最新 weather、做
  changed-only `0600` backup、atomic `0644` install、验证并在失败时 rollback。
- Credential-free LaunchAgent 每 300 秒运行；`run_scheduled_refresh.py` 限时 150 秒，并 atomic
  replace 最大 8192-byte、mode `0600` 的 latest status。Quota no-go 导致的 last exit `2` 是
  partial health，不是 scheduler/publish failure。
- Server weather timer 每 30 分钟只更新 weather，并通过 `/usr/bin/flock` 使用同一 remote lock。

Live topology：

- Host alias `myecs`，runtime root `/srv/ai-desk-card-online`。
- HTTP `/` 跳转 HTTPS；`:443` 使用 Caddy explicit certificate、Basic Auth、security headers 和
  runtime allowlist。认证后只允许页面 assets 与 `widgets.json`；repository/non-runtime/path
  traversal probes 必须为 `404`。
- Caddy 使用 `auto_https off`。`:80` 先服务 `/.well-known/acme-challenge/*`，再 redirect。
- Certificate renewal 是 `snap.certbot.renew.timer -> webroot HTTP-01 -> renewed lineage ->
  root-owned deploy hook -> Caddy cert directory -> Caddy reload`。通用 `certbot.timer` 不是该
  Snap 安装的 health signal。
- Certificate issuer/SAN/dates、Certbot version、timer/service results 是 runtime facts；必须
  重新检查，不能把 archived value 写成 current configuration。

## 7. 当前验证与 Operator 命令

Repository gates：

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 -m compileall -q scripts deploy/scripts
node --check web/app.js
bash -n deploy/scripts/verify_ip_https.sh deploy/scripts/verify_ip_only.sh
plutil -lint deploy/launchd/com.ethereal.ai-desk-card-refresh.plist.example
python3 .codex/hooks/ensure_plan_updated.py
git diff --check
```

Frontend change 后，在 `web/` 启动 static server，并用 Codex built-in Browser：

```bash
cd web
python3 -m http.server 4173
```

必须覆盖 `758x1024`、`740x951`、`467x600`，normal/failed-fetch、短文本、长中文、长英文和
无断点 token；断言 page/widget geometry、六 widget、完整 DOM、两行 ellipsis、row counts 和
4px bottom inset。实体设备复核首次 fit、底边和可读性。

Authenticated live gate 只通过调用者环境接收 password：

```bash
export AI_DESK_CARD_AUTH_USER=desk
export AI_DESK_CARD_AUTH_PASSWORD='<live-password>'
deploy/scripts/verify_ip_https.sh
```

Credential-free live checks 至少包括：

```bash
ssh myecs 'systemctl is-active caddy ai-desk-card-weather.timer snap.certbot.renew.timer'
openssl s_client -connect 112.74.73.134:443 -servername 112.74.73.134 \
  </dev/null 2>/dev/null | openssl x509 -noout -issuer -dates -ext subjectAltName
```

完整 bounded certificate/Snap/hook/Caddy audit 见 `deploy/README.md`。不得只读配置后宣布 live
gate 通过，也不得在 documentation audit 中运行 renewal、reload 或其他 mutation。

## 8. 当前限制、Residual Risks 与唯一下一步

Current limitations：

- Codex quota 没有 stable authoritative fresh local surface；LKG stale + partial exit `2` 是当前
  正确 no-go，不是待调高阈值的 parser bug。只有发现 privacy-safe stable source 时才重开。
- Browser 在第一次异步 load 前按 fallback `300s` 建立 interval，成功后未 reschedule；因此
  非 300 的 `refresh_seconds` 当前只改变 label，不改变实际 polling。更改 cadence 前必须另开
  implementation task 修复并增加行为测试。
- `weather.current` Focus 使用 publish 前 baseline；若 weather 在 remote lock 前更新，installer
  会保留新 weather，但 Focus 最多到下一次 local tick 才一致。
- 上述 polling 与 `weather.current` 限制也分别记录在 frontend lifecycle 和 backend publish
  code-spec 中，避免后续实现把目标合同误认成当前行为。
- 不支持 line-clamp 的 browser fallback 只能保证 bounded hidden overflow，不能保证可见
  ellipsis；必须以目标设备实测为准。
- 实体设备的 `?viewport=1` 曾保持默认 source label，是非阻塞 diagnostic limitation。

Evidence boundaries / waivers：

- Phase 4 被用户停止后的最终 `T+24h` physical state、当时最新 certificate reload 和最终
  authenticated `200/404` 没有在该 phase 内完成，不能回写为通过。
- Phase 5 direct system sleep/wake observation 被用户显式 waiver；自然 ticks、non-overlap、
  shared lock 和后续恢复证据仍成立。
- In-app Browser 对 authenticated public IP 曾受 client policy 阻断；authenticated shell gate
  与实体设备是现有 live/visual authority。
- Short-lived certificate health 必须周期性重新检查；archive expiry 不证明当前健康。

唯一已授权下一步：把 Phase 7 implementation evidence 保留在 draft PR #1 供 review；不 merge，
也不预授权新的 product feature 或 live mutation。后续若修复 browser polling mismatch、恢复
fresh quota source 或重跑 waived/security live gates，应分别创建 owning task。

## 9. Archive Index

历史细节只在 archive 中保留；本计划不复制 checkpoint prose：

| Scope | Durable outcome | Archive |
| --- | --- | --- |
| Phase 3 real-use gates | 六 widget、auth/privacy、Browser/device baseline | `.trellis/tasks/archive/2026-07/07-12-phase3-real-use-gates/` |
| Phase 4 stability | 服务器观察完成；明确保留未完成 physical/auth boundary | `.trellis/tasks/archive/2026-07/07-18-phase4-device-stability/` |
| Phase 5 publish workflow | real sources、locked publish、LaunchAgent、waiver evidence | `.trellis/tasks/archive/2026-07/07-23-phase5-daily-publish-workflow/` |
| Phase 6 Focus/UI | final projection Focus、两行 ellipsis、三视口与设备验收 | `.trellis/tasks/archive/2026-07/07-23-phase6-configurable-focus-visual-alignment/` |
| Phase 7 quota | authoritative-source inventory 与 evidence-backed no-go | `.trellis/tasks/archive/2026-07/07-25-phase7-codex-quota-freshness/` |
| Phase 7 Focus CLI | private atomic `get/set/reset` operator contract | `.trellis/tasks/archive/2026-07/07-25-phase7-focus-config-cli/` |
| Phase 7 certificate | Snap/webroot/hook/Caddy read-only renewal contract | `.trellis/tasks/archive/2026-07/07-25-phase7-certificate-docs/` |
| Phase 7 plan | current-state source of truth 与 retention/path audit | `.trellis/tasks/archive/2026-07/07-25-phase7-plan-current-state/` |
| Phase 7 parent | 四 child integration、PR evidence 与 closeout | `.trellis/tasks/archive/2026-07/07-25-phase7-reliability-operator-ergonomics/` |

Branch：`agent/phase7-planning-handoff`。Draft PR：
`https://github.com/Ethereal49/ai-desk-card-online/pull/1`。
