#!/usr/bin/env python3
"""Validate declared code-reading coverage, not completeness or semantic truth.

No target code, tools, or run commands are executed. Source anchors come from
source_evidence.py or manual review; this checker checks their contract only.
"""
import argparse
import json
import re


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def records(items, field):
    require(isinstance(items, list), f'{field}: expected list')
    result = {}
    for item in items:
        require(isinstance(item, dict) and text(item.get('id')), f'{field}: missing id')
        require(item['id'] not in result, f'{field}: duplicate id {item["id"]}')
        result[item['id']] = item
    return result


def references(item, key, known, nonempty=True):
    values = item.get(key)
    require(isinstance(values, list) and all(text(v) for v in values), f'{item["id"]}: invalid {key}')
    require(len(values) == len(set(values)), f'{item["id"]}: duplicate {key}')
    require(not nonempty or values, f'{item["id"]}: empty {key}')
    require(set(values) <= set(known), f'{item["id"]}: unknown {key}')
    return values


def validate(report):
    require(isinstance(report, dict) and type(report.get('schema_version')) is int and report['schema_version'] == 1, 'schema_version must be 1')
    commit = report.get('commit')
    require(isinstance(commit, str) and re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', commit), 'full commit required')
    evidence = records(report.get('evidence'), 'evidence')
    coverage = records(report.get('coverage'), 'coverage')
    claims = records(report.get('claims'), 'claims')
    runs = records(report.get('runs'), 'runs')
    require(coverage and claims, 'nonempty coverage and claims required')
    for item in evidence.values():
        require(item.get('commit') == commit, f'{item["id"]}: stale source commit')
        for key in ('path', 'symbol'):
            require(text(item.get(key)), f'{item["id"]}: missing {key}')
        lo, hi = item.get('start_line'), item.get('end_line')
        require(type(lo) is int and type(hi) is int and 1 <= lo <= hi, f'{item["id"]}: invalid line range')
        digest = item.get('blob_sha256')
        require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest), f'{item["id"]}: missing blob hash')
    for row in coverage.values():
        for key in ('entry', 'condition', 'model', 'producer', 'consumer', 'input', 'output'):
            require(text(row.get(key)), f'{row["id"]}: missing {key}')
        status = row.get('status')
        require(status in ('inspected', 'unresolved', 'not_applicable'), f'{row["id"]}: invalid status')
        references(row, 'evidence', evidence, nonempty=status != 'unresolved')
        if status != 'inspected':
            require(text(row.get('reason')), f'{row["id"]}: explain exclusion or gap')
    for run in runs.values():
        require(run.get('commit') == commit, f'{run["id"]}: stale run commit')
        references(run, 'covers', coverage)
        for key in ('command', 'environment'):
            require(text(run.get(key)), f'{run["id"]}: missing {key}')
        for key in ('inputs', 'outputs', 'logs'):
            artifacts = run.get(key)
            require(isinstance(artifacts, list) and artifacts, f'{run["id"]}: missing {key}')
            for artifact in artifacts:
                require(isinstance(artifact, dict) and text(artifact.get('path')), f'{run["id"]}: invalid artifact')
                digest = artifact.get('sha256')
                require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest), f'{run["id"]}: missing artifact hash')
    for claim in claims.values():
        require(text(claim.get('text')), f'{claim["id"]}: empty text')
        level = claim.get('level')
        require(level in ('source_fact', 'static_inference', 'executed', 'unknown'), f'{claim["id"]}: invalid level')
        scope = references(claim, 'covers', coverage)
        references(claim, 'evidence', evidence, nonempty=level != 'unknown')
        run_ids = references(claim, 'runs', runs, nonempty=level == 'executed')
        if level != 'unknown':
            require(all(coverage[row]['status'] == 'inspected' for row in scope), f'{claim["id"]}: assertion covers an unresolved/excluded row')
        if level == 'executed':
            observed = {row for run in run_ids for row in runs[run]['covers']}
            require(set(scope) <= observed, f'{claim["id"]}: unobserved execution scope')
    return {'status': 'contract_valid', 'coverage_rows': len(coverage), 'claims': len(claims),
            'unresolved_rows': [r['id'] for r in coverage.values() if r['status'] == 'unresolved'],
            'limitation': 'Declared contract only; no source verification, omitted-entry detection, semantic or log-authenticity proof.'}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report')
    args = parser.parse_args()
    try:
        with open(args.report, encoding='utf-8') as stream:
            result = validate(json.load(stream, object_pairs_hook=unique_object))
    except (OSError, ValueError) as exc:
        parser.exit(2, f'coverage contract failed: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
