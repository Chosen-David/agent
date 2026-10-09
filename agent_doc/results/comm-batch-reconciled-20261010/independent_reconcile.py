"""Fresh /root/batch_verify reconciliation; frozen measurements never replayed."""
import ast,hashlib,importlib.util,io,json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];R=Path(__file__).parent;D=R.parent/'comm-batch-20261010';sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,_review,inspect_result

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha(p))
s=importlib.util.spec_from_file_location('frozen_actual_verifier',D/'independent_validate.py');h=importlib.util.module_from_spec(s);s.loader.exec_module(h)

def properties():
 # Reuse the reviewed independent oracle code under fresh dependencies; all writes target R.
 h.D=R
 # Atomic reference helper remains frozen original code, loaded read-only from D.
 original_module=h.module
 h.module=lambda p,n: original_module(D/'benchmark_v2.py' if p==R/'benchmark_v2.py' else p,n)
 h.properties()
 stream=io.StringIO();suite=unittest.TestSuite()
 for file in ['tests/test_handoff.py','tests/test_handoff_basis.py','tests/test_handoff_consumer.py','tests/test_handoff_encoding.py','tests/test_handoff_scaling.py','tests/test_handoff_scope.py']:
  m=original_module(ROOT/file,'fresh_'+Path(file).stem);suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(m))
 result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);(R/'independent_handoff_tests.log').write_text(stream.getvalue());assert result.wasSuccessful() and result.testsRun==63

def validate():
 contract=json.loads((R/'contract.json').read_text());manifest,plan,proof=_snapshot(ROOT,contract);assert proof['manifest_sha256']=='13acc2d8a39158870b8143f4f9e49d5d6b5216e83f11df17c484df9b7e9bce4f'
 assert proof==json.loads((R/'independent_before_snapshot.json').read_text())
 binding=json.loads((R/'reconciliation_binding.json').read_text())
 assert sha(D/'manifest.json')==binding['original_native_manifest']['sha256'] and sha(D/'validation.json')==binding['original_validation']['sha256']
 old=json.loads((D/'manifest.json').read_text())
 for group,rs in old['artifacts'].items():
  for r in rs:
   p=ROOT/r['path']
   if r['path']=='agent_runtime/handoff_basis.py':p=R/'measured_handoff_basis.py'
   assert sha(p)==r['sha256'],r['path']
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==binding['fresh_main']
 for n in ['baseline.py','candidate.py','batch_tests.py','producer_checks.py']:assert (R/n).read_bytes()==(D/n).read_bytes()
 assert (ROOT/'agent_runtime/communication.py').read_bytes()==(D/'baseline.py').read_bytes()
 assert (R/'producer_raw.json').read_bytes()==(D/'producer/raw.json').read_bytes() and (R/'independent_raw.json').read_bytes()==(D/'independent_replay/raw.json').read_bytes()
 # Review concurrent diff: only default context-format validation and opt-in encoding in handoff functions.
 diff=subprocess.check_output(['git','diff','e6b3dc14ad9eb2c5d3c1cb09ccda5027a7d74019',binding['fresh_main'],'--','agent_runtime/handoff_basis.py','agent_runtime/handoff_encoding.py'],cwd=ROOT,text=True)
 (R/'independent_dependency.diff').write_text(diff)
 source=(R/'candidate.py').read_text();tree=ast.parse(source);box=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Mailbox')
 for n in box.body:
  if isinstance(n,ast.FunctionDef) and n.name in ['publish','publish_many','_prepare_publish','_store_publish','acknowledge','connect','__init__','_init_usage']:
   assert 'handoff_basis' not in ast.get_source_segment(source,n) and 'handoff_encoding' not in ast.get_source_segment(source,n)
 assert 'from .handoff_encoding import' in (ROOT/'agent_runtime/handoff_basis.py').read_text()
 assert "request.get('context_format', 'json')" in (ROOT/'agent_runtime/handoff_basis.py').read_text()
 cohorts={n:h.summarize(R/(n+'_raw.json')) for n in ['producer','independent']};keep=all(c['guard'] and (not c['primary'] or c['improved']) for rs in cohorts.values() for c in rs)
 assert keep
 for n in ['producer_batch_tests','producer_existing_tests']:
  t=json.loads((R/(n+'.json')).read_text());assert t['ok'] and t['run']==(7 if n=='producer_batch_tests' else 25)
 assert 'Ran 63 tests' in (R/'fresh_handoff_tests.log').read_text() and '\nOK\n' in (R/'fresh_handoff_tests.log').read_text()
 assert 'Ran 63 tests' in (R/'independent_handoff_tests.log').read_text() and '\nOK\n' in (R/'independent_handoff_tests.log').read_text()
 assert json.loads((R/'independent_batch_oracles.json').read_text())['count']==29
 (R/'independent_after_snapshot.json').write_text(json.dumps(proof,indent=2)+'\n');decision=dict(keep=keep,cohorts=cohorts,original_validation_sha256=sha(D/'validation.json'),fresh_main=binding['fresh_main'],performance_replays=0)
 (R/'independent_decision.json').write_text(json.dumps(decision,indent=2)+'\n')
 evidence=[ref(p) for p in sorted(R.glob('independent*')) if p.is_file() and p.name not in ['independent_validation.log','independent_native_readback.json']]+[ref(D/'validation.json'),ref(D/'independent_validate.py')]
 reasons=dict(implementation='Exact frozen baseline/candidate remain byte-identical on9073 main. Concurrent diff limited to handoff default-format check and opt-in encoding; publish/ACK/setup paths do not call changed dependency. Live fresh dependencies pinned.',reference_boundary='Fresh61 public checks and2 regressions per source,29 batch/list/Unicode/budget/ref/live-route/thread/reader WAL+DELETE oracles,7 frozen API tests,atomic originalpublish reference valid/failing fixture,63 focused handoff tests; default behavior compatible.',data_integrity='Original manifest/proof unchanged; every original artifact hash rechecked, oldhandoff_basis mapped only to exact measured snapshot. R timing copies byte-identical; fresh native manifest hashes unchanged before/after; all contracts bound.',numerical_sanity='Both original cohorts recomputed from exact byte copies:34 ordered attempts,31 finite positive samples, exact output/state hashes and all medians/gains/guards remain valid. Fresh counts7/25/63 and own29 verified.',measurement_validity='No performance execution in reconciliation. Original public publish/ACK measurement path unaffected by concurrent handoff change; reused historical measurements identified accurately and not represented as newly measured9073 data.',reproducibility='Original independent31replay preserved; targeted independent fresh functional/reference/visibility/default/handoff tests passed; no performance retry, candidate change, threshold change, budget reset or third planner review.')
 review=dict(schema_version='experiment-validation/v1',**proof,verifier=dict(actor='batch-independent-verifier',independent=True,source='actual trusted host child /root/batch_verify followup; parent authenticates dispatch and completion',run_id='comm-batch-independent-reconciled-20261010',method='Fresh dependency diff/call-path and old provenance audit, independent fresh targeted checks, exact raw copy recomputation; no performance replay'),limitations=['Original performance observations belong to e6b3dc checkout and measured dependency snapshot; current acceptance concerns proven unchanged measured paths plus fresh compatibility.','Shared CPU synthetic SQLite scope only; no network/LLM/token improvement claim.','Finite checks, caller-stable JSON values, single-caller benchmark-only atomic reference.','Full integration and actual newCLI8th remain pending adoption; oldmanifest livehash nowstale is historical only.','Initial helper selected only23 handoff tests and asserted63, failure and initial premature proof preserved; corrected suite uses all six frozen focused files and validation now requires independent63 log; no source or performance replay changed.'],checks={k:dict(verdict='pass',reason=v,evidence=evidence) for k,v in reasons.items()},decision=decision)
 assert _snapshot(ROOT,contract)[2]==proof;_review(ROOT,manifest,plan,proof,review);(R/'validation.json').write_text(json.dumps(review,indent=2)+'\n')
 out=inspect_result(ROOT,contract,verifier=lambda root,manifest,plan:review);(R/'independent_native_readback.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status=out['status'],keep=keep,validation_sha256=sha(R/'validation.json'))))
if __name__=='__main__':
 if sys.argv[1]=='snapshot':
  proof=_snapshot(ROOT,json.loads((R/'contract.json').read_text()))[2];assert proof['manifest_sha256']=='13acc2d8a39158870b8143f4f9e49d5d6b5216e83f11df17c484df9b7e9bce4f';(R/'independent_before_snapshot.json').write_text(json.dumps(proof,indent=2)+'\n')
 elif sys.argv[1]=='properties':properties()
 elif sys.argv[1]=='validate':validate()
