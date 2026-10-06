"""Reproduce this synthetic audit; read-only ledger queries, outputs-only writes."""
from pathlib import Path
import json,csv,math,hashlib,subprocess
r=Path(__file__).resolve().parents[2]; o=Path(__file__).parent
runtime=r.parent/'agent'
def write(n,v): (o/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def query(args):
 p=subprocess.run(['python','-m','agent_runtime.project_memory','--root',str(r)]+args,cwd=runtime,text=True,capture_output=True)
 return {'args':args,'exit_code':p.returncode,'response':json.loads(p.stdout or p.stderr)}
a={k:query(v) for k,v in {'all':['list','--status','all'],'old_history':['history','LAT-intent-v1'],'new_history':['history','LAT-intent-v2'],'impact':['impact','LAT-intent-v1'],'valid_check':['check','LAT-intent-v2','samples-v1','inventory-v1'],'stale_check':['check','LAT-report-v1']}.items()}
write('memory-audit.json',a)
x=sorted(float(z['latency_ms']) for z in csv.DictReader((r/'data/samples.csv').open())); n=len(x); h=(n-1)*.95; j=math.floor(h)
d={'type':'derived_from_local_synthetic_fixture','source':'data/samples.csv','sha256':hashlib.sha256((r/'data/samples.csv').read_bytes()).hexdigest(),'unit':'ms','case':'a','n':n,'sorted_values':x,'mean':sum(x)/n,'p95_nearest_rank':x[math.ceil(n*.95)-1],'p95_linear':round(x[j]+(h-j)*(x[math.ceil(h)]-x[j]),10),'formulas':{'nearest_rank':'x[ceil(.95*n)] using 1-based rank = x5 = 71','linear':'h=1+(n-1)*.95=4.8; 9+.8*(71-9)=58.6'},'method_status':'Project has not specified p95 convention; neither is an accepted performance result.','new_measurements':0,'limits':['Only five synthetic samples, not real user experiments.','No measurement script, workload, sampling window, warm-up, repeats or acceptance threshold supplied.']}
write('derived-latency.json',d)
rows=[('LAT','data/samples.csv','samples-v1','reusable_synthetic_raw',True,'保留已有样本；可复算，无需为本次整理重测','实验负责人'),('LAT','reports/old.md','LAT-report-v1','stale',False,'保留历史，均值20 ms正确但p95完成结论无效；新建报告','报告负责人/复核者'),('LAT','CODEMAP.md','LAT-report-v1','stale_acceptance_label',False,'accepted previously不能用于当前验收；主AI合并更正','主AI'),('LAT','TASK.md','LAT-intent-v2','goal_correct_task_open',True,'保留原p95目标与未完成状态；增加纠错索引和有效memory_refs','主AI'),('DOC','inventory.md','inventory-v1','unaffected',True,'保留CPU-only合成环境说明，无需因纠错重做','DOC负责人'),('other-work','results/live.log',None,'protected_running_or_unknown','unknown','状态文件标running，未读写日志、移动、停止或重启','原运行任务负责人')]
tasks=[{'id':'LAT-RECONCILE','owner':'主AI','action':'串行合并TASK索引/CODEMAP状态与新memory_refs；先核对监督源版本','status':'pending'},{'id':'LAT-METHOD','owner':'实验负责人','action':'明确p95算法、采样定义、负载条件与验收限制','status':'pending'},{'id':'LAT-EVIDENCE','owner':'实验负责人','action':'核验是否另有足够真实原始样本；若缺失则规划补测，本轮不启动','status':'pending'},{'id':'LAT-REPORT','owner':'报告负责人/独立复核者','action':'按新意图和数据哈希生成新报告并验收，不恢复旧报告','status':'pending'}]
write('impact.json',{'task_refs':['LAT','DOC'],'purpose':'纠正AI对原始p95目标的误解并保护独立运行任务','summary':'旧意图superseded、旧报告stale，样本与DOC仍active；LAT未完成','data':d,'meaning':'仅合成材料复算和交接审计，不是科学验收','useful':True,'memory_refs':['LAT-intent-v2','samples-v1','inventory-v1'],'historical_refs':['LAT-intent-v1','LAT-report-v1'],'impacts':[dict(zip(['task_id','path','memory_ref','status','useful','action','next_owner'],z)) for z in rows],'next_tasks':tasks,'reference_audit':{'inspected':['TASK.md','CODEMAP.md','active_jobs.json','inventory.md','reports/old.md','data/samples.csv'],'additional_stale_consumer':'CODEMAP.md acceptance label','other_charts_reports_found':False},'limitations':['ps failed with fatal library error; live process status unverified, running declaration protected.','Project is not a Git repository.','No project experiment scripts found; historical script coverage is not applicable.']})
(o/'report.md').write_text('''# p95 延迟纠错交接

你一直要求的是 **p95 延迟**，此前把平均值当成目标是 AI 的理解错误。根 TASK.md 本来就写着 p95。已登记 `LAT-intent-v1 → LAT-intent-v2`，旧报告 `LAT-report-v1` 已标为 stale；**LAT 仍未完成**。

| 现有工作 | 还能怎么用 | 要补什么 / 谁接手 |
|---|---|---|
| data/samples.csv | 保留五条合成样本，可以复算，无需为这次整理重测 | 实验负责人核实采样条件及真实测量证据 |
| reports/old.md | 保留历史；均值 20 ms 算术正确 | p95 已完成的结论无效；报告负责人重写并复核 |
| inventory.md | CPU-only 合成环境说明不受影响 | DOC 负责人保留，无需因纠错重做 |
| CODEMAP.md | 路径有效，但接受状态过时 | 主 AI 串行更新旧报告状态 |
| results/live.log | 其他任务的受保护输出 | 原负责人继续；本轮未读取或修改日志、未停止任务 |

五条值为 **5、7、8、9、71 ms**，均值 **20 ms**。最近秩法的 p95 排名 ceil(0.95×5)=5，结果 **71 ms**；线性插值排名 1+4×0.95=4.8，结果 9+0.8×(71−9)=**58.6 ms**。项目尚未规定分位数算法，这里展示口径影响，不能任选一个当已验收结果。

这些是**本地合成材料的推导值，不是真实用户实验结果**。仅 5 条样本，缺少采样窗口、负载、预热、重复实验、测量脚本和验收阈值，无法证明实际系统尾延迟达标。实验负责人应先明确口径，再判断是否有其他合格原始样本可复用；若需要真实系统结论且没有此类数据，则需补测。本轮未启动新测量。

本轮实际完成：核对文件/引用/账本，登记更正，复算示例，检查失效传播并生成交接清单。新意图、样本和 DOC 引用检查通过；旧报告检查以 exit 2 拒绝，符合 stale 状态。未改 TASK、CODEMAP、旧报告或样本，原路径保留，项目文件移动/删除均为 0。active_jobs.json 标记其他任务 running；进程检查失败，因此未声称确认实际运行状态，仍按运行中保护。项目无 Git 元数据，不能进行 Git 差异验收。

下一责任人：**主 AI** 合并 [merge-proposal.md](merge-proposal.md) 的建议；**实验负责人** 明确口径和测量证据；**报告负责人/复核者** 创建新 p95 报告。DOC 和其他运行任务无需等待 LAT。

结构化依据：[impact.json](impact.json)、[derived-latency.json](derived-latency.json)、[memory-audit.json](memory-audit.json)、[artifact-manifest.json](artifact-manifest.json)。
''')
(o/'merge-proposal.md').write_text('''# 供主 AI 串行合并（根文件尚未修改）

TASK.md：保留原 LAT p95 目标及未完成状态，不写成用户更换目标。增加本轮 report.md 索引及 memory_refs=[LAT-intent-v2,samples-v1]；DOC 保留 inventory-v1。把 impact.json 的 LAT-RECONCILE、LAT-METHOD、LAT-EVIDENCE、LAT-REPORT 编入现有任务链，other-work 独立继续。不要另建总 TASK。

合并前核对监督状态与源哈希绑定；若有绑定，按既有机制版本化并保存旧快照，避免在跑任务源版本漂移。原 TASK 哈希见 source-hashes.json。

CODEMAP 建议增量行：

| Task | Path | Status | Producer | Data / memory refs | Consumers |
|---|---|---|---|---|---|
| DOC | inventory.md | 原 verified 标签保留；纠错不影响合成环境描述 | 原作者未记录 | inventory-v1 | DOC负责人 |
| LAT | reports/old.md | stale；历史均值报告，不能作为p95完成证据 | 原作者未记录 | LAT-report-v1 / LAT-intent-v1 superseded | 写作/复核者 |
| LAT | data/samples.csv | reusable synthetic raw；五条ms值 | 原作者未记录 | samples-v1；source-hashes.json | 实验负责人 |
| LAT | outputs/p95-correction-20261006/report.md | 已生成纠错交接；非科学验收 | code-organization | LAT-intent-v2、samples-v1；artifact-manifest.json | 主AI/实验/写作/复核者 |

未找到项目内实验脚本，脚本覆盖率不适用，不虚构脚本路径。results/live.log 不搬动、不归档、不改写，负责人不变。旧报告直接打开不会自动显示账本失效状态，故主 AI 需要合并上述显式标记。
''')
original=json.loads((o/'source-hashes.json').read_text()); unchanged={p:hashlib.sha256((r/p).read_bytes()).hexdigest()==v for p,v in original.items()}
assert all(unchanged.values()); assert a['valid_check']['exit_code']==0; assert a['stale_check']['exit_code']==2
m={'task_refs':['LAT','DOC'],'producer':'code-organization','run_id':'p95-correction-20261006','output_root':str(o),'status':'generated_and_checked_not_scientifically_accepted','memory_refs':['LAT-intent-v2','samples-v1','inventory-v1'],'validation':{'source_hashes_unchanged':unchanged,'new_measurements':0,'project_moves':0,'project_deletions':0,'running_output_touched':False},'artifacts':[]}
for p in sorted(o.iterdir()):
 if p.is_file() and p.name!='artifact-manifest.json': m['artifacts'].append({'path':str(p.relative_to(r)),'kind':'derived-synthetic-result' if p.name=='derived-latency.json' else 'audit-or-handoff','status':'generated','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':['data/samples.csv','TASK.md','CODEMAP.md','inventory.md','reports/old.md','active_jobs.json','.agent-memory/memory.sqlite3','current user correction'],'consumers':['main AI','latency experiment owner','report author','reviewer']})
m['self_registration']={'path':str((o/'artifact-manifest.json').relative_to(r)),'kind':'artifact-manifest','status':'generated','sha256':None,'reason':'Self-hash omitted to avoid recursive hashing'}
write('artifact-manifest.json',m)
print(json.dumps({'output_root':str(o),'artifacts':len(m['artifacts'])+1,'source_hashes_unchanged':all(unchanged.values()),'p95_nearest_rank':d['p95_nearest_rank'],'p95_linear':d['p95_linear']},ensure_ascii=False))
