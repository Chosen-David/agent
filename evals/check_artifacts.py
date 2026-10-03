#!/usr/bin/env python3
"""Recheck deterministic observations; does not grade semantic/visual quality."""
import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def check(root):
    observations = []
    orchestration = root/'research-assistant-v2/run-v2-20261003'
    tasks = json.loads((orchestration/'task_chain.yaml').read_text())['tasks']
    by_id = {t['task_id']:t for t in tasks}
    assert len(by_id)==len(tasks)
    pending = set(by_id)
    for task in tasks:
        assert all(d in by_id for d in task['depends_on'])
        if task['status']=='done':
            assert all(by_id[d]['status']=='done' for d in task['depends_on'])
            assert task['outputs'] and all((orchestration/p).is_file() for p in task['outputs'])
        elif task['status']=='blocked':
            assert task['on_failure']
    while pending:
        ready = {t for t in pending if not (set(by_id[t]['depends_on']) & pending)}
        assert ready, 'orchestration task dependency cycle'
        pending -= ready
    observations.append('rerun orchestration has an acyclic dependency graph; done dependencies and output files exist')
    expected = {'small':(100,80),'medium':(120,100),'large':(200,220),'kernel':(20,10)}
    figure = root/'research-figures/FIG-20261003-01'
    rows = list(csv.DictReader((figure/'derived_values.csv').open()))
    assert len(rows)==4 and {r['workload'] for r in rows}==set(expected)
    for row in rows:
        b,c=expected[row['workload']]
        assert (float(row['baseline_ms']),float(row['candidate_ms']))==(b,c)
        assert math.isclose(float(row['speedup']),b/c)
        assert row['scope']==('kernel_only' if row['workload']=='kernel' else 'end_to_end')
    observations.append('figure derived values preserve all four rows and scopes')
    data=root/'research-data-visualization-split/fig_timing_20261003'
    plotted=list(csv.DictReader((data/'plotted_values.csv').open()))
    actual={(r['scope'],r['workload'],r['series']):float(r['value_ms']) for r in plotted}
    wanted={(('kernel_only' if workload=='kernel' else 'end_to_end'),workload,series):values[index]
            for workload,values in expected.items() for index,series in enumerate(['Baseline','Candidate'])}
    assert len(plotted)==8 and actual==wanted
    architecture=json.loads((Path(__file__).parent/'fixtures/architecture.json').read_text())
    semantic=json.loads((root/'research-diagrams-split/semantic_contract.json').read_text())
    assert {n['id']:n['label'] for n in semantic['nodes']}=={n['id']:n['label'] for n in architecture['nodes']}
    assert len(semantic['edges'])==5
    assert {(e['source'],e['target']) for e in semantic['edges']}=={tuple(e) for e in architecture['edges']}
    assert all(e['kind']=='data_flow' for e in semantic['edges']) and semantic['status']=='proposed'
    mixed=root/'research-figures-split'
    manifest=json.loads((mixed/'manifest.json').read_text())
    assert manifest['route']=='mixed' and {p['route'] for p in manifest['panels']}=={'diagram','data_visualization'}
    assert len({manifest['owner'],*(p['owner'] for p in manifest['panels'])})==1
    assert all((mixed/p['editable_source']).is_file() for p in manifest['panels'])
    assert (mixed/manifest['assembly_source']).is_file() and (mixed/'figure.png').is_file()
    observations.append('new figure specialists preserve all eight plotted values and exact semantic graph; mixed source/owner manifest complete; visual review separate')
    bundle=json.loads((root/'travel-planner/delivery_bundle.json').read_text())
    minute=lambda s: int(s[:2])*60+int(s[3:])
    for version,duration in [('v1',20),('v2',35)]:
        plan=bundle['revisions'][version]['itinerary']
        assert minute(plan[0]['start'])==660 and minute(plan[-1]['end'])==1080
        previous=660;counts={'rest':0,'photo':0,'lunch':0,'travel':0}
        for block in plan:
            start,end=minute(block['start']),minute(block['end']);assert start==previous and end>start
            previous=end;kind=block['kind']
            if kind in counts:counts[kind]+=1
            if kind=='rest':assert end-start==75
            if kind=='photo':assert (start,end)==(960,1020)
            if kind=='lunch':assert end-start==60 and 630<=start<=840 and end<=870
            if kind=='travel':assert end-start==duration
        assert counts==dict(rest=1,photo=1,lunch=1,travel=4)
        assert bundle['revisions'][version]['known_cost_subtotal']==[2*80+300+4*15,2*100+300+4*25]
    observations.append('both travel versions satisfy windows, full durations, rest, booking and budget units')
    for version,duration in [(1,20),(2,35)]:
        bundle=json.loads((root/f'travel-planner-v2/delivery_bundle_v{version}.json').read_text())
        assert bundle['schema_version']=='local-travel/v1' and bundle['revision']==version
        slots=bundle['itinerary']; previous=None; counts={'transfer':0,'rest':0,'lunch':0,'photo':0}
        for slot in slots:
            start,end=map(datetime.fromisoformat,[slot['start'],slot['end']])
            assert end>start and (previous is None or start==previous)
            previous=end; elapsed=(end-start).total_seconds()/60
            assert slot['validated_for_revision']==version
            if slot['kind']=='transfer':
                counts['transfer']+=1;assert elapsed==duration
            if slot['kind']=='rest':
                counts['rest']+=1;assert elapsed==75
            if 'lunch' in slot['intent_ids']:
                counts['lunch']+=1;assert elapsed==60
                assert 630<=start.hour*60+start.minute<840 and end.hour*60+end.minute<=870
            if 'photo' in slot['intent_ids']:
                counts['photo']+=1;assert (start.hour,start.minute,end.hour,end.minute)==(16,0,17,0)
        assert counts=={'transfer':4,'rest':1,'lunch':1,'photo':1}
        assert datetime.fromisoformat(slots[0]['start']).hour==11 and previous.hour==18
        budget=bundle['budget'];assert budget['known_subtotal']=={'min':520,'max':600}
        assert budget['known_total_with_contingency']=={'min':572,'max':720}
        assert [(x['price']['unit'],x['price']['quantity']) for x in budget['lines']]==[('per_person',2),('per_package',1),('per_car',4)]
        assert budget['unknown_items'] and budget['currency_assumption']
    observations.append('latest travel contract rerun preserves both schedules, revisions, rest and explicit price-unit mappings')
    fixture=Path(__file__).parent/'fixtures/paper.pdf'
    digest=hashlib.sha256(fixture.read_bytes()).hexdigest()
    coverage=[json.loads(l) for l in (root/'research-read-pdf'/digest/'page_coverage.jsonl').read_text().splitlines()]
    assert len(coverage)==3 and {x['physical_page'] for x in coverage}=={1,2,3}
    for p in coverage:
        assert p['snapshot_id']==digest and p['opened'] is True and p['read_complete'] is True
        assert (root/'research-read-pdf'/digest/p['image']).is_file()
    observations.append('PDF coverage declarations bind all three physical pages to fixture hash; actual viewing requires trace review')
    reader=root/'paper-reading-companion'
    notes=json.loads((reader/'notes.json').read_text())
    assert notes['paper_sha256']==digest and len(notes['cards'])==2
    assert all(c['page']==2 for c in notes['cards'])
    state=json.loads((reader/'reading_state.json').read_text());assert state['current_physical_page']==2
    html=(reader/'reader.html').read_text();assert digest in html and 'data:image/png;base64,' in html
    observations.append('reader notes, state and actual embedded HTML match the PDF')
    return observations


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',type=Path)
    parser.add_argument('--run-code',action='store_true',help='run the reviewed generated toy-code checks')
    args=parser.parse_args()
    try:
        checks=check(args.root)
        if args.run_code:
            run=subprocess.run([sys.executable,str(args.root/'research-implement-optimize/check_moving_average.py')],capture_output=True,text=True,timeout=30)
            if run.returncode:raise AssertionError(run.stderr)
            checks.append('generated code: 7 unittest groups including 200 seeded cases pass')
        print(json.dumps({'status':'pass','scope':'deterministic artifacts only','checks':checks},ensure_ascii=False,indent=2))
        return 0
    except (AssertionError,OSError,KeyError,ValueError,subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status':'fail','error':str(exc)},ensure_ascii=False))
        return 1

if __name__=='__main__':sys.exit(main())
