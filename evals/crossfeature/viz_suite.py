"""Bounded synthetic figure evaluation; no host-model success is inferred.

Run: python evals/crossfeature/viz_suite.py --output /tmp/crossfeature-viz
The semantic audit uses instrumented Matplotlib state, not general image recognition.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.data_visualization_checks import validate_pdf_exports


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cases():
    return [
        ('v01', 'development', [], 17, False),
        ('v02', 'development', ['scale'], 19, False),
        ('v03', 'development', ['unit'], 23, False),
        ('v04', 'development', ['uncertainty'], 29, False),
        ('v05', 'development', ['protocol'], 31, False),
        ('v06', 'development', ['palette'], 37, False),
        ('v07', 'development', ['pdf_glyphs'], 41, True),
        ('v08', 'development', [], 43, False),
        ('v09', 'development', [], 47, True),
        ('v10', 'holdout', [], 101, False),
        ('v11', 'holdout', ['unit', 'protocol', 'palette'], 107, False),
        ('v12', 'holdout', ['pdf_glyphs'], 113, True),
    ]


def build(folder, case):
    import matplotlib
    matplotlib.use('Agg')
    matplotlib.rcParams['pdf.fonttype'] = 3
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    import numpy as np
    import fitz
    cid, split, defects, seed, chinese = case
    folder.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    samples = rng.normal([12, 16], [1, 1.5], (7, 2))
    mean = samples.mean(axis=0)
    sem = samples.std(axis=0, ddof=1) / math.sqrt(len(samples))
    colors = ['#0072b2', '#d55e00']
    source = {'samples_ms': samples.tolist(), 'unit': 'ms', 'colors': colors,
              'protocol': [{'batch': 8, 'warmup': 10}, {'batch': 8, 'warmup': 10}],
              'label': '耗时' if chinese else 'Latency', 'n': len(samples)}
    (folder / 'source.json').write_text(json.dumps(source, ensure_ascii=False, indent=2))
    protocol = [dict(x) for x in source['protocol']]
    if 'protocol' in defects: protocol[1]['batch'] = 32
    (folder / 'run_records.json').write_text(json.dumps({
        'kind': 'synthetic_fixture_run_metadata_not_benchmark_execution',
        'methods': [{'method': name, 'protocol': value} for name, value in zip(['A', 'B'], protocol)]}, indent=2))
    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    if chinese and not Path(font_path).exists():
        raise RuntimeError('Chinese font unavailable: cannot claim Chinese render evaluation')
    font = FontProperties(fname=font_path) if chinese else None
    vals = mean / 1000 if 'unit' in defects else mean
    errors = samples.std(axis=0, ddof=1) if 'uncertainty' in defects else sem
    actual_colors = colors[::-1] if 'palette' in defects else colors
    bar = ax.bar([0, 1], vals, color=actual_colors)
    err = ax.errorbar([0, 1], vals, yerr=errors, fmt='none', color='black', capsize=3)
    ax.set_xticks([0, 1], ['A', 'B'])
    ylabel = ax.set_ylabel(source['label'] + ' (ms)', fontproperties=font)
    ax.legend(bar, ['A', 'B'])
    ax.set_title('Synthetic; SEM; n=7')
    if 'scale' in defects:
        ax.set_ylim(float(min(vals) * .8), float(max(vals) * 1.2))
    if cid == 'v08':
        # A log-scale point plot has no encoded bar length; legitimate boundary.
        for patch in bar: patch.remove()
        ax.set_yscale('log')
        points = [ax.plot([i], [value], 'o', color=color)[0]
                  for i, (value, color) in enumerate(zip(vals, actual_colors))]
        ax.legend(points, ['A', 'B'])
    fig.tight_layout()
    fig.savefig(folder / 'figure.png')
    # Independent reference export at the PNG-good stage; rasterize with the same
    # engine to isolate export corruption from cross-renderer antialiasing.
    fig.savefig(folder / 'png_stage_reference.pdf')
    with fitz.open(folder / 'png_stage_reference.pdf') as reference:
        reference[0].get_pixmap(matrix=fitz.Matrix(100 / 72, 100 / 72)).save(
            str(folder / 'png_stage_reference_render.png'))
    observed = {'values': [float(x.get_ydata()[0]) for x in points] if cid == 'v08' else [float(x.get_height()) for x in bar], 'scale': ax.get_yscale(),
                'kind': 'point' if cid == 'v08' else 'bar', 'ylim': list(ax.get_ylim()),
                'ylabel': ax.get_ylabel(), 'title': ax.get_title(), 'protocol': protocol,
                'colors': [list(matplotlib.colors.to_rgb(x.get_color())) for x in points] if cid == 'v08' else [list(x.get_facecolor()[:3]) for x in bar],
                'legend_colors': [list(matplotlib.colors.to_rgb(x.get_color())) if cid == 'v08' else list(x.get_facecolor()[:3]) for x in ax.get_legend().legend_handles],
                'errors': [float((s[1, 1] - s[0, 1]) / 2) for s in err.lines[2][0].get_segments()]}
    if 'pdf_glyphs' in defects:
        # Export-only corruption: PNG remains correct; actual PDF loses the label.
        ylabel.set_text('□□ (ms)')
    fig.savefig(folder / 'figure.pdf')
    plt.close(fig)
    with fitz.open(folder / 'figure.pdf') as pdf:
        page = pdf[0]
        page.get_pixmap(matrix=fitz.Matrix(100 / 72, 100 / 72)).save(str(folder / 'pdf_render.png'))
        observed['pdf_text'] = page.get_text()
    (folder / 'observed.json').write_text(json.dumps(observed, ensure_ascii=False, indent=2))
    return source, observed


def audit(folder):
    import numpy as np
    from matplotlib.colors import to_rgb
    from PIL import Image
    source = json.loads((folder / 'source.json').read_text())
    actual = json.loads((folder / 'observed.json').read_text())
    samples = np.asarray(source['samples_ms'])
    import fitz
    # Reopen and rasterize current PDF on every audit; cached observations cannot certify it.
    with fitz.open(folder / 'figure.pdf') as pdf:
        actual['pdf_text'] = pdf[0].get_text()
        pdf[0].get_pixmap(matrix=fitz.Matrix(100 / 72, 100 / 72)).save(str(folder / 'pdf_render.png'))
    reasons = {}
    if actual['kind'] == 'bar' and actual['ylim'][0] > 0:
        reasons['scale'] = 'Observed bar baseline clips zero: ' + str(actual['ylim'])
    if '(ms)' not in actual['ylabel'] or not np.allclose(actual['values'], samples.mean(axis=0)):
        reasons['unit'] = 'Observed artist heights disagree with source mean in milliseconds'
    expected_sem = samples.std(axis=0, ddof=1) / math.sqrt(len(samples))
    if not np.allclose(actual['errors'], expected_sem) or 'SEM; n=7' not in actual['title']:
        reasons['uncertainty'] = 'Observed error-bar segments disagree with source SEM or caption'
    run_records = json.loads((folder / 'run_records.json').read_text())
    protocols = [row['protocol'] for row in run_records['methods']]
    if protocols[0] != protocols[1]:
        reasons['protocol'] = 'Actual comparison uses incompatible batch/warmup protocols'
    intended = [to_rgb(c) for c in source['colors']]
    if not np.allclose(actual['colors'], intended) or not np.allclose(actual['legend_colors'], intended):
        reasons['palette'] = 'Observed artist/legend method colors differ from specified mapping'
    png = np.asarray(Image.open(folder / 'figure.png').convert('RGB'), dtype=float)
    pdf = np.asarray(Image.open(folder / 'pdf_render.png').convert('RGB'), dtype=float)
    # Actual render crop is the y-label region. Text extraction is complementary,
    # not substituted for pixel comparison. AA differences tolerated by threshold.
    mae = float(np.abs(png[:, :45] - pdf[:, :45]).mean())
    reference = np.asarray(Image.open(folder / 'png_stage_reference_render.png').convert('RGB'), dtype=float)
    export_pixel_mae = float(np.abs(reference[:, :45] - pdf[:, :45]).mean())
    missing_label = source['label'] not in actual['pdf_text']
    if export_pixel_mae > 0.5:
        reasons['pdf_glyphs'] = f'Actual PDF label missing={missing_label}; export-only label-strip pixel MAE={export_pixel_mae:.3f}'
    return reasons, {'label_strip_mae': mae, 'export_only_pixel_mae': export_pixel_mae, 'pdf_label_missing': missing_label,
                     'png_pixel_sha256': digest(folder / 'figure.png'),
                     'pdf_render_sha256': digest(folder / 'pdf_render.png')}


def declared_pdf_control(folder):
    # Existing production validator consumes declarations; deliberate lying report
    # documents its trust boundary rather than claiming semantic detection.
    receipt = {'path': str(folder / 'figure.pdf'), 'sha256': digest(folder / 'figure.pdf')}
    errors = []
    entry = {k: receipt for k in ('export', 'rendered_pixels', 'read_receipt', 'font_report')}
    entry.update(chart_id='chart', format='pdf', reviewed_sha256=receipt['sha256'],
                 pixel_read=True, glyph_check='pass', font_check='pass')
    def run(item):
        errors.clear()
        validate_pdf_exports({'data_export_qa': [item]}, {'data_visual_design': {'charts': [{'id': 'chart'}]}},
                             lambda ok, why: errors.append(why) if not ok else None,
                             lambda value: isinstance(value, str) and bool(value),
                             lambda value: isinstance(value, dict) and Path(value.get('path', '')).is_file()
                             and digest(value['path']) == value.get('sha256'))
        return list(errors)
    accepted = not run(entry)
    bad = dict(entry, format='png')
    return {'self_reported_pass_accepted': accepted, 'png_proxy_rejection': run(bad),
            'scope': 'Existing validator checks declarations, not PDF pixels or semantic correctness'}


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for case in cases():
        cid, split, expected, seed, chinese = case
        folder = output / cid
        build(folder, case)
        reasons, render = audit(folder)
        found = set(reasons)
        records.append({'id': cid, 'split': split, 'expected': expected, 'actual': sorted(found),
                        'reasons': reasons, 'false_positive': sorted(found - set(expected)),
                        'false_negative': sorted(set(expected) - found), 'render': render,
                        'production_declaration_control': declared_pdf_control(folder),
                        'input_sha256': digest(folder / 'source.json'),
                        'output_sha256': digest(folder / 'observed.json'),
                        'artifacts': {p.name: digest(p) for p in sorted(folder.iterdir()) if p.is_file()}})
    result = {'rubric_sha256': digest(Path(__file__).with_name('viz_rubric.json')),
              'execution': 'actual_program_instrumented_figures', 'host_model': 'not_run',
              'cases': records, 'limitations': [
                  'Semantic detection uses live artist state and source metadata, not arbitrary image OCR.',
                  'PDF pixels are compared to a same-renderer reference exported at the PNG stage; Chinese text extraction is complementary.',
                  'Existing production declaration validator accepts truthful and falsified pass declarations.',
                  'Holdout changes seeds and combinations, not defect mechanisms; no generalization claim from 12 deterministic synthetic cases.']}
    (output / 'outcomes.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    errors = sum(bool(x['false_positive'] or x['false_negative']) for x in result['cases'])
    print(json.dumps({'cases': len(result['cases']), 'mismatches': errors, 'host_model': 'not_run'}))
    raise SystemExit(bool(errors))
