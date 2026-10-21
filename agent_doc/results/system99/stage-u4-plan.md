# SYSTEM-99 / U4 tmux 使用体验方案（Version 34 候选）

状态：`PROPOSED / blocked-on-real-host`。Version 32、33 均被独立 review-main 判定 `REVISE`；本版继续收紧 SONAME 物化、utmp 边界、配置读回和可恢复卸载合同，须重新审核。本文件不是完成回执。

## 目标与既有证据

- 复用 `agent_runtime.task_supervisor` 的唯一 tmux 监督入口，不创建第二套任务池、聊天池或 TASK。
- 既有 `docs/tmux_supervisor_validation.md` 只证明 worker/guard/恢复逻辑；当时真实 tmux 会话因 Unix socket 被禁而跳过，不能作为 U4 会话验收。
- 本次 result-store 查询扫描270个目录且`partial=true`，未发现适用的 tmux 安装结果。旧验证只作边界证据。

## 固定平台、包与许可

首版仅声明 **Ubuntu 24.04 Noble amd64**。安装与每次复用必须核对 `/etc/os-release` 的 `ID=ubuntu`、`VERSION_ID=24.04`、`VERSION_CODENAME=noble`，`dpkg --print-architecture=amd64`，并读取宿主包版本满足：`libc6>=2.38`、`libsystemd0>=221`、`libtinfo6>=6.4+20230603且<6.5~`。其它发行版、架构、WSL版本和宿主依赖不推断兼容。

固定 Ubuntu 24.04 LTS `main` 三个 archive：

| 包 | 版本 | SHA-256 | archive完整许可集合摘要 | copyright SHA-256 |
| --- | --- | --- | --- | --- |
| tmux | 3.4-1build1 | `8a62bd2fbe4e17bad9585c4428d95e275a0850b65bafcee599d672e5f11df5bb` | ISC、BSD-2/3及包内列出的Expat/FSF许可 | `9c587ac09a351692c23a910e4e59008d4a5ce66125c7aad1279065f3a272a3e1` |
| libevent-core-2.1-7t64 | 2.1.12-stable-9ubuntu2 | `3da51e864e4067779a2ba3a87daf5e4d8030c0aaa6291a1ce12483d4f73bf752` | BSD-2/3、Expat及包内列出的FSF等许可 | `d32d223a2f96bb222faa1f6d2b4573b512465b2b234f56e040a4d7daab060d69` |
| libutempter0 | 1.2.1-3build1 | `46c0dfbfeca19ba0773398d654b7e7225b178f26b414f0e2f8250519551bfb32` | LGPL-2.1-or-later、BSD-2-Clause | `8d0ad082a8402aa9b432a33ce630f33bc7d076997ace50f3162eece84f896015` |

profile记录精确URL、大小、archive哈希、依赖、完整copyright哈希和许可集合，不把archive简写为单一SPDX许可。receipt同时绑定archive、实际提取copyright及配置哈希。`tmux -V == tmux 3.4`仅是动态链接smoke，不代替宿主依赖或真实server验收。

## 安装、缓存与rootless提取

1. 新增显式 `agent_runtime.tmux_tools`；普通 `setup.py`、Codex同步、import、prepare均不安装、不联网、不启动server。
2. 专用root由 `--root` 显式给定；默认仅CLI便捷值：绝对`XDG_DATA_HOME/chosen-agent/tmux`，否则`$HOME/.local/share/chosen-agent/tmux`。root含`owner.json`、`install.lock`、`cache/`、`versions/<binding_sha>/`、`current.json`。默认路径只在显式install时创建。
3. 首次联网安装只取profile固定URL并把三个原archive以固定文件名存入受管cache。`--package-dir DIR --offline`允许从独立只读目录首装；完全禁网且只接受恰好三个已跟踪普通文件，额外项、symlink、截断或hash错均拒绝。已有cache也按同规则逐项核验。
4. 不调用`dpkg-deb -x`并忽略失败。受限提取器先完整枚举可信哈希archive的data成员，只允许精确allowlist：tmux ELF、两个共享库的真实ELF源文件及三个copyright；拒绝绝对/`..`路径、重复项、symlink、hardlink、device、FIFO、socket、超出文件数或合计大小。物化映射固定为：`usr/bin/tmux` → 普通文件`bin/tmux`（0755，SHA-256 `88e9b027bbe0dd11b6e7ea39fd9a6489f97addd751e25ed6a54f1607f42ad4df`）；`usr/lib/x86_64-linux-gnu/libevent_core-2.1.so.7.0.1` → 普通文件`lib/libevent_core-2.1.so.7`（0644，SHA-256 `07bc5c896da3469064935f60595b5a3e44f5cc5bad9b8d7d71adc4ea1cd628aa`）；`usr/lib/x86_64-linux-gnu/libutempter.so.1.2.1` → 普通文件`lib/libutempter.so.0`（0644，SHA-256 `ee1185b2506922223bc55b1530a391ce1bdde755c204808dcf609f1465c89004`）。输出不含symlink；receipt同时绑定archive成员源路径、输出相对路径、hash和mode。运行环境固定`LD_LIBRARY_PATH=<version>/lib`，缺任一SONAME输出即硬失败。只创建普通文件/目录，不恢复owner、group、setuid/setgid。
5. 明确排除并且不提取archive中的`/usr/lib/.../utempter/utempter`特权helper；但受管`libutempter.so.0`内嵌绝对宿主helper路径，不能据此承诺不更新utmp/wtmp。receipt/文档固定记录`bundled_utempter_helper=false`、`utmp_behavior=host-dependent/unknown`，并在安装、复用和真实session验收分别记录绝对宿主helper是否存在；不声称完整系统包语义或`utmp_updates=false`。
6. 安装使用同root跨进程锁、`.incomplete`、绑定哈希、receipt/current。失败升级保留旧current；重复install先重验平台、profile、receipt、copyright、配置及真实`tmux -V`，返回`reused`，网络/提取器/包管理器调用均为0。

## 独立配置、resolver和server漂移

仓库配置固定为以下364字节（末尾换行保留），SHA-256 `60039b05b3d92f5be879b5146b073e9c99500b774baf08284af44f0f691ec9ea`：

```tmux
set -g @agent-config-id "tmux-ux-v1"
set -g mouse on
set -g history-limit 50000
set -g focus-events on
set -g status-style "bg=default,fg=white"
set -g status-left "#[fg=cyan,bold] #S "
set -g status-right "#[fg=white]%Y-%m-%d %H:%M "
setw -g window-status-current-style "fg=cyan,bold"
set -g pane-border-style "fg=black"
set -g pane-active-border-style "fg=cyan"
```

不读取、写入、source或覆盖`~/.tmux.conf`；不强制`terminal-overrides`、RGB、OSC52或系统剪贴板。解析失败则fail-closed。

resolver逐次冻结一个绝对binary及环境：

1. `AGENT_TMUX_ROOT`一旦设置，必须是有效绝对受管root；任一错误硬失败，不降级。
2. 未设置时检查上述默认root；不存在才查PATH，存在但owner/receipt/hash/smoke漂移则硬失败。
3. PATH结果在调用前解析为不经symlink的绝对普通文件并固定；只支持真实输出精确`tmux 3.4`，其它版本拒绝，不进入卸载范围。
4. 三种来源都使用上述config和固定socket`agent-supervisors`。若socket已有server，先逐项读回`@agent-config-id`，以及其余九项`mouse`、`history-limit`、`focus-events`、`status-style`、`status-left`、`status-right`、`window-status-current-style`、`pane-border-style`、`pane-active-border-style`的精确值，并读取root table中的`WheelUpPane`绑定确认进入copy-mode；任一缺失或漂移即拒绝启动/状态声明，不杀server、不换socket、不覆盖会话。新server启动后同样完整读回才可写live receipt。旧`-f /dev/null` server是明确负控。

## 鼠标、回滚与三类上下文限制

- `mouse on`使用tmux 3.4默认WheelUpPane绑定进入copy-mode；拖选和copy只写tmux buffer，不等同系统剪贴板。终端原生选择通常需终端自己的modifier（常见为Shift），具体键由终端决定；本工具不承诺统一modifier。
- 真实PTY验收覆盖支持声明中的`xterm-256color`与`screen-256color`；8色终端只要求基础状态/前缀/copy-mode可用。缺`TERM`必须清晰失败，不写成已验证fallback。
- `history-limit=50000`只影响配置加载后创建的新window/pane；既有pane不改变。它不扩大模型context window。
- 模型context window/供应商token上限仍由宿主模型路由决定；项目任务包预算继续由现有`task_context`、`dispatch_context`、`prompt_context`管理，U4不另设竞争入口。

## 卸载与恢复

- `uninstall-version`只删除receipt清单中类型/hash均匹配且不含未知项的版本；无论是否current，任何删除前都必须用冻结binary/socket得到固定socket“明确无server”。EPERM、超时、协议错均是unknown并拒绝；除非未来server receipt能证明其绑定到其它版本，否则不作版本归属推断。绝不kill server、删socket或删除system tmux。
- current版本需先显式切换，或通过`--remove-current`执行同一锁内状态机：验证平台、owner、receipt、完整文件树及明确无server → 原子切换`current.json`到已验证目标或原子撤销current → 将目标version原子rename为同root受管`.removing-<binding_sha>`墓碑 → 仅按冻结且再次核验的receipt清单删除 → 删除空墓碑并提交成功。恢复流程识别墓碑并从最近已提交边界继续或安全拒绝，`current.json`在任何时刻都不指向部分删除目录。
- 普通卸载保留三个受管cache archive供离线重装；`purge-cache`是独立显式动作，仅在无version、无server且cache逐项hash匹配时删除。任何symlink/特殊文件/未知项/本地漂移均整体拒绝。
- 中断安装保留`.incomplete`诊断目录和旧current；中断卸载使用同root锁，并逐一注入验证后、current切换/撤销后、rename后、每个清单删除后和墓碑提交前的中断，证明恢复幂等且current永不悬空，不把部分删除写成成功。import/setup/install均不启动server，只有显式supervisor start可启动自有session。

## 固定验收与发布门禁

先保存修前失败，再实现；专项普通及`python -O`各跑一次。

1. 隔离HOME/PATH无tmux：真实首次安装校验三archive、allowlist提取、copyright、`tmux -V`、receipt/current；断网重复install为`reused`且网络/提取/包管理0调用；独立`--package-dir --offline`首装同样通过。
2. 安全负控：平台/宿主包版本不合、路径穿越、绝对路径、重复、链接、设备/FIFO、数量/字节超限、archive/hash/copyright/config漂移、并发install、非受管root、`.incomplete`均fail-closed且旧current可复用。
3. 无侵入：预置`~/.tmux.conf`及用户文件在安装、复用、失败、卸载后逐字节不变；普通setup不创建root。
4. 授权Ubuntu Noble真实主机：无tmux→安装→断网复用→新server/session；读回config ID、其余九项配置精确值及root `WheelUpPane`绑定；两种TERM的PTY滚轮进入copy-mode、拖选/copy后tmux buffer精确；新pane历史限额；记录宿主utempter helper存在性；完成/幂等/清理由既有supervisor真实链复测。
5. 真实负控：缺SONAME普通文件、旧`/dev/null` server/任一配置或WheelUpPane漂移拒绝；活动server下任意版本卸载拒绝；无法连接socket时卸载状态unknown并拒绝；server明确不存在后逐中断点验证原子current撤销/切换、墓碑恢复、version卸载与cache保留/显式purge符合合同。
6. 运行supervisor/安装器/项目文档相关回归、全库、Reader、引用同步、compileall、diff；独立结果验收检查实际代码、包字节、PTY、配置读回和原始日志。

当前宿主确认为Ubuntu24.04.3 amd64，三项宿主依赖版本符合，PATH无tmux；固定archive在临时目录已通过`tmux -V`。但内核策略禁止任何AF_UNIX socket（Python与tmux均EPERM），所以第4/5项不可能在这里完成。

**发布门禁：** 本版若独立方案审核通过，只允许在隔离工作树实现未启用候选和fixture；真实会话门禁完成前，不接入默认`task_supervisor`、不提交/推送生产代码到`main`、不宣称一次安装/鼠标/卸载可用。可发布的只有标明`PROPOSED / blocked-on-real-host`的计划检查点；若未来要放宽此门禁，必须经用户明确对齐，不由实现者自行解释。
