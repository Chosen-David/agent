"""Exact Python symbol retrieval, not source rewriting or semantic acceptance."""
import ast
import json
from pathlib import Path
import re

from .result_validation import _bound

DEFINITIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
DYNAMIC = {'globals', 'locals', 'vars', 'eval', 'exec', 'getattr', 'setattr',
           'delattr', '__import__', '__builtins__'}
DYNAMIC_ATTRIBUTES = DYNAMIC | {'__globals__', '__dict__', '__getattribute__',
                                '__code__'}


def physical_lines(text):
    """AST line numbers use LF/CRLF/CR, never Unicode string separators."""
    return [line for line in re.findall(r'[^\r\n]*(?:\r\n|\r|\n|$)', text) if line]


def _names(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _safe_default(node):
    # Containers may raise while being constructed (e.g. an unhashable key).
    return node is None or isinstance(node, ast.Constant)


def source_context(root, request, *, full=False, max_chars=20000):
    """Keep all non-definition text, declaration effects and static name closure.

    Hosts choose top-level targets. Classes stay whole; unknown/dynamic scope
    keeps the full file. External modules/callbacks are not resolved here.
    """
    root = Path(root)
    if not root.is_absolute():
        raise ValueError('absolute PROJECT_ROOT required')
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError('PROJECT_ROOT must be a directory')
    if (not isinstance(request, dict) or set(request) !=
            {'schema_version', 'source', 'symbols'} or
            request['schema_version'] != 'source-context/v1'):
        raise ValueError('explicit source-context contract required')
    ref = request['source']
    if (not isinstance(ref, dict) or set(ref) != {'path', 'sha256'} or
            not isinstance(ref['path'], str) or
            Path(ref['path']).suffix.lower() != '.py'):
        raise ValueError('SHA-bound Python source required')
    wanted = request['symbols']
    if (not isinstance(wanted, list) or not 1 <= len(wanted) <= 32 or
            any(not isinstance(x, str) or not x.isidentifier() for x in wanted) or
            len(set(wanted)) != len(wanted)):
        raise ValueError('explicit unique top-level symbols required')
    if type(full) is not bool or type(max_chars) is not int or not 1 <= max_chars <= 100000:
        raise ValueError('invalid view flag or character budget')
    raw = _bound(root, ref)
    if len(raw) > 262144:
        raise ValueError('source exceeds parser byte bound')
    text = raw.decode('utf-8')
    lines = physical_lines(text)
    common = {'schema_version': 'source-context-view/v1', 'project_root': str(root),
              'source': dict(ref), 'requested_symbols': list(wanted),
              'scope': 'exact local source view; external dependencies and whole-program behavior require further reading'}
    def whole(reason):
        return {**common, 'mode': 'full', 'reason': reason,
                'omitted_symbols': [], 'chunks': [{'start_line': 1,
                'end_line': len(lines), 'text': text}]}
    if full:
        view = whole('explicit full source')
    else:
        try:
            tree = ast.parse(text)
        except (SyntaxError, RecursionError):
            tree = None
        definitions = [n for n in tree.body if isinstance(n, DEFINITIONS)] if tree else []
        by_name = {n.name: n for n in definitions}
        if not tree or len(definitions) > 256 or len(by_name) != len(definitions):
            view = whole('unsupported or ambiguous syntax')
        elif not set(wanted) <= by_name.keys():
            raise ValueError('requested top-level symbol is absent')
        else:
            selected = set(wanted)
            # Retain whole classes/decorated or annotated declarations and
            # defaults whose definition-time effects cannot be proved literal.
            for node in definitions:
                args = getattr(node, 'args', None)
                if (isinstance(node, ast.ClassDef) or node.decorator_list or
                        getattr(node, 'type_params', []) or
                        getattr(node, 'returns', None) is not None or
                        (args and (any(a.annotation is not None for a in
                         args.posonlyargs + args.args + args.kwonlyargs +
                         ([args.vararg] if args.vararg else []) +
                         ([args.kwarg] if args.kwarg else [])) or
                         not all(_safe_default(n) for n in args.defaults + args.kw_defaults)))):
                    selected.add(node.name)
            nondefs = [n for n in tree.body if not isinstance(n, DEFINITIONS)]
            for node in nondefs:
                selected.update(_names(node) & by_name.keys())
            pending = list(selected)
            while pending:
                for name in _names(by_name[pending.pop()]) & by_name.keys() - selected:
                    selected.add(name)
                    pending.append(name)
            inspected = nondefs + [by_name[n] for n in selected]
            dynamic = any(_names(node) & DYNAMIC or any(
                (isinstance(n, ast.Attribute) and n.attr in DYNAMIC_ATTRIBUTES) or
                (isinstance(n, ast.alias) and (n.name in DYNAMIC or n.name == '*'))
                for n in ast.walk(node)) for node in inspected)
            if dynamic:
                view = whole('dynamic namespace access requires full source')
            else:
                omitted = [n for n in definitions if n.name not in selected]
                excluded = set()
                for node in omitted:
                    # Omitted nodes have no decorators. Keep all other bytes,
                    # including comments, imports, globals and ordering.
                    excluded.update(range(node.lineno, node.end_lineno + 1))
                chunks = []
                for number, line in enumerate(lines, 1):
                    if number in excluded:
                        continue
                    if chunks and chunks[-1]['end_line'] == number - 1:
                        chunks[-1]['end_line'] = number
                        chunks[-1]['text'] += line
                    else:
                        chunks.append({'start_line': number, 'end_line': number, 'text': line})
                candidate = {**common, 'mode': 'focused',
                             'reason': 'host targets plus conservative static local closure',
                             'omitted_symbols': [n.name for n in omitted], 'chunks': chunks}
                fallback = whole('focused view is not smaller')
                compact = lambda x: json.dumps(x, ensure_ascii=False, separators=(',', ':'))
                view = candidate if omitted and len(compact(candidate)) < len(compact(fallback)) else fallback
    serialized = json.dumps(view, ensure_ascii=False, separators=(',', ':'))
    if len(serialized) > max_chars:
        raise ValueError('complete source view exceeds character budget; no truncation')
    return view
