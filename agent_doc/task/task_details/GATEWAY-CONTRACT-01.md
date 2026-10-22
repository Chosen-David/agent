# GATEWAY-CONTRACT-01：发现元数据不可冒作已验证能力

Task-ID: GATEWAY-CONTRACT-01
Date: 2026-10-22

## Plan

Version: 1

SYSTEM-99同一未完成批次，基线44110e54e82f66b3bff24450e026e4aea46934f9。已fetch/同步、保留其他工作和未决项；AGENTS与空GUIDE hash未变，人类guide只读。EXECUTE：在现有model_routing.resolve“未知权限/能力回退默认”及docs/role_models.md“同接口身份验证后声明available”的契约内修复，非更换模型策略/架构。用户授权代码修复、验证后普通main发布。上一INSTALL-RECOVERY-01明确排除名称能力推测、tmux异常；旧通过不抵扣本次验收。

已查真实脚本：fetch_models只取id，build_inventory却把任何型号available=True、tools=True，claude/kimi/gpt等广泛推定vision；--from-inventory覆盖明确能力列表。无推理/同身份工具验证，不能证明精确型号可经当前Claude调用。doctor的tmux TimeoutExpired未经捕获，非零退出写入fixes_applied；缺二进制也不能保留完整诊断报告。

方法：
1. 自动发现输出仍为现有inventory/v1，但型号仅目录线索：available=false、capabilities=[]，transport字段保留native占位并明确未验证，不作为可调用证据。分类标签只用于人类预览、标明推测，不影响路由。所有当前角色均要求tools，未知条目因此按已有resolve契约fallback。不变更已安装旧快照；历史推测来源无法识别，文档明确旧快照需宿主复核/显式重传，不声称自动撤销。显式--from-inventory直接严格validate并保留调用者能力、availability、transport，不再按名字增强；仍无密钥/多余字段许可。宿主已验证目录经原setup --model-inventory正常选偏好模型。
2. 网关目录解析有界读取1MiB+1，复用strict_json拒绝坏UTF8/重复key/NaN/深度，核对envelope/list及每个id为非空字符串后交库存validator；不把坏项部分过滤为可信成功。非零/空/畸形/超时/无效输入CLI受控诊断，不打印traceback/凭据，timeout正整数。仅本地进程/HTTP替身，不访问真实网关。
3. doctor tmux分支保留5秒、原source-file参数且不重试；OSError/TimeoutExpired/非零记录doctor.warnings而非fixes_applied，成功才记录Applied。其它安装/模型检查报告保留。needs_restart既有语义、本次真实tmux鼠标/滚动/宿主验证仍待后续。

验收先保存基线失败：未知型号不路由、explicit库存能力保持、非法目录/JSON/oversize受控、同预算已验证库存仍选原候选、自动发现→真实install→run_role dry-run回退、explicit库存→真实install→dry-run选模型、tmux成功/非零/缺命令/超时和无TMUX无调用。专项普通/-O、setup/doctor/recovery/model-routing/role-process/install相关回归；独立计划→实现→独立源码/数据/真实消费者复核→fetch/CAS普通发布→回读整树/关键hash。独审仅写分配.agent-runs/gateway-contract-1859/；主AI唯一写源码/测试/TASK/detail/advice，无后台/付费资源。

正确性修复可能增加回退，不称性能/质量提升；未测live模型、认证、网关、Windows或tmuxserver，不保证旧快照已可信。保留同批14篇正文阅读记录，无新增阅读数或新轮完成。没有重大agent_doc迁移/竞争清单；SYSTEM99其它任务质量/usage/成本缺口继续open。

## Progress

- 原始名称推测已复现：gpt-5-text-only被标tools+vision，任意unverified-model被标tools；tmux TimeoutExpired直接抛出。回归与独审待完成。

- 独立计划APPROVE，确认属于现有unknown→default接口契约修复。13项原回归17failure/9error；候选普通/-O各13、相关73通过。显式输入列表/空能力/false+adapter保持，实际setup→run_role dry-run覆盖新发现fallback及显式host声明夹具仍选opus；没有模型执行。
- 最后源内仅删误导/冗余分类注释，docstring明确schema-valid inactive，_classify错误dict返回注解改实际list[str]；分类body不变，最终hash已交独审。docs明确旧快照未自动撤销、需要宿主复核，不能将false写成已证明不可用。
- 原doctor非零测试现在严格检查warnings、fixes为空；保留原命令/5秒断言，不将失败冒作applied。独立最终源码/基线与消费者复核待完成，发布前fetch/精确路径/整树回读另核。

- 独审v1为REVISE：Request构造位于try外，缺scheme含合成user:password的URL在零网络下ValueError被main回显，违反原Plan凭据遮罩。完整REVISE与合成原始复现保留，不把13/13+73冒作最终通过。
- 同Plan实现返修：Request构造/加header纳入try，ValueError与HTTPException通用诊断，不拼原URL/异常文本。新增2项修前1failure及1failure/1error，最终15项普通/-O通过，73集成通过；独立新hash复验待完成。无真实凭据或live调用，原失败/旧源码均保留。

- 最终独审ACCEPT usable-with-scope：15项普通/-O、73相关通过，最终15项对44110e54原源码17failure/12error；新增旧源码错误与中间版本泄漏failure计数来源不同，不合并冒作独立bug数。实际HTTP main→安装→无显式库存run_role dry-run新发现fallback/明确host声明夹具选opus，fake tmux CLI保留configured报告/警告且fixes空。
- 独立实际CLI无scheme含userinfo、stdlib坏端口/URL控制字符/header换行、HTTPError/URLError/TimeoutError在禁止真实连接时受控脱敏；1MiB有效JSON可接受，+1字节拒绝。最终普通/优化/集成完整raw日志回读及hash绑定，旧REVISE/合成失败保留，原工具执行不等于真实服务验证。
- 公开证据agent_doc/results/gateway-contract-1859/manifest.json，原producer各版完整log私有检查点保留hash。原角色偏好、显式声明、no-retry和5秒约束不变；旧库存未批量改写，真实网关/模型/tmux与SYSTEM99原缺口继续open。无新增阅读数或整轮完成声明，发布及远端整树/关键hash由主控最后核对。
