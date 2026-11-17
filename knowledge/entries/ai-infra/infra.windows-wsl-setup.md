# Windows 下载和安装 WSL

## 什么时候用

Windows 上需要运行 Linux 命令、tmux 或本库的 WSL 运行器时使用。安装 Agent Skill 本身不要求 WSL，也不会替你安装它。

## 最短路径：检查 → 显式安装 → 首次启动

适用 Windows 10 2004（build 19041）及以上或 Windows 11，Windows PowerShell 5.1。需要联网；WSL2 还依赖硬件虚拟化。使用平时工作的同一个 Windows 账号，安装时为该账号提升管理员权限；换成另一个管理员账号会改变发行版归属。

完整 clone 本库后，进入仓库根目录运行。脚本不需要 Python 或额外 PowerShell 模块：

```powershell
# 普通 PowerShell：只读检查，输出 JSON 计划，不安装。
powershell.exe -NoProfile -File .\scripts\setup_wsl.ps1

# 以管理员身份打开 PowerShell，进入同一目录，开始下载/安装。
powershell.exe -NoProfile -File .\scripts\setup_wsl.ps1 -Apply

# Microsoft Store 下载受阻时，显式选择官方命令的网络下载路径。
powershell.exe -NoProfile -File .\scripts\setup_wsl.ps1 -Apply -WebDownload
```

默认目标为 `Ubuntu`。如需其他版本，先 `wsl --list --online`，再将列表中的准确名称传给 `-Distribution Ubuntu-24.04`。脚本只接受字母/数字开头、包含字母/数字/点/下划线/连字符的名称，不导入自定义 TAR，也不接受路径。

若文件被 Windows 标记为下载文件，可在阅读脚本后对**这个文件**运行 `Unblock-File -LiteralPath .\scripts\setup_wsl.ps1`。若本机策略仍限制运行，按组织策略处理；组织允许时仅对本次进程使用 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup_wsl.ps1 -Apply`，不修改永久策略。

安装后如提示重启，保存工作并手动重启，然后重新运行只读检查。接着在普通 Windows PowerShell 中首次启动目标发行版：

```powershell
wsl -d Ubuntu
```

按发行版提示创建 Linux 用户与密码；密码输入时通常不显示字符。用户名/密码由人类交互输入，脚本不存储它们。在 Linux 提示符内执行：

```bash
whoami
uname -r
exit
```

回到 Windows PowerShell，执行 `wsl --list --verbose`，确认目标发行版的 VERSION 是 2。已有 WSL1 发行版会保持原状；需要迁移时先备份，再单独按微软指南决定是否转换。Linux 程序通常宜放 Linux 文件系统（如 `~/projects`）；Windows 目录在 WSL 中对应 `/mnt/c/...`，不要混用 Windows `C:\...` 与 Bash 路径。

独立安装的 `model-with-knowledge` Skill 带这份知识正文，**不附带系统安装脚本**。可从[完整仓库的脚本页面](https://github.com/Chosen-David/agent/blob/main/scripts/setup_wsl.ps1)查看脚本，或直接按[微软安装指南](https://learn.microsoft.com/en-us/windows/wsl/install)在管理员 PowerShell 使用 `wsl --install -d Ubuntu --no-launch`，再完成上述重启与首次启动步骤。

## 脚本做什么，状态怎样判断

实际安装只调用系统 `wsl.exe --install --distribution <名称> --no-launch`，可选 `--web-download`。`--no-launch` 避免在安装进程里启动交互式 Linux 初始化。不会自动重启、更新 WSL、转换或删除发行版，也不改现有默认发行版。

| JSON status | 含义与下一步 |
|---|---|
| `planned` | 只读检查结束。查看 `before`；需要安装时再显式 `-Apply`。 |
| `already-registered` | 当前 Windows 用户已注册同名发行版，跳过安装；仍需核查首次启动和 WSL2。 |
| `install-command-completed` | 官方安装命令返回 0；不证明发行版已可运行。检查提示、重启要求，完成首次启动。 |
| `restart-required` | 返回 3010，保留待重启状态；不会自动重启或继续探测。 |
| `install-failed` / `error` | 查看 `install` 或 `diagnostic`；修复后重试。 |

`before.state=unknown` 表示列表命令或输出解码失败，**不表示没有安装**。脚本保留诊断；显式 `-Apply` 时仍可交给微软安装命令处理 WSL 尚未启用的情况。stdout 与 stderr 独立解码，保留正常通道的原文与失败通道的 Base64 字节，只有成功列表的 stdout 用于名称匹配。

Windows 进程退出码：计划/跳过/命令返回成功为 0，参数/环境预检失败为 1，安装分支保留原生有效退出码（例如 3010），可用 `$LASTEXITCODE` 获取。输出解码失败时若原生返回 0，有效退出码提升为 1，原始码保留在 `NativeExitCode`。工具不能从退出码 0 推断 Linux 已就绪。

脚本只支持可信 Windows 系统 WSL 控制命令的默认 UTF-16LE 重定向输出；它仅在子进程中移除 `WSL_UTF8`，保留父进程环境，不猜测任意第三方程序的编码。损坏字节返回诊断/unknown；这不是通用编码检测器。该假设依据微软自己的诊断脚本，实际其他 WSL 实现或未来改变需重新核验。

## 失败与恢复

- **缺少管理员权限**：用同一账号的管理员 PowerShell 执行 `-Apply`。只读检查和已注册发行版的跳过不要求管理员。
- **系统太旧或找不到 wsl.exe**：先检查 `winver`，按[微软手动安装](https://learn.microsoft.com/en-us/windows/wsl/install-manual)处理；脚本不从第三方下载可执行文件。
- **不认识 `--no-launch` / `--web-download` 等参数**：脚本会在修改前检查 `wsl --help`。按[微软命令说明](https://learn.microsoft.com/en-us/windows/wsl/basic-commands)检查并手动更新系统/WSL，再重试；不会悄悄降级安装方式。
- **下载卡住、代理或 Store 失败**：检查官方命令诊断与网络，可尝试 `-WebDownload`；组织策略/离线环境按微软说明部署，不重复点击启动多个安装。
- **重启后仍无法启动、虚拟化报错**：检查固件虚拟化与 Windows 虚拟机相关组件，按[微软排错页](https://learn.microsoft.com/en-us/windows/wsl/troubleshooting)的具体错误处理。不要通过删除发行版“修复”。

一个可核对的例子：当前列表只有 `Debian`，默认只读运行计划安装 `Ubuntu`，修改次数为 0；`-Apply -Distribution Debian` 则匹配已注册目标，安装次数仍为 0。若列表失败，即使 stderr 含 `Ubuntu`，也不能据此匹配目标或声明已安装。

## 验证范围和任务映射

这是官方命令的工程操作方法，不含数学证明或性能结论。自动化回归使用隔离命令替身验证计划、错误、3010、权限、参数和原始输出边界；现有 Windows 主机只做只读检查。**未执行洁净机器完整下载、重启、首次用户初始化；未实测 PowerShell 7 或 Windows Server。** 不能据此保证每种企业镜像/网络均安装成功。

先完成上述用户初始化与 WSL2 验证，再按具体项目指南运行 Linux 工具。本卡不启动知识库定时维护、不创建额外模型进程，也不授予后台运行权限。

## 来源定位

核查于 2026-11-17；命令可能随 Windows/WSL 版本变化，以本机 `wsl --help` 为准。

- [Microsoft Learn：Install WSL](https://learn.microsoft.com/en-us/windows/wsl/install)：系统前提、安装、重启和首次 Linux 用户。
- [Microsoft Learn：Basic commands](https://learn.microsoft.com/en-us/windows/wsl/basic-commands)：安装参数、发行版列表、版本验证。
- [Microsoft WSL 官方诊断脚本](https://github.com/microsoft/WSL/blob/master/diagnostics/collect-wsl-logs.ps1)：`WSL_UTF8` 与默认重定向编码说明。此处引用编码约定，不复制其实现，不承诺 master 内容永远不变。
