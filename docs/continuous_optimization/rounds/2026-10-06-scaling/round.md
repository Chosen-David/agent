# 有界轮次：验收规模与有效上下文

日期：2026-10-06。起始干净工作树执行 `git pull --ff-only origin main`；实际基线 `cb3e133ded7f2c878b3eddb10a0e7876fe6cac2b`。源码候选本地提交 `4ee5f7f2b1e189514c876b2290e368aff0899c7a`，validator SHA256 `d182adfa0d118d6245f0a58623114d8fbeb70dd6ab8fa3ea4c1d93754bcedf9d`。这是共享验收工具的内部实现精修，不改变用户目标、权限、交付边界或角色架构。

读取最新 root TASK、AGENTS、决策协议、角色与后端注册表、主AI/相关Skill入口、记忆workflow、实际validator及已有pipeline。沿用 CO-004 候选，没有重复启动上一轮或另造评测体系。当前 active_run 只是审计记录，不是分布式排他锁；启动前核对实际宿主执行。

## 学习与选择

完成10篇新增原始论文方法、实验、相关消融、成本和局限阅读；完整作者/版本/哈希/实际阅读范围/未读范围保存在 `research/*-papers.json`，逐篇证据与最小实验在对应MD，总对照表 `research/synthesis.md`。对去重台账22篇检查后追加为32篇。主执行者复核关键原文证据，分工意见不作为效果依据。

实际打开固定 Anthropic skill-creator 的SKILL、run_eval和utils，以及Superpowers验证Skill；入口/依赖/验收对照见 `research/source-review.md`。不安装外部runtime，不照搬以首次触发事件当成功的评测。保持14角色、通用主AI、科研/旅行/代码阅读、Claude接入；按需记忆与程序复用候选待测，不新增重复Prompt。

## 实际改进与程序证据

预先固定验收：64MiB文件的Python分配峰值减少≥80%、长链耗时明显改善、旧新诊断一致，文件≤128MiB/链≤10000/CPU≤120秒/三重复。不为保证采纳放宽门槛。

- artifact SHA256从整文件 `read_bytes` 改为1MiB流式 `update`，空文件、短读、读取异常/关闭均有独立控制。
- dependency cycle由反复扫描pending改为Kahn已知边遍历，保留unknown、重复边、依赖状态与消费者任务范围诊断。
- 64MiB Python traced peak中位数：67,114,576→2,103,164 bytes，下降96.87%；6000链验证中位3.60865→0.01070秒，各3次。参数/全部原始runs/来源见 `evidence/scaling-{baseline,candidate,summary}.json`。
- 366个确定性旧新案例的诊断多重集一致，240随机图与独立DFS oracle一致；根复跑差分366/366。不把自动生成例子当模型任务。
- 全仓 `python -m unittest discover -s tests -v`：360总计、352通过、8跳过；reader3/3。日志在evidence。8跳过依赖实际tmux/socket等宿主条件，不记通过。

反向邻接增加O(V+E)图内存，图峰值未测；tracemalloc不是RSS；页缓存/系统负载未控制，文件I/O速度不作收益声明。这是单CPU宿主合成validator测量，不是模型质量、全系统成本/延迟提升。源码既有稳定目录假设与并发替换边界保持。

## 模型任务门禁检查点

固定候选上新的17案例（14角色、主AI、真实交接）最终17/17通过：16基础最终16/16、首次可评分收集15/16；corrected fresh writer1/1通过。合计首次可评分收集16/17，不含旧writer错误评分材料。评分者与执行材料隔离，真实工具代理、输入/Skill快照/产物/轨迹哈希绑定。首次收集包含工具QA，不能叫无辅助首次生成成功。

实际发现并保留：code-organization首次缺可执行rollback，fresh feedback retry通过；wrong-to-correct1/correct-to-wrong0仅此样本；mixed figure缺cairosvg首次渲染exit1、用现有工具修复并保留before。Writer旧rubric medium-regression与新fixture medium-parity矛盾，原run标ungradable1，修正事实后另prepare/fresh执行，不追溯变pass、不算模型恢复。Main rubric错误转账例仍保留，按原条显式equivalent correct settlement与独立净额oracle判分，没有改manifest。

根查看最终混合图、数据图PDF渲染、结构图及reader4物理页，核对writer实际接收到coordinator原字节/hash，复算主AI一般结算任务。详细矩阵与安全恢复/重放证据见 `evidence/model-eval/`，独立根复核见 `evidence/root-review.md`。全部模型门禁已通过；1.80MB共享快照归档，根实际安全恢复重放四run退出0，旧writer ungradable保留。最终回归仍为360总计352通过8跳过。发布/readback正在进行。

额外baseline代码阅读fresh任务与候选各1/1通过，case输入/任务/entry及该case rubric逐项相同；两版实际CLI均完成12MiB/1800链。20真实dispatch（≤21预算）。旧新程序A/B条件一致，原始指标如上；精确模型版本/seed/token/费用不可固定，因此模型收益A/B为inconclusive，不报告成功率提升。实际模型任务是合成/公开材料 smoke，实时backend、ClaudeCLI、GPU与目标服务器tmux/SSH断链未执行。

## TASK与下一步

T15论文/来源完成，T16程序改进通过；T17全部角色/交接通过且归档独立重放通过；T18发布/readback进行中。优先继续CO-016具体回滚保留任务及CO-020评分事实一致性；候选 CO-017有效scope/status前置检索、CO-018版本/条件绑定程序复用、CO-019无新观测空转与有界探索待测。先用现有权限下的纠错/位置/单位保留输入验证，不自动增加付费服务或无限探索。

本轮不是收敛轮次；没有完成全部模型门禁时不算有效无改进探索。持续优化保持启用，既有停止条件不变；没有新建重复自动化或声称已连接目标服务器监督器。
