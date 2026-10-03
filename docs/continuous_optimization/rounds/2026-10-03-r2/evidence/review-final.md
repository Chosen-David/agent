# Independent final recheck

Frozen runner SHA-256: `6b077b725f35ba31f50697ecf83f459fdc7f9e5991082dbf0d2dd13786d5dcf0`.

25/25 independent program acceptance cases produced the expected decision; zero false accepts and zero exceptions. The valid synthetic control still passes. CLI `report --require-complete` returned expected exits for all 25 cases with no traceback.

Original 9 false accepts and the later 2 ancestor-symlink false accepts have been repaired; initial/intermediate records are retained. No further material bug was found within this bounded case set. This establishes program contract behavior for these synthetic records only; it does not authenticate host model execution or establish semantic task success.

Files: `results-initial.json`, `results-repaired.json`, `results-repaired2.json`, `results-final.json`, `cli-final.json`, `adversarial_checks.py`.
