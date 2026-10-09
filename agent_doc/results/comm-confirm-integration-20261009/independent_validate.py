"""Final integration audit by the independent confirmation host context."""
import hashlib, importlib.util, json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];D=Path(__file__).parent;P=D.parent/'comm-confirm-20261009'
sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,_review
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return dict(path=str(path.relative_to(ROOT)),sha256=digest(path))
contract=json.loads((D/'contract.json').read_text());manifest,plan,proof=_snapshot(ROOT,contract)
assert proof['manifest_sha256']=='afff516decbf701893bcfb90096eb2b6cd6ce68735c4d7ddb90b707ddfb101f9'
assert json.loads((D/'ready.json').read_text())['manifest']['sha256']==proof['manifest_sha256']
prior_contract=json.loads((P/'contract.json').read_text());pm,pp,pr=_snapshot(ROOT,prior_contract)
binding=json.loads((D/'integration_binding.json').read_text())
nodes={n['id']:n for n in binding['nodes']}
assert nodes['regression']['experiment_result']==contract
assert nodes['integration_review']['result_validation']==contract
for node in ('regression','integration_review'): assert nodes[node]['required_result_refs']==[prior_contract]
for node in ('publish','readback'): assert nodes[node]['required_result_refs']==[prior_contract,contract]
prior=json.loads((P/'validation.json').read_text());_review(ROOT,pm,pp,pr,prior)
assert digest(P/'validation.json')=='107922ce57fb1873cae48db8a2c25e80078d75d00a42feb0dfb8ef0357160663'
assert prior['decision']['keep'] is True
assert (ROOT/'agent_runtime/communication.py').read_bytes()==(P/'candidate.py').read_bytes()
spec=importlib.util.spec_from_file_location('confirmation_verifier',P/'independent_validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
cohorts={name:v.summarize(json.loads(path.read_text())) for name,path in [('producer',P/'raw.json'),('independent',P/'independent_replay/raw.json')]}
assert all(c['guard'] and(not c['primary'] or c['improved']) for rows in cohorts.values() for c in rows)
report=(P/'report.md').read_text()
for name,rows in cohorts.items():
    for c in rows:
        expected=f"|{name}|{c['total']}|{c['layout']}|{c['median_ms']['baseline']:.6f}|{c['median_ms']['candidate']:.6f}|{c['speedup']:.3f}×|通过|"
        assert expected in report,expected
assert '不是所有形状都加速' in report and 'VM增加16' in report and '6.35×/8.16×' in report
assert '共享CPU' in report and '负结果' in report
# Historical negative artifacts remain byte-identical to the original authenticated record.
assert digest(P.parent/'comm20-20261009-r17/validation.json')=='362137cf3028fc25bae69f491e0db761eb49ec050bf9aff65c41b0c9eceaab98'
summary=json.loads((D/'summary.json').read_text())
assert summary['full_tests']=={'run':889,'pass':881,'skip':8} and summary['reader_pass']==3
assert manifest['metrics']==[dict(name='full_test_count',value=889,unit='dimensionless')]
full=(D/'full_tests.log').read_text(); reader=(D/'reader_tests.log').read_text()
assert re.search(r'Ran 889 tests in [0-9.]+s\n\nOK \(skipped=8\)',full)
assert len(re.findall(r'^test_.* \.\.\. ok$',full,re.M))==881
assert len(re.findall(r'^test_.* \.\.\. skipped ',full,re.M))==8
assert re.search(r'Ran 3 tests in [0-9.]+s\n\nOK',reader)
for f in (D/'adaptive_tests.log',D/'independent_adaptive_tests.log'):
    text=f.read_text();assert re.search(r'Ran 2 tests in [0-9.]+s\n\nOK',text)
assert 'test_wal_writer_commits_between_ledger_and_rows' in full
assert 'test_rollback_writer_completes_after_reader_releases_snapshot' in full
for label in ('baseline','candidate'):
    assert json.loads((P/f'independent_properties_{label}.json').read_text())['count']==61
assert len(json.loads((P/'independent_snapshot.json').read_text())['checks'])==6
# Only transparent delegation was added to fix the initial proxy's missing executemany.
initial=(P/'integration-attempt1/test_adaptive.py').read_text()
current=(ROOT/'tests/test_communication_adaptive.py').read_text()
for block in ("\n                    def __getattr__(self, name):\n                        return getattr(self.cursor, name)\n", "\n                    def __getattr__(self, name):\n                        return getattr(self.db, name)\n"):
    assert block in current;current=current.replace(block,'')
assert current==initial
evidence=[ref(p) for p in [D/'independent_validate.py',D/'integration_binding.json',D/'independent_adaptive_tests.log',D/'full_tests.log',D/'reader_tests.log',D/'adaptive_tests.log',P/'validation.json',P/'independent_validate.py',P/'independent_decision.json',P/'independent_snapshot.json',P/'independent_properties_baseline.json',P/'independent_properties_candidate.json',P/'report.md',P/'integration-attempt1/test_adaptive.py',P/'integration-attempt1/failure.json',D/'validation_plan_draft_v1.json']]
reasons=dict(implementation='Final runtime equals exact accepted candidate; twelve-line inbox-only patch unchanged. Read transparent test proxy and report; corrected integration procedures preserve old draft and align current source/result.',reference_boundary='Revalidated61public properties per source, both numeric nested-plan and mutated-reference regressions,6 prior WAL/DELETE snapshots; newly integrated2adaptive tests independently rerun successfully. WAL initial1 discriminates missing read snapshot.',data_integrity='All integration manifest/protocol/artifact hashes and accepted prior manifest/validation/six-domain evidence rehashed with native contract before/after. Old r17 negative validation remains exact; failed initial proxy preserved.',numerical_sanity='All14 producer/replay rows independently recalculated from complete31pair samples and matched report rounded values.889total=881pass+8skip,reader3 and2adaptive tests agree with complete logs/summary.',measurement_validity='No additional performance experiment; accepted sharedCPU synthetic timing reused with exact software/source and honest limitations. Seven optional visual tests and one opt-in tmux test skipped; communication/adaptive tests executed.',reproducibility='Actual independent rerun of both current adaptive tests covering6subcases. Fresh prior acceptance proof and complete root regression logs align exact runtime; no performance retries.')
review=dict(schema_version='experiment-validation/v1',**proof,verifier=dict(actor='comm-confirm-independent-verifier',independent=True,source='actual host collaboration child /root/confirm_verify; parent authenticates returned message',run_id='comm-confirm-integration-independent-20261009',method='Exact source/test/report review; native prior/integration proof and complete logs audit; focused adaptive rerun'),limitations=['Shared CPU synthetic local SQLite scope; no model/network/token/service/deployment claim.','Seven optional visualization tests and one real tmux test skipped for unavailable dependencies/backend.','Append-only concurrent writer fallback initial4 preserves first3 rows so its equality does not discriminate snapshots; WAL initial1 does. Finite tests do not prove universal correctness.','Initial proxy test error and stale integration protocol draft preserved; only proxy delegation/protocol descriptions corrected, candidate and measured data unchanged.'],checks={k:dict(verdict='pass',reason=reason,evidence=evidence) for k,reason in reasons.items()},decision=dict(accepted=True,keep=True,publication_eligible=True,scope='Exact accepted local source plus functional integration; remote publication/readback remains root responsibility'))
_snapshot(ROOT,contract);_snapshot(ROOT,prior_contract);_review(ROOT,manifest,plan,proof,review)
(D/'validation.json').write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps(dict(status='usable-with-scope',accepted=True,validation_sha256=digest(D/'validation.json'),manifest_sha256=proof['manifest_sha256'])))
