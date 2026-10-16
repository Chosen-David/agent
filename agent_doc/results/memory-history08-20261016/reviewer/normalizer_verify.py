import importlib.util,copy,json
from pathlib import Path
R=Path('.agent-runs/memory-history-20261016-1601');O=R/'reviewer'
spec=importlib.util.spec_from_file_location('independent_history_clock',R/'measure.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old={'entries':[{'id':'a','created_at':'fixed-old'}],'events':[{'sequence':1,'created_at':'fixed-old'}]};results=[]
for kind in ['old_clock_changed','malformed_new_clock','unknown_new_entry']:
 state=copy.deepcopy(old)
 if kind=='old_clock_changed':state['entries'][0]['created_at']='changed'
 elif kind=='malformed_new_clock':state['entries'].append({'id':'new-entry','created_at':'invalid'})
 else:state['entries'].append({'id':'unknown-new-entry','created_at':'2026-10-16T08:00:00.000Z'})
 try:m.normalized(state,old)
 except AssertionError:results.append({'case':kind,'rejected':True})
 else:raise AssertionError(kind+' incorrectly normalized')
(O/'normalizer-verification.json').write_text(json.dumps(results,indent=2)+'\n');print('3 invalid clock/identity normalization probes rejected')
