#!/usr/bin/env python3
"""Validate declarations, not scientific quality or actual reading."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paper_exemplar_checks import validate_learning
from data_visualization_checks import validate_data_design

ROLES = ('research-assistant', 'research-write', 'research-review', 'research-read-pdf')
CRITERIA = ('artifact_fit', 'contribution', 'method', 'evidence', 'related_work',
            'limitations', 'language_parity', 'format', 'blueprint_application')


def validate(record, root):
    errors = []
    root = Path(root).resolve()
    def need(ok, message):
        if not ok:
            errors.append(message)
    def text(value):
        return isinstance(value, str) and bool(value.strip())
    def file_ok(item):
        if not isinstance(item, dict) or not text(item.get('path')):
            return False
        try:
            raw = Path(item['path'])
            path = (root / raw).resolve()
            return (not raw.is_absolute() and path.is_relative_to(root) and path.is_file()
                    and hashlib.sha256(path.read_bytes()).hexdigest() == item.get('sha256'))
        except (OSError, ValueError, RuntimeError):
            return False
    if not isinstance(record, dict):
        return ['record must be an object']
    need(type(record.get('schema_version')) is int and record['schema_version'] == 1, 'schema_version')
    need(record.get('requested_artifact') == 'submission_paper', 'requires submission_paper request')
    need(text(record.get('target')), 'missing user target')
    complete = record.get('status') == 'submission_checks_complete'
    validate_learning(record, need, text, file_ok)
    learning = record.get('exemplar_learning')
    validate_data_design(record, learning if isinstance(learning, dict) else {}, need, text, file_ok)
    need(record.get('status') in ('validation_partial', 'blocked', 'submission_checks_complete'), 'invalid status')
    need(record.get('delivered_artifact') in ('working_paper', 'submission_paper'), 'audit cannot replace paper')
    if complete:
        need(record.get('delivered_artifact') == 'submission_paper', 'completion requires submission_paper')
    bindings = record.get('bindings')
    bindings = bindings if isinstance(bindings, list) else []
    actors = {}
    for role in ROLES:
        entries = [b for b in bindings if isinstance(b, dict) and b.get('role') == role]
        need(len(entries) == 1, f'{role}: unique binding required')
        if len(entries) != 1:
            continue
        b = entries[0]
        state = b.get('state')
        need(state in ('completed', 'not_run', 'blocked'), f'{role}: execution state required')
        if state != 'completed':
            need(not complete, f'{role}: incomplete execution')
            need(text(b.get('reason')), f'{role}: pending execution reason required')
            continue
        need(b.get('loaded_before_execution') is True, f'{role}: instructions not loaded before execution')
        need(text(b.get('revision')) and text(b.get('read_scope')), f'{role}: version/read scope required')
        need(text(b.get('actor')), f'{role}: actor required')
        need(b.get('mode') in ('independent', 'staged'), f'{role}: execution mode required')
        actors[role] = b.get('actor')
        for event in ('start_receipt', 'result_receipt'):
            need(file_ok(b.get(event)), f'{role}: actual {event} required')
        files = b.get('files')
        files = files if isinstance(files, list) else []
        need(bool(files) and all(file_ok(f) for f in files), f'{role}: instruction files/hash invalid')
        names = {Path(f['path']).name for f in files if isinstance(f, dict) and text(f.get('path'))}
        need({'SKILL.md', 'execution.md', 'paper_delivery_contract.md', 'paper_exemplar_learning.md'} <= names and
             bool({'workflow.md', 'orchestrator.md'} & names), f'{role}: incomplete instruction coverage')
        if role in ('research-review', 'research-read-pdf') and b.get('mode') == 'independent':
            need(b.get('actor') != actors.get('research-write'), f'{role}: independent actor equals writer')
        if complete and role in ('research-review', 'research-read-pdf'):
            need(b.get('mode') == 'independent', f'{role}: independent review required for completion')
    if complete:
        need(len({actors.get(r) for r in ROLES[1:] if text(actors.get(r))}) == 3,
             'writer/reviewer/reader must use separate actors')
    versions = record.get('versions')
    versions = versions if isinstance(versions, list) else []
    need(bool(versions), 'missing language versions')
    languages = []
    for v in versions:
        if not isinstance(v, dict):
            errors.append('version must be an object')
            continue
        language = v.get('language')
        need(text(language) and language not in languages, 'missing/duplicate language')
        languages.append(language)
        need(file_ok(v.get('snapshot')), f'{language}: snapshot invalid')
        snapshot = v.get('snapshot') if isinstance(v.get('snapshot'), dict) else {}
        checks = v.get('checks') if isinstance(v.get('checks'), dict) else {}
        criteria = CRITERIA + (('diagram_scientific_accuracy', 'diagram_visual_design')
                               if record.get('architecture_requested') else ())
        if record.get('data_visualization_requested'):
            criteria += ('data_scientific_fidelity', 'data_visual_design')
        for criterion in criteria:
            c = checks.get(criterion)
            if not isinstance(c, dict):
                errors.append(f'{language}: missing {criterion}')
                continue
            need(c.get('verdict') in ('pass', 'fail', 'unresolved'), f'{language}/{criterion}: verdict')
            need(all(text(c.get(k)) for k in ('location', 'reason', 'evidence')), f'{language}/{criterion}: review rationale required')
            if complete:
                need(c.get('verdict') == 'pass', f'{language}/{criterion}: incomplete scientific/format check')
        if complete:
            need(file_ok(v.get('implementation_map')), f'{language}: blueprint implementation evidence required')
            if record.get('data_visualization_requested'):
                need(file_ok(v.get('data_implementation_map')), f'{language}: data design implementation evidence required')
            count, pages = v.get('page_count'), v.get('read_pages')
            need(type(count) is int and count > 0 and isinstance(pages, list) and
                 all(type(p) is int for p in pages) and sorted(pages) == list(range(1, count + 1)),
                 f'{language}: incomplete page coverage')
            need(v.get('reader_snapshot_sha256') == snapshot.get('sha256'), f'{language}: stale reader snapshot')
            need(v.get('reviewer_snapshot_sha256') == snapshot.get('sha256'), f'{language}: stale scientific review snapshot')
    requested = record.get('requested_languages')
    need(isinstance(requested, list) and bool(requested) and all(text(x) for x in requested)
         and sorted(requested) == sorted(x for x in languages if isinstance(x, str)), 'requested language coverage')
    blockers = record.get('blockers')
    need(isinstance(blockers, list), 'blockers must be a list')
    if isinstance(blockers, list):
        need(not complete or not blockers, 'unresolved blockers prevent completion')
        need(complete or bool(blockers), 'partial delivery requires concrete blockers')
        for b in blockers:
            need(isinstance(b, dict) and all(text(b.get(k)) for k in
                 ('claim', 'missing', 'owner', 'next_action', 'resume_when')), 'incomplete blocker/recovery')
    return errors


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('record', type=Path)
    p.add_argument('--root', type=Path, required=True)
    args = p.parse_args()
    try:
        errors = validate(json.loads(args.record.read_text()), args.root)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    print(json.dumps({'declarations_valid': not errors, 'errors': errors,
                      'scope': 'record integrity only; not semantic or visual certification'}, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
