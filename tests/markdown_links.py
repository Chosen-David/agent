"""Repository-test Markdown link scanning, excluding actual code literals.

This intentionally handles the inline-link syntax used by package contracts,
not all of CommonMark. Fenced blocks and backtick spans are examples, not package
navigation. Prose quotes and blockquotes still contain live links and are checked.
"""
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

_FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})(.*)$')
_TICKS = re.compile(r'`+')
_LINK = re.compile(r'!?\[[^\]\n]*\]\(\s*(<[^>\n]+>|[^\s)]+)'
                   r'(?:[ \t]+(?:"[^"\n]*"|\'[^\'\n]*\'|\([^\n]*?\)))?\s*\)')


def _blank(text):
    return ''.join('\n' if char == '\n' else ' ' for char in text)


def _quoted_line(line):
    """Remove blockquote containers only for recognizing a quoted fence."""
    depth = 0
    while match := re.match(r'^ {0,3}>[ \t]?', line):
        depth += 1
        line = line[match.end():]
    return depth, line


def without_code_literals(text):
    lines, fence = [], None
    for line in text.splitlines(keepends=True):
        depth, content = _quoted_line(line)
        if fence is not None:
            char, length, quote_depth = fence
            if quote_depth and depth < quote_depth and line.strip():
                # Leaving a quoted container ends its fenced block. Do not hide
                # an unrelated live link following that container.
                fence = None
            else:
                # In ordinary code, '>' is literal. In quoted code, remove only
                # the enclosing quote containers, not content that looks quoted.
                content = line
                for _ in range(quote_depth):
                    prefix = re.match(r'^ {0,3}>[ \t]?', content)
                    if prefix:
                        content = content[prefix.end():]
                lines.append(_blank(line))
                if re.fullmatch(r' {0,3}' + re.escape(char) + '{' + str(length) + r',}[ \t]*\n?', content):
                    fence = None
                continue
        opening = _FENCE.match(content)
        if opening and not (opening[1][0] == '`' and '`' in opening[2]):
            fence = opening[1][0], len(opening[1]), depth
            lines.append(_blank(line))
        else:
            lines.append(line)
    text = ''.join(lines)
    chars = list(text)
    runs = list(_TICKS.finditer(text))
    index = 0
    while index < len(runs):
        opening = runs[index]
        # Outside code, an escaped backtick is not a span opener.
        backslashes = len(text[:opening.start()]) - len(text[:opening.start()].rstrip('\\'))
        if backslashes % 2:
            index += 1
            continue
        paragraph_break = re.search(r'\n[ \t]*\n', text[opening.end():])
        limit = opening.end() + paragraph_break.start() if paragraph_break else len(text)
        closing = next((other for other in range(index + 1, len(runs))
                        if runs[other].start() < limit
                        and len(runs[other][0]) == len(opening[0])), None)
        if closing is None:
            index += 1  # Unmatched backticks remain literal; following links live.
            continue
        end = runs[closing].end()
        chars[opening.start():end] = _blank(text[opening.start():end])
        index = closing + 1
    return ''.join(chars)


def local_markdown_links(text):
    """Yield local inline link/image paths with fragments/titles removed."""
    for match in _LINK.finditer(without_code_literals(text)):
        parsed = urlsplit(match[1].strip('<>'))
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        yield unquote(parsed.path)


def package_markdown_targets(source, package):
    """Resolve real navigation, rejecting missing and package-escaping files."""
    source, package = Path(source), Path(package).resolve()
    for target in local_markdown_links(source.read_text(encoding='utf-8')):
        resolved = (source.parent / target).resolve()
        if not resolved.is_relative_to(package):
            raise ValueError(f'Markdown link leaves package: {source}: {target}')
        if not resolved.is_file():
            raise ValueError(f'Markdown link file missing: {source}: {target}')
        yield resolved
