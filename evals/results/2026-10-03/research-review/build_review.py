from pathlib import Path
import csv, hashlib, json
B=Path('/tmp/agent-forward-v1/research-review'); O=B/'outputs'; I=B/'inputs'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={p.name:sha(p) for p in sorted(I.iterdir()) if p.is_file()}
sid='REV-'+inputs['manuscript.md'][:12]+'-'+inputs['measurements.csv'][:12]
rows=list(csv.DictReader((I/'measurements.csv').open()))
checks=[]
for line,r in enumerate(rows,2):
 b=float(r['baseline_ms']); c=float(r['candidate_ms'])
 checks.append(dict(csv_line=line,**r,speedup_baseline_over_candidate=b/c,candidate_latency_change_percent=100*(c-b)/b))
with (O/'numeric_checks.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(checks[0]));w.writeheader();w.writerows(checks)
def write(name,text): (O/name).write_text(text,encoding='utf-8')
def structured(name,x):write(name,json.dumps(x,ensure_ascii=False,indent=2)+'\n')
snapshot=dict(id=sid,review_date='2026-10-03',inputs=inputs,pdf=None,venue=None,track=None,rubric='provisional rubric',scope='仅给定正文、附录及 CSV；未联网、未改稿、未执行新性能实验',submission_cutoff=None,search_cutoff=None)
structured('snapshot.json',dict(**snapshot,skill_mode='offline_fallback',skill_selection='用户指定本地 research-review；采用终端文本核对与 Python CSV 算术复算，不安装依赖、不检索候选。',skill_files={str(p.relative_to(B)):sha(p) for p in [B/'skill/SKILL.md',B/'skill/references/execution.md',B/'skill/references/workflow.md']},tool_version='Python 标准库；具体运行版本见 execution.txt',unverified=['实现与计时真实性','质量保持','方差与性能稳定性','新颖性、外部强基线与当前领域进展'],input_unchanged=True))
findings=[]
def add(fid,category,severity,atype,status,anchor,evidence,why,verify,options,accept,related=[]):
 findings.append(dict(finding_id=fid,snapshot_id=sid,category=category,severity=severity,confidence='high',assertion_type=atype,status=status,location=dict(physical_page=None,printed_page=None,anchor=anchor),evidence=evidence,why_it_matters=why,verification=verify,resolution_options=options,acceptance=accept,related_findings=related,history=[dict(state='open',note='材料内待核验项目；不是已成立的指控'),dict(state=status,note='正文、附录与 CSV 全部核验后判定')]))
add('REV-F001','correctness','major','confirmed_error','confirmed','manuscript.md:4（Abstract）；measurements.csv:2–5；附录 manuscript.md:10',[
 '摘要主张每个工作负载均有 2x 端到端加速且无退化。',
 'small 100/80=1.25x；medium 120/100=1.20x；large 200/220=0.90909x，候选时延增加 10%。',
 'kernel 20/10=2x，但 scope=kernel_only。Results 第8行明确核计时已包含在端到端路径中。',
 '附录第10行承认 200→220 ms 退化，与 CSV 一致，但未消除摘要矛盾。'],
 '给定观测直接反驳摘要的两个全称断言；微基准收益不能作为端到端收益。',
 '按 baseline_ms/candidate_ms 逐行复算，只将 scope=end_to_end 行用于端到端主张；对照附录。已完成，证据为 numeric_checks.csv。',
 ['最低充分处理：在后续获得改稿授权时，把摘要限制为给定 CPU 设置的单次观测，列明 1.25x/1.20x 及 large 时延增加10%，把2x明确限定为kernel-only。','如认为 CSV 标记或数值有误，先提供可追溯原始日志及新版本，不能凭猜测更改数据。'],
 ['摘要与所有三条端到端观测一致，并明确kernel-only范围。','若提供新证据推翻本输入，重新冻结快照并重算；仅重复摘要或引用附录不能撤销问题。'])
add('REV-F002','evidence','major','reporting_gap','confirmed','manuscript.md:4、8、10',[
 'Results 第8行明确每个值只有一次运行，无独立重复；附录第10行明确未测量方差。',
 'CSV 不含重复编号或重复样本；不同工作负载不是同一条件的独立重复。'],
 '材料支持这四组单次时延的描述，无法估计条件内不确定性或判断收益、退化是否稳定；此证据不足独立于 F001 的算术矛盾。此处 reporting_gap 指支撑证据缺口，不指作者隐瞒。',
 '检查正文与附录是否给出独立重复或方差，以及 CSV 是否含重复样本。已完成；这些材料未提供，不能由此断言作者从未做过其他实验。',
 ['无需新增实验的最小处理：明确探索性、单次观测，只陈述观测结果，删除普遍或稳定收益的表述。','若保留稳定性能结论，作者补充同一配置下每种方法和工作负载的独立重复、运行顺序与预热/计时方法，并报告样本量、效应量及不确定性；预先确定精度目标，不临时挑选有利运行。'],
 ['选择描述性范围：所有相关结论明确限定为单次观测，保留方差未知，不宣称统计显著或稳定无退化。','或选择稳定性主张：提供原始重复测量与分析，并让结论与不确定性一致；不以不显著证明等效。'],['REV-F001'])
add('REV-F003','reporting','minor','suspected_error','rejected','manuscript.md:9–10',[
 '反证核查：附录明确写出 large 从200 ms变为220 ms，且数值与CSV相符。'],
 '“退化未报告/被隐藏”不成立；应把有效意见限定为摘要与已报告结果矛盾。',
 '已读 Appendix A 并对照 CSV 第4行，疑点驳回。', ['不因该疑点改稿；保留 F001 的摘要矛盾。'],['附录中的退化报告与数据一致；本快照已满足。'],['REV-F001'])
add('REV-F004','correctness','minor','suspected_error','rejected','manuscript.md:8；measurements.csv:2–5',[
 '反证核查：正文明确 kernel-only pair 独立计时，已包含在端到端路径，要求不相加。'],
 '不能将核计时再加到端到端时延，也不能指控稿件已重复计时；独立核计时不能解释所有端到端差异。',
 '已核对 Results 原文与 scope 列；未发现文稿实施重复加和。', ['无需修改该计时范围说明；性能解释仅保留可直接支持的范围。'],['复算不把 kernel-only 行加进端到端数值；本轮 numeric_checks.csv 已满足。'],['REV-F001'])
structured('findings.yaml',dict(schema_version='1.0',agent='reviewer',snapshot=snapshot,findings=findings))
tasks=[]
for i,f in enumerate(findings):
 ids=[f'REV-T{3*i+j:03d}' for j in (1,2,3)]; rejected=f['status']=='rejected'
 for j,stage in enumerate(['verify','resolve','recheck']):
  status=('done' if j==0 else ('skipped' if j==1 else 'done') if rejected else 'blocked')
  action=[f['verification'], '驳回项不修改。' if rejected else '仅在后续获得明确改稿授权后，依据核验结果选择最小充分处理；本轮任务仅审阅。', '已复核驳回依据，无需修改。' if rejected else '对新快照逐项检查该发现 acceptance，并同步检查摘要、Results 和附录。'][j]
  tasks.append(dict(task_id=ids[j],finding_ids=[f['finding_id']],stage=stage,depends_on=[] if j==0 else [ids[j-1]],owner='reviewer' if j!=1 else 'main_ai_or_author',preconditions=['相同快照可访问'] if j==0 else ['上一步证据可读','仅修改阶段需要后续改稿授权'],action=action,outputs=['review_report.md','numeric_checks.csv'] if j==0 or rejected else [f'future/{ids[j]}.md'],done_when=[f['status']+'；依据见 findings.yaml'] if j==0 else (['有证据驳回，不修改原稿'] if rejected else f['acceptance']),on_missing_input='保持 blocked；列明缺失输入和恢复条件，不编造测量或修改记录。',status=status,blocker=None if status!='blocked' else ('本轮不授权改稿；主 AI/作者获得后续改稿授权后恢复。' if j==1 else '缺少处理后的新快照；上游完成后恢复。')))
structured('task_chain.yaml',dict(schema_version='1.0',snapshot_id=sid,tasks=tasks))
write('task_chain.md','''# 核验—处理—复查任务链

本轮已完成所有材料内核验。用户仅授权审阅，原稿未改，待修问题未标 resolved。

| 发现 | 核验 | 处理 | 复查 | 优先级/下一负责人 |
|---|---|---|---|---|
| REV-F001 摘要与数值矛盾 | REV-T001 done | REV-T002 blocked | REV-T003 blocked | 首先；主 AI/作者在后续改稿授权后按单次结果缩小摘要范围 |
| REV-F002 无稳定性证据 | REV-T004 done | REV-T005 blocked | REV-T006 blocked | 与F001同步；主 AI/作者选择描述性范围或新增重复测量 |
| REV-F003 隐藏退化疑点 | REV-T007 done | REV-T008 skipped | REV-T009 done | 附录反证成立，不修改 |
| REV-F004 重复加和疑点 | REV-T010 done | REV-T011 skipped | REV-T012 done | 计时说明反证成立，不修改 |

最先可执行的后续工作是决定要保留的主张范围。当前授权内无剩余材料内核验。处理阶段因“不改原稿”的范围约束暂停；复查依赖处理后的新快照。若仅保留探索性单次观测，无须为关闭F002强行安排新实验。若要主张稳定收益，补齐重复测量与计时日志后分析不确定性；性能实验尚未运行，也未获资源授权。

任何外部查新均不属于本次材料内任务；不把未联网判定为缺乏新颖性。各任务字段、依赖、撤销/关闭条件见 task_chain.yaml 与 findings.yaml。
''')
write('review_report.md',f'''# 材料内科学审阅

审阅日期：2026-10-03。快照：`{sid}`。标准：**provisional rubric**；未提供 venue、年份或 track，不给评分或录用概率。正文是明确标注的 synthetic fixture，不按正式完整投稿的篇幅要求额外制造缺陷。

## 中性总结与覆盖范围

方法替换一个选定核，在相同 CPU 进程及输入配置下测量三个端到端工作负载和一对独立核计时。摘要声称每种工作负载均2倍端到端加速且无退化；Results说明每值一次运行，核计时已包含于端到端路径；附录明确报告large退化，质量和方差未测。

已完整读取 manuscript.md（1–10行，包括Appendix A）及 measurements.csv（1–5行），先读稿件、附录，再用 CSV 复算。无 PDF、代码、原始计时日志、质量指标或重复测量。按任务要求未联网、未安装工具、未修改原稿、未运行性能实验。所有数字为给定CSV的算术复算，不是独立复现实验。

## 主张—证据映射

| ID | 主张/位置 | 给定证据与检查结论 |
|---|---|---|
| C1 | 摘要第4行：每个工作负载2x端到端加速 | CSV第2–4行分别1.25x、1.20x、0.90909x；直接矛盾，REV-F001 |
| C2 | 摘要第4行：无任何退化 | large时延增加10%；附录第10行主动报告；摘要矛盾，REV-F001 |
| C3 | Method第6行：替换选定核，同CPU/输入配置 | 仅有方法描述；无实现或环境日志可独立审计。不据此假定GPU结果 |
| C4 | Results第8行：独立核计时包含于端到端路径；每值单次 | kernel为2x，范围是kernel_only；不可相加。样本量不足以判断稳定性，REV-F002 |

## 可复核的优点

1. CSV 明确标注计时范围，Results解释包含关系，能避免把微基准与端到端计时相加。
2. 附录直接报告large的200→220 ms退化，与CSV一致；无依据指控隐藏结果。
3. 方法和附录明确CPU条件、无GPU测量、单次运行以及质量/方差缺口，限制可被准确定位。

## 主要问题

**REV-F001（major，high，confirmed_error）**：摘要第4行的全称断言与CSV不符。加速比定义为基线时延/候选时延；small=1.25x，medium=1.20x，large≈0.91x。large候选时延增加10%，其加速比低于1的幅度约9.09%，两种百分比不能混用。唯一2x来自kernel-only。最小补救是后续获得改稿授权后限定单次CPU观测及核计时范围，明确退化；只有可追溯的新日志证明当前数据/范围错误时，才重新评估这一意见。详见findings.yaml中的撤销条件。

**REV-F002（major，high，confirmed evidence gap）**：第8行和附录已披露无重复及方差，但仍不足以支持稳定、普遍收益。不能从一个观测估计条件内变异，也不能把三个工作负载当作重复。最小补救可以只缩小结论为描述性结果；若保留稳定收益主张，需独立重复、可追溯计时配置和不确定性分析。此意见不是“没有报告样本量”或“作者隐藏方差”，也不声称观测虚假。

## 反证检查与撤销项

- REV-F003 rejected：附录第10行已回答退化是否报告；不保留“隐藏退化”意见。摘要矛盾仍由F001处理。
- REV-F004 rejected：第8行已明确包含关系；没有稿件重复加和的证据，本轮未相加。不能将核微基准的10 ms节省机械地当作三个端到端变化的分解。
- 没有GPU主张，不要求GPU实验。没有质量保持主张，不把“未测质量”升级为已证实的质量下降；若后续宣称等质量替换，需要定义质量/正确性约束及检验证据。

## 可回答的问题及条件性判断

作者希望报告这次单次观测，还是声称可重复的稳定性能？前者允许通过范围澄清关闭F002；后者需要重复数据。若作者认为摘要数值正确，哪份具有版本和计时范围标记的日志可替代当前CSV？未提供这类证据前，F001成立。

当前材料能支持“核微基准2x，两个端到端单次观测变快，一个变慢”的有限描述；不能支持现摘要。先处理REV-F001，再同步决定REV-F002的证据范围。当前稿件仍为原快照，两个主要问题均未修复；另两个疑点已驳回。实现真实性、质量、可重复性和外部新颖性保持未验证。

## 版本与执行证据

输入 SHA-256、所用技能文件哈希与范围记录在 snapshot.json。numeric_checks.csv含逐行复算。build_review.py可重建本次审阅产物（会重写本轮输出，不触碰输入）。execution.txt记录实际运行和输入只读校验。结构化 .yaml 文件使用 YAML 1.2 兼容的 JSON 语法。下一负责人是主AI/作者；精确依赖、阻塞原因和验收条件见 task_chain.yaml / task_chain.md。
''')
write('novelty_utility_matrix.md','''# 贡献、新颖性与价值矩阵

日期2026-10-03；投稿截止/首次公开日期/版本日期均未知。未联网；没有外部原始来源，历史新颖性与当前新颖性均未核验，不认定已有更强方案或被支配。

| 主张 | 新颖性/最近工作 | 可行性 | 必要性与替代 | 公平性 | 收益/代价 | 状态与最小下一步 |
|---|---|---|---|---|---|---|
| C1 每个工作负载2x端到端加速 | 无来源，无法判断 | 给定观测不支持，不等于机制不可实现 | 材料内baseline是唯一对照；无法确定是最强替代 | 声明同CPU进程/输入；计时范围可分辨，无配置日志/质量约束 | 1.25x、1.20x、0.91x；成本未知 | insufficient_evidence；具体数值全称断言被反例反驳，按REV-F001处理 |
| C2 无任何退化 | 非新颖性证据 | large单次时延增加10%，普遍无退化不成立 | 是否按规模选择替换属于后续研究，不能从当前数据断言可行 | 同上；单次观测不能评估稳健性 | 收益随工作负载变化；质量未测 | insufficient_evidence；范围收缩及必要时重复测量 |
| C3/C4 替换核并观测kernel-only 2x | 无引用，历史和当前重合未知 | 数据与2x微基准算术一致；实现未审计 | 无核移除/选择机制说明；不认定组件必要或不必要 | 独立核计时不代表端到端所有条件 | 20→10ms；工程、能耗、维护成本未报告 | insufficient_evidence；保留为有限观测，不作实现/新颖性结论 |

最强替代方案：材料无法确定；仅有baseline。建议保留可核验的探索性定位并修正摘要，不因未查新要求转向。不增加未经支持的外部基线清单。
''')
write('domain_brief.md','''# 材料内问题定义与评价边界

本材料研究CPU上替换选定核的时延变化。定义加速比=baseline_ms/candidate_ms；大于1表示观测加速。端到端路径包含所计核，但独立核测量不是同次端到端trace的可加性分量。评价需分清微基准与端到端、单次描述与重复性推断、时延与质量。

唯一可访问对照是CSV中的baseline，未知其实现、调优预算及是否强基线。未知目标硬件型号、操作系统、运行顺序、预热、质量约束等，无法审计公平性全过程。本轮不以领域记忆补充“公认”强路线或瓶颈。对这个短synthetic fixture仅审给定主张，不要求完整系统论文材料。

当前/历史领域进展、新颖性及替代方案均未进行外部核验，详见search_log.md。
''')
write('search_log.md','''# 检索边界

review_date: 2026-10-03
submission_cutoff: unknown
search_cutoff: null
external_search_status: blocked_by_task_scope

任务明确仅材料内审阅、不联网，因此未执行任何网络查询、外部技能发现、文献更新或第三方上传。没有查询串或外部命中；不把空检索当“没有相关工作”。用户指定技能与本地Python标准库足以完成稿内核对，采用offline_fallback。外部查新的恢复条件仅是未来任务明确改变范围，当前无需请求扩权。

材料搜索/读取：完整读取稿件、CSV、技能入口、执行补充及工作流，并对照附录排除隐瞒退化和重复计时误报。来源注册表只记录实际读取的本地材料。正文先读、附录核对完成后才使用CSV进行第二阶段复算。
''')
structured('source_registry.yaml',dict(review_date='2026-10-03',sources=[dict(source_id='SRC-MANUSCRIPT',path=str(I/'manuscript.md'),sha256=inputs['manuscript.md'],coverage='1–10行，含附录A',kind='synthetic manuscript'),dict(source_id='SRC-MEASUREMENTS',path=str(I/'measurements.csv'),sha256=inputs['measurements.csv'],coverage='1–5行，全部4条观测',kind='author supplied measurements')],external_sources=[]))
assert inputs=={p.name:sha(p) for p in sorted(I.iterdir()) if p.is_file()}
ids={t['task_id'] for t in tasks}
for t in tasks: assert all(x in ids for x in t['depends_on'])
seen=set()
for t in tasks: assert set(t['depends_on'])<=seen;seen.add(t['task_id'])
print(json.dumps(dict(snapshot_id=sid,inputs_unchanged=True,numeric_rows=len(checks),findings_by_status={'confirmed':2,'rejected':2},tasks=len(tasks),dependency_check='passed',artifacts=sorted(p.name for p in O.iterdir())),ensure_ascii=False,indent=2))
