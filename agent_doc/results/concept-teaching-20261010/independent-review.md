# EXPL-BLOG-01 independent review

Reviewer: separate collaboration context `/root/verify_teaching`, 2026-10-10. This reviewer did not produce or edit the implementation or task files. Only this result file is reviewer-owned. Baseline: `4de59de41fbd4abad079f83e894a92fd72345468`.

## Scope and current decision

Implementation/source and three-prompt trial review: **usable-with-scope** after correction of F1 below and the candidate display-math delimiter repair. No unresolved new blocker was found in this bounded scope. The pre-existing full-suite/package failures remain explicitly outside acceptance. This is a repository instruction/package change; no live plugin installation, deployed supervisor, independent figure-generation backend, or learner study is certified.

Read AGENTS.md, prompts/decision_review.md, workflows/project_document_workflow.md, EXPL-BLOG-01 detail and TASK index context; inspected git diff, the complete new explanation_patterns.md, changed concept/visual workflows, skill entry and execution supplement, sync mapping/rewrite implementation and all six generated consumers. GUIDE.md is empty; no reviewer guide or task writes were performed. The main producer owns task reconciliation and publishing.

Prior-result query before targeted testing: `rg -n 'concept|explain|教学|讲解' agent_doc/results --glob '*verification*' --glob '*manifest*' --glob '*review*' | head -35`. Hits concern unrelated knowledge/math/communication verification, not this teaching protocol; none reused as acceptance. Also inspected this run's already present baseline outputs. These were produced for the exact fixed prompts, but require independent review below rather than trusting their self-reported pass.

## Findings

- **F1 — new portability defect, corrected before acceptance.** The initial generated `research-assistant/references/explain-research-concepts_execution.md` linked the new patterns document through an online GitHub URL despite a local bundled copy. The sync resolver only knew the canonical workflow source mapping, while the execution supplement linked its plugin-local alias. Reported to producer; producer replaced the redundant direct reference with navigation through existing SKILL/full-workflow links and regenerated this one consumer. Independently re-read the diff and recomputed all changed mappings; the new online-only edge is gone, and the actual concept/visual consumers retain local links. No unresolved new blocker.
- **F2 — pre-existing package closure error, not a regression.** Existing `project_document_workflow.md` links to missing package-local `../docs/token_optimization/advice_meetings.md`. Both current and baseline visual suite fail at the same path. General standalone package closure therefore cannot be reported as clean. New changed-source links were checked separately.
- **F3 — pre-existing generated knowledge drift, not a regression.** Full reference sync check reports stale knowledge coverage.json and learning_state.json on both candidate and baseline. These are unrelated to this diff and were not fixed by reviewer. Scoped changed-source sync passes.

The new content correctly separates author-inspired engineering choices from proven pedagogy; retains primary technical-source checks, calculation/geometry requirements and synthetic-data labels; uses one continuous example, explicit misconception/reading target and a boundary case; honors two-sentence/no-figure requests. New patterns references are on demand rather than forcing every short answer to retrieve all exemplars. Main orchestration, permission and evidence gates remain present. SGLang is outside the diff. These are content and interface observations, not proof of model adherence across unseen tasks.

## Attribution and primary-source checks

Independently opened all eight original author pages on 2026-10-10 via web retrieval; read relevant passages rather than accepting search snippets. The following table records bounded support for the new source table. Each observation is a paraphrase and the transfer rule is the repository's choice, not author endorsement.

| Source | Actual checked passage and support | Limit |
| --- | --- | --- |
| https://jalammar.github.io/illustrated-transformer/ | A High-Level Look and Bringing The Tensors Into The Picture proceed from translation input/output to component stacks and vectors. | Supports layered exposition; does not validate every technical simplification in the historic blog. |
| https://colah.github.io/posts/2015-08-Understanding-LSTMs/ | Notation before Step-by-Step LSTM Walk Through, followed by forget-gate operation. Original forget-gate image URL also successfully resolves. | No interaction claim; webpage image retrieval alone is not a separate user-study outcome. |
| https://www.redblobgames.com/pathfinding/a-star/introduction.html | Breadth First Search introduces frontier and a short loop; movement costs/A* change queue priorities and costs. | Article's textual controls described, not operated by reviewer. |
| https://ciechanow.ski/curves-and-surfaces/ | Linear Segment connects progress t to control-point weights; A Step Further extends a dragged segment into surfaces. | No controls operated or WebGL/runtime functionality certified. |
| https://www.3blue1brown.com/lessons/linear-transformations/ | Matrices and later formal explanation identify columns with basis-vector images, then use unchanged coefficients. | Two-dimensional teaching example does not replace general proof. |
| https://jvns.ca/blog/2020/11/15/simple-explanations-without-sounding-condescending/ | Searchable jargon, useful truth, relevant stories and audience prerequisites are explicit sections. | Writing advice, not measured learning gains. |
| https://distill.pub/2019/computing-receptive-fields/ | Problem setup and Single-path networks introduce assumptions before recurrence/general graph treatment. | Does not endorse ignoring assumptions in multi-path models. |
| https://distill.pub/2016/augmented-rnns/ | Neural Turing Machines starts from differentiable memory reading and weighted sums; Attentional Interfaces connects distribution to scores. | Historical exposition does not prove current implementation or performance claims. |

New guidance paraphrases techniques, identifies origins and local transfer boundaries, and does not copy complete articles or figures. Actual browser interaction, all original figures and current implementation claims are outside this source-review scope.

## Commands and raw outcomes

All commands run in `/workspace/scratch/a2f250bdd851/agent` unless explicitly noted. Targeted tests were chosen for the changed content/mapping interfaces. No unrelated broad suite was run.

1. `python scripts/sync_plugin_references.py --check`: exit 1, original raw failure below.
2. `python -m unittest discover -s tests -p 'test_visual_explanation.py' -v`: 7 tests, 6 pass and 1 error, original raw failure below.
3. `python -m unittest discover -s tests -p 'test_figure_contract.py' -v`: 16 tests pass, exit 0.
4. Baseline isolation: Python `subprocess.check_output(['git','archive','HEAD'])`, extracted with `tarfile.open(fileobj=io.BytesIO(blob)).extractall(p, filter='data')` to `/tmp/expl-blog-review-baseline-holu1erp`; same commands 1 and 2 run with that cwd. Both reproduce the exact failures, at baseline SHA above. No producer working-tree files were reset or overwritten.
5. Targeted source/consumer check: import scripts/sync_plugin_references.py with importlib; for `workflows/explanation_patterns.md`, `workflows/concept_explanation_workflow.md`, `workflows/visual_explanation_workflow.md`, `plugins/research-assistant/skills/explain-research-concepts/references/execution.md`, assert every mapped destination text equals `render(source,dest)`. **16/16 pass**. For each of the six affected roles, assert local `references/explanation_patterns.md` exists and visual workflow contains `(explanation_patterns.md)`: **6/6 pass**. Re-read fixed execution supplement and actual main consumer to confirm F1 resolved.
6. Read actual baseline `render_figures.py`, answers, checks and input_versions.json; opened both `attention_mass_720.png` and `linear_basis_720.png` with view_image. Full candidate review follows only after producer declares its output complete.

Raw full-sync failure (same current and baseline):

```text
stale generated references:
 - plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/coverage.json
 - plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/learning_state.json
```

Raw visual-suite failure (current):

```text
ERROR: test_entry_and_shared_workflow_links_stay_inside_each_skill (test_visual_explanation.VisualTeachingPackageTests.test_entry_and_shared_workflow_links_stay_inside_each_skill)
Traceback (most recent call last):
  File "/workspace/scratch/a2f250bdd851/agent/tests/test_visual_explanation.py", line 57, in test_entry_and_shared_workflow_links_stay_inside_each_skill
    for resolved in package_markdown_targets(path, package):
  File "/workspace/scratch/a2f250bdd851/agent/tests/markdown_links.py", line 100, in package_markdown_targets
    raise ValueError(f'Markdown link file missing: {source}: {target}')
ValueError: Markdown link file missing: /workspace/scratch/a2f250bdd851/agent/plugins/research-assistant/skills/explain-research-concepts/references/project_document_workflow.md: ../docs/token_optimization/advice_meetings.md
Ran 7 tests in 0.007s
FAILED (errors=1)
```

Baseline raw tail, same test and stack locations relative to isolated checkout:

```text
ValueError: Markdown link file missing: /tmp/expl-blog-review-baseline-holu1erp/plugins/research-assistant/skills/explain-research-concepts/references/project_document_workflow.md: ../docs/token_optimization/advice_meetings.md
Ran 7 tests in 0.008s
FAILED (errors=1)
```

## Initial implementation identity

SHA-256 values below bind the inspected post-F1 implementation sources; generated bytes are validated against them through the scoped check, not assumed from filenames.

- `workflows/explanation_patterns.md`: `732352b1ce3e2a72642d53462c12deb7d686e58d49f962e6f3d4795bc8fac56e`
- `workflows/concept_explanation_workflow.md`: `3e5326f288b402926e6ebd3e6db9e866b640f58226967544cbe22b70361cacc0`
- `workflows/visual_explanation_workflow.md`: `eaa5eed48eabfcafb53c1f0073a4817a869bab73a4c73e67ac34706c6c0a76df`
- `plugins/research-assistant/skills/explain-research-concepts/SKILL.md`: `01f49b8309d05f8741f684e7b9b0e6ffc938abc01ce5c9e901db21f243267f18`
- `plugins/research-assistant/skills/explain-research-concepts/references/execution.md`: `726eb12931ef0a05f9cd32fc8bb2dd00a9edc1df3e03367c4645d04aa4b3cca0`
- `scripts/sync_plugin_references.py`: `8317939e1ea677bf12ba59e08d0926866f5b03a79c16fe81e28fa39f3b47f7af`

## Final independent trial review

Final candidate handoff received from parent after producer completion; re-read final answers, execution notes and artifact manifest. Candidate's aligned display block now has display-math delimiters. Both actual 720px figures for each variant were inspected, not merely the SVG or producer self-check.

| Fixed prompt / acceptance | Baseline evidence | Candidate evidence | Bounded comparison |
| --- | --- | --- | --- |
| Q1: answer misconception, compute mass, preserve whole distribution | answer-1.md: same target/query/head, 0.65, denominator 1; bars plus 65/35 aggregate | answers.md Q1: same constraints; one full stacked bar with token identities and in-S labels; same 0.65/0.75 alternative metric | Both correct. Candidate uses one continuous probability bar rather than baseline's two panels; explicitly distinguishes cumulative axis from token index and warns renormalization loses coverage. No demonstrated learning advantage. |
| Q2: exactly two sentences, algebra, no figure/retrieval | answer-2.txt: finite-input identity and exponential cancellation, two sentences | answers.md Q2: exact-math invariance and same cancellation, two sentences | Both comply. Test archival files do not count as requested user-facing file output. General mathematical proof is supplied; no numerical sample is used as proof. |
| Q3: basis images, unchanged coefficients, precise diagram, general proof and boundary | answer-3.md: columns, e1+2e2, Ax=(3,2), general alpha/beta proof; nonlinear map agreeing with identity on basis | answers.md Q3: columns, same example, general s/t proof; nonlinear map agrees with the specific A on both basis vectors yet differs at x | Both correct. Candidate directly labels each translated step and uses unchanged coordinate grid; baseline shows transformed grid. Candidate's nonlinear counterexample is tied to A, a concrete structural difference rather than measured teaching improvement. |

At 720px, all four plots have readable key labels, no critical crop/overlap, and accurate quantities. Selected probability values are 0.50 and 0.15 out of total 1. Candidate blue highlighting is redundant with in-S labels; baseline uses hatching. Geometry panels have equal axis scales, correct endpoints and path steps; arrow meaning is explained in text. Candidate axis label and footer are close but remain separate. Figures use English/math labels with Chinese prose, transparently documented given missing CJK font. The baseline title's A=[(1,0) (1,1)] shorthand can be read ambiguously in isolation, but text and plotted columns make its intended column-vector interpretation clear; no incorrect numerical claim results.

Delivery boundary: candidate archive Markdown uses relative PNG links, appropriate within the saved directory; baseline uses absolute sandbox links. Final Work Mode chat image delivery must convert candidate paths to absolute sandbox image links. This review certifies actual local renders and image inspection, not that the final human user has already received an inline preview. No interactive controls were built or tested.

## Independent replay and arithmetic oracle

Read both actual renderer scripts before executing. Copied each renderer to its own variant directory under `/tmp/expl-teaching-independent-render-1s715d5x`, copied fixed prompts.md into its parent (candidate resolves this path), then executed `python /tmp/expl-teaching-independent-render-1s715d5x/<variant>/render_figures.py` via subprocess, capturing stdout/stderr. This prevented overwriting raw producer outputs. Both exit 0 with empty stderr. PIL `ImageChops.difference` on RGBA pixels confirms every saved PNG (full and 720px) exactly equals independent rerender; both numeric JSON objects also exactly equal independent rerun. SVG timestamps/IDs were not required to be byte-identical; actual SVG source and renderer were read.

Raw independent replay output:

```text
baseline render exit= 0 stderr= ''
pixel-equal baseline attention_mass.png (1500, 690)
pixel-equal baseline attention_mass_720.png (720, 331)
pixel-equal baseline linear_basis.png (1500, 870)
pixel-equal baseline linear_basis_720.png (720, 418)
numeric JSON equals independent rerun baseline
candidate render exit= 0 stderr= ''
pixel-equal candidate attention_mass.png (1440, 608)
pixel-equal candidate attention_mass_720.png (720, 304)
pixel-equal candidate linear_map.png (1600, 848)
pixel-equal candidate linear_map_720.png (720, 382)
numeric JSON equals independent rerun candidate
Independent Fraction/math oracle PASS: mass 13/20; top2 3/4; ratio 13/15; linear map and both nonlinear counterexamples
```

Separate independent oracle used exact Fraction/integer operations, without importing either renderer:

```python
from fractions import Fraction as F
a = [F(1,2), F(1,4), F(3,20), F(1,10)]
assert sum(a) == 1 and a[0]+a[2] == F(13,20)
assert sum(sorted(a)[-2:]) == F(3,4)
assert (a[0]+a[2])/sum(sorted(a)[-2:]) == F(13,15)
A = ((1,1),(0,1))
mv = lambda x: tuple(sum(ai*xi for ai,xi in zip(row,x)) for row in A)
assert mv((1,0)) == (1,0) and mv((0,1)) == (1,1) and mv((1,2)) == (3,2)
f = lambda u,v: (u,v+u*v)
g = lambda u,v: (u+v+u*v,v)
assert f(1,0) == (1,0) and f(0,1) == (0,1) and f(1,2) == (1,4)
assert g(1,0) == mv((1,0)) and g(0,1) == mv((0,1)) and g(1,2) == (5,2)
```

Softmax proof checked independently: for finite real z and c, positive common e^c cancels from numerator and denominator. The algebra does not assert floating-point overflow invariance. Basis uniqueness proof checked: coordinates in a basis are unique and linearity transports sums/scalars, so prescribed basis images uniquely determine the linear map, even when its images are dependent.

Integrity commands: Python hashlib recomputed all 10 entries in baseline/input_versions.json; all match actual files. For 9 baseline skill/reference entries, `git show HEAD:plugins/research-assistant/skills/explain-research-concepts/<relative path>` bytes match the isolated baseline files. All 11 candidate/artifact_manifest.json SHA-256 values and byte counts match actual files. Candidate Q2 extraction between its headings contains exactly two Chinese full stops and no image syntax; human review also confirms exactly two complete sentences. Candidate aligned block passes explicit delimiter check. Final `git diff --check` exits 0 after producer normalized appended CODEMAP/task lines. Earlier exit 2 due CRLF whitespace at CODEMAP lines 175–176 is retained here as resolved formatting evidence.

Provenance limit: baseline input hashes bind initial archived bytes. Candidate execution notes disclose that its first execution-reference read preceded the navigation-only F1 repair and lacked an initial-read hash; final implementation hashes do not retroactively prove those initial-read bytes. Parent and actual producer messages establish the bounded forward run; this reviewer does not manufacture a native runtime receipt. The observed navigation repair changes where to load patterns, not the teaching method, and final local routes were independently rechecked.

Root report.md was read and agrees with bounded results, baseline errors and no learner-effect claim. Three fixed prompts, one generated output per variant, one model reviewer, no real learners and no randomized repeated sampling support only concrete sample/content observations. Nothing here demonstrates causal or statistical improvement in understanding, speed, cost or general teaching quality.

## Final evidence SHA-256 inventory

Each hash below was independently recomputed after candidate completion. Any later content change requires checking the affected acceptance scope again. Task progress/report publication edits are not part of the teaching-source identity above.

- `baseline/answer-1.md`: `3c695d80bb2720608f666ff17807119cd5e9aca5dadb87e312a9de006c881948`
- `baseline/answer-2.txt`: `c7b61cf20bf5e929d6b497a1358efb81ff0d9405faa2d3c619a58646c355cbe0`
- `baseline/answer-3.md`: `e419b7156068ce19df83e396c3b4f672e1559789aab0a68bf9bcb63bdb9c5e9b`
- `baseline/attention_mass.png`: `8143ae5517cbaf26320df64571618ce4fb3555f551ba364d7d6dd76d8c64d5dc`
- `baseline/attention_mass.svg`: `cb9c6212c3e0fc92b96ae861dfbbd8d4c77d90e7e95949a3bb378a225e02dd93`
- `baseline/attention_mass_720.png`: `31534193ce562de482d684ac7a0af8dc5cb8c08722ba1745074204b76fac5e81`
- `baseline/execution-notes.md`: `789068a330897936441df2980152e5264315016209c5b4d435a98c44804a341b`
- `baseline/input_versions.json`: `9733c02425e4be05fbdbfc6b92d7468995edbd1a29171963cf780ca6921cb9d4`
- `baseline/linear_basis.png`: `b46ffd26af36c5f2f32aeb336de169df46b8b64ef834c8fa2ec9710228b589a5`
- `baseline/linear_basis.svg`: `f33fce9204ca90e0b8b17e0cdc4e1bdd286ba38ef3795347a25631e36a57d111`
- `baseline/linear_basis_720.png`: `fcbc981f8edd96553cfac3f56c271e46a478c4194e0836101cc78fe303505877`
- `baseline/numeric_checks.json`: `c784c1be25e5200951ce45525283ae5c40102a13615c81ee1904863e9a1f24d3`
- `baseline/render_figures.py`: `217a8cf7c38fc9ee526e00ca937533c26f16f4bfa2c7be890d3d291724e39cca`
- `baseline/render_stderr.log`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `baseline/render_stdout.log`: `c784c1be25e5200951ce45525283ae5c40102a13615c81ee1904863e9a1f24d3`
- `candidate/answers.md`: `e8df5224df0f12f4ad5db07ef88c715698a8564dc91a001d8c0f94aa2d836c2f`
- `candidate/arithmetic_checks.json`: `1f98c205771ea09059efa4e150c3d4cbdd5957dff6fd66ed8bedae635d55355d`
- `candidate/artifact_manifest.json`: `b2b39cdda94bc7fb5bdbe8a513d2f3357f225b3947852db2ea277c4453a26e5b`
- `candidate/attention_mass.png`: `c804a011b537ad4ad1e963e10292fca36e672cf4875c5c5725b9883a27f629ee`
- `candidate/attention_mass.svg`: `950f450c52408e60e6650ccd8a53f30e88dc7b07ef863855d23e3658a7d4b39d`
- `candidate/attention_mass_720.png`: `921dddefd2d438a65b15650121d9f02ccd8f63dbf537da4742b42534da9feab7`
- `candidate/execution_notes.md`: `fbd796b802516782eb165a7bae9c8792214c9bcad62ea96fa8e5155d43a8282d`
- `candidate/linear_map.png`: `c9dac8d7ef74e4ba5429d90a92e72085983ef03a3bb41782a4564bfaecb844a2`
- `candidate/linear_map.svg`: `0f41fb974ae31849fb3cebc177824dd2408042e4a0c5dc6dd66d6a3e4be9fb3c`
- `candidate/linear_map_720.png`: `55179ad8e9627889384f249ef446cb6de77a8645a9c2bef3112e8eecaed48fd1`
- `candidate/render_figures.py`: `4a6f19647b90a1aa11d9b6b0979d6678e2cba9a1a4c74262d30e3efa9b3b7e8e`
- `candidate/render_stdout.log`: `1f98c205771ea09059efa4e150c3d4cbdd5957dff6fd66ed8bedae635d55355d`
- `prompts.md`: `f63147f8f4955cff0d5189c984a9a17368877e9f33ac79182b9bf25af9d66096`
