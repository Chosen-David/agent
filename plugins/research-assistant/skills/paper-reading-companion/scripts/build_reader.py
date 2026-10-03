#!/usr/bin/env python3
"""Build an offline, original-page + notes reader. No model/network backend."""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path


def parse_pages(spec, total):
    if not spec:
        return list(range(1, min(total, 20) + 1))
    chosen = set()
    for item in spec.split(','):
        ends = item.strip().split('-')
        if len(ends) > 2:
            raise ValueError('Use page numbers or ranges, for example 1-3,7')
        lo, hi = int(ends[0]), int(ends[-1])
        if lo < 1 or hi < lo or hi > total:
            raise ValueError(f'Page range must be within 1..{total}')
        chosen.update(range(lo, hi + 1))
    return sorted(chosen)


def load_cards(path, digest, total):
    if not path:
        return []
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict) or value.get('paper_sha256') != digest:
        raise ValueError('Notes must match this PDF SHA-256')
    cards = value.get('cards', [])
    if not isinstance(cards, list):
        raise ValueError('cards must be an array')
    ids = set()
    for card in cards:
        if not isinstance(card, dict) or type(card.get('page')) is not int or not 1 <= card['page'] <= total:
            raise ValueError('Every card needs a valid physical page')
        for key in ('id', 'anchor', 'question', 'answer'):
            if not isinstance(card.get(key), str):
                raise ValueError(f'Card {key} must be text')
        if not card['id'] or card['id'] in ids:
            raise ValueError('Card IDs must be nonempty and unique')
        ids.add(card['id'])
        if not isinstance(card.get('sources', []), list):
            raise ValueError('sources must be an array')
        for source in card.get('sources', []):
            if not isinstance(source, dict) or not isinstance(source.get('label'), str) or not isinstance(source.get('url'), str):
                raise ValueError('Every source needs label and url strings')
    return cards


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--pages', help='Physical pages, e.g. 1-3,7; defaults to first 20')
    parser.add_argument('--notes', type=Path)
    parser.add_argument('--dpi', type=int, default=120)
    args = parser.parse_args()
    if not 72 <= args.dpi <= 200:
        parser.error('--dpi must be between 72 and 200')
    if args.out.resolve() in {args.pdf.resolve(), args.notes.resolve() if args.notes else None}:
        parser.error('Output must not overwrite the PDF or notes')
    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz
        except ImportError:
            parser.error('Install PyMuPDF in your project environment: python -m pip install pymupdf')
    digest = hashlib.sha256(args.pdf.read_bytes()).hexdigest()
    try:
        with fitz.open(args.pdf) as doc:
            if doc.needs_pass:
                raise ValueError('Password-protected PDF: provide an authorized decrypted copy')
            if not doc.page_count:
                raise ValueError('PDF contains no pages')
            chosen = parse_pages(args.pages, doc.page_count)
            cards = load_cards(args.notes, digest, doc.page_count)
            pages = []
            for number in chosen:
                page = doc[number - 1]
                pix = page.get_pixmap(dpi=args.dpi, alpha=False, colorspace=fitz.csRGB)
                pages.append({'number': number, 'label': page.get_label(),
                              'image': base64.b64encode(pix.tobytes('png')).decode('ascii'),
                              'text': page.get_text(sort=True)})
            data = {'title': doc.metadata.get('title') or args.pdf.name, 'sha256': digest,
                    'total_pages': doc.page_count, 'pages': pages, 'cards': cards}
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    # Keep arbitrary PDF/notes text inert even inside the JSON script element.
    encoded = json.dumps(data, ensure_ascii=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    template = (Path(__file__).resolve().parent.parent / 'assets/reader.html').read_text(encoding='utf-8')
    output = template.replace('__DOCUMENT_TITLE__', html.escape(data['title'])).replace('__READER_DATA__', encoded)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(output, encoding='utf-8')
    print(json.dumps({'output': str(args.out), 'paper_sha256': digest, 'rendered_pages': chosen,
                      'total_pages': data['total_pages'], 'ai_read_coverage': 'not_assessed',
                      'live_chat_backend': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
