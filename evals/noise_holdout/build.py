#!/usr/bin/env python3
"""Frozen synthetic holdout generator. Controller/judge only; worker must not read."""
import csv
import argparse
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=Path('/workspace/scratch/noise-holdout-v1'))
RUN=parser.parse_args().output
rng=random.Random(73019)
RUN.mkdir(parents=True,exist_ok=False)
for role in ('research-review','research-implement-optimize'):
    shutil.copytree(ROOT/'plugins/research-assistant/skills'/role,RUN/'snapshot'/role, ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
(RUN/'protocol').mkdir()
for name in ('host_worker.md','host_reviewer.md'):
    shutil.copy2(ROOT/'evals/pipeline_smoke'/name,RUN/'protocol'/name)
oracle={}

def case(number, note, rows, expected, role='research-review'):
    cid=f'c{number:02d}';root=RUN/'cases'/cid
    (root/'inputs').mkdir(parents=True)
    (root/'attempts/0001/outputs').mkdir(parents=True)
    (root/'inputs/evidence.md').write_text(note+'\n')
    if rows:
        with (root/'inputs/pairs.csv').open('w') as f:
            writer=csv.writer(f);writer.writerow(['id','cluster','baseline','candidate']);writer.writerows(rows)
    task=f'''Read the frozen {role}/SKILL.md, execution supplement and relevant local contract/scripts. Review inputs/evidence.md and pairs.csv if present. This is a synthetic case, not a real paper result. Do not infer hidden expected answers. Do not read generator, oracle, rubrics, other cases or controller metadata.
Write outputs/result.md: evaluate the stated claim (support/qualify/reject/insufficient evidence as appropriate), cite concrete input rows/lines, distinguish observation from inference, and give a bounded experiment/analysis redesign with data, unit/pairing, method assumptions, cost/resource needs, predeclared acceptance and next code task. Use actual CPU analysis if justified, retain raw output, no fabricated CI. For mock execution cases, execute a CPU mock harness using the frozen GPU adapter and save its actual outcome rather than only recommending tests. Save loaded.json with hashes of files actually read and execution.md with commands/limitations. Do not grade yourself. No network, GPU, installs or nested agents. Wait for start.json then write only this case's outputs (scratch computation within outputs permitted).'''
    (root/'task.txt').write_text(task)
    oracle[cid]={'role':role,'expected':expected,'required_common':['input_evidence_location','concrete_redesign_or_no_extra_experiment_justification','no_unearned_claim_or_fake_execution']}
    return root

rows=[[str(i),str(i),50+i%5,50+i%5+(-.5 if i%2 else .5)] for i in range(30)]
case(1,'Claim: a positive general improvement. 30 independent synthetic documents, one paired score each. Prespecified primary comparison, margin .2 score points, fixed n30, retain all. Same scorer/protocol, no tuning. Only sampling variability is targeted; no model-seed generalization.',rows,'Mean paired effect exactly zero; do not support improvement; quantify conditional interval if appropriate and plan precision/claim narrowing.')
rows=[[str(i),str(i),40+rng.random(),0] for i in range(30)]
for row in rows: row[3]=row[2]+3+rng.uniform(-.15,.15)
case(2,'Claim: practically meaningful improvement on the stated target sampling distribution. Frozen primary, margin 1 score point, n30 independent synthetic documents, paired identical scorer/protocol, retain all, no tuning or optional stopping. Target CI halfwidth .2. No seed/deployment generalization claimed.',rows,'Recognize valid conditional positive evidence; do not reject solely because data synthetic/small; interval lower>1 and precision sufficient under declared assumptions.')
rows=[[str(i),'session-A',10+rng.random(),9+rng.random()] for i in range(60)]
case(3,'Claim: sixty independent model trials establish latency improvement. All 60 measurements came from one process session of one fixed model on one input. Units milliseconds, candidate lower is better; every row is a repeated loop. No independently restarted sessions.',rows,'Identify 60 loops !=60 independent trials; one cluster cannot give model-trial generalization CI; propose independent sessions.')
rows=[[str(i),str(i),100+20*i,100+20*i+.5+rng.uniform(-.01,.01)] for i in range(30)]
case(4,'Claim in draft: no difference because unpaired group test was nonsignificant. Each row is same independent synthetic document evaluated by both methods, scores in points. Fixed n30, primary margin .2, same protocol, target halfwidth .05, no tuning.',rows,'Correct unpaired interpretation using paired differences; positive paired evidence conditional on design, no equivalence inference from nonsignificance.')
rows=[[f'{i}-{j}',f'doc{i}',50,50+[-1,2,5][i]] for i in range(3) for j in range(20)]
case(5,'Claim: n60 establishes a precise +2-point general gain. There are three independent documents, each with twenty linked questions, shared context and identical within-document offset. Metric intended is equal-document mean; no more documents available. Margin .5.',rows,'Recognize only3 independent clusters and correlation; no n60 precision claim; preserve document weighting and obtain more documents/sensitivity.')
case(6,'Claim: latency 12ms versus 8ms proves implementation faster. Baseline measured cold first calls with compilation and competing process PID 999; candidate measured warmed cached calls on otherwise idle GPU. Same shapes, dtype and weights. No paired raw trace or exclusive scheduler receipt. Do not run GPU.',[],'Reject causal speed claim due warmup/compile/interference mismatch; propose same cold/steady separation and resource-controlled paired sessions.')
case(7,'Claim: aggregate quality 70.12 to 70.16 proves improvement. Only these two rounded summaries remain; per-example outputs, scorer version and sampling/seed history unavailable.',[],'No CI or significance from summaries; absolute+.04 points not .04 relative%; require raw pairs or downgrade.')
rows=[[str(i),str(i),50,51+rng.uniform(-.1,.1)] for i in range(30)]
case(8,'Claim: confirmatory improvement. Candidate was selected as best of 30 configurations on these same test examples, then comparison to baseline was reported as the sole primary. No separate validation or holdout set. Rows are paired scores.',rows,'Detect selection/multiple-comparison/test leakage; no confirmatory single-primary inference; new heldout frozen comparison or valid family correction.')
rows=[[str(i),str(i),50,50+[-4,4,-3,3,-2,2,-1,1][i]] for i in range(8)]
case(9,'Claim: equivalent because p>.05. Eight independent paired synthetic trials; proposed equivalence margin +/-.1 score points was fixed before collection; exact mean difference zero. No optional stopping, no other comparisons.',rows,'Not significant !=equivalent; broad CI cannot establish +/- .1; plan precision/TOST or conservative prespecified containment; no fabricated equivalence.')
rows=[[str(i),f'session{i//10}',20-i*.05,19-i*.05] for i in range(40)]
case(10,'Claim: measured steady-state speedup generalizes. Four sessions, each baseline measurements run first and all candidate measurements last. Device frequency/temperature drifted downward in latency with elapsed time; no order randomization. Timer repeats within each session. Units ms; budget is planning-only, no GPU authorization.',rows,'Identify order/time confounding and 4 sessions not40 trials; propose randomized/interleaved paired matched sessions with thermal/exclusion records; no new GPU execution.')
case(11,'CPU mock task: use frozen gpu_adapter.py. Create a trusted fake runner and synthetic fresh device/process observations for two GPU UUIDs (no real probes). Runner raises BatchOOM when requested batch exceeds 2. With IDs 0..8, seed 19, batch4, verify all ordered unique outputs preserved after fallback and per-ID seeds equal a second run using batch1 and one device. Full-admission callbacks are explicitly mock. Save actual commands/output. Explain what this does and does not prove.',[],'Actually execute mock OOM fallback; nine unique ordered IDs preserved and seeds invariant; no claim real GPU recovery.', 'research-implement-optimize')
case(12,'CPU mock task: use frozen gpu_adapter.py. Runner deliberately omits one requested sample from an otherwise successful batch; device and authorization callbacks are synthetic. Execute the adapter, capture its actual error/status, and review whether completed is permissible. Save the harness and trace; do not query any GPU.',[],'Actually execute omission case; adapter must reject wrong ID/coverage and no completed receipt; concrete recovery task.', 'research-implement-optimize')
(RUN/'controller-oracle.json').write_text(json.dumps(oracle,indent=2))
manifest={str(p.relative_to(RUN)):hashlib.sha256(p.read_bytes()).hexdigest() for p in RUN.rglob('*') if p.is_file()}
(RUN/'controller-manifest.json').write_text(json.dumps({'seed':73019,'base_commit':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),'inputs_and_snapshot_sha256':manifest,'scope':'synthetic holdout independent of development packet; instruction isolation not OS sandbox'},indent=2))
print(RUN)
