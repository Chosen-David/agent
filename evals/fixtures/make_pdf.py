"""Generate a reproducible synthetic PDF fixture, never a claimed real paper."""
from pathlib import Path
import fitz
out = Path(__file__).with_name('paper.pdf')
doc = fitz.open()
for title, lines in [
 ('Synthetic paper: Two logit paths', ['Physical page 1; printed page i.', 'y = softmax(a + b) V.', 'Both paths contribute to the same normalized weights.']),
 ('Example and a claim', ['Physical page 2; printed page 1.', 'a=(0,0); b=(0,0); V=(0,10). Output is 5.', 'Change b to (0, log(3)). Output is 7.5.', 'Claim: this proves RoPE always amplifies error in every real model.']),
 ('Appendix: scope', ['Physical page 3; printed page A1.', 'This is an invented teaching example, not empirical evidence.', 'No RoPE-specific model, data or experiment was studied.'])]:
 p=doc.new_page(width=595,height=842)
 p.insert_text((50,65),title,fontsize=18)
 for i,line in enumerate(lines): p.insert_text((50,110+i*32),line,fontsize=11)
doc.save(out, no_new_id=True)
print(out)
