import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

RUN = Path(__file__).resolve().parent
ROOT = next(p for p in RUN.parents if (p / 'agent_runtime/task_manifest.py').is_file())
sys.path.insert(0, str(ROOT))


def main():
    source = ROOT / 'agent_runtime/token_usage.py'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    records = []
    for directory in ('tests', 'apps/paper-reader/tests'):
        stream = io.StringIO()
        suite = unittest.defaultTestLoader.discover(str(ROOT / directory), pattern='test*.py',
                                                   top_level_dir=str(ROOT / directory))
        result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
        (RUN / (directory.replace('/', '-') + '-full.log')).write_text(stream.getvalue())
        records.append({'directory': directory, 'run': result.testsRun, 'skipped': len(result.skipped),
                        'successful': result.wasSuccessful(),
                        'errors': [(str(t), err) for t, err in result.errors],
                        'failures': [(str(t), err) for t, err in result.failures]})
    after = hashlib.sha256(source.read_bytes()).hexdigest()
    (RUN / 'final-regression.json').write_text(json.dumps({
        'source_sha256_before': before, 'source_sha256_after': after, 'results': records}, indent=2) + '\n')
    return 0 if before == after and all(r['successful'] for r in records) else 1


if __name__ == '__main__':
    raise SystemExit(main())
