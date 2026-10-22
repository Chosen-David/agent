# GATEWAY-CONTRACT-01：型号目录与能力证据分离

adopt：44110e54的scripts/discover_models.py只取得ID，却将所有型号标available/tools，按kimi/claude/gpt等子串标vision；--from-inventory还覆盖明确能力列表。与resolve及docs/role_models.md“同接口身份验证、未知回退”契约冲突。setup.py doctor的tmux超时会抛出，非零被计作fixes_applied。

新发现保留现有schema的inactive条目（available=false、capabilities=[]，native仅占位）；不自动调用偏好模型，名称提示仅dry-run人类预览。explicit宿主目录只验证不猜测，仍可经setup安装及真实run_role离线预览选原候选。网关响应先限1MiB再strict_json/ID校验，坏目录不部分接受；错误受控。tmux保留5秒且不重试，失败写warnings，成功才写fixes。

原13项修前17failure/9error，初版13项通过，但独审因无scheme URL可回显合成凭据而REVISE；同验收返修后最终普通/-O各15和相关73通过，源码哈希及[短日志/独立复核](../results/gateway-contract-1859/manifest.json)定位实际范围。旧doctor非零测试转查warnings并要求fixes为空，原命令/timeout断言保留。清理原来“flagged for routing”等误导注释和错误返回注解，分类body未变。

重要边界：旧安装目录来源未知，不批量重写或冒称已经可信；请宿主复核旧available:true并显式重新提供目录。false表示未验证，不表示已实测不可用。未运行真实网关/模型/tmuxserver，既有needs_restart、模型质量/usage/成本、Windows、SYSTEM99整体验证仍未决；不声称性能提升或新轮完成，无新增论文阅读计数。
