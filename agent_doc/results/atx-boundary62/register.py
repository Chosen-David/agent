"""Index frozen manual evidence without inventing a managed validation receipt."""
import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.result_store import ResultStore


if __name__ == '__main__':
    paths = ['report.md', 'plan.md', 'plan_review.md', 'revision-v2.md',
             'raw.json', 'raw-O.json', 'raw-v2.json', 'raw-v2-O.json',
             'candidate-v1.py', 'tests-v1.py', 'probe.py', 'result_review.md',
             'independent-raw-v1.summary.json', 'independent-raw-v1-O.summary.json',
             'independent-raw-v2.summary.json', 'independent-raw-v2-O.summary.json',
             'independent-regression-v2.json', 'validation.txt']
    refs = []
    for name in paths:
        path = Path(__file__).parent / name
        refs.append(dict(path=path.relative_to(ROOT).as_posix(),
                         sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    result = ResultStore(ROOT).register_history(
        'atx-boundary62',
        'ATX-BOUNDARY-62 knowledge heading raw ATX delimiter correctness: '
        'fixed 33/72 to 72/72, 115 corpus unchanged, genuine v5 cache migration; '
        'v1 long whitespace regex rejected, v2 independently checked. '
        'Manual scoped evidence, no managed approval or model/performance claim.', refs)
    print(result['record_ref'])
