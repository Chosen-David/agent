import argparse
import base64
import binascii
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, unquote_to_bytes, urlsplit


VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
        'param', 'source', 'track', 'wbr'}


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.nodes = []
        self.stack = []
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attrs):
        node = dict(tag=tag, attrs=dict(attrs), text=[], parent=self.stack[-1] if self.stack else None)
        self.nodes.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.stack.pop()

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]['tag'] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        for node in self.stack:
            node['text'].append(data)


def text(node):
    return ''.join(node['text']).strip()


def validate(path, offline=False, with_video=False, paper_figures=False):
    path = path.resolve(strict=True)
    root = path.parent
    page = Page(path.read_text(encoding='utf-8'))
    nodes = page.nodes
    need(any(n['tag'] == 'html' and n['attrs'].get('lang') for n in nodes), 'document language missing')
    need(any(n['tag'] == 'title' and text(n) for n in nodes), 'document title missing')
    need(any(n['tag'] == 'meta' and (n['attrs'].get('name') or '').lower() == 'viewport'
             and 'width=device-width' in (n['attrs'].get('content') or '') for n in nodes), 'viewport missing')
    ids = {n['attrs']['id']: n for n in nodes if n['attrs'].get('id')}
    checked = set()

    def resource(raw, navigation=False):
        need(isinstance(raw, str) and raw.strip(), 'empty asset URL')
        raw = raw.strip()
        if (raw, navigation) in checked:
            return
        url = urlsplit(raw)
        if url.scheme == 'data':
            try:
                header, data = raw.split(',', 1)
                if ';base64' in header.lower():
                    decoded = base64.b64decode(data, validate=True)
                else:
                    decoded = unquote_to_bytes(data)
                need(bool(decoded), 'empty data URI')
            except (ValueError, binascii.Error) as exc:
                raise ValueError('invalid data URI') from exc
        elif url.scheme in ('http', 'https') or url.netloc:
            need(navigation or not offline, 'remote offline asset')
        elif url.scheme in ('mailto', 'tel') and navigation:
            pass
        else:
            need(not url.scheme, 'unsupported asset URL scheme')
            if not url.path:
                need(not url.fragment or unquote(url.fragment) in ids, 'missing anchor: ' + url.fragment)
            else:
                local = (root / unquote(url.path)).resolve()
                need(local.is_relative_to(root), 'asset outside delivery root')
                need(local.is_file(), 'missing local asset: ' + url.path)
                if local == path and url.fragment:
                    need(unquote(url.fragment) in ids, 'missing anchor: ' + url.fragment)
        checked.add((raw, navigation))

    for node in nodes:
        tag, attrs = node['tag'], node['attrs']
        if tag == 'button':
            need(text(node) or attrs.get('aria-label') or
                 text(ids.get(attrs.get('aria-labelledby'), {'text': []})), 'unlabelled button')
        if tag in ('input', 'select', 'textarea') and attrs.get('type') != 'hidden':
            named = attrs.get('aria-label') or text(ids.get(attrs.get('aria-labelledby'), {'text': []}))
            named = named or any(n['tag'] == 'label' and n['attrs'].get('for') == attrs.get('id')
                                 and attrs.get('id') and text(n) for n in nodes)
            ancestor = node['parent']
            while ancestor:
                named = named or (ancestor['tag'] == 'label' and text(ancestor))
                ancestor = ancestor['parent']
            need(named, 'unlabelled control')
        if tag == 'img':
            need('alt' in attrs, 'image alt missing')
        if tag in ('img', 'script', 'source', 'track', 'audio', 'video', 'iframe'):
            if 'src' in attrs:
                resource(attrs['src'])
        if tag == 'video' and 'poster' in attrs:
            resource(attrs['poster'])
        if tag == 'link' and set((attrs.get('rel') or '').split()) & {'stylesheet', 'icon', 'preload'}:
            resource(attrs.get('href'))
        if tag == 'a' and 'href' in attrs:
            resource(attrs['href'], navigation=True)
        css = text(node) if tag == 'style' else (attrs.get('style') or '')
        for match in re.finditer(r'url\(\s*[\'"]?(.*?)[\'"]?\s*\)', css, re.I):
            resource(match.group(1))
        for match in re.finditer(r'@import\s+[\'"]([^\'"]+)[\'"]', css, re.I):
            resource(match.group(1))
    videos = [n for n in nodes if n['tag'] == 'video']
    if with_video:
        need(bool(videos), 'video element missing')
        for video in videos:
            need('controls' in video['attrs'], 'video controls missing')
            need(video['attrs'].get('poster'), 'video poster missing')
            children = [n for n in nodes if n['parent'] is video]
            need(video['attrs'].get('src') or any(n['tag'] == 'source' and n['attrs'].get('src')
                                                 for n in children), 'video source missing')
            need(any(n['tag'] == 'track' and n['attrs'].get('kind') in ('captions', 'subtitles')
                     and n['attrs'].get('srclang') and n['attrs'].get('src') for n in children),
                 'video captions missing')
        need(any(n['tag'] == 'a' and n['attrs'].get('href')
                 and any(word in text(n).lower() for word in ('文字稿', 'transcript')) for n in nodes),
             'transcript link missing')
    originals = [n for n in nodes if n['tag'] == 'figure'
                 and n['attrs'].get('data-paper-figure') == 'original']
    if paper_figures:
        need(bool(originals), 'original paper figure missing')
    for figure in originals:
        attrs = figure['attrs']
        need(all(isinstance(attrs.get(k), str) and attrs[k].strip() for k in
                 ('data-source-url', 'data-source-version', 'data-source-location')),
             'figure source metadata missing')
        need(urlsplit(attrs['data-source-url']).scheme in ('http', 'https'), 'figure source URL invalid')
        descendants = []
        for node in nodes:
            parent = node['parent']
            while parent:
                if parent is figure:
                    descendants.append(node)
                    break
                parent = parent['parent']
        images = [n for n in descendants if n['tag'] == 'img']
        need(len(images) == 1, 'one original image per figure required')
        need(any(n['tag'] == 'figcaption' and text(n) for n in descendants), 'figure caption missing')
        legends = [n for n in descendants if n['tag'] == 'dl' and 'data-figure-legend' in n['attrs']]
        need(len(legends) == 1, 'figure legend missing')
        terms = [n for n in descendants if n['parent'] is legends[0] and n['tag'] == 'dt']
        definitions = [n for n in descendants if n['parent'] is legends[0] and n['tag'] == 'dd']
        need(terms and len(terms) == len(definitions) and all(text(n) for n in terms + definitions),
             'figure legend missing')
        image = images[0]['attrs'].get('src', '')
        url = urlsplit(image)
        if url.scheme == 'data':
            header, payload = image.split(',', 1)
            data = base64.b64decode(payload, validate=True) if ';base64' in header.lower() else unquote_to_bytes(payload)
        else:
            need(not url.scheme and not url.netloc and url.path, 'original figure must be bundled')
            data = (root / unquote(url.path)).resolve().read_bytes()
        need(hashlib.sha256(data).hexdigest() == attrs.get('data-original-sha256'),
             'original figure digest mismatch')
    return dict(status='structural-pass', checked_urls=len(checked), visual_review='pending',
                voice_review='pending', bound_original_figures=len(originals), figure_semantics='pending', scope='declared HTML resources and controls only; no JavaScript execution or browser/media certification')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('html', type=Path)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--with-video', action='store_true')
    parser.add_argument('--paper-figures', action='store_true')
    args = parser.parse_args()
    try:
        result = validate(args.html, args.offline, args.with_video, args.paper_figures)
    except (ValueError, OSError) as exc:
        print(json.dumps(dict(status='rejected', reason=str(exc)), ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
