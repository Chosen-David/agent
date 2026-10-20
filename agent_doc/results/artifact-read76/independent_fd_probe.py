"""Bounded diagnostic for a pre-existing directory-error descriptor leak."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independent_probe', here / 'independent_probe.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
real_open = os.open
rows = []
with tempfile.TemporaryDirectory(prefix='independent-fd76-') as temp:
    root = Path(temp)
    (root / 'directory').mkdir()
    for name, reader in probe.readers:
        opened = []
        def record_open(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            opened.append(fd)
            return fd
        before = len(os.listdir('/proc/self/fd'))
        errors = []
        try:
            with patch.object(probe.rv.os, 'open', record_open):
                for _ in range(2):
                    errors.append(probe.outcome(lambda: reader(root, 'directory')))
            after = len(os.listdir('/proc/self/fd'))
        finally:
            for fd in opened:
                try: os.close(fd)
                except OSError: pass
        cleaned = len(os.listdir('/proc/self/fd'))
        assert after - before == 2 and cleaned == before
        rows.append({'reader': name, 'before': before, 'after_two_errors': after,
                     'after_test_owned_fd_cleanup': cleaned, 'errors': errors})
record = {'scope': 'pre-existing in baseline and candidate; not fixed in this candidate',
          'baseline_source_sha256': probe.sha(probe.source),
          'candidate_source_sha256': probe.sha((probe.ROOT / 'agent_runtime/result_validation.py').read_bytes()),
          'probe_sha256': probe.sha(Path(__file__).read_bytes()), 'rows': rows}
(here / 'independent-fd-raw.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
