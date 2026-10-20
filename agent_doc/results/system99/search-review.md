# SYSTEM-99 H1：独立查询漂移审查

结论：严格拦截**候选、缺口或未知输入变化**是有意契约，不能删除。当前实现还把仅 `scanned` 变化视为必须重规划；本轮已用真实 `ResultStore → ReviewSession → Engine → ReportingHandler` CPU fixture 确认这种保守可用性限制。它不是错误授信或安全绕过。完整双生产者、各自独立 gate 的因果链由主控另行验证；本文不冒领其结果，也不声称生产宿主/模型部署已验。

## 范围与当前决定

- 源版本：`789697f2b3e2e190a6954248d4b18cbbe0b44a4d`；起始 `git status --short` 为空。仅新增本文，不改源码、TASK、guide 或旧结果。源码/TASK 由主控独占；本角色不拉取整合、发布或改变冻结源版本。
- 已完整读取 `AGENTS.md`、`prompts/decision_review.md`、`prompts/review_main.md`、`workflows/project_document_workflow.md`、`workflows/dual_main_workflow.md`、`workflows/result_reuse_workflow.md`，核对 SYSTEM-99 v5、零字节 GUIDE 及既有 `independent-chain-audit.md`。
- 决策：`EXECUTE` 只读追踪和既有授权内低风险 CPU 判别；实现修复仍属主控版本化方案/独立审查范围。本文不是运行时认证回执，不批准新预算/服务或越过工具授权。
- 历史先查：实际命令 `python scripts/result_store.py --root /workspace/scratch/6416f20dc59b/agent-audit97 search 'prior_result_search ReportingHandler scanned' --limit 5 --max-scan 5000`，返回 `scanned=252, status=incomplete, results=[], partial=false`，错误为现有缺登记目录（含 system99）。无候选不证明无历史文本。既有 H1 仅静态假设，不能复用为本轮完整复现；旧 search-invariant 的性能/等价结果也不是本轮调度证据。

## 实际交接链

| 边界 | 固定源码事实 | 结论 |
| --- | --- | --- |
| prepare → 计划 | `task_manifest.py:56–66,89–119` 对每个标题实际搜索并存完整 `prior_result_search`；失败转 unavailable/partial/errors，不伪造 absence。 | 结果统计目前确实进入计划，不只是日志。 |
| 计划 → 审核 | `plan_review.py:49–51` 哈希只排除顶层 receipt；`current_inputs:170–191` 绑定候选 record 与声明证据的当前字节。 | 不可从计划哈希中全局排除搜索字段或未知 adapter 字段。 |
| 审核 → 派发 | `ReportingHandler.run:246–284` 首次 claim 做活查询、写 journal、核对 planner 判断；保护 producer/reuse 比较整个响应，不同则 blocked。 | 对错误/截断/新候选保持 fail-closed 是现行有意行为。 |
| 保护派发 → handler | `task_manifest.py:271–286` 先 deepcopy；保护分支不换搜索输入，非保护分支才注入活查询。 | 不能为解除阻塞把新响应静默塞进已审任务。 |
| producer → ResultStore | `task_manifest.py:304–312` 完成报告通过后调用 `register_task_result`；`result_store.py:498–526` 登记新结果或核对精确重放。 | pending 登记不是独立科学验收；后续 gate/消费者仍必须验证。 |
| ResultStore → 搜索 | `_directories:230–250` 收集有界目录；`search:350–394` 逐目录 show，只有命中才入 results，但所有目录计入 scanned；错误、截断仍返回。 | 新合法不命中目录可只改变 scanned；新未登记输出目录通常还会改变 errors，后者不能当纯统计忽略。 |

`dual_main_workflow.md` 明确“候选/缺口变化不能静默替换输入，应重编排”；未明确要求扫描计数独立触发重审。因完整响应又是已审 adapter 输入，现行为一致且保守，不属于已证明违反安全契约的实现错误。把这一保守限制缩窄到语义证据变化，需要显式声明新比较边界，而非声称原先允许绕过。

## 本轮独立判别

首个简化探针只设置 `produces_data=True`，未提供 experiment_result/gate，`ReviewSession.submit` 在 `validate_result_plan` 报 `experiment/data producer requires experiment_result`。该次不构成有效复现；清理 fixture 后重建完整合法 producer/gate。保留这个失败说明没有通过删结果门禁来获得阳性。

第二次使用既有 `tests/test_plan_review.py` 的 `PlanReviewTests`，真实 prepare/ReviewSession 审核后，调用实际 `register_history` 添加一个合法、词法不相关的登记，再由 Engine 派发保护生产者。结果：

```json
{
  "changed_fields": ["scanned"],
  "before": {"status":"no_hits","results":[],"scanned":0,"partial":false,"errors":[]},
  "after": {"status":"no_hits","results":[],"scanned":1,"partial":false,"errors":[]},
  "state":"blocked",
  "node_status":"blocked",
  "reason":"prior-result evidence changed after main review; versioned replan required",
  "underlying_handler_calls":0,
  "journaled_live_search_equals_after":true
}
```

完整 before/after 的 schema/query/strategy/authority 也完全相等。这里历史登记只用于制造实际目录/记录增量；并非 A 生产者的数据验证，也不是把旧历史授信。本探针有一个合法独立 gate 声明，但 gate 不执行，因为 producer 在副作用前已被拦截。因而独立确认的是“纯统计漂移会阻塞保护派发”，不是完整双生产者流水线已复现。

实际执行的第二探针命令（仅临时 fixture 写入，`doCleanups()` 清理）：

```bash
PYTHONDONTWRITEBYTECODE=1 python - <<'PY'
import copy, hashlib, json, sys
sys.path.insert(0, 'tests')
from test_plan_review import PlanReviewTests
from agent_runtime.result_store import ResultStore
from agent_runtime.core import ArtifactHandler, Engine, Store
from agent_runtime.task_manifest import ReportingHandler
class CountingHandler(ArtifactHandler):
    calls = 0
    def run(self, task, context):
        self.calls += 1
        return super().run(task, context)
case = PlanReviewTests('test_prepare_protected_and_missing_receipt_cannot_dispatch')
case.setUp()
try:
    task = case.plan['tasks'][0]
    protocol = case.root / 'validation-plan.json'
    protocol.write_text('{"scope":"synthetic fixture only"}\n')
    contract = {'result_id':'synthetic-result', 'producer_task_id':'T1',
        'producer_actor':task['owner'], 'manifest_path':'agent_doc/results/fixture/manifest.json',
        'validation_plan':{'path':protocol.name, 'sha256':hashlib.sha256(protocol.read_bytes()).hexdigest()},
        'scope':'Synthetic plan-review fixture; data not yet produced'}
    task['experiment_result'] = contract
    gate = copy.deepcopy(task)
    gate.pop('experiment_result')
    gate.update(task_id='verify-T1', action='verify_experiment_result', owner='independent-verifier',
        depends_on=['T1'], result_validation=contract, report_path='.agent-runs/verify-T1.json')
    case.plan['tasks'].append(gate)
    before = copy.deepcopy(task['prior_result_search'])
    case.approve()
    ResultStore(case.root).register_history('zzz-unrelated', 'qqq zzz', [
        {'path':'result.txt', 'sha256':hashlib.sha256(b'ok').hexdigest()}])
    after = ResultStore(case.root).search(task['inputs']['goal'])
    store = Store(case.root / 'run.sqlite')
    store.create(case.plan)
    handler = CountingHandler(case.root)
    engine = Engine(store, {'verify_artifacts':ReportingHandler(handler, case.root)},
        authorize=lambda *_:True, project_root=case.root, plan_review_verifier=case.session.verify)
    state = engine.tick('r1', 'new-unrelated-registry')
    node = state['tasks']['T1']
    with store.transaction() as db:
        logs = [json.loads(row['detail']) for row in db.execute(
            "SELECT detail FROM journal WHERE kind='prior_result_search'")]
    print(json.dumps({'kind':'CPU-fixture-one-producer-plus-gate-unrelated-registration-not-live-model',
        'changed_fields':[k for k in sorted(set(before)|set(after)) if before.get(k)!=after.get(k)],
        'before':before, 'after':after, 'state':state['status'], 'node_status':node['status'],
        'reason':node['reason'], 'underlying_handler_calls':handler.calls,
        'journaled_live_search_equals_after':logs[-1]['search']==after}, ensure_ascii=False, indent=2))
finally:
    case.doCleanups()
PY
```

其它实际命令：`git rev-parse HEAD`、`git status --short`、针对上述源码/测试的 `rg`/`sed`/`cat` 只读定位；`PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p test_plan_review_independent.py -v`（31/31 通过），同方式 `-p test_result_store.py -v`（21/21 通过）。这52项验证既有门禁，不包含新的双生产者回归；未跑本轮全库，无GPU/收费/模型调用/服务启动。

## 最小可验证修复边界（建议，不是已实施/已验收）

最小候选：保持原计划完整哈希及原 `dispatched_task` 不变，仅把**完整、已知 schema 且穷尽无错误**搜索中纯 scanned 差异分类为非阻塞观测。可保守限定两端字段集合严格等于当前 v1、字段类型合法、`partial is False`、`errors == []`、除 scanned 外逐字段完全相等；unknown schema/额外字段/缺字段/错误类型仍拒绝。日志保留完整新旧响应及分类理由。此规则不改变当前 handler 看见的已审搜索输入，不使 hit 自动复用，也不触碰计划认证/验收。

| 情况 | 应保持边界 |
| --- | --- |
| 完整无错查询仅 scanned 增减，候选/状态/其它字段不变 | 可作为最小显式新契约评估；须证明 handler 收到的仍是原冻结 task。 |
| 新候选、候选消失/哈希/排序/分数/元信息变化 | 当前重规划保留；“属于本DAG”或“未独立验收”不能自动忽略。 |
| errors/partial/status、查询/策略/schema/未知字段变化 | fail-closed 保留；特别是两个响应都 partial/都有错误，也不能仅删除这些字段后宣称等价。 |
| A 新建无 record 的输出目录，B errors 新增/旧缺口消失 | 属于真实发现缺口变化；不能当统计噪声。新建目录的时间与计划搜索时点须在双生产者复现中单独控制。 |
| 扫描预算/limit 或有界枚举截断改变 | 不自动允许；超出预算可藏候选，且 `_directories` 不承诺跨扫描快照隔离。 |

不可接受方向：关闭活查询、只比 run_id 忽略 hash/缺口、legacy 降级、把新响应写回已审计划/handler、从 plan_sha256 全局排除 prior_result_search、放宽 producer/gate 或独立结果验收、隐藏新候选/错误、把同一计划自产结果普遍排除。若要定义“已审DAG预期新结果集合”，这是更大查询/审核语义设计，须独立固定来源身份、污染/撤销、候选哈希与可见性，不能用此小修顺带加入。

验收最少包含：完整实际CPU双生产者各自独立gate且不同result run_id；确保 A 正常报告/登记后 B 才派发；无关合法登记的纯scanned情境；相关候选、候选改hash/消失、新坏目录、partial/不可用、未知字段负控；显式复现/new_claim不被跳过；journal保留完整活查询；handler输入逐字等于已审任务；重启后同规则；独立结果gate/consumer依旧执行且当前验收。没有这些，不把本探针结果外推为并发改进已完成。

## review-main 七项核对

| 项 | 本轮只读判别 | 修复接受条件 |
| --- | --- | --- |
| intent | pass：定位H1且不以并发名义关闭检查。 | 不改变用户目标或授信边界。 |
| guide | pass（有限）：现GUIDE空，未写人类目录；当前授权来自主控交接。 | 主控核对新TASK/稳定Plan版本。 |
| assumptions | pass：明确CPU fixture/真实宿主区别，失败简化探针已披露。 | 全双生产者及并发/重启边界另验。 |
| prior_results | pass：先查并记录incomplete，不将旧测试/登记当验收。 | 新候选与缺口变化继续重审。 |
| acceptance | pass于本轮窄结论；实现验收尚unknown。 | 上述正负控与输入不变断言。 |
| risk | pass：仅本文新增和临时CPU fixture；无源修改/权限扩张。 | 防止静默换输入、放宽unknown及自动复用。 |
| resources | pass：实际52项CPU测试；生产宿主/模型成本质量unknown。 | 不将程序fixture冒充独立宿主认证或收益。 |

综合意见：支持主控继续该有限CPU判别，并将“仅统计漂移”的可用性缺口与“必须重审的发现变化”分开；**不审批尚未提供的修复实现**。当前保守行为可作为明确设计限制保留；若主控要改善它，先固定上述语义边界及新验收，再由独立角色复核。

## Version6 阶段F独立方案审核（追加，不覆盖前述证据）

决定：`approve`，仅批准主控按阶段F窄边界实现并验证；不是代码/结果验收通过，也不是运行时签名回执。当前源码仍为 `789697f2b3e2e190a6954248d4b18cbbe0b44a4d`，生产源码尚无本修复。独立读取的对象：

- `agent_doc/task/task_details/SYSTEM-99.md` Version6，完整文件 SHA-256 `b639ade3b4135ef68c4b5c6a33e68f03c7c20b578b869aa3ea74d1a2b4e457af`；git diff 仅 Version5→6 与增加阶段F段落，未修改其余既有要求。
- `tests/test_prior_search_drift.py`，SHA-256 `b54bec509a4bdd80dbfa24b97a6c1cdb36482ad21665d5d00bbbc014f7eef0bc`，已全文阅读。
- `.agent-runs/system99/drift-before-v2.log`，实际 `sha256sum` 为 `a45c6dbf880c96d00cde24adccc6117bbefa5614820d1f0143ee9102853a19ea`，末尾5方法2失败；这是新修前日志，不替换或追溯改变首版fixture错误记录。

实际独立命令 `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_prior_search_drift -v`：5方法，2断言失败、3通过、0 error，与冻结日志一致。alpha真执行CPU代码、完成报告/中央登记，verify-alpha通过独立算术/代码/数据检查后done；beta因整个查询不同而blocked。两个失败分别覆盖继续派发与重开Engine，且已有断言证明第二生产者查询仅scanned 0→1。新候选和新坏目录负控通过。该补充使原先“尚未独立复现双生产者链”更新为：**现已独立复跑真实CPU双生产者DAG的修前阻塞链**；修后第二生产者与gate完成仍待实现验证。首版canonical producer未中央存储的5errors不作生产红证。

拟议私有helper不修改搜索器、缓存或计划：两端必须是完整已知9键 `project-result-search/v1`/`lexical`，合法类型、query/authority及status/results一致，默认scanned为非bool int且0..200、至少覆盖返回hits，无错误/截断；除此计数之外全部相同才允许。完整plan SHA、原task及传给handler的搜索保持不变；现有活查询journal不减少，增加明确分类计数。该边界可在当前ReportingHandler中实现，不必扩大权限、跳过_result gate或新增模型/服务。

七域核对：

| 检查 | 状态 | 理由 |
| --- | --- | --- |
| intent | pass | 只解除已确认的纯扫描统计假阻塞；不把并发优先于计划/结果验收。 |
| guide | pass | GUIDE仍零字节且只读；当前明确交接授权允许该CPU边界，SYSTEM-99既有要求保留。 |
| assumptions | pass | 冻结Plan/test/log哈希已核对；真实CPU双生产者前置与独立gate已到达；宿主/模型质量仍未知且不据此决策。 |
| prior_results | pass | 原本次检索与独立单producer探针保留；现在只补有判别力的双producer复跑，不把登记或旧pass当复用授权。 |
| acceptance | pass | 正向、重启、候选/缺口负控及全库/Reader/独立结果复查已在计划中；下述测试注意须在结果接受前完成。 |
| risk | pass | 严格白名单仅scanned差异、冻结输入不变，候选hash/顺序/分数、unknown/errors/partial继续阻塞；没有授权扩张。 |
| resources | pass | 有现成本地CPU fixture与现有认证fixture；不需要GPU/收费模型/后台部署，未承诺性能收益。 |

实施与结果验收注意（非阻止此窄方案实现的意见；结果接受前必须关闭）：

1. `test_partial_unknown_fields_and_invalid_counts_still_block` 目前在同一Store上循环。首个partial子例把beta持久blocked，后续仅重开Engine不会自行重新派发，故其它字段子例可能空过；每个变更应用独立fixture/Store，或显式证明每例wrapper确实执行并journal对应新查询。不能据当前3个通过方法声称unknown/True/-1四种变更均已真实进入门禁。
2. 除scanned“完全一致”须类型敏感，避免Python `True == 1`、`1.0 == 1`的宽相等；例如严格类型校验配合标准JSON字节比较。新增/缺失字段、非有限值、畸形hits/status/查询/authority与扫描计数边界应有helper表驱动覆盖；候选hash、排序、分数差异均有独立负控，不只测“新增候选”。不要求扩大helper支持其它schema/策略。
3. 正向用例须验证两个producer各调用一次、两个独立gate确实完成，beta收到的整个已审task（不只搜索字段）不变，计划SHA/回执未改写，日志同时保留活响应与分类。重启用例须继续验证不触发第二次计划审核；明确复现/new_claim依旧实际执行，不能变成复用。
4. 新增分类日志如果失败，不能吞异常后放行；复用现有事务/日志路径，不更改Engine授权或结果注册语义。保留失败/已执行副作用的恢复边界。

compact verdict：`decision=approve; checks={intent:pass,guide:pass,assumptions:pass,prior_results:pass,acceptance:pass,risk:pass,resources:pass}; blocking_findings=[]`。批准对象仅上述Version6及交接中同一helper边界；实际实现若放宽unknown/错误/截断、替换dispatch输入或排除计划字段，需重新审查，不在本次approve内。

### Version6 输入修正复查：独立负控已关闭空过缺口

主控随后仅修正测试隔离；Plan哈希不变。已读取修正测试：`tests/test_prior_search_drift.py` SHA-256 `17ba2b2b083df0f9df87e5fc25ecd8ab4195a3ab586339a7920e555d32f1f08f`；`.agent-runs/system99/drift-before-v3.log` SHA-256 `f0654e4be7dad59c387cea9a5aeb0b0a343eda24dbb9b69cf35b00eb6e6c1d4d`，实际核对相符。

partial/未知字段/bool/-1各成独立test，使用各自setUp/Store；共享`block_changed_search`同时断言lookup确实一次及beta journal等于对应observed。因此上述注意1针对旧测试版本的缺口现已关闭。实际独立复跑命令 `PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_prior_search_drift -v 2>&1 | tail -n 6`，报告8方法、2失败、6通过、0error；两个原有CPU双producer/重启断言仍在同一原因失败，未用fixture错误替代生产红证。

基于修正输入，再次明确 `decision=approve`：七域状态均为pass、无阻止Version6窄方案实施的finding。批准绑定上述Plan6哈希与当前测试哈希；注意2–4继续作为实现/独立结果验收要求，尚未宣称代码修复通过。完整原审查和首版失败证据保持不变。
