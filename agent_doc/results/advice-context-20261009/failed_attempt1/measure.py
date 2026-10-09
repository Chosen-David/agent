"""Deterministic public representation experiment; writes only requested output."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.project_docs import snapshot_project_docs, task_document_refs

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('frozen_baseline_docs', HERE / 'baseline_project_docs.py')
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)


def size(value):
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return {'chars': len(text), 'bytes': len(text.encode('utf-8')), 'tokens': None}


def compare(label, snapshot, tids, assessments, reviews):
    frozen = copy.deepcopy(snapshot)
    before, after = [], []
    for tid in tids:
        old = baseline.task_document_refs(snapshot, [tid], assessments, reviews)
        new = task_document_refs(snapshot, [tid], assessments, reviews)
        # Independent contract: only the advice discovery field is different.
        assert {k: v for k, v in old.items() if k != 'advice'} == {k: v for k, v in new.items() if k != 'advice'}
        assert new['advice'] == new['adopted_advice']
        assert set(new['advice']) <= set(old['advice'])
        before.append(old); after.append(new)
    assert snapshot == frozen
    return {'workload': label, 'tasks': len(tids), 'advice_files': len(snapshot['advice']),
            'adopted_references': sum(len(x['adopted_advice']) for x in after),
            'node_refs_baseline': size(before), 'node_refs_candidate': size(after),
            'global_and_nodes_baseline': size({'project_documents': snapshot, 'nodes': before}),
            'global_and_nodes_candidate': size({'project_documents': snapshot, 'nodes': after})}


def main(out):
    rows = []
    for tasks, advice_count in ((1, 0), (4, 50), (40, 500)):
        tids = [f'T{i}' for i in range(tasks)]
        snapshot = {'schema_version': 'project-documents/v1', 'layout': 'canonical',
                    'task_index': {'path': 'agent_doc/task/TASK.md', 'sha256': '0' * 64},
                    'task_details': {tid: {'path': f'agent_doc/task/task_details/{tid}.md', 'sha256': '1' * 64} for tid in tids},
                    'guides': {'agent_doc/guide/合成约束.md': '2' * 64},
                    'advice': {f'agent_doc/advice/意见-{i}.md': hashlib.sha256(str(i).encode()).hexdigest() for i in range(advice_count)},
                    'adopted_advice': {}, 'future_field': {'retain': True}}
        assessments = []
        for i, (path, sha) in enumerate(snapshot['advice'].items()):
            assessments.append({'path': path, 'sha256': sha, 'task_refs': [tids[i % tasks]],
                                'disposition': 'adapt' if i < 2 * tasks else 'defer',
                                'reason': 'Synthetic explicit scope; not real adoption.'})
        snapshot['adopted_advice'] = {a['path']: a['sha256'] for a in assessments if a['disposition'] == 'adapt'}
        reviews = [{'path': 'agent_doc/guide/合成约束.md', 'sha256': '2' * 64, 'task_refs': tids,
                    'disposition': 'applied', 'reason': 'Synthetic retained guide.'}]
        rows.append(compare('public-synthetic', snapshot, tids, assessments, reviews))
    current = snapshot_project_docs(ROOT)
    # This is a shape diagnostic, not a runnable/adopted/reviewed project plan.
    rows.append(compare('current-repository-shape/no-adoptions', current,
                        sorted(current['task_details']), [], []))
    source = (ROOT / 'agent_doc/task/task_details/WRITE-EVIDENCE-20261009-01.md').read_bytes()
    old = (HERE / 'malformed_detail_before.md').read_bytes()
    expected = old.replace(b'## Stable plan', b'Task-ID: WRITE-EVIDENCE-20261009-01\nDate: 2026-10-09\n\n## Plan', 1)
    assert source == expected, 'metadata repair changed other source bytes'
    result = {'scope': 'same-input JSON representation only; no model, tokenizer, latency, billing or semantic quality experiment',
              'serialization': 'ensure_ascii=False,sort_keys=True,separators=comma/colon; UTF-8',
              'environment': {'python': platform.python_version(), 'platform': platform.platform(), 'tokenizer': None},
              'rows': rows, 'metadata_repair_exact': True,
              'snapshot_recovered': {'task_details': len(current['task_details']), 'guides': len(current['guides']), 'advice': len(current['advice'])}}
    Path(out).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'rows': rows, 'metadata_repair_exact': True}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=HERE / 'raw.json')
    main(parser.parse_args().out)
