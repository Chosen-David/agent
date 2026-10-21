"""SHA-bound Markdown navigation and literal retrieval; no inferred completeness."""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from .knowledge_index import sections
from .result_validation import _bound

def _load(root, source):
    root = Path(root)
    if not root.is_absolute() or not root.is_dir():
        raise ValueError('existing absolute PROJECT_ROOT required')
    root = root.resolve()
    if (not isinstance(source, dict) or set(source) != {'path', 'sha256'} or
            not isinstance(source['path'], str) or Path(source['path']).suffix.lower() != '.md'):
        raise ValueError('exact SHA-bound Markdown source required')
    raw = _bound(root, source, max_bytes=1024*1024)
    text = raw.decode('utf-8')
    nodes = sections({'title': Path(source['path']).name, 'content': text})
    common = {'schema_version': 'markdown-context/v1', 'project_root': str(root),
              'source': dict(source), 'scope': 'literal source navigation; headings delimit blocks until the next heading; select required global sections explicitly; no completeness or acceptance proof'}
    return common, nodes

def _budget(value, max_chars, max_tokens=None, token_counter=None):
    if type(max_chars) is not int or not 1 <= max_chars <= 200000:
        raise ValueError('invalid Markdown character budget')
    rendered = json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    if len(rendered) + len(os.linesep) > max_chars:
        raise ValueError('complete Markdown payload exceeds budget; narrow selection or increase budget')
    if max_tokens is not None:
        if type(max_tokens) is not int or max_tokens < 1 or not callable(token_counter):
            raise ValueError('explicit positive token bound and trusted counter required')
        count = token_counter(rendered + os.linesep)
        if type(count) is not int or count < 0:
            raise ValueError('token counter must return a nonnegative integer')
        if count > max_tokens:
            raise ValueError('complete Markdown payload exceeds token budget')
    elif token_counter is not None:
        raise ValueError('token counter requires explicit token budget')
    return value

def outline(root, source, *, max_chars=20000, limit=20, after_id=None, expected_snapshot=None, max_tokens=None, token_counter=None):
    common, nodes = _load(root, source)
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError('invalid Markdown page limit')
    snapshot = hashlib.sha256(json.dumps(common, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
    if expected_snapshot is not None and expected_snapshot != snapshot:
        raise ValueError('Markdown snapshot changed; restart outline')
    start = 0
    if after_id is not None:
        if expected_snapshot is None:
            raise ValueError('continuation requires snapshot')
        position = next((i for i, n in enumerate(nodes) if n['node'] == after_id), None)
        if position is None:
            raise ValueError('Markdown cursor outside source')
        start = position + 1
    page = nodes[start:start+limit]
    more = start + len(page) < len(nodes)
    return _budget({**common, 'mode': 'outline', 'snapshot': snapshot, 'total_nodes': len(nodes),
                   'start': start, 'partial': more, 'next_after_id': page[-1]['node'] if more and page else None,
                   'nodes': [{k: v for k, v in n.items() if k != 'text'} for n in page]}, max_chars, max_tokens, token_counter)

def read_sections(root, source, selected, *, max_chars=20000, mandatory=(), max_tokens=None, token_counter=None):
    common, nodes = _load(root, source)
    if (not isinstance(selected, (list, tuple)) or not selected or
            any(type(x) is not str for x in selected) or len(set(selected)) != len(selected)):
        raise ValueError('explicit unique section IDs required')
    if (not isinstance(mandatory, (list, tuple)) or any(type(x) is not str for x in mandatory) or len(set(mandatory)) != len(mandatory)):
        raise ValueError('mandatory section IDs must be unique text')
    wanted = set(selected) | set(mandatory)
    if not wanted <= {n['node'] for n in nodes}:
        raise ValueError('unknown Markdown section')
    chosen = [n for n in nodes if n['node'] in wanted or n['node'] == 'intro']
    return _budget({**common, 'mode': 'read', 'requested': list(selected), 'mandatory': list(mandatory), 'sections': chosen}, max_chars, max_tokens, token_counter)

def main(argv=None):
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--path', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--max-chars', type=int, default=20000)
    parser.add_argument('--max-tokens', type=int)
    parser.add_argument('--tokenizer')
    commands = parser.add_subparsers(dest='command', required=True)
    nav = commands.add_parser('outline')
    nav.add_argument('--limit', type=int, default=20)
    nav.add_argument('--after-id')
    nav.add_argument('--snapshot', dest='expected_snapshot')
    read = commands.add_parser('read')
    read.add_argument('--section', action='append', required=True)
    read.add_argument('--mandatory', action='append', default=[])
    args = parser.parse_args(argv)
    try:
        if (args.max_tokens is None) != (args.tokenizer is None):
            raise ValueError('max-tokens and explicit tokenizer must be supplied together')
        counter = None
        if args.tokenizer is not None:
            from .handoff_basis import make_token_counter
            counter = make_token_counter(args.tokenizer)
        source = {'path': args.path, 'sha256': args.sha256}
        value = (outline(args.root, source, max_chars=args.max_chars, limit=args.limit,
                         after_id=args.after_id, expected_snapshot=args.expected_snapshot, max_tokens=args.max_tokens, token_counter=counter)
                 if args.command == 'outline' else
                 read_sections(args.root, source, args.section, max_chars=args.max_chars, mandatory=args.mandatory, max_tokens=args.max_tokens, token_counter=counter))
        print(json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({'status': 'blocked', 'error': str(exc)}, ensure_ascii=False, separators=(',', ':')))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
