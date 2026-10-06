#!/usr/bin/env python3
"""Replay a small synthetic acceptance comparison against two pinned Git revisions.

No models or servers. The candidate ledger supplies the same validity state to
both versions. Only ReportingHandler behavior is compared, not overall quality.
"""
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def load_runtime(repo, revision, destination, package):
    directory = destination / package
    directory.mkdir()
    names = subprocess.check_output(['git','-C',str(repo),'ls-tree','--name-only',revision,'agent_runtime/']).decode().splitlines()
    for name in names:
        if name.endswith('.py'):
            (directory / Path(name).name).write_bytes(subprocess.check_output(['git','-C',str(repo),'show',f'{revision}:{name}']))
    sys.path.insert(0,str(destination))
    return importlib.import_module(package+'.task_manifest')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--baseline',required=True)
    p.add_argument('--candidate',required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        work=Path(tmp)
        old=load_runtime(a.repo,a.baseline,work,'baseline_runtime')
        new=load_runtime(a.repo,a.candidate,work,'candidate_runtime')
        memory=importlib.import_module('candidate_runtime.project_memory')
        core=importlib.import_module('candidate_runtime.core')
        project=work/'project';project.mkdir()
        ledger=memory.MemoryLedger(project,create=True)
        # Held-out scenario: the user requested tail latency, not throughput.
        raw=project/'observed.csv';raw.write_text('sample,latency_ms\n1,2\n2,3\n3,80\n')
        raw_hash=hashlib.sha256(raw.read_bytes()).hexdigest()
        ledger.add('intent-throughput','intention','Optimize throughput','synthetic chat turn 1 interpretation',scope=['TAIL'],evidence='user_confirmed')
        ledger.add('raw-observation','observation','Three sample latencies in ms',f'observed.csv sha256={raw_hash}',evidence='verified')
        ledger.add('old-claim','claim','Task is complete','synthetic old analysis',deps=['intent-throughput','raw-observation'],evidence='verified')
        ledger.add('old-figure','artifact','Figure based on old interpretation','synthetic figure receipt',deps=['old-claim'],evidence='verified')
        ledger.add('unrelated','procedure','Sort independent inventory','synthetic independent check',scope=['OTHER'],evidence='verified')
        ledger.add('unconfirmed','assumption','Timeout is acceptable','synthetic model guess')
        correction=ledger.correct('intent-throughput','intent-tail','Measure p95 latency','synthetic user turn 2: I meant p95 latency','Wrong prior interpretation')
        (project/'result.json').write_text(json.dumps({'task_id':'TAIL','summary':'Historical result','data':[{'kind':'synthetic','description':'Fixed teaching measurements'}]}))
        cases=[('corrected-intent',['intent-tail'],True),('raw-observation',['raw-observation'],True),('unrelated',['unrelated'],True),('superseded-intent',['intent-throughput'],False),('stale-claim',['old-claim'],False),('transitive-figure',['old-figure'],False),('unknown-reference',['missing'],False),('candidate-guess',['unconfirmed'],False)]
        records=[]
        for label,refs,expected in cases:
            row={'case':label,'memory_refs':refs,'expected_accept':expected}
            for name,module in [('baseline',old),('candidate',new)]:
                class Handler:
                    idempotent=True
                    required_capabilities=()
                    def run(self,task,context):return core.Outcome('complete','fixture independent acceptance',[{'verified':'synthetic'}])
                    def verify(self,task,evidence):return evidence==[{'verified':'synthetic'}]
                task={'task_id':'TAIL','report_path':'result.json','memory_refs':refs}
                handler=module.ReportingHandler(Handler(),project)
                result=handler.run(task,{})
                accepted=result.status=='complete' and handler.verify(task,result.evidence)
                row[name]={'accepted':accepted,'matches_expected':accepted==expected,'status':result.status,'reason':result.reason}
            records.append(row)
        result={'scope':'deterministic synthetic ReportingHandler gate; not model A/B or scientific performance','baseline':a.baseline,'candidate':a.candidate,'cases':records,'baseline_correct':sum(x['baseline']['matches_expected'] for x in records),'candidate_correct':sum(x['candidate']['matches_expected'] for x in records),'count':len(records),'correction':correction,'raw_bytes_preserved':hashlib.sha256(raw.read_bytes()).hexdigest()==raw_hash,'limitations':['Explicit dependency registration required','Host/user/source authenticity supplied by caller','This comparison does not evaluate semantic interpretation quality']}
        a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({k:result[k] for k in ('count','baseline_correct','candidate_correct','raw_bytes_preserved')}))
        return 0 if result['candidate_correct']==len(records) and result['raw_bytes_preserved'] else 1

if __name__=='__main__':raise SystemExit(main())
