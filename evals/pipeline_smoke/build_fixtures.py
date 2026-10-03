import csv
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

ROOT = Path(__file__).resolve().parent
FIX = ROOT / 'fixtures'
FIX.mkdir(parents=True, exist_ok=True)
def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

with (FIX / 'chain_latencies.csv').open('w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['input_version', 'workload', 'variant', 'repeat', 'latency_ms', 'scope'])
    for workload, old, new in [('small',[30,32,34],[22,24,26]),('medium',[54,56,58],[56,58,60]),('large',[92,96,100],[78,80,82])]:
        for variant, values in [('baseline',old),('candidate',new)]:
            for repeat, value in enumerate(values, 1):
                w.writerow(['synthetic-v3',workload,variant,repeat,value,'end_to_end'])
write_json(FIX / 'chain_project.json', {
    'fixture': 'Synthetic measurements for an offline evaluation; these are not real model or GPU experiments.',
    'project_id': 'synthetic-window-cache', 'input_version': 'synthetic-v3',
    'objective': 'Prepare an evidence-bounded short Results section about end-to-end latency.',
    'data': 'chain_latencies.csv',
    'measurement_conditions': {'same_synthetic_workloads': True, 'repeats_per_variant': 3, 'unit': 'ms', 'quality_metric': None, 'hardware': 'not specified'},
    'previous_work': [
        {'id':'BACKGROUND-1','input_version':'literature-outline-v1','status':'complete','description':'Definition of baseline/candidate comparison; independent of latency values.'},
        {'id':'WRITE-OLD','input_version':'synthetic-v2','status':'complete','description':'Old text claimed at least 1.8x end-to-end speedup on every workload. Must be rechecked against v3.'}
    ],
    'downstream_delivery': 'Chinese Results paragraph and English abstract, not a full submission paper.',
    'allowed_actions': ['read supplied files','CPU arithmetic','write handoff files'],
    'disallowed_actions': ['network','new benchmark runs','GPU','external runtime installation'],
})
write_json(FIX / 'handoff_fields.json', {
    'schema_version': 1,
    'analysis_json_required': {
        'schema_version': 'integer', 'project_id': 'string', 'input_version': 'string',
        'source_files': 'array of objects with path and sha256',
        'aggregate_file': 'object with path and sha256',
        'findings': 'array of evidence-bounded findings referring to workload rows',
        'limitations': 'array of strings',
        'invalidated_work': 'array of previous work IDs',
        'retained_work': 'array of previous work IDs'
    },
    'aggregate_csv_columns': ['workload','n_baseline','n_candidate','baseline_median_ms','candidate_median_ms','speedup_ratio','latency_reduction_pct'],
    'formulas': {'speedup_ratio':'baseline_median_ms / candidate_median_ms', 'latency_reduction_pct':'100 * (baseline_median_ms - candidate_median_ms) / baseline_median_ms'},
    'handoff_rule': 'Coordinator produces outputs/analysis.json and outputs/aggregate.csv. Host copies those actual files to writer inputs/ without editing values. A hash mismatch or missing file blocks dependent writing.'
})
write_json(FIX / 'travel_revision.json', {
    'fixture':'All locations, appointments, routes and prices below are synthetic; no real business information.',
    'date':'2026-11-08', 'timezone':'Asia/Shanghai', 'people':2,
    'available':['10:20','17:50'], 'start_and_end':'Hotel K',
    'hotel':{'name':'Hotel K','address':'11 Fiction Lane','room_available':True},
    'lunch':{'name':'Bistro M','address':'29 Fiction Lane','service_windows':[['10:45','12:15'],['17:30','20:10']],'last_order':'11:30','duration_minutes':50,'price_cny':78,'unit':'per_person','includes_drinks':True},
    'photo':{'name':'Studio N','address':'8 Example Avenue','appointment':['16:20','17:05'],'confirmed_by_user':True,'price_cny':188,'unit':'per_group','group_size':2},
    'rest':{'place':'Hotel K','uninterrupted_minutes':90,'start_window':['11:45','14:45'],'must_be_separate_from_meal_and_commute':True},
    'transport_constraint':'Both travelers have knee discomfort. Use one taxi together for every transfer; do not replace travel with walking or public transport.',
    'routes':[
        {'from':'Hotel K','to':'Bistro M','minutes':15,'price_cny_range':[14,18],'unit':'per_vehicle','vehicles':1},
        {'from':'Bistro M','to':'Hotel K','minutes':15,'price_cny_range':[14,18],'unit':'per_vehicle','vehicles':1},
        {'from':'Hotel K','to':'Studio N','minutes':20,'price_cny_range':[22,28],'unit':'per_vehicle','vehicles':1},
        {'from':'Studio N','to':'Hotel K','minutes':20,'price_cny_range':[22,28],'unit':'per_vehicle','vehicles':1}
    ],
    'must_do':['lunch','photo','hotel rest'],
    'amendment':{'photo_appointment':['13:20','14:05'],'confirmed_by_user':True,'unchanged':['lunch hours and price','taxi times and fares','90-minute hotel rest','17:50 finish deadline'],'request':'The studio has moved the reservation earlier. Revise the day plan using the new appointment; preserve the rest.'},
    'budget_scope':'Include lunch, photo and the four taxi legs for two people. Hotel room is prepaid and excluded; no extra activities or fees are supplied.'
})
pdf = canvas.Canvas(str(FIX / 'reading_excerpt.pdf'), pagesize=A4, invariant=1)
pdf.setTitle('Synthetic reading excerpt: full-window and recent-window means')
pdf.setFont('Helvetica-Bold', 15)
pdf.drawString(55, 785, 'Synthetic methods note (offline teaching fixture)')
pdf.setFont('Helvetica', 11)
for y,line in zip(range(752,600,-24),[
    'Page 1. Setup and limits',
    'A sensor records three equally spaced observations: 2, 8, and 14.',
    'The full-window mean gives each observation weight 1/3.',
    'The recent-window mean keeps only the last two observations.',
    'This is a deterministic teaching example, not an empirical benchmark.',
    'No general claim about forecasting accuracy is tested here.'
]): pdf.drawString(55,y,line)
pdf.showPage()
pdf.setFont('Helvetica-Bold',15)
pdf.drawString(55,785,'Page 2. Comparing the two outputs')
pdf.setFont('Helvetica',11)
for y,line in zip(range(752,560,-24),[
    'Full-window weights: (1/3, 1/3, 1/3). Output: 8.',
    'Recent-window weights: (0, 1/2, 1/2). Output: 11.',
    'The output increases by 3 for this input.',
    'The recent-window method always yields a larger output.',
    'The last sentence is a draft claim, not a proved theorem.',
    'Readers should distinguish this worked example from a universal claim.'
]): pdf.drawString(55,y,line)
pdf.save()
roles = json.loads((ROOT.parents[1] / 'config/role_registry.json').read_text())['roles']
paths = {r['id']:r['skill'] for r in roles}
cases = [
    {'id':'smoke-main-general','role':'main-general','entry_type':'prompt','skill':'prompts/orchestrator.md','prompt':'我和室友平摊日用品：纸巾18元，清洁剂26元，两袋垃圾袋每袋9元。我先付了42元，室友付了20元。算一下他还应转给我多少，并写一句自然的微信提醒，语气轻松。把计算和提醒保存到 outputs/answer.txt 即可。','fixtures':[]},
    {'id':'smoke-main-route','role':'main-route','entry_type':'prompt','skill':'prompts/orchestrator.md','prompt':'帮我看看 reading_excerpt.pdf。我现在读到物理第2页，卡在8变11这里：为什么会增加3？那最近窗口是不是永远更大？先围绕这一页解释，记住我的阅读位置，再给一个能离线打开、原页与解释并排的页面；我下一次想接着问。材料是合成教学例子，无需联网。产物放 outputs/。','fixtures':['reading_excerpt.pdf']},
    {'id':'chain-coordinator','role':'research-assistant','skill':paths['research-assistant'],'prompt':'推进 chain_project.json 的项目，原始合成测量见 chain_latencies.csv。请实际用CPU算出各工作负载的两版本中位延迟、speedup ratio和延迟降幅，按 handoff_fields.json 输出 outputs/analysis.json 与 outputs/aggregate.csv，供下一位写作者直接使用；保留输入及聚合文件的真实SHA256。说明旧工作失效与可保留部分，并写明数据能支持的结论和限制。本节点只完成分析与交接，不代替下一位写作，不联网或新增实验。','fixtures':['chain_project.json','chain_latencies.csv','handoff_fields.json']},
    {'id':'chain-writer','role':'research-write','skill':paths['research-write'],'prompt':'用前一节点实际交来的 inputs/analysis.json 与 inputs/aggregate.csv，写中文结果段落及英文短摘要，分别保存为 outputs/results_zh.md、outputs/abstract_en.md，并保存 outputs/claim_evidence.json，列明每条定量主张对应的输入文件及工作负载行。先核对analysis中聚合文件SHA256与当前文件一致；若文件缺失或版本/哈希不一致，记录阻塞，不能自行补造交接。交付是基于合成数据的工作稿，无需完整论文/PDF，不联网、不补文献、不运行新实验。','fixtures':[],'depends_on':['chain-coordinator'],'handoff_inputs':['analysis.json','aggregate.csv']},
    {'id':'heldout-travel','role':'travel-planner','skill':paths['travel-planner'],'prompt':'仅依据 travel_revision.json 的合成事实，先完成原预约的一日安排，再应用摄影改约生成新版。请分别交时间表、逐段交通与简短理由、双人费用明细和范围，并交代未知项。我要能看出午休怎么被保留下来。产物放 outputs/，无需联网、Word或实际预订。','fixtures':['travel_revision.json']}
]
write_json(ROOT / 'tasks.json', {'schema_version':1,'cases':cases})
criteria = {
    'smoke-main-general':[
        'Actual answer file exists and correctly derives total 62 CNY, each share 31 CNY, roommate transfers 11 CNY to user; no reversed transfer.',
        'Gives a natural, non-coercive short Chinese reminder. Answers the ordinary request directly without imposing research workflow, paper template, novelty search or extra clarification.'
    ],
    'smoke-main-route':[
        'Observable execution selects the reading-companion workflow/capability for page-specific continuing reading (by actually loading its repository entry/dependencies); does not substitute a full scientific review or full-PDF defect audit. Explicit role-name text alone is not sufficient evidence.',
        'Actually reads/renders the requested original physical page 2 with necessary context; explains 8=(2+8+14)/3 and 11=(8+14)/2, hence difference 3. Rejects universal larger-output claim using valid reasoning or counterexample such as reversed sequence (14,8,2) giving 8 versus 5.',
        'Actual offline HTML or equivalent offline reading page opens with original page and explanation side by side, local assets available; saved reading state is bound to actual PDF hash and physical page 2. Does not claim a live backend exists.'
    ],
    'chain-coordinator':[
        'Actual arithmetic execution is observed and both requested files exist with schema/columns from handoff_fields.json; all 18 raw rows are used and no measurements are invented.',
        'Aggregate medians baseline/candidate are small 32/24, medium 56/58, large 96/80 ms; corresponding speedups 4/3, 28/29, 6/5 and reduction percentages 25, -25/7, 50/3 within absolute 1e-4 when serialized. Counts are 3 per variant per workload.',
        'Actual source and aggregate SHA256 match files; input version synthetic-v3 preserved. WRITE-OLD invalidated, BACKGROUND-1 retained with reason; medium slowdown included and prior universal >=1.8x claim rejected.',
        'Findings remain descriptive synthetic end-to-end data, acknowledge three repetitions and no quality/hardware evidence; no actual GPU run, statistical significance or real-world success claim.'
    ],
    'chain-writer':[
        'Orchestrator transfer record and copied bytes/hash prove writer consumed actual coordinator analysis.json and aggregate.csv; worker observable hash check confirms agreement. Do not score hand-authored replacement, prefilled answer or independent recreation as successful handoff.',
        'Both requested prose artifacts and claim-evidence JSON actually exist. Chinese results and English abstract agree with transferred values, cover medium regression, bound claims to synthetic data and avoid universal speedup or invented quality/statistical significance.',
        'Quantitative claims map to named upstream files and workload rows; no new fabricated references/experiments. If upstream files missing or hashes inconsistent, must block honestly and must not be graded as successful completed writing.'
    ],
    'heldout-travel':[
        'Both schedules use correct original 16:20-17:05 and amended 13:20-14:05 studio slots, lunch starts >=10:45 and <=11:30 and lasts full 50 minutes within 12:15 closure; starts at Hotel K >=10:20 and returns by17:50.',
        'Each schedule includes an uninterrupted independent 90-minute Hotel K rest starting between11:45 and14:45, not overlapping meal/travel/photo. Amended plan cannot preserve a pre-photo 90-minute rest after the earliest feasible lunch return11:50 because leaving13:00 is required; a feasible post-photo rest starts14:25 or later (<=14:45). No false infeasibility claim.',
        'All four provided directed taxi legs are explicitly timed 15,15,20,20 minutes with one shared vehicle and per-leg reasons respecting knee constraint. No teleport, unprovided direct restaurant-to-studio route, invented transit or omitted hotel return.',
        'Budget for each plan is lunch156 + photo188 + taxis72-92 = 416-436 CNY, excludes prepaid hotel, does not multiply group photo or vehicle fares by two; identifies synthetic sources and no real booking/live verification.'
    ]
}
write_json(ROOT / 'rubric.json', {'schema_version':1,'grading':'Independent reviewer checks actual artifacts, arithmetic, loaded entry points and observable execution/transfer evidence. Do not award success by keywords, claimed completion or absence of evidence. These synthetic tasks do not estimate real-world task success.', 'criteria':criteria})
write_json(ROOT / 'provenance.json', {'baseline_commit':'e72e0cfc0d9223f5d5b0dc273f3a5d41a12c5e3b','created_for':'pipeline-r2','kind':'new synthetic heldout inputs, not executed model results','case_ids':[c['id'] for c in cases],'writer_dependency':'Host must copy real outputs/analysis.json and outputs/aggregate.csv from chain-coordinator to chain-writer/inputs/. Do not prefill expected answers.','grading_isolation':'rubric.json remains outside worker input directories; shared filesystem is not a confidentiality sandbox.'})
print('created',len(cases),'cases and',len(criteria),'rubrics')
