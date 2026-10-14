"""Fixed CPU transport check for existing R6; never an LLM quality benchmark."""
import hashlib
import json
import platform
import statistics
import sys
import tempfile
import time
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.text_dictionary import text_view, restore_text_view
from agent_runtime.reference_context import _wire


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def run(out):
    here = Path(__file__).resolve().parent
    original = (here / 'long-original.txt').read_bytes()
    revised = (here / 'long-revised.txt').read_bytes()
    checks = []
    samples = {'full': [], 'dictionary': []}
    sizes = {}
    with tempfile.TemporaryDirectory(prefix='r6-transport-') as folder:
        root = Path(folder).resolve()
        path = root / 'document.txt'
        path.write_bytes(original)
        sha = digest(original)
        packet = text_view(root, 'document.txt', sha)
        assert packet['encoding'] == 'dictionary'
        wire = _wire(packet)
        text = restore_text_view(root, wire, 'document.txt', sha)
        assert text.encode() == original
        checks.append('byte-exact-original')
        lines = text.splitlines()
        assert lines[0] == 'RES-EXACT-0007: measurement=17; unit=ms; status=pending'
        assert lines[-1] == 'FIG-EXACT-0901 cites RES-EXACT-0007; publish=false; answer-to-Q-MISSING=not-provided'
        checks.append('distant-fact-and-exact-reference-preserved')
        ids = [line.split(':', 1)[0] for line in lines if line.startswith('ISSUE-')]
        assert ids == [f'ISSUE-{i:05d}' for i in range(2048)]
        checks.append('all-2048-ordered-IDs')
        assert 'answer-to-Q-MISSING=not-provided' in text
        checks.append('missing-answer-marker-preserved')
        disk = root / 'packet.json'
        disk.write_text(wire, encoding='utf-8')
        recovered = restore_text_view(root, disk.read_bytes(), 'document.txt', sha)
        assert recovered.encode() == original
        checks.append('disk-reload-recovery')
        assert restore_text_view(root, wire, 'document.txt', sha) == recovered
        checks.append('duplicate-retry-same-bytes')
        bad = deepcopy(packet)
        bad['order'].pop()
        try:
            restore_text_view(root, _wire(bad), 'document.txt', sha)
        except ValueError:
            checks.append('truncated-retry-refused')
        else:
            raise AssertionError('truncated packet accepted')
        path.write_bytes(revised)
        try:
            restore_text_view(root, wire, 'document.txt', sha)
        except ValueError:
            checks.append('stale-version-refused')
        else:
            raise AssertionError('stale source accepted')
        new_sha = digest(revised)
        new = text_view(root, 'document.txt', new_sha)
        new_text = restore_text_view(root, _wire(new), 'document.txt', new_sha)
        assert new_text.encode() == revised
        assert 'measurement=17' in new_text and 'measurement=23' in new_text
        assert 'REV-0002 supersedes RES-EXACT-0007; measurement=23; unit=ms; status=unverified; publish=false' in new_text
        checks.append('contradiction-and-explicit-revision-preserved')
        path.write_bytes(original)
        for iteration in range(12):
            order = (True, False) if iteration % 2 == 0 else (False, True)
            for full in order:
                name = 'full' if full else 'dictionary'
                start = time.perf_counter_ns()
                value = text_view(root, 'document.txt', sha, full=full)
                frame = _wire(value)
                restored = restore_text_view(root, frame, 'document.txt', sha)
                elapsed = time.perf_counter_ns() - start
                assert restored.encode() == original
                if iteration:
                    samples[name].append(elapsed)
                sizes[name] = {'serialized_characters':len(frame), 'serialized_utf8_bytes':len(frame.encode()), 'provider_tokens':None}
        assert path.read_bytes() == original
    result = {
        'scope':'local synthetic lossless transport only; no LLM semantic QA or model costs',
        'checks':checks, 'all_checks_passed':True,
        'input_sha256': {'original':digest(original), 'revised':digest(revised)},
        'input_bytes':len(original), 'source_characters':len(original.decode()),
        'sizes':sizes, 'elapsed_ns_samples':samples,
        'median_elapsed_ns':{k:statistics.median(v) for k,v in samples.items()},
        'timing_scope':'encode + compact JSON serialization + fresh-bound restoration, including file reads/hashes; 1 warmup and 11 alternating pairs',
        'provider_tokens':None,'actual_cost':None,'all_role_latency':None,
        'environment':{'python':sys.version, 'platform':platform.platform(), 'machine':platform.machine()},
        'limitations':['Python assertions check exact restoration and markers, not reasoning or citation correctness by a model', 'Fixture is synthetic, no production edge/hotspot attribution', 'Elapsed samples are local CPU overhead, not latency savings', 'Temporary absolute root is included in packets; same root used within each pair']
    }
    Path(out).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    run(sys.argv[1])
