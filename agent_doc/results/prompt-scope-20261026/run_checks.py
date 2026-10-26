"""Bounded correctness regression; no token, cost or performance measurement."""
import hashlib,json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[3]
phase=sys.argv[1]
if phase not in ('baseline','fixed'):raise SystemExit('baseline or fixed required')
patterns=['test_prompt_context.py']
if phase=='fixed':patterns+=['test_context_serialization.py','test_markdown_protocol_regressions.py']
paths=['agent_runtime/prompt_context.py','scripts/prompt_context.py','agent_runtime/project_docs.py',*['tests/'+p for p in patterns]]
def hashes():return {p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
script="""import unittest,sys
sys.path.insert(0,'tests')
suite=unittest.TestSuite(unittest.defaultTestLoader.discover('tests',pattern=p) for p in sys.argv[1:])
r=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(suite)
raise SystemExit(not r.wasSuccessful())
"""
before=hashes();timeout=False
try:
 result=subprocess.run([sys.executable,'-B','-c',script,*patterns],cwd=root,capture_output=True,timeout=120)
 code=result.returncode;stdout=result.stdout;stderr=result.stderr
except subprocess.TimeoutExpired as exc:
 timeout=True;code=124;stdout=exc.stdout or b'';stderr=exc.stderr or b''
out=Path(__file__).resolve().parent
(out/(phase+'.log')).write_bytes(stdout+stderr)
metadata={'phase':phase,'patterns':patterns,'python':sys.version,'executable':sys.executable,'returncode':code,'timeout':timeout,'outer_timeout_seconds':120,'before':before,'after':hashes(),'scope':'local correctness only; old gates untouched'}
(out/(phase+'.json')).write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'phase':phase,'returncode':code,'timeout':timeout,'stable':before==metadata['after'],'tail':(stdout+stderr).decode('utf-8')[-400:]}))
raise SystemExit(code)
