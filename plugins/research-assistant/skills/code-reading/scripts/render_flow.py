#!/usr/bin/env python3
"""Render a manually verified source-flow manifest as offline HTML and SVG."""
import argparse
import html
import json
import os
from pathlib import Path
import re

KINDS = {'source_fact': '源码事实', 'static_inference': '静态推断', 'unknown': '尚未验证'}


def text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('nonempty text required')
    if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]', value):
        raise ValueError('text contains characters forbidden in XML')
    return html.escape(value, quote=True)


def evidence(items):
    if not isinstance(items, list) or not items:
        raise ValueError('each node and edge requires source evidence')
    parts = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError('evidence must be an object')
        if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', item.get('commit', '')):
            raise ValueError('evidence needs immutable commit')
        lo, hi = item.get('start_line'), item.get('end_line')
        if type(lo) is not int or type(hi) is not int or not 1 <= lo <= hi:
            raise ValueError('invalid source line range')
        parts.append(f'<li><code>{text(item["path"])}:{lo}–{hi}</code> · '
                     f'{text(item["symbol"])}<br><small>{item["commit"]}</small></li>')
    return '<ul>' + ''.join(parts) + '</ul>'


def render(graph):
    title = text(graph['title'])
    nodes, edges = graph['nodes'], graph['edges']
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= 40:
        raise ValueError('use 1–40 nodes; split larger views')
    if not isinstance(edges, list) or len(edges) > 100:
        raise ValueError('use at most 100 edges')
    ids = [n['id'] for n in nodes]
    if any(not isinstance(i, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', i) for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('node IDs must be unique simple identifiers')
    cards, shapes, paths = [], [], []
    for index, node in enumerate(nodes):
        kind = node['kind']
        if kind not in KINDS:
            raise ValueError('unsupported evidence kind; runtime claims require separate verification')
        label = text(node['label'])
        if len(node['label']) > 30:
            raise ValueError('node labels exceed 30 characters; put detail in disclosure')
        refs = evidence(node['evidence'])
        y = 32 + index * 120
        shapes.append(f'<a href="#node-{node["id"]}"><rect x="24" y="{y}" width="392" height="82" rx="14"/>'
                      f'<text x="44" y="{y+30}">{label}</text>'
                      f'<text class="meta" x="44" y="{y+57}">{KINDS[kind]} · {index+1:02}</text><desc>{html.escape(json.dumps(node["evidence"], ensure_ascii=False))}</desc></a>')
        cards.append(f'<details id="node-{node["id"]}"><summary>{index+1:02} · {label} '
                     f'<span>{KINDS[kind]}</span></summary><p>{text(node["detail"])}</p>{refs}</details>')
    edge_cards = []
    for index, edge in enumerate(edges):
        if edge['source'] not in ids or edge['target'] not in ids:
            raise ValueError('edge references missing node')
        if edge['kind'] not in KINDS:
            raise ValueError('unsupported edge kind')
        label, condition = text(edge['label']), text(edge['condition'])
        refs = evidence(edge['evidence'])
        a, b = ids.index(edge['source']), ids.index(edge['target'])
        y1, y2 = 73 + a*120, 73 + b*120
        lane = 440 + index*18
        paths.append(f'<g><title>E{index+1}: {label} · {KINDS[edge["kind"]]} · {condition}</title><desc>{html.escape(json.dumps(edge["evidence"], ensure_ascii=False))}</desc><path d="M416 {y1} H{lane} V{y2+12} H416" marker-end="url(#arrow)"/>'
                     f'<text class="meta" x="{lane+3}" y="{(y1+y2)//2+8}">E{index+1}</text></g>')
        edge_cards.append(f'<details><summary>E{index+1} · {text(edge["source"])} → {text(edge["target"])} '
                          f'<span>{KINDS[edge["kind"]]}</span></summary><p>{label}</p>'
                          f'<p>条件 / 数据约束：{condition}</p>{refs}</details>')
    width, height = max(560, 480+len(edges)*18), max(180, len(nodes)*120+40)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="flow-title">
<title id="flow-title">{title} — 节点及编号连线，详见下方证据</title>
<style>rect{{fill:#122d3c;stroke:#83cbb8}}text{{fill:#f0f6f5;font:18px sans-serif}}.meta{{fill:#a9c6c9;font:12px sans-serif}}path{{fill:none;stroke:#52bfa7;stroke-width:2}}</style>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" style="fill:#52bfa7"/></marker></defs>
{''.join(paths)}{''.join(shapes)}</svg>'''
    page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>
:root{{color-scheme:dark;font-family:Inter,"Noto Sans SC",system-ui,sans-serif;background:#091b26;color:#e8f1ef}}*{{box-sizing:border-box}}body{{margin:0}}main{{max-width:1180px;margin:auto;padding:clamp(20px,5vw,72px)}}header{{border-bottom:1px solid #33515c;padding-bottom:28px}}.eyebrow{{color:#83cbb8;letter-spacing:.16em;font-size:12px}}h1{{font-size:clamp(28px,5vw,52px);line-height:1.2;margin:18px 0}}p{{line-height:1.8;color:#b8cdd1}}.layout{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:32px;margin-top:32px}}section{{min-width:0}}svg{{width:100%;height:auto}}details{{border-top:1px solid #33515c;padding:18px 0;overflow-wrap:anywhere}}summary{{cursor:pointer;line-height:1.7}}summary span{{display:block;color:#83cbb8;font-size:12px}}small{{color:#a5bfc3}}li{{margin:14px 0;line-height:1.6}}a{{color:#91ddc6}}a:focus-visible,summary:focus-visible{{outline:3px solid #ffc778;outline-offset:4px}}@media(max-width:720px){{.layout{{grid-template-columns:1fr}}}}@media(prefers-reduced-motion:reduce){{*{{scroll-behavior:auto}}}}
</style><main><header><div class="eyebrow">SOURCE / FLOW / EVIDENCE</div><h1>{title}</h1><p>沿编号连线理解流程，展开查看条件与源码位置。源码事实、静态推断与尚未验证分别标注；此图不证明运行时执行。</p><a href="flow.svg" download>下载可编辑 SVG</a></header><div class="layout"><section aria-label="流程概览">{svg}</section><section aria-label="源码证据"><h2>节点与证据</h2>{''.join(cards)}<h2>数据与调用关系</h2>{''.join(edge_cards)}</section></div></main></html>'''
    return page, svg


def write_if_changed(path, content):
    raw = content.replace('\n', os.linesep).encode('utf-8')
    try:
        if path.read_bytes() == raw:
            return
    except OSError:
        pass
    path.write_bytes(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        page, svg = render(json.loads(args.manifest.read_text(encoding='utf-8')))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f'flow rejected: {exc}\n')
    args.out.mkdir(parents=True, exist_ok=True)
    write_if_changed(args.out / 'index.html', page)
    write_if_changed(args.out / 'flow.svg', svg)


if __name__ == '__main__':
    main()
