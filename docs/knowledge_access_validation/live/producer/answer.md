# Top-k stability under vector replacement

Task: `knowledge-access-live/producer`; root task references: `KB-ACCESS-01`, `KB-ACCESS-03`. Decision: EXECUTE within the delegated synthetic task. No root edits, repository tests, network access, commits, or background supervision were performed.

**With a per-vector error bound, the top-k set is certified unchanged.** Treat the replacement scores as \(\hat s_i=q^T\hat k_i\) with the same fixed real query \(q\). Cauchy–Schwarz gives

\[
|s_i-\hat s_i|\leq\|q\|_2\|k_i-\hat k_i\|_2\leq3(0.02)=0.06.
\]

For every original selected index \(i\) and unselected index \(j\), \(s_i-s_j\geq0.15\). Therefore

\[
\hat s_i-\hat s_j\geq0.15-0.06-0.06=0.03>0.
\]

All cross-boundary comparisons remain strict, so membership is unchanged. The statement does not guarantee the internal order of the selected indices. A positive original boundary gap ensures a unique selected set even if scores tie within either side.

**If only the arithmetic mean of the vector error norms is bounded by 0.02, no such guarantee holds for all allowed n.** A one-dimensional counterexample is \(n=3,k=1,q=3\), with original vectors \((0.05,0,-1)\) and replacements \((-0.01,0,-1)\). Original scores are \((0.15,0,-3)\), with gap 0.15 and index 0 selected. Vector errors are \((0.06,0,0)\), whose mean is exactly 0.02. Replacement scores are \((-0.03,0,-3)\), selecting index 1 strictly instead.

There is an **n=2 exception**: the mean bound implies total vector error at most 0.04. For the only boundary pair, the score-gap loss is at most \(3(0.04)=0.12\), still leaving 0.03. More generally, the mean bound gives the sufficient condition \(\Delta>\|q\|_2 n(0.02)\); with only \(\|q\|_2\leq3\), this certifies the given gap for n=2, but not n>=3. Failure of a sufficient condition alone does not prove a reversal; the explicit n=3 example supplies that evidence.

Assumptions and knowledge use:

| Assumption | Task evidence | Outcome |
|---|---|---|
| Fixed real query, common dimension, Euclidean inner product/norm | Real dot products and stated 2-norm; replacement applies to keys only | Satisfied; fixed query made explicit |
| Finite n and 1<=k<n | Given n>=2 and range of k | Satisfied |
| Error bound applies to every vector | Given in first variant | Satisfied; implies uniform score error 0.06 |
| Strict gap greater than twice score error | 0.15>0.12 | Satisfied |
| Uniform error in mean-only variant | Only mean of norms <=0.02 | Not supplied; cannot substitute mean for maximum |
| Global score-vector 2-norm <=0.06 for a sharper sqrt(2) bound | No such joint bound given | Not satisfied; reject that substitution |

Actual local retrieval used `python -m agent_runtime.knowledge --root knowledge`, file backend, snapshot `dd4b298b81ff2ed3fe04de930456a86d58b33946590e3276c8c4c95686e237c8`. Full entries read: `math.cauchy-schwarz`, `math.score-difference-bound`, and related `math.topk-margin`. Adopted Cauchy–Schwarz and the strict uniform-error top-k lemma; used the score-difference entry's warning to reject an unjustified global-norm substitution. All full pinned references and candidate decisions are in `knowledge-use.json`; source URLs there are local provenance, not a claim of fresh web verification.

`verify.py` runs exact rational checks: the uniform worst-case pair retains gap 0.03, the mean-only example strictly reverses top-1, and the n=2 mean-only bound remains positive. Actual output is `verification-output.json`. This is an algebraic proof plus finite exact checks, not a formal prover result or a performance measurement. The reviewer must independently retrieve the knowledge and validate applicability before accepting the handoff.

Reproduce from the repository root:

```bash
python .agent-runs/knowledge-access-live/producer/verify.py
python -m agent_runtime.knowledge --root knowledge check-refs .agent-runs/knowledge-access-live/producer/knowledge-use.json
```

Current scope outcome: the delegated solve is complete. Main AI retains ownership of root TASK updates, independent review, handoff publication, and broader KB-ACCESS requirements.
