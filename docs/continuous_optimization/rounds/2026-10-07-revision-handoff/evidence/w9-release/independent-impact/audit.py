"""Read-only historical evidence/hash audit; writes only adjacent audit result."""
from pathlib import Path
import hashlib, io, json, subprocess, tarfile, zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[7]
OUT = Path(__file__).resolve().parent
OLD = ROOT / 'docs/continuous_optimization/rounds/2026-10-06-eval-coherence/evidence'
NEW = ROOT / 'docs/continuous_optimization/rounds/2026-10-07-revision-handoff'
sha = lambda b: hashlib.sha256(b).hexdigest()
def readjson(p): return json.loads(p.read_text())
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT).decode().strip()

candidate = readjson(NEW/'candidate.json')
result = {'observed_at': datetime.now(timezone.utc).isoformat(), 'head': git('rev-parse','HEAD'),
          'candidate': candidate, 'scope': 'Historical integrity and applicability audit, not new model execution, paper reading, visual review, or grading of W9 roles.',
          'candidate_hash_checks': {p: sha((ROOT/p).read_bytes()) == h for p,h in candidate['production_files'].items()},
          'runtime_hash_check': sha((ROOT/'agent_runtime/communication.py').read_bytes()) == candidate['runtime_sha256'],
          'tracked_diff_paths_at_start': git('diff','--name-only').splitlines()}

parts = readjson(OLD/'writing/split-archive.json')
blob = b''.join((OLD/'writing'/p['path']).read_bytes() for p in parts['parts'])
t = tarfile.open(fileobj=io.BytesIO(blob),mode='r:xz')
# Materialize regular members in archive order once; resolve internal hardlinks below.
tar_bytes = {m.name:t.extractfile(m).read() for m in t.getmembers() if m.isfile()}
for m in t.getmembers():
    if m.islnk(): tar_bytes[m.name] = tar_bytes[m.linkname]
zblob = (OLD/'w4-modern-architecture/modern-architecture-evidence.zip').read_bytes()
z = zipfile.ZipFile(io.BytesIO(zblob))
result['archive_integrity'] = {'writing': {'sha256':sha(blob),'matches':sha(blob)==parts['sha256'],
    'parts_match':all(sha((OLD/'writing'/p['path']).read_bytes())==p['sha256'] for p in parts['parts'])},
    'modern': {'sha256':sha(zblob),'matches':sha(zblob)==readjson(OLD/'w4-modern-architecture/package-receipt.json')['sha256']}}

roles = ('research-write','research-diagrams','research-review','research-read-pdf','research-data-visualization')
workflow_names = ('paper_writing_workflow.md','paper_delivery_contract.md','paper_exemplar_learning.md',
    'data_visualization_learning.md','data_visualization_workflow.md','diagram_workflow.md',
    'figure_shared.md','figure_inputs.md','figure_tools.md','figure_workflow.md','reader_workflow.md','reviewer_workflow.md')
def selected(p): return any(p.startswith(f'plugins/research-assistant/skills/{r}/') for r in roles) or p in ['workflows/'+n for n in workflow_names] or p=='AGENTS.md'

for label, names, read in [('writing',t.getnames(),tar_bytes.__getitem__),('modern',z.namelist(),z.read)]:
    name_set=set(names)
    audit={'manifests':{},'collections':[],'grades':[],'instruction_records':[], 'reading_records':[]}
    if label=='writing':
        ix=json.loads(read('archive-files.json'))
        mismatches=[p for p,h in ix.items() if p not in name_set or sha(read(p))!=h]
        audit['indexed_files']={'count':len(ix),'mismatches':mismatches}
    else:
        audit['trace_omissions']=json.loads(read('redaction-manifest.json'))
    for n in names:
        if n in ('run/manifest.json','writer-run/manifest.json'):
            m=json.loads(read(n)); bindings=[]
            for p,h in m['snapshot_hashes'].items():
                cur=sha((ROOT/p).read_bytes()) if (ROOT/p).is_file() else None
                archived=n.rsplit('/',1)[0]+'/snapshot/'+p
                bindings.append({'path':p,'old':h,'current':cur,'same':h==cur,
                    'snapshot_bytes_match':archived in name_set and sha(read(archived))==h,'selected_scientific_dependency':selected(p)})
            audit['manifests'][n]={'revision':m['revision'],'binding_count':len(bindings),
                'changed':[x for x in bindings if not x['same']],
                'selected_dependencies':[x for x in bindings if x['selected_scientific_dependency']],
                'snapshot_integrity_failures':[x for x in bindings if not x['snapshot_bytes_match']]}
        if n.endswith('/collection.json'):
            c=json.loads(read(n)); prefix=n.rsplit('/',1)[0]+'/outputs/'
            missing=[prefix+p for p in c['output_hashes'] if prefix+p not in name_set]
            mismatch=[prefix+p for p,h in c['output_hashes'].items() if prefix+p in name_set and sha(read(prefix+p))!=h]
            audit['collections'].append({'path':n,'output_count':len(c['output_hashes']),'missing':missing,'mismatches':mismatch,'receipt':c.get('receipt')})
        if n.endswith('/grade.json'):
            g=json.loads(read(n)); audit['grades'].append({'path':n,'case_id':g.get('case_id'),'attempt':g.get('attempt'),
                'verdict':g.get('verdict'), 'semantic_verdict':g.get('semantic_verdict'),'checks':len(g.get('checks',[])),
                'grade_hashes_equal_collection':g.get('output_hashes') == json.loads(read(n.rsplit('/',1)[0]+'/collection.json'))['output_hashes'],
                'failed_checks':[c for c in g.get('checks',[]) if c.get('verdict')!='pass'],
                'record_other_fields':{k:v for k,v in g.items() if k not in ('checks',)}})
        if n.endswith(('instruction_load.json','instruction_binding.json','loaded_instructions.json','handoff-receipt.json')) and '/work/' not in n:
            d=json.loads(read(n)); records=[]
            def walk(x):
                if isinstance(x,dict):
                    if isinstance(x.get('path'),str) and '/snapshot/' in x['path']:
                        p=x['path'].split('/snapshot/',1)[1]; h=x.get('sha256'); cur=sha((ROOT/p).read_bytes()) if (ROOT/p).is_file() else None
                        records.append({'path':p,'recorded':h,'current':cur,'same':h==cur})
                    for v in x.values(): walk(v)
                elif isinstance(x,list):
                    for v in x: walk(v)
            walk(d);audit['instruction_records'].append({'archive_path':n,'bindings':records})
        if n.endswith(('page_coverage.jsonl','page-coverage.jsonl','reader_report.json','first_pass_complete.json')):
            s=read(n).decode(); audit['reading_records'].append({'path':n,'sha256':sha(read(n)), 'lines':len(s.splitlines()), 'record':json.loads(s) if n.endswith('.json') else [json.loads(x) for x in s.splitlines() if x]})
    result[label]=audit

copies=[]
for case in ('attention','systems','unet'):
    n=f'run/cases/full-paper-{case}/attempts/0001/outputs/paper/paper.pdf'
    p=OLD/f'writing/{case}-paper.pdf'
    copies.append({'public_path':str(p.relative_to(ROOT)),'archive_path':n,'sha256':sha(p.read_bytes()),'same':p.read_bytes()==tar_bytes[n]})
for case,attempt in [('ditfuse2026','0002'),('doubt2026','0001'),('gazing2026','0001')]:
    n=f'run/cases/{case}/attempts/{attempt}/outputs/figure.pdf';p=OLD/f'w4-modern-architecture/figures/{case}/figure.pdf'
    copies.append({'public_path':str(p.relative_to(ROOT)),'archive_path':n,'sha256':sha(p.read_bytes()),'same':p.read_bytes()==z.read(n)})
n='writer-run/cases/modern-architecture-writing-handoff/attempts/0001/outputs/manuscript.pdf';p=OLD/'w4-modern-architecture/modern-architecture-comparison.pdf'
copies.append({'public_path':str(p.relative_to(ROOT)),'archive_path':n,'sha256':sha(p.read_bytes()),'same':p.read_bytes()==z.read(n)})
result['public_pdf_copies']=copies

binding=readjson(OLD/'final-candidate-source-binding.json')
result['previous_final_binding']={'candidate':binding['candidate'],'count':len(binding['files']),
    'changed':[dict(x,current_sha256=sha((ROOT/x['path']).read_bytes()) if (ROOT/x['path']).exists() else None) for x in binding['files'] if not (ROOT/x['path']).exists() or sha((ROOT/x['path']).read_bytes())!=x['sha256']]}
ledger=readjson(ROOT/'docs/continuous_optimization/papers.json'); entries=ledger['papers'] if isinstance(ledger,dict) else ledger
current=[p for p in entries if p.get('notes','').startswith('rounds/2026-10-07-revision-handoff/')]
paper_audit=[]
for p in current:
    note=ROOT/'docs/continuous_optimization'/p['notes']
    rr=ROOT/'docs/continuous_optimization'/p['reading_record'] if p.get('reading_record') else None
    paper_audit.append({'id':p['id'],'dedup_key':p.get('dedup_key'),'version':p.get('version'),'title':p.get('title'),
        'notes':p['notes'],'note_exists':note.is_file(),'note_sha256':sha(note.read_bytes()) if note.is_file() else None,
        'required_identity_scope_fields_present':all(p.get(k) for k in ('id','title','authors','version','version_date','full_text','read_at','read_scope','not_read','notes','candidate_ids')),
        'read_scope':p.get('read_scope'),'not_read':p.get('not_read'),'reading_record':p.get('reading_record'),
        'reading_record_exists':rr.is_file() if rr else None,'reading_record_sha256':sha(rr.read_bytes()) if rr and rr.is_file() else None,
        'ledger_dedup_occurrences':sum(x.get('dedup_key')==p.get('dedup_key') for x in entries)})
result['papers_audit']={'count':len(current),'entries':paper_audit,'scope':'Audit of recorded reads and completeness only; no originals downloaded or read in this audit.'}
(OUT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'output':str(OUT/'audit.json'),'candidate':result['candidate_hash_checks'],
    'archives':result['archive_integrity'],'writing_index':result['writing']['indexed_files'],
    'collections':{k:[{'path':x['path'],'count':x['output_count'],'missing':len(x['missing']),'mismatch':len(x['mismatches'])} for x in result[k]['collections']] for k in ('writing','modern')},
    'selected_dependency_changes':{k:[x['path'] for m in result[k]['manifests'].values() for x in m['selected_dependencies'] if not x['same']] for k in ('writing','modern')},'papers':len(current)},indent=2))
