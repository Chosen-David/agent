from pathlib import Path
import sys,unittest
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root))
names=['test_context_cli_wire','test_context_cli_output','test_context_serialization','test_source_context','test_dispatch_context','test_grid_context','test_advice_context','test_advice_discovery','test_artifact_context','test_artifact_bound','test_artifact_edits','test_artifact_identity','test_artifact_identical_fastpath','test_artifact_localized_diff','test_artifact_token_selection']
suite=unittest.TestSuite()
for name in names:suite.addTests(unittest.defaultTestLoader.discover(str(root/'tests'),pattern=name+'.py'))
r=unittest.TextTestRunner(verbosity=1).run(suite)
sys.exit(not r.wasSuccessful())
