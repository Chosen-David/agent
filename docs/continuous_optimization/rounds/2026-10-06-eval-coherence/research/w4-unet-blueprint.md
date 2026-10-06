# unet: writing blueprint frozen before drafting

Question: Is changing valid convolutions to zero-padded same convolutions sufficient to preserve U-Net geometry and boundary behavior?

Study object: Scalar original-channel geometry and separate reduced-channel fixed-positive-weight NumPy forward network.

Mechanism: Derive encoder/pool/upconv/crop dimension recurrences; distinguish strict symmetric, asymmetric and no-crop policies; define structural versus effective support.

Reader path: Introduction: drop-in substitution premise. Geometry: dimension/crop contract. Experiments: incompatible inputs, boundary response and selected support checks. Interpretation: aligned output shape differs from operator equivalence.

| Dimension | Decision | Source anchor | Target | Own evidence / missing |
|---|---|---|---|---|
|organization|adapt|EX03 Figure1 p2 / §2 p4; EX06 conditional theorem discussion; EX10 Figure2 p4|Introduction and section ordering|unet/evidence.md; runs/run01/unet/geometry.csv,forward.csv,receptive_fields.csv,layer_traces.json; reproduce.py|
|claim_evidence|adapt|EX04 Theorem1/2 p5; EX06 theorem conditions|Method and results|unet/evidence.md; runs/run01/unet/geometry.csv,forward.csv,receptive_fields.csv,layer_traces.json; reproduce.py; no external effectiveness evidence|
|figures|adapt|EX03 Figure1 p2 / §2 p4; EX06 conditional theorem discussion; EX10 Figure2 p4|Methods/results figure(s)|Use input-output geometry and actual boundary-response panel. Do not label reduced-channel fixed-weight curves as original trained U-Net.|
|rhetoric|adopt|EX05 §2.2/§3; EX04 §3.1|Paragraph topic and conclusion sentences|Explain what each actual contrast resolves. Equations/definitions serve that question; audit commands remain separate.|
|content|reject broad benchmark imitation|EX04 AppendixE; EX03 §2|Discussion and reproducibility appendix|No segmentation accuracy, universal same-padding inferiority, faithful training reproduction or learned effective receptive-field claim. 572→388 is scalar only.|

Use exact supplied inputs and primary-source metadata. Keep full scientific prose distinct from claim/evidence and process companions. Working-paper scope does not remove evidence or readable full-PDF requirements. Figures arrive through an actual producer handoff, and writers must open them before integration. No article draft existed when this blueprint was created.
