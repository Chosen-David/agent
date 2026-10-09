"""Inspect seven real role entries against unchanged file-link contract and source section."""
import hashlib,json,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
roles=json.loads((D/'baseline.json').read_text())['roles'];rows=[]
for role in roles:
 p=R/role['skill'];text=p.read_text();old=subprocess.check_output(['git','show','7c2449ed16f979ca9f59579651f8f9d022525c02:'+role['skill']],cwd=R,text=True)
 original='[全面取证与贡献导向写作](references/paper_exemplar_learning.md#evidence-to-contribution)'
 revised='[全面取证与贡献导向写作](references/paper_exemplar_learning.md) 的 §9（evidence-to-contribution）'
 assert text==old.replace(original,revised) and old.count(original)==1
 targets=[x for x in re.findall(r'\]\(([^)]+)\)',text) if '://' not in x and not x.startswith('#')]
 assert all((p.parent/x).is_file() for x in targets)
 ref=p.parent/'references/paper_exemplar_learning.md';body=ref.read_text();source=(R/'workflows/paper_exemplar_learning.md').read_text()
 assert '## 9. 全面取证与贡献导向写作' in body and '<a id="evidence-to-contribution"></a>' in body
 assert body.endswith(source)
 assert '只加载该节不强制重启全稿范文学习' in text
 assert (R/role['execution']).is_file()
 rows.append({'role':role['role'],'skill':role['skill'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'local_links':len(targets),'reference_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'exact_one_link_and_section_label_replacement':True,'execution_exists':True,'reference_source_suffix_matches':True})
protected=['tests','agent_runtime','knowledge','evals','workflows','agent_doc/guide']
assert not subprocess.check_output(['git','diff','--name-only','HEAD','--',*protected],cwd=R,text=True)
assert not subprocess.check_output(['git','ls-files','--others','--exclude-standard','--',*protected],cwd=R,text=True)
result={'passed':True,'roles':rows,'role_count':len(rows),'local_links':sum(x['local_links'] for x in rows),'protected_unchanged':protected,'scope':'document compatibility and path/section semantics, not model behavior'}
(D/'link-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':True,'roles':len(rows),'links':result['local_links']}))
