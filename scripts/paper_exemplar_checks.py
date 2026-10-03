"""Structural checks only: receipts and semantic observations require human review."""

DIMENSIONS = ('organization', 'claim_evidence', 'figures', 'rhetoric', 'content')


def validate_learning(record, need, text, file_ok):
    architecture = record.get('architecture_requested')
    need(type(architecture) is bool, 'architecture_requested must be explicit')
    started = record.get('drafting_started')
    need(type(started) is bool, 'drafting_started must be explicit')
    learning = record.get('exemplar_learning')
    if not isinstance(learning, dict):
        need(False, 'missing exemplar_learning preflight')
        return
    complete = record.get('status') == 'submission_checks_complete'
    state = learning.get('state')
    need(state in ('completed', 'not_run', 'blocked'), 'invalid exemplar learning state')
    if state != 'completed':
        need(not started and not complete, 'exemplar learning must precede drafting/completion')
        need(text(learning.get('reason')), 'exemplar learning blocker reason required')
        return
    template = learning.get('template')
    template = template if isinstance(template, dict) else {}
    need(template.get('verified') is True and all(text(template.get(k)) for k in
         ('venue', 'year', 'track', 'source_url', 'checked_at')) and file_ok(template.get('evidence')),
         'template verification required before drafting')
    need(type(template.get('provisional')) is bool, 'template provisional status required')
    if complete:
        need(template.get('provisional') is False, 'provisional template cannot certify submission')
    skills = learning.get('skills')
    need(isinstance(skills, dict) and file_ok(skills.get('selection_notes')), 'skill selection evidence required')
    for name in ('synthesis', 'blueprint', 'preflight_receipt'):
        need(file_ok(learning.get(name)), f'exemplar {name} evidence required')
    need(learning.get('completed_before_drafting') is True, 'learning completed too late for this drafting run')
    papers = learning.get('papers')
    papers = papers if isinstance(papers, list) else []
    need(len(papers) == 10, 'exactly 10 distinct fully read published exemplars required')
    identities, hashes = set(), set()
    for i, paper in enumerate(papers):
        label = f'exemplar {i + 1}'
        if not isinstance(paper, dict):
            need(False, f'{label}: invalid paper'); continue
        identity = paper.get('identity')
        need(text(identity) and identity not in identities, f'{label}: duplicate/missing identity')
        if text(identity):
            identities.add(identity)
        need(all(text(paper.get(k)) for k in ('title', 'venue', 'year', 'publication_url',
             'selection_reason', 'quality_reason')), f'{label}: publication/selection evidence required')
        need(paper.get('published') is True and paper.get('access') == 'full_text',
             f'{label}: abstract/access-blocked/unpublished cannot count as read')
        pdf = paper.get('pdf')
        need(file_ok(pdf), f'{label}: original PDF/hash required')
        digest = pdf.get('sha256') if isinstance(pdf, dict) else None
        need(text(digest) and digest not in hashes, f'{label}: duplicate/missing PDF')
        if text(digest):
            hashes.add(digest)
        count, pages = paper.get('page_count'), paper.get('read_pages')
        need(type(count) is int and count > 0 and isinstance(pages, list) and
             all(type(p) is int for p in pages) and sorted(pages) == list(range(1, count + 1)),
             f'{label}: incomplete full-text page coverage')
        inventory, read = paper.get('figure_inventory'), paper.get('figures_read')
        valid = (isinstance(inventory, list) and isinstance(read, list) and
                 all(text(x) for x in inventory + read))
        need(valid and len(set(inventory)) == len(inventory) and
             len(set(read)) == len(read) and set(inventory) == set(read),
             f'{label}: incomplete figure/table coverage')
        if inventory == []:
            need(text(paper.get('absence_reason')), f'{label}: no-figure claim requires full-page justification')
        for name in ('read_receipt', 'notes'):
            need(file_ok(paper.get(name)), f'{label}: {name} required')
        analysis = paper.get('analysis')
        analysis = analysis if isinstance(analysis, dict) else {}
        for dimension in DIMENSIONS:
            item = analysis.get(dimension)
            need(isinstance(item, dict) and all(text(item.get(k)) for k in
                 ('location', 'observation', 'transfer')), f'{label}: missing {dimension} analysis')
    decisions = learning.get('decisions')
    decisions = decisions if isinstance(decisions, list) else []
    dimensions = set()
    for item in decisions:
        if not isinstance(item, dict):
            need(False, 'invalid blueprint decision'); continue
        dimension = item.get('dimension')
        need(dimension in DIMENSIONS, 'invalid blueprint dimension')
        if isinstance(dimension, str):
            dimensions.add(dimension)
        refs = item.get('source_ids')
        need(isinstance(refs, list) and bool(refs) and all(text(x) and x in identities for x in refs),
             'blueprint source IDs must resolve to read exemplars')
        need(item.get('decision') in ('adopt', 'adapt', 'reject') and all(text(item.get(k)) for k in
             ('source_locations', 'rationale', 'target_location', 'own_evidence')), 'blueprint needs concrete transfer decisions')
        need(not text(item.get('own_evidence')) or item['own_evidence'] not in identities,
             'exemplar identity cannot replace own scientific evidence')
    need(set(DIMENSIONS) <= dimensions, 'blueprint must cover all five learning dimensions')
    if architecture:
        visual = learning.get('visual_design')
        visual = visual if isinstance(visual, dict) else {}
        for name in ('brief', 'reader_receipt', 'diagram_role_receipt', 'selection_evidence'):
            need(file_ok(visual.get(name)), f'visual design {name} required')
        mode = visual.get('mode')
        need(mode in ('independent', 'staged'), 'visual collaboration mode required')
        need(text(visual.get('reader_actor')) and text(visual.get('diagram_actor')),
             'actual reader/diagram role identities required')
        if mode == 'independent':
            need(visual.get('reader_actor') != visual.get('diagram_actor'),
                 'actual reader/diagram role collaboration required')
        else:
            need(not complete and text(visual.get('reason')),
                 'staged visual design needs reason and cannot certify completion')
        figures = visual.get('source_figures')
        figures = figures if isinstance(figures, list) else []
        need(bool(figures), 'architecture source pixel reading required')
        for f in figures:
            if not isinstance(f, dict):
                need(False, 'invalid architecture source figure'); continue
            source = next((p for p in papers if isinstance(p, dict) and p.get('identity') == f.get('identity')), {})
            inventory = source.get('figure_inventory')
            pages = source.get('read_pages')
            need(bool(source) and text(f.get('figure_id')) and
                 isinstance(inventory, list) and f['figure_id'] in inventory and
                 type(f.get('page')) is int and isinstance(pages, list) and f['page'] in pages and
                 f.get('pixel_read') is True and file_ok(f.get('receipt')), 'architecture figure pixel coverage invalid')
        analysis = visual.get('analysis')
        analysis = analysis if isinstance(analysis, dict) else {}
        for d in ('focus', 'hierarchy', 'abstraction', 'layout_flow', 'color_semantics', 'type_whitespace', 'panels'):
            item = analysis.get(d)
            need(isinstance(item, dict) and all(text(item.get(k)) for k in
                 ('source_location', 'observation', 'design_choice')), f'visual design needs concrete {d} analysis')
