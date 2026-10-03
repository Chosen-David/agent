"""Data-figure declarations only; original pixels, data and judgments need review."""

DIMENSIONS = ('comparison_chart', 'axes_baselines', 'uncertainty', 'encoding_accessibility',
              'palette_legend', 'typography', 'layout_density', 'panels')


def validate_data_design(record, learning, need, text, file_ok):
    requested = record.get('data_visualization_requested')
    need(type(requested) is bool, 'data_visualization_requested must be explicit')
    if not requested or learning.get('state') != 'completed':
        return
    complete = record.get('status') == 'submission_checks_complete'
    data = learning.get('data_visual_design')
    data = data if isinstance(data, dict) else {}
    for name in ('brief', 'reader_receipt', 'visualization_role_receipt', 'selection_evidence', 'skill_selection'):
        need(file_ok(data.get(name)), f'data visual {name} required')
    mode = data.get('mode')
    need(mode in ('independent', 'staged'), 'data visual collaboration mode required')
    need(text(data.get('reader_actor')) and text(data.get('visualization_actor')), 'data visual role identities required')
    if mode == 'independent':
        need(data.get('reader_actor') != data.get('visualization_actor'), 'data visual roles must be independent')
    else:
        need(not complete and text(data.get('reason')), 'staged data visual collaboration cannot certify completion')
    papers = learning.get('papers')
    papers = papers if isinstance(papers, list) else []
    figures = data.get('source_figures')
    figures = figures if isinstance(figures, list) else []
    need(bool(figures), 'data figure pixel reading required')
    for f in figures:
        if not isinstance(f, dict):
            need(False, 'invalid data source figure'); continue
        p = next((p for p in papers if isinstance(p, dict) and p.get('identity') == f.get('identity')), {})
        inventory, pages = p.get('figure_inventory'), p.get('read_pages')
        need(bool(p) and text(f.get('figure_id')) and isinstance(inventory, list) and
             f['figure_id'] in inventory and type(f.get('page')) is int and isinstance(pages, list) and
             f['page'] in pages and f.get('pixel_read') is True and file_ok(f.get('receipt')),
             'data source pixel coverage invalid')
    analysis = data.get('analysis')
    analysis = analysis if isinstance(analysis, dict) else {}
    for d in DIMENSIONS:
        item = analysis.get(d)
        need(isinstance(item, dict) and all(text(item.get(k)) for k in
             ('source_location', 'observation', 'design_choice')), f'data visual needs concrete {d} analysis')
    charts = data.get('charts')
    charts = charts if isinstance(charts, list) else []
    need(bool(charts), 'data chart provenance required')
    ids = set()
    for chart in charts:
        if not isinstance(chart, dict):
            need(False, 'invalid chart'); continue
        cid = chart.get('id')
        need(text(cid) and cid not in ids, 'missing/duplicate chart id')
        if text(cid):
            ids.add(cid)
        kind = chart.get('source_kind')
        need(kind in ('measured', 'simulated', 'theoretical', 'reported', 'synthetic', 'placeholder'),
             'chart source kind required')
        need(chart.get('presented_as') == kind, 'chart evidence type misrepresented')
        need(not complete or kind != 'placeholder', 'placeholder cannot be final result chart')
        for field in ('source', 'exclusions'):
            need(file_ok(chart.get(field)), f'chart {field} evidence required')
        need(all(text(chart.get(k)) for k in ('chart_type', 'scale', 'baseline')), 'chart scale/baseline required')
        if chart.get('chart_type') == 'bar':
            need(chart.get('baseline') == 'zero', 'bar length baseline must be zero')
        u = chart.get('uncertainty')
        u = u if isinstance(u, dict) else {}
        need(type(u.get('available')) is bool and type(u.get('shown')) is bool and text(u.get('definition')),
             'uncertainty availability and definition required')
        if u.get('shown'):
            need(u.get('available') is True and file_ok(u.get('evidence')) and
                 text(u.get('sample_size')) and text(u.get('sampling_unit')),
                 'uncertainty cannot be invented without source/replication definition')
        claim = chart.get('comparison_claim')
        need(claim in ('descriptive', 'superiority'), 'comparison claim scope required')
        if claim == 'superiority':
            need(file_ok(chart.get('statistical_review')), 'superiority needs reviewer statistical evidence')
            if kind in ('measured', 'reported', 'simulated'):
                need(u.get('available') is True and file_ok(u.get('evidence')),
                     'empirical superiority cannot follow from missing uncertainty')
