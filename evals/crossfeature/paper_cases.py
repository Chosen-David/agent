"""Build generic paper controls. Reuses legacy declaration fixture, never model output.

All role receipts and publication metadata are *synthetic test data*. Host testing
must start real roles separately and must not reuse these receipts as provenance.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SECTIONS = [
    ('Abstract', 'We study whether indexing a two-coordinate view preserves full-width returned values. On two synthetic rows, selecting by the final two coordinates returns row 2 with all four coordinates. This is a mechanism demonstration, not a performance claim.'),
    ('Introduction', 'An index may score fewer coordinates without changing the representation consumed downstream. Confusing these stages produces incorrect architecture descriptions. Our contribution is an executable separation of selection and value consumption.'),
    ('Related work', 'The ten supplied synthetic examples illustrate comparison layouts only. They are generated test material, not published scientific sources. No external novelty or superiority is claimed.'),
    ('Method', 'Convert rows to float32, score each row by its last two coordinates, select the first maximum, then return the original converted row. The optional projection uses a different score and does not change final width.'),
    ('Evaluation', 'Input rows are [9,1,0,1] and [1,2,3,4]. Scores are 1 and 7. The selected value is [1,2,3,4]. Figure 1 shows the two scores. Exact deterministic outputs are supplied; no sampling uncertainty or speedup is asserted.'),
    ('Limitations', 'Only synthetic width-four arrays and one two-row example are covered. No accuracy, latency, production tensor-library behavior, or generalization result follows. Empty or malformed rows are rejected.'),
    ('Conclusion', 'In this bounded executable example, reduced score width and full returned width coexist. Trace the consumer before labeling an entire algorithm reduced-width.')]
AUDIT = '\n\n'.join('# '+title+'\nRepository files were inspected. The manifest has three files. Checksum mismatches were logged. This section lists audit statuses and no research question, method, or experiment.' for title, _ in SECTIONS)


def pdf(pages):
    """A small real ASCII PDF writer; no third-party test dependencies."""
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'', b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    kids = []
    import textwrap
    for page in pages:
        page_id = len(objects) + 1
        stream_id = page_id + 1
        kids.append(f'{page_id} 0 R')
        objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {stream_id} 0 R >>'.encode())
        lines = [line for block in page.splitlines() for line in textwrap.wrap(block, 88)]
        escaped = [line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)') for line in lines]
        stream = ('BT /F1 10 Tf 48 744 Td 14 TL '+ ' '.join('('+line+') Tj T*' for line in escaped)+' ET').encode('ascii')
        objects.append(b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream')
    objects[1] = f'<< /Type /Pages /Count {len(kids)} /Kids [{" ".join(kids)}] >>'.encode()
    data = b'%PDF-1.4\n'; offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(data)); data += f'{index} 0 obj\n'.encode()+obj+b'\nendobj\n'
    xref = len(data)
    data += f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode()
    data += b''.join(f'{offset:010} 00000 n \n'.encode() for offset in offsets[1:])
    return data + f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()


def refresh(record, root):
    if isinstance(record, dict):
        if 'path' in record and 'sha256' in record:
            record['sha256'] = hashlib.sha256((root / record['path']).read_bytes()).hexdigest()
        for value in record.values(): refresh(value, root)
    elif isinstance(record, list):
        for value in record: refresh(value, root)


def build(root):
    root = Path(root); root.mkdir(parents=True, exist_ok=True)
    fixture = load(ROOT/'tests/test_paper_delivery.py', '_crossfeature_legacy_paper').PaperDeliveryTests()
    fixture.setUp()
    try:
        shutil.copytree(fixture.root, root, dirs_exist_ok=True)
        record = copy.deepcopy(fixture.good)
        record['requested_languages'] = ['en']
        record['versions'] = record['versions'][:1]
    finally:
        fixture.doCleanups()
    body = '\n\n'.join('# '+title+'\n'+text+('\n![Figure 1: deterministic scores](figure-1.svg)' if title == 'Evaluation' else '') for title,text in SECTIONS)
    (root/'manuscript.md').write_text(body+'\n')
    (root/'paper.pdf').write_bytes(pdf([title+'\n'+text for title,text in SECTIONS]))
    (root/'figure-1.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="120"><text x="5" y="15">Synthetic scores, linear units</text><rect x="20" y="90" width="40" height="10"/><rect x="100" y="30" width="40" height="70"/><text x="20" y="115">1</text><text x="100" y="115">7</text></svg>')
    (root/'receipt.json').write_text(json.dumps({'synthetic':True,'kind':'start','status':'fixture_only','note':'Never use as real host execution proof'}))
    for i in range(10):
        text = f'Synthetic exemplar {i}.\nAbstract: compare deterministic offsets.\nMethod: add {i} to inputs zero and one.\nResults: outputs {i} and {i+1}.\nLimitations: two constructed inputs only.'
        (root/f'exemplar-{i}.md').write_text(text+'\nFigure 1: two bars. Table 1: the two exact outputs.\n')
        (root/f'exemplar-{i}.pdf').write_bytes(pdf([text, f'Figure 1: two bars with heights {i} and {i+1}. Table 1: input 0 output {i}; input 1 output {i+1}.']))
    refresh(record, root)
    for version in record['versions']:
        for field in ('reader_snapshot_sha256', 'reviewer_snapshot_sha256'):
            version[field] = version['snapshot']['sha256']
    cases = {}
    names = json.loads((Path(__file__).parent/'paper_rubric.json').read_text())['cases']
    for name in names:
        path = root/'cases'/name; path.mkdir(parents=True, exist_ok=True)
        r = copy.deepcopy(record)
        content = body
        if name == 'audit_declared': r['delivered_artifact']='technical_audit'; content=AUDIT
        if name == 'audit_disguised': content=AUDIT
        if name == 'abstracts_only':
            for paper in r['exemplar_learning']['papers']: paper['access']='abstract_only'
        if name == 'missing_figure_coverage': r['exemplar_learning']['papers'][0]['figures_read']=['Table1']
        if name == 'copied_body': content=(root/'exemplar-3.md').read_text()
        if name == 'role_not_started':
            r['bindings'][1]={'role':'research-write','state':'not_run','reason':'No worker dispatch occurred'}
        if name == 'dispatch_as_start':
            (path/'dispatch.json').write_text(json.dumps({'synthetic':True,'kind':'dispatch','status':'queued'}))
            r['bindings'][1]['start_receipt']={'path':str((path/'dispatch.json').relative_to(root)), 'sha256':hashlib.sha256((path/'dispatch.json').read_bytes()).hexdigest()}
        if name == 'holdout_attributed_quote': content += '\n\nAttributed short quotation from synthetic exemplar 3: "two constructed inputs only." This describes that exemplar, not our evidence.\n'
        (path/'manuscript.md').write_text(content)
        (path/'paper.pdf').write_bytes(pdf(content.split('\n\n')))
        snapshot={'path':str((path/'paper.pdf').relative_to(root)),'sha256':hashlib.sha256((path/'paper.pdf').read_bytes()).hexdigest()}
        for version in r['versions']:
            version['page_count'] = len(content.split('\n\n'))
            version['read_pages'] = list(range(1, version['page_count'] + 1))
            version['snapshot']=copy.deepcopy(snapshot)
            version['reader_snapshot_sha256']=snapshot['sha256']
            version['reviewer_snapshot_sha256']=snapshot['sha256']
        if name == 'holdout_stale_snapshot': r['versions'][0]['reader_snapshot_sha256']='0'*64
        (path/'record.json').write_text(json.dumps(r,indent=2)+'\n')
        cases[name] = r
    blind = root/'blind'
    blind.mkdir(exist_ok=True)
    for filename, case in {'item-a.md':'good_control', 'item-b.md':'copied_body', 'item-c.md':'holdout_attributed_quote', 'item-d.md':'audit_disguised'}.items():
        shutil.copyfile(root/'cases'/case/'manuscript.md', blind/filename)
    shutil.copyfile(root/'exemplar-3.md', blind/'reference.md')
    shutil.copyfile(root/'figure-1.svg', blind/'figure-1.svg')
    (blind/'learning.json').write_text(json.dumps({'synthetic':True,'scope':'Constructed learning records; no real publication or model execution is attested', 'exemplar_learning':record['exemplar_learning']},indent=2)+'\n')
    for filename, case in {'learning-1.json':'good_control', 'learning-2.json':'abstracts_only', 'learning-3.json':'missing_figure_coverage'}.items():
        (blind/filename).write_text(json.dumps({'synthetic':True, 'scope':'Protocol simulation only; no real publication or role execution attested', 'exemplar_learning':cases[case]['exemplar_learning']},indent=2)+'\n')
    for i in range(10):
        for suffix in ('md','pdf'):
            shutil.copyfile(root/f'exemplar-{i}.{suffix}', blind/f'exemplar-{i}.{suffix}')
    shutil.copyfile(root/'receipt.json', blind/'receipt.json')
    shutil.copyfile(root/'cases'/'dispatch_as_start'/'dispatch.json', blind/'event.json')
    return cases


def evaluate(root):
    root = Path(root)
    cases = build(root)
    validator = load(ROOT/'scripts/validate_paper_delivery.py', '_crossfeature_validator')
    expected = json.loads((Path(__file__).parent/'paper_rubric.json').read_text())['cases']
    outcomes = []
    for name, record in cases.items():
        errors = validator.validate(record, root)
        actual = 'reject' if errors else 'accept'
        manuscript = root/'cases'/name/'manuscript.md'
        outcomes.append(dict(case_id=name, layer='program_declaration_control', expected=expected[name], actual=actual,
            classification=('correct' if actual==expected[name] else 'false_negative' if actual=='accept' else 'false_positive'),
            errors=errors, artifact_sha256=hashlib.sha256(manuscript.read_bytes()).hexdigest(),
            reason='Validator validates declarations/hash integrity, not manuscript genre, copying, or receipt event semantics.',
            model_execution='not_run'))
    return outcomes


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--out', type=Path, required=True)
    args=parser.parse_args()
    result=evaluate(args.out)
    (args.out/'program_outcomes.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
