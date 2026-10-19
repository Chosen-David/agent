"""Bounded diagnostic of frozen v1 suffix regex; not a production speed claim."""
import hashlib
import json
from pathlib import Path
import re
import time

out = Path(__file__).with_name('independent-suffix-diagnostic-v1.json')
if out.exists():
    raise SystemExit('refusing to overwrite evidence')
pattern = r'[ \t]+#+[ \t]*$'
rows = []
for n in (1000, 2000, 4000, 8000):
    value = ' value' + ' ' * n
    samples = []
    for repeat in range(3):
        start = time.perf_counter()
        result = re.sub(pattern, '', value).strip(' \t')
        samples.append(time.perf_counter() - start)
        if result != 'value':
            raise RuntimeError('unexpected result')
    rows.append(dict(spaces=n, input_sha256=hashlib.sha256(value.encode()).hexdigest(), seconds=samples))
with out.open('x') as handle:
    json.dump(dict(pattern=pattern, method='perf_counter three repeats; no warmup; diagnostic only',
                   rows=rows, script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()), handle, indent=2)
print(json.dumps(rows))
