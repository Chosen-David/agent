"""Hash explicit delivery files; an inventory is not independent acceptance."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
RUN = Path(__file__).resolve().parent
selected = ['plan.md', 'plan_review.md', 'prior-search.json', 'measure.py',
            'raw-v5-serial.json', 'independent-v5.json', 'native-v5.json',
            'native-integrated-66c.json', 'independent-integrated-66c.json',
            'review.md', 'final-review.md', 'delta-review.md',
            'reviewer-empty-subclass.json', 'reviewer-boundaries.py',
            'reviewer-boundaries-v5.json', 'reviewer-native-boundaries.json',
            'reviewer-native-boundaries-opt.json', 'baseline-tests.log',
            'full-tests.log', 'reader-tests.log', 'full-integrated-tests.log',
            'reader-integrated-tests.log', 'report.md', 'capture.py']
paths = [ROOT / 'agent_runtime/result_store.py', ROOT / 'agent_doc/task/TASK.md',
         ROOT / 'agent_doc/task/task_details/RESULT-SEARCH-INVARIANT.md'] + [RUN / p for p in selected]
entries = []
for path in paths:
    b = path.read_bytes()
    entries.append({'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)})
print(json.dumps({'scope': 'guarded ordinary-context eligibility cache in full ResultStore.search; warm-cache local CPU, exact returns and 18 boundary cases',
                  'main_base': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
                  'files': entries, 'publication_permission': 'user explicitly authorized tested direct main; no PR/force',
                  'limitations': ['manual independent hosted review, no managed runtime deployment',
                                  'no concurrent caller mutation contract', 'no model/token/cold-cache/end-to-end claim',
                                  'early/interfered measurements excluded from acceptance']}, indent=2, sort_keys=True))
