"""Same-scope continuation; original evidence is never overwritten."""
import hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[3]
out=Path(__file__).resolve().parent
patterns=['test_prompt_context.py','test_context_serialization.py','test_markdown_protocol_regressions.py']
paths=['agent_runtime/prompt_context.py','scripts/prompt_context.py','agent_runtime/project_docs.py',*['tests/'+p for p in patterns]]
def hashes():return {p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
script="""import unittest,sys
sys.path.insert(0,'tests')
suite=unittest.TestSuite(unittest.defaultTestLoader.discover('tests',pattern=p) for p in sys.argv[1:])
r=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(suite)
raise SystemExit(not r.wasSuccessful())
"""
if any((out/name).exists() for name in ('fixed-v2.log','fixed-v2.json')):
    raise SystemExit('do not overwrite continuation evidence')
before=hashes();timeout=False
try:
 r=subprocess.run([sys.executable,'-B','-c',script,*patterns],cwd=root,capture_output=True,timeout=120)
 code=r.returncode;stdout=r.stdout;stderr=r.stderr
except subprocess.TimeoutExpired as e:timeout=True;code=124;stdout=e.stdout or b'';stderr=e.stderr or b''
(out/'fixed-v2.log').write_bytes(stdout+stderr)
(out/'fixed-v2.json').write_text(json.dumps({'lineage':'PROMPT-SCOPE-01','version':2,'patterns':patterns,'python':sys.version,'returncode':code,'timeout':timeout,'outer_timeout_seconds':120,'before':before,'after':hashes(),'scope':'native-newline oracle correction, no production change or old-source retry'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'returncode':code,'stable':before==hashes(),'timeout':timeout,'tail':(stdout+stderr).decode('utf-8')[-400:]}))
raise SystemExit(code)
