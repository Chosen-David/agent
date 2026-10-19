#!/usr/bin/env python3
"""Frozen-baseline complete prompt assembly: CPU wall time, not LLM latency."""
import hashlib
import itertools
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime import prompt_context as candidate

BASE = '38a6451306dba93fcf40d4c23391876471682891'


def outcome(module, root, **kwargs):
    try:
        return ('ok', module.compose_entries(root, **kwargs))
    except ValueError as error:
        return ('ValueError', str(error))


def main():
    source = subprocess.check_output(['git', 'show', BASE + ':agent_runtime/prompt_context.py'], cwd=ROOT)
    baseline = types.ModuleType('frozen_prompt_context')
    exec(compile(source, BASE, 'exec'), baseline.__dict__)
    originals = {name: (ROOT / name).read_bytes() for name in candidate.ENTRIES.values()}
    scenarios = {'repository': originals,
                 'large_valid': {n: b'x' * 50000 + b'\n' + b for n, b in originals.items()},
                 'missing': {n: b.replace(candidate.MARKER.encode(), b'absent') for n, b in originals.items()},
                 'repeated': {n: b + b'\n' + candidate.MARKER.encode() + b'\n' for n, b in originals.items()}}
    report = {'base': BASE, 'python': sys.version, 'platform': platform.platform(),
              'clock': 'perf_counter_ns; complete compose_entries; warm page cache; no CLI startup',
              'warmup': 5, 'rounds': 7, 'calls_per_round': 20,
              'candidate_sha256': hashlib.sha256((ROOT / 'agent_runtime/prompt_context.py').read_bytes()).hexdigest(),
              'scenarios': {}}
    for scenario, files in scenarios.items():
        with tempfile.TemporaryDirectory(prefix='prompt-scan69-') as directory:
            root = Path(directory)
            for name, data in files.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            checks = 0
            for length in (1, 2, 3):
                for entries in itertools.permutations(candidate.ENTRIES, length):
                    for dedup in (False, True):
                        kwargs = dict(entries=entries, deduplicate=dedup, max_chars=1000000)
                        expected = outcome(baseline, root, **kwargs)
                        assert outcome(candidate, root, **kwargs) == expected
                        checks += 1
                        if expected[0] == 'ok':
                            size = len(expected[1]['prompt'])
                            for cap in (size - 1, size, size + 1):
                                kwargs['max_chars'] = cap
                                assert outcome(candidate, root, **kwargs) == outcome(baseline, root, **kwargs)
                                checks += 1
            timings = {'baseline': [], 'candidate': []}
            modules = {'baseline': baseline, 'candidate': candidate}
            expected = outcome(baseline, root, max_chars=1000000)
            for module in modules.values():
                for _ in range(5):
                    assert outcome(module, root, max_chars=1000000) == expected
            for round_index in range(7):
                order = ('baseline', 'candidate') if round_index % 2 == 0 else ('candidate', 'baseline')
                for label in order:
                    start = time.perf_counter_ns()
                    for _ in range(20):
                        result = outcome(modules[label], root, max_chars=1000000)
                    elapsed = (time.perf_counter_ns() - start) / 20
                    assert result == expected
                    timings[label].append(elapsed)
            before, after = (statistics.median(timings[n]) for n in ('baseline', 'candidate'))
            report['scenarios'][scenario] = {
                'files': {n: {'bytes': len(b), 'chars': len(b.decode()), 'sha256': hashlib.sha256(b).hexdigest()} for n, b in files.items()},
                'differential_checks': checks, 'ns_per_call_raw': timings,
                'median_before_ns': before, 'median_after_ns': after,
                'improvement_fraction': 1 - after / before,
                'nonregression_pass': after - before <= max(before * .05, 50000)}
    report['accepted'] = (report['scenarios']['repository']['improvement_fraction'] >= .10 and
                          all(s['nonregression_pass'] for s in report['scenarios'].values()))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['accepted'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
