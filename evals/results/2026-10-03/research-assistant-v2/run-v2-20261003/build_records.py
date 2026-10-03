from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
R=O.parents[1]
run='run-v2-20261003'
def dump(n,obj): (O/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
dump('historical_state.json',json.loads((R/'inputs/project.json').read_text())['state'])
tasks=[]
def task(id,stage,deps,inputs,action,outputs,done,status='done',recovery=None,owner='本执行者'):
    tasks.append(dict(task_id=run+'/'+id,stage=stage,depends_on=[run+'/'+d for d in deps],owner=owner,inputs=inputs,action=action,outputs=outputs,done_when=done,on_failure=recovery or '保留原输入及已有产物；修正本任务后只重建依赖它的后续产物。',resource_budget='仅本地 CPU；单项分析至多 60 秒；无新性能实验、GPU 或外部服务；资料缺失即停止依赖项。',status=status))
task('RES-T001','input-audit',[],['inputs/project.json','inputs/measurements.csv@v2','inputs/concept.txt@v1'],'读取版本声明并校验 CSV；记录内容哈希，不重采集。',['input_manifest.json'],'4 行均通过有限正数、scope、唯一标签检查；三个输入哈希已记录。')
task('RES-T002','retention',['RES-T001'],['project.json.state','concept.txt@v1'],'追踪测量变更的直接及传递依赖；保留历史状态并明确缺失产物。',['retention_check.md','historical_state.json','project_state.md'],'列出 collect/figure/write/background 的处置；不得把缺失 background 正文称为已验收。')
task('CODE-T001','analysis',['RES-T001'],['measurements.csv@v2'],'运行 analyze.py，计算每行速度比及延迟变化，保留两类 scope。',['analyze.py','derived_metrics.csv'],'small=1.25×、medium=1.20×、large=0.90909×、kernel=2.00×；无混合范围总体收益。')
task('RES-T003','decision',['CODE-T001'],['derived_metrics.csv','input_manifest.json'],'据已知值作有条件继续判断，列证据边界。',['results.md','claim_evidence_ledger.yaml'],'指出 large 回退；继续仅限补资料后诊断；不宣称因果、显著性或普遍提速。')
task('FIG-T001','figure',['CODE-T001'],['measurements.csv@v2','derived_metrics.csv'],'使用 analyze.py 生成分范围的两面板图并实际查看 PNG。',['figure_v2.png','figure_v2.svg','figure_v2.pdf','qa.md'],'图含全部 8 个报告值、单位、分范围标签、零起点；无虚构误差棒；完成 PNG 视觉检查。')
task('WRITE-T001','writing',['RES-T003','FIG-T001'],['derived_metrics.csv','figure_v2.png','claim_evidence_ledger.yaml'],'撰写结果段落和图注；逐项核对数字、范围和限制。',['results.md'],'结果含 small/medium 收益、large 退化及 kernel 边界，标注重复次数和配置缺失。')
task('RES-T004','delivery',['RES-T002','WRITE-T001'],['本轮产物','task_chain.yaml'],'检查任务依赖存在、无环、done 产物存在；绑定文件哈希。',['qa.md','validation.json','artifact_hashes.json'],'所有 done 输出存在；依赖 DAG 无环；当前交付不依赖缺失的历史背景产物。')
task('RES-T005','restore-background',['RES-T002'],['background@v1（缺失）','concept.txt 历史版本（缺失）'],'仅在要复用背景时，找回旧正文及输入版本并核对。',['background_reuse_audit.md'],'实际正文与其输入版本可定位，完成内容审读再允许引用。','blocked','项目维护者提供原 background@v1 及来源；不需重采样，也不阻塞当前结果段落。',owner='项目维护者')
task('RES-T006','recover-existing-evidence',['RES-T003'],['原始配置、日志、代码（缺失）','目标权重与容许回退（未知）'],'补齐已有测量的硬件、代码版本、计时边界、重复次数、正确性记录；明确目标工作负载，不生成数据。',['measurement_context.md'],'每个字段提供原来源；没有资料明确记未知；仅在可比条件与定位材料齐备后解除下一项阻塞。','blocked','维护者提供现有资料；无法取得则停止优化诊断并保留本轮有边界结果。',owner='项目维护者')
task('CODE-T002','bounded-diagnosis',['RES-T006'],['measurement_context.md','既有代码与日志'],'只对既有资料核对比较条件并检查 large 相关代码路径；归因必须有证据；若资料不足仍保持 inconclusive。',['large_diagnosis.md'],'给出代码/日志定位及证据，或明确无法定位；没有新实验不得标记优化成功；如需新运行另提有预算的方案。','blocked','待 RES-T006 满足资料条件；仅本地 CPU 读代码及现有日志；不在本轮创建新性能结果。')
dump('task_chain.yaml',{'run_id':run,'format_note':'JSON syntax is valid YAML 1.2','tasks':tasks})
claims=[]
for cid,text,loc,scope in [
('WRITE-C001','small 延迟减少 20.0%，速度比 1.25×；medium 减少 16.7%，速度比 1.20×','measurements.csv@v2 lines 2-3','给定两个 end_to_end 报告值'),
('WRITE-C002','large 延迟增加 10.0%，速度比约 0.91×','measurements.csv@v2 line 4','给定 large end_to_end 报告值'),
('WRITE-C003','kernel 延迟减少 50.0%，速度比 2.00×','measurements.csv@v2 line 5','kernel_only；不能代表端到端收益')]:
    claims.append(dict(claim_id=run+'/'+cid,text=text,kind='derived_from_supplied_measurements',status='limited',evidence_ids=[run+'/CODE-T001'],source_locations=[loc,'input_manifest.json'],scope=scope,counterevidence=[],manuscript_locations=['results.md','figure_v2.png'],action_if_unsupported='修正派生计算并重建受影响图文。'))
claims.append(dict(claim_id=run+'/RES-C004',text='优先诊断 large 回退，暂不宣称普遍提速或启动新实验。',kind='decision_inference',status='conditional',evidence_ids=[run+'/CODE-T001'],source_locations=['measurements.csv@v2','project.json.budget'],scope='本轮调度判断，非已验证优化效果',counterevidence=['small/medium 有收益，但权重未知；large 报告值变差'],manuscript_locations=['results.md','project_state.md'],action_if_unsupported='新证据或目标权重明确后重新评估。'))
dump('claim_evidence_ledger.yaml',{'claims':claims,'unknowns':['重复次数与测量波动','硬件与代码版本','计时协议及公平性','large 回退原因','工作负载权重','旧背景正文']})
ids={t['task_id']:t for t in tasks}
visited=set();active=set()
def visit(id):
    assert id in ids
    assert id not in active, 'cycle'
    if id in visited:return
    active.add(id)
    for dep in ids[id]['depends_on']:visit(dep)
    active.remove(id);visited.add(id)
for id in ids:visit(id)
# validator files are created below, then all done outputs checked.
dump('validation.json',{'dependency_references_exist':True,'acyclic':True,'task_count':len(tasks),'done_count':sum(t['status']=='done' for t in tasks),'blocked_count':sum(t['status']=='blocked' for t in tasks),'note':'No skipped dependency. All done tasks depend only on done tasks. Historical claims are separate.'})
dump('artifact_hashes.json',{})
for t in tasks:
    if t['status']=='done':
        assert all(ids[d]['status']=='done' for d in t['depends_on'])
        for file in t['outputs']:assert (O/file).is_file(),file
    if t['status']=='blocked':assert t['on_failure']
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.iterdir()) if p.is_file() and p.name!='artifact_hashes.json'}
dump('artifact_hashes.json',{'algorithm':'SHA-256','files':hashes,'note':'This manifest excludes itself.'})
print(json.dumps({'tasks':len(tasks),'done':7,'blocked':3,'validation':'PASS','hashed_files':len(hashes)}))
