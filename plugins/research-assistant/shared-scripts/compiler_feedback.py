#!/usr/bin/env python3
"""Read a single, non-interleaved PTXAS verbose log; emit evidence, not a verdict.

No compiler execution or file writes. Missing metrics remain unknown. The caller
must bind the log to the actual compile command, exit status and source revision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

MAX_BYTES = 8 * 1024 * 1024
MAX_RECORDS = 4096
INFO = re.compile(r"^\s*ptxas\s+info\s*:\s*(.*)$")
ENTRY = re.compile(r"Compiling entry function '([^']+)' for '(sm_[A-Za-z0-9]+)'\s*$")
PROPERTIES = re.compile(r"Function properties for (\S+)\s*$")
METRICS = {
    'registers_per_thread': re.compile(r'\bUsed\s+(\d+)\s+registers\b'),
    'static_shared_bytes': re.compile(r'(?:^|,\s+)(\d+)\s+bytes smem\b'),
    'stack_frame_bytes': re.compile(r'(?:^|,\s+)(\d+)\s+bytes stack frame\b'),
    'spill_store_bytes': re.compile(r'(?:^|,\s+)(\d+)\s+bytes spill stores\b'),
    'spill_load_bytes': re.compile(r'(?:^|,\s+)(\d+)\s+bytes spill loads\b'),
}
DIAGNOSTIC = re.compile(r'^\s*ptxas\s+(warning|error|fatal)\b', re.I)


def parse_log(raw: bytes) -> dict:
    if len(raw) > MAX_BYTES:
        raise ValueError('log exceeds 8 MiB; split by compiler invocation first')
    text = raw.decode('utf-8')  # Refuse lossy decoding of evidence.
    records, issues, diagnostics = [], [], []
    current = None

    def start(name, arch, number):
        if len(records) >= MAX_RECORDS:
            raise ValueError('too many function records; split the log')
        record = {'ordinal': len(records) + 1, 'function': name, 'target': arch,
                  'header_line': number, 'metrics': dict.fromkeys(METRICS),
                  'observations': [], 'conflicts': []}
        records.append(record)
        return record

    for number, line in enumerate(text.splitlines(), 1):
        diagnostic = DIAGNOSTIC.match(line)
        if diagnostic:
            diagnostics.append({'line': number, 'severity': diagnostic[1].lower(), 'text': line})
            continue
        info = INFO.match(line)
        body = info[1] if info else line.strip()
        entry = ENTRY.fullmatch(body) if info else None
        properties = PROPERTIES.fullmatch(body) if info else None
        if entry:
            current = start(entry[1], entry[2], number)
            continue
        if properties:
            if current is None or current['function'] != properties[1] or current['observations']:
                # Standalone device functions must not inherit the last entry's target.
                current = start(properties[1], None, number)
            continue
        if info and body.startswith(('Compiling entry function', 'Function properties')):
            current = None
            issues.append({'line': number, 'reason': 'unrecognized_function_boundary', 'text': line})
            continue
        # Only resource lines, never metrics embedded in arbitrary build output.
        resource_line = ((info and body.startswith('Used ')) or
                         (not info and re.match(r'^\d+ bytes stack frame\b', body)))
        found = [(key, int(match[1])) for key, pattern in METRICS.items()
                 for match in pattern.finditer(body)] if resource_line else []
        if not found:
            if info or resource_line:
                issues.append({'line': number, 'reason': 'unparsed_ptxas_info', 'text': line})
                # Unknown or truncated info may start another function. Prefer
                # losing scope over attributing later resources to the old one.
                current = None
            continue
        if current is None:
            issues.append({'line': number, 'reason': 'unscoped_metrics', 'text': line})
            continue
        for key, value in found:
            previous = current['metrics'][key]
            current['observations'].append({'metric': key, 'value': value, 'line': number})
            if previous is not None and previous != value:
                if key not in current['conflicts']:
                    current['conflicts'].append(key)
            current['metrics'][key] = None if key in current['conflicts'] else value

    incomplete = any(r['target'] is None or r['conflicts'] or
                     any(v is None for v in r['metrics'].values()) for r in records)
    return {
        'schema_version': 'ptxas-feedback/v1',
        'log_sha256': hashlib.sha256(raw).hexdigest(),
        'log_bytes': len(raw),
        'parse_status': ('no_records' if not records else
                         'partial' if incomplete or issues or diagnostics else 'parsed'),
        'compile_success': None,
        'performance_verdict': 'not_measured',
        'records': records, 'issues': issues, 'diagnostics': diagnostics,
        'scope': 'Static compiler report only; absent fields are unknown, not zero. '
                 'Input must be one non-interleaved compiler invocation. '
                 'No execution frequency, dynamic shared memory, occupancy or latency inferred.',
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path, help='UTF-8 PTXAS -v log from one compiler invocation')
    args = parser.parse_args(argv)
    try:
        with args.log.open('rb') as stream:
            result = parse_log(stream.read(MAX_BYTES + 1))
    except (OSError, ValueError) as exc:
        print(f'compiler_feedback: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0  # Parsing succeeded; does NOT certify compiler or kernel success.


if __name__ == '__main__':
    raise SystemExit(main())
