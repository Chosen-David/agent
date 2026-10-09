"""Execution glue for the approved frozen pre-adoption checks; CLI8th explicitly deferred."""
import importlib.util,io,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));D=Path(__file__).parent
from scripts.benchmark_communication_candidates_v2 import load,tests
C=load(D/'candidate.py').Mailbox
spec=importlib.util.spec_from_file_location('batch_frozen_checks',D/'batch_tests.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.Mailbox=C
names=[n for n in unittest.defaultTestLoader.getTestCaseNames(m.BatchTests) if n!='test_cli_batch_entry_and_failure_exit']
stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite(m.BatchTests(n) for n in names))
(D/'producer_batch_tests.log').write_text(stream.getvalue());summary=dict(run=r.testsRun,failures=len(r.failures),errors=len(r.errors),ok=r.wasSuccessful(),selected=names,cli_deferred='8th actualCLI test after adoption in integration')
(D/'producer_batch_tests.json').write_text(json.dumps(summary,indent=2)+'\n');assert r.wasSuccessful() and r.testsRun==7
result,log=tests(C);(D/'producer_existing_tests.log').write_text(log);(D/'producer_existing_tests.json').write_text(json.dumps(result,indent=2)+'\n');assert result['ok'] and result['run']==25
print('7 candidatebatchAPI and25existing candidate-injected tests pass; existingCLI subprocess baseline, newCLI deferred.')
