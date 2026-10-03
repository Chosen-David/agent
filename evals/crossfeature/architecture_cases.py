"""Execute controls and emit source evidence separately from model-role judgments."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent


def evaluate():
    source=BASE/'architecture_inputs/core.py'
    spec=importlib.util.spec_from_file_location('crossfeature_engine',source)
    core=importlib.util.module_from_spec(spec); spec.loader.exec_module(core)
    functions={node.name:{'path':'architecture_inputs/core.py','start_line':node.lineno,
        'end_line':node.end_lineno,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
        for node in ast.parse(source.read_text()).body if isinstance(node,ast.FunctionDef)}
    cases=json.loads((BASE/'architecture_inputs/cases.json').read_text())
    oracle=json.loads((BASE/'architecture_oracle.json').read_text())
    outcomes=[]
    for split,items in cases.items():
        for case in items:
            try: actual=core.run(case['rows'],mode=case.get('mode','default'))
            except (ValueError,LookupError) as exc: actual={'error':type(exc).__name__}
            outcomes.append(dict(case_id=case['id'],split=split,actual=actual,expected=oracle[case['id']],
                matches_oracle=actual==oracle[case['id']],layer='program_execution',model_execution='not_run',
                input_sha256=hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest(),
                anchored_code_evidence=functions))
    return outcomes


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(); args.out.parent.mkdir(parents=True,exist_ok=True)
    outcomes=evaluate()
    args.out.write_text(json.dumps(outcomes,indent=2)+'\n')
    print(str(args.out))
    raise SystemExit(any(not case['matches_oracle'] for case in outcomes))
