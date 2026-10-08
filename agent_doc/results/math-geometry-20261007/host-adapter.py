import json,hashlib
from pathlib import Path
EXPECTED='2fd91e7a27cc630986512ccb81d391c1d9910ac91126d9925a8fd282372196af'
def verify(root, manifest, plan):
    data=(Path(root)/'doc/results/math-geometry-20261007/independent/validation.json').read_bytes()
    if hashlib.sha256(data).hexdigest()!=EXPECTED: raise ValueError("authenticated independent review changed")
    return json.loads(data)
