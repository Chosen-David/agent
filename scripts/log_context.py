import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.log_context import log_view
from agent_runtime.context_serialization import configure_utf8_output, render_cli_context
def main():
    configure_utf8_output()
    p=argparse.ArgumentParser(description='Read-only exact-version log excerpts; no clearance inference.')
    p.add_argument('--root',required=True);p.add_argument('--path',required=True);p.add_argument('--sha256',required=True)
    p.add_argument('--needle',action='append',default=[])
    p.add_argument('--compact',action='store_true',help='preserve exact payload, omit JSON whitespace')
    p.add_argument('--encoding',choices=['lines','chunks','runs'],default='lines',help='lossless selected-line transport')
    for name,default in (('head',2),('tail',2),('context',1),('max-chars',20000)):
        p.add_argument('--'+name,type=int,default=default)
    a=p.parse_args()
    try:
        if not 1 <= a.max_chars <= 1000000:
            raise ValueError('display max_chars must be 1..1000000')
        value=log_view(a.root,a.path,a.sha256,needles=a.needle,head=a.head,tail=a.tail,
                       context=a.context,max_chars=1000000,encoding=a.encoding)
        print(render_cli_context(value,compact=a.compact,max_chars=a.max_chars))
        return 0
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2
if __name__=='__main__':raise SystemExit(main())
