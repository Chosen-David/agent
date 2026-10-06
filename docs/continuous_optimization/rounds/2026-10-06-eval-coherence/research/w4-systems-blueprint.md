# systems: writing blueprint frozen before drafting

Question: When can observing unfinished work consume a retry, and how does queue selection affect a second ready task?

Study object: Two local SQLite scheduler implementations under matched controlled-clock plans; not server jobs or an autonomous optimizer.

Mechanism: Define pending, retry, done and independent wait/retry bounds; explain persisted rotating selection.

Reader path: Introduction: observable premature failure/exclusion. Semantics/design: the distinct budgets and eligibility rule. Evaluation: matched failure, competing-ready trace, bounded termination and legacy/cancel outcomes. Discussion: finite trace scope.

| Dimension | Decision | Source anchor | Target | Own evidence / missing |
|---|---|---|---|---|
|organization|adapt|EX05 Figure2 p3; EX04 Figure2 p6; EX02 controlled architecture comparison|Introduction and section ordering|systems/evidence.md; runs/run01/systems/traces.csv and full JSON traces; systems/source_versions.json; unchanged suite stdout/stderr|
|claim_evidence|adapt|EX04 Theorem1/2 p5; EX06 theorem conditions|Method and results|systems/evidence.md; runs/run01/systems/traces.csv and full JSON traces; systems/source_versions.json; unchanged suite stdout/stderr; no external effectiveness evidence|
|figures|adapt|EX05 Figure2 p3; EX04 Figure2 p6; EX02 controlled architecture comparison|Methods/results figure(s)|A trace/tick panel and compact outcome table reveal changed transition behavior. Use ticks/dispatch counts, not invented time or speedup.|
|rhetoric|adopt|EX05 §2.2/§3; EX04 §3.1|Paragraph topic and conclusion sentences|Explain what each actual contrast resolves. Equations/definitions serve that question; audit commands remain separate.|
|content|reject broad benchmark imitation|EX04 AppendixE; EX03 §2|Discussion and reproducibility appendix|No production, fairness theorem, total reliability, GPU or model quality claim; budget exhaustion is blocked/failed, never done.|

Use exact supplied inputs and primary-source metadata. Keep full scientific prose distinct from claim/evidence and process companions. Working-paper scope does not remove evidence or readable full-PDF requirements. Figures arrive through an actual producer handoff, and writers must open them before integration. No article draft existed when this blueprint was created.
