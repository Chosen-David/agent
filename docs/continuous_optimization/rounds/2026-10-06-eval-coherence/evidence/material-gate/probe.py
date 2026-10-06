from pathlib import Path
import shutil,json,subprocess,hashlib
S=Path('/workspace/scratch/c12f3d9f92bd/w4-role-controller')
B=Path('/workspace/scratch/c12f3d9f92bd/coherence-design/mutant')
B.mkdir()
shutil.copytree(S/'fixtures',B/'fixtures')
for n in ['tasks.json','rubric.json','writer-task.json','writer-rubric.json','adapter.json']:
 shutil.copyfile(S/n,B/n)
r=json.loads((B/'writer-rubric.json').read_text())
r['criteria']['chain-writer'][1]=r['criteria']['chain-writer'][1].replace('medium regression','medium parity and large regression')
(B/'writer-rubric.json').write_text(json.dumps(r,indent=2))
r=json.loads((B/'rubric.json').read_text())
r['criteria']['smoke-main-general'][0]='Actual answer must state roommate transfers 99 CNY to user, total 74 CNY, each share 37 CNY.'
(B/'rubric.json').write_text(json.dumps(r,indent=2))
source=(S/'validate_material.py').read_text().replace("R=B.parent/'agent'","R=Path('/workspace/scratch/c12f3d9f92bd/agent')")
(B/'validate_material.py').write_text(source)
p=subprocess.run(['python',str(B/'validate_material.py')],capture_output=True,text=True)
result={'probe':'isolated current preflight contradictory-rubric mutation; no workers','source_sha256':hashlib.sha256((S/'validate_material.py').read_bytes()).hexdigest(),'harness_change':'Only repository path redirected to existing repo; controller/fixtures copied to isolated scratch','mutations':['chain writer falsely requires medium parity and large regression','settlement rubric falsely demands 99 CNY transfer'],'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
if p.returncode==0:
 v=json.loads((B/'material-validation.json').read_text());result['accepted_fact_groups']=len(v['facts']);result['contradictions_still_in_source_map']={k:[x['criterion'] for x in v['criterion_source_map'][k]] for k in ['chain-writer','smoke-main-general']};result['catalog_hashes']=v['catalog_hashes']
(Path('/workspace/scratch/c12f3d9f92bd/coherence-design/probe-result.json')).write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
