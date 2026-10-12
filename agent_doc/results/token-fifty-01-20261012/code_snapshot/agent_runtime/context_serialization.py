"""Lossless JSON whitespace reduction; no field selection or trust change."""
import json

def render_context(value, *, compact=False, indent=None):
    if type(compact) is not bool or (indent is not None and (type(indent) is not int or not 0<=indent<=8)):
        raise ValueError('explicit compact flag and bounded indentation required')
    return json.dumps(value,ensure_ascii=False,allow_nan=False,
                      indent=None if compact else indent,
                      separators=(',',':') if compact else None)
