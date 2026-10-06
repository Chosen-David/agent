# attention: writing blueprint frozen before drafting

Question: Which transformations retain global softmax attention, and which merely change its operator?

Study object: Independent CPU NumPy stable blockwise attention, stable dense reference, unstable dense comparator, and explicit local-mask counterexample.

Mechanism: Define masked scaled-dot-product attention; derive running maximum, denominator and numerator merge; handle empty tiles and fully masked rows.

Reader path: Introduction: storage tiling versus semantics. Method: stable recurrence and conditions. Results: fixed numerical sweep, unstable comparator, local-global counterexample. Discussion: theoretical operator versus floating point and resource scope.

| Dimension | Decision | Source anchor | Target | Own evidence / missing |
|---|---|---|---|---|
|organization|adapt|EX04 §3 pp4–5 / E.6 p28; EX01 scaled attention §3; EX09 algorithm pseudocode|Introduction and section ordering|attention/evidence.md; runs/run01/attention/accuracy.csv,naive_failures.csv,counterexample.json,masked_row_contract.json; reproduce.py|
|claim_evidence|adapt|EX04 Theorem1/2 p5; EX06 theorem conditions|Method and results|attention/evidence.md; runs/run01/attention/accuracy.csv,naive_failures.csv,counterexample.json,masked_row_contract.json; reproduce.py; no external effectiveness evidence|
|figures|adapt|EX04 §3 pp4–5 / E.6 p28; EX01 scaled attention §3; EX09 algorithm pseudocode|Methods/results figure(s)|Show errors against predeclared dtype thresholds and failure counts; exact score-tile shapes are accounting, not measured peak memory.|
|rhetoric|adopt|EX05 §2.2/§3; EX04 §3.1|Paragraph topic and conclusion sentences|Explain what each actual contrast resolves. Equations/definitions serve that question; audit commands remain separate.|
|content|reject broad benchmark imitation|EX04 AppendixE; EX03 §2|Discussion and reproducibility appendix|No FlashAttention CUDA reproduction, backward/dropout/training/speed/total linear-memory claims. Distinguish source versions: study source arXiv34p, writing exemplar official35p.|

Use exact supplied inputs and primary-source metadata. Keep full scientific prose distinct from claim/evidence and process companions. Working-paper scope does not remove evidence or readable full-PDF requirements. Figures arrive through an actual producer handoff, and writers must open them before integration. No article draft existed when this blueprint was created.
