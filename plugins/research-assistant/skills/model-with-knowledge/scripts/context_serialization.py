"""Lossless JSON whitespace reduction; no field selection or trust change."""
import json
import os
import sys


class ContextBudgetError(ValueError):
    """A complete CLI response cannot fit; no partial response is usable."""


def configure_utf8_output():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')

def render_context(value, *, compact=False, indent=None):
    if type(compact) is not bool or (indent is not None and (type(indent) is not int or not 0<=indent<=8)):
        raise ValueError('explicit compact flag and bounded indentation required')
    return json.dumps(value,ensure_ascii=False,allow_nan=False,
                      indent=None if compact else indent,
                      separators=(',',':') if compact else None)


def render_cli_context(value, *, max_chars=20000, compact=False, indent=None):
    """Count the complete printed JSON including native newline translation.

    This bounds displayed characters, not database reads, allocations or tokens.
    Use standard text stdout after configure_utf8_output, then print once.
    """
    if type(max_chars) is not int or not 1 <= max_chars <= 1000000:
        raise ContextBudgetError('display max_chars must be 1..1000000')
    text = render_context(value, compact=compact, indent=indent)
    count = len(text) + text.count('\n') * (len(os.linesep) - 1) + len(os.linesep)
    if count > max_chars:
        raise ContextBudgetError('complete context exceeds display budget; narrow selection or increase --max-chars')
    return text
