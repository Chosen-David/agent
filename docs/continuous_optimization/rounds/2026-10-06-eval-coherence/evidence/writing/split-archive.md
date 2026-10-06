# Complete writing evidence archive

The full original archive is published in two parts because the GitHub plugin request cap is16MiB. Download both files next to split-archive.json. Their ordered concatenation restores the original immutable full-paper-evidence.tar.xz. FinalSHA256:153b4c53fdb76438008709529bae3da11f6d46f2816dbb7b4b1c129e74204c7c.

- [Part01](full-paper-evidence.tar.xz.part01)
- [Part02](full-paper-evidence.tar.xz.part02)
- [Hashes](split-archive.json)

Run from this directory:

```python
import json, pathlib, hashlib
p=pathlib.Path('.');m=json.loads((p/'split-archive.json').read_text());parts=[]
for x in m['parts']:
 b=(p/x['path']).read_bytes()
 assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256']
 parts.append(b)
b=b''.join(parts)
assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256']
(p/m['original']).write_bytes(b)
```

The original archive manifest and full manuscript evidence remain unchanged. Follow report.md for fresh extraction/replay; this is packaging, not a new model run.
