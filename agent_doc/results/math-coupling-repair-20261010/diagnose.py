from pathlib import Path
import importlib.util,json
b=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('rounder',b/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
c=json.loads((b/'fixtures.json').read_text())['cases'][5]
G,tau,*_=v.repair(c['F'],c['a'],c['b']);print('T6',G,'tau',tau,'actual cost',sum(G[i][j]*abs(v.Q(c['v'][i])-v.Q(c['v'][j])) for i in range(2) for j in range(2)),'expected',c['expected_U'])
