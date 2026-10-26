import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.advice_context import advice_headings,advice_view
from agent_runtime.context_serialization import configure_utf8_output, render_cli_context, ContextBudgetError
def main():
    configure_utf8_output()
    p=argparse.ArgumentParser(description='Read-only exact-version advice topics; not a human GUIDE reader.')
    p.add_argument('--root',required=True);p.add_argument('--path',required=True)
    selection=p.add_mutually_exclusive_group(required=True)
    selection.add_argument('--heading',action='append')
    selection.add_argument('--list-headings',action='store_true',help='discover all literal H2 titles and line positions; no topic bodies')
    p.add_argument('--sha256',required=True);p.add_argument('--max-chars',type=int,default=20000)
    p.add_argument('--compact',action='store_true',help='preserve exact payload, omit JSON whitespace')
    a=p.parse_args()
    try:
        if not 1 <= a.max_chars <= 1000000:
            raise ContextBudgetError('invalid display budget')
        value=(advice_headings(a.root,a.path,a.sha256,max_chars=1000000) if a.list_headings
               else advice_view(a.root,a.path,a.heading,a.sha256,max_chars=1000000))
        print(render_cli_context(value,compact=a.compact,max_chars=a.max_chars))
        return 0
    except (OSError,ValueError,TypeError,RecursionError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2
if __name__=='__main__':raise SystemExit(main())
