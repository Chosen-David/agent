"""Independent final artifact/trace checks; not a producer or host service."""
from pathlib import Path
import collections,hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[4];RUN=ROOT/'agent_doc/results/kernel-feedback-20261008';OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
contract=json.loads((RUN/'contract.json').read_text());manifest,plan,proof=_snapshot(ROOT,contract)
checks={}
config=json.loads((RUN/'final/candidate-inputs.json').read_text())
checks['candidate_hash_mismatches']=[p for p,h in config.items() if sha(ROOT/p)!=h]
log=(RUN/'final/repository-tests.log').read_text();rows=[s for s in log.splitlines() if re.match(r'^test_.*\.\.\. ',s)]
counts=collections.Counter('skipped' if ' ... skipped ' in s else s.rsplit(' ... ',1)[-1] for s in rows)
checks['repository_result_rows']=len(rows);checks['repository_status_counts']=dict(counts)
checks['repository_unique_cases']=len({s.split(' ... ')[0] for s in rows})
checks['repository_summary_matches']=len(rows)==813 and counts=={'ok':805,'skipped':8} and 'Ran 813 tests' in log and log.endswith('OK (skipped=8)\n')
reader=(RUN/'final/reader-tests.log').read_text();checks['reader_summary_matches']='Ran 3 tests' in reader and reader.endswith('OK\n')
checks['reference_sync_empty_log']=(RUN/'final/reference-sync.log').read_bytes()==b''
checks['project_docs_valid_json']=json.loads((RUN/'final/project-docs.log').read_text())['schema_version']=='project-documents/v1'
lock=json.loads((RUN/'forward/revalidation/input-lock.json').read_text());comp=json.loads((RUN/'forward/revalidation/comparison.json').read_text());trace=json.loads((RUN/'forward/revalidation/tool-trace.json').read_text())
checks['forward_current_input_mismatches']=[r['path'] for r in lock['files'] if sha(ROOT/r['path'])!=r['sha256']]
checks['forward_original_artifact_mismatches']=[p for p,h in lock['original_artifacts_before'].items() if sha(ROOT/p)!=h or comp['original_artifacts_after'][p]!=h]
checks['forward_trace_hashes_valid']=all(hashlib.sha256(t['stdout'].encode()).hexdigest()==t['stdout_sha256'] and hashlib.sha256(json.dumps(t['argv'],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==t['argv_json_sha256'] for t in trace)
checks['forward_stdout_exact']=trace[0]['stdout'].encode()==(RUN/'forward/revalidation/compiler-feedback.stdout').read_bytes()
new=json.loads((RUN/'forward/revalidation/compiler-feedback.json').read_text());old=json.loads((RUN/'forward/compiler-feedback.json').read_text())
checks['forward_json_same']=new==old==json.loads(trace[0]['stdout'])
run=subprocess.run([sys.executable,'-B',str(ROOT/'plugins/research-assistant/skills/research-implement-optimize/scripts/compiler_feedback.py'),str(RUN/'forward-input.log')],cwd=ROOT,capture_output=True,text=True,timeout=10)
checks['independent_rerun_exit']=run.returncode;checks['independent_rerun_matches']=json.loads(run.stdout)==new
checks['independent_rerun_stderr']=run.stderr
(OUT/'final-forward-rerun.stdout').write_text(run.stdout)
checks['explicit_expected_resources']=new['records'][0]['metrics']==dict(registers_per_thread=128,static_shared_bytes=32768,stack_frame_bytes=64,spill_store_bytes=32,spill_load_bytes=16) and new['records'][1]['metrics']==dict(registers_per_thread=None,static_shared_bytes=None,stack_frame_bytes=0,spill_store_bytes=0,spill_load_bytes=0) and new['records'][1]['target'] is None
checks['compile_and_performance_unknown']=new['compile_success'] is None and new['performance_verdict']=='not_measured'
report={'proof':proof,'checks':checks,'limitations':['Raw repository log counts are verified, not an independent replay of every repository test.','One synthetic repeated forward case is not an unseen-task or performance comparison.']}
(OUT/'final-evidence-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(checks,indent=2))
