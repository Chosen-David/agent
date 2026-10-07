import json, hashlib
from pathlib import Path
EXPECTED = '87f7b9382e1ae2f14f160be7a47e3017039ba001d6532b4be28bdcf47579c0b7'
def verify(root, manifest, plan):
    # Root explicitly authenticated actual independent relocation-review events.
    data = (Path(root) / 'doc/results/math-softmax-20261007-v2/independent/review.json').read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED:
        raise ValueError('authenticated review changed')
    return json.loads(data)
