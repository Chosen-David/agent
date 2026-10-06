# Independent final reader and scientific integration review

Reviewer: `/root/architecture_final_reader`, independent of producer `/root/architecture_writer`.
Case: `figure-writing`, attempt 1. Status: all four frozen rubric criteria pass for this bounded comparative section.
Final PDF SHA-256: `ab942daf96731fc448c317b9fada15c470539a88f9708133748dd7b355360988`. Scope: all four physical pages, including all references, captions and three figure plates.

The pinned research-read-pdf Skill, execution and relevant workflow instructions were loaded. Existing local PyMuPDF and `view_image` were used under the offline task restriction. Source facts and frozen rubric were supplied before review; manuscript source and producer inspection claims were read only after the first full visual pass. No collected output was modified. No new full-paper, novelty or experimental requirements were imposed.

## Actual page coverage

| Physical / printed page | Opened and read | Added information and observations |
|---|---|---|
| 1 / 1 | Yes | The comparison explains three receiving operations: query-conditioned attention, same-shaped elementwise residual addition, and spatially aligned channel concatenation. All mechanism paragraphs, equation, size examples, and three source references were read; citations and figure references resolve. |
| 2 / 2 | Yes | Transformer plate expands the sequence-conditioning paragraph: source/shifted-target streams, positional sums, six-layer templates, all five residual additions before LayerNorm, decoder Q and final-encoder K/V, and linear-softmax head. Full caption and footer were read; no collision or clipping. |
| 3 / 3 | Yes | ResNet plate expands residual refinement through separately traceable basic and bottleneck identity paths, own additions, post-add ReLU, channel/kernel progression, BN-omission note and equation. Full caption specifies original same-shape scope. White space preserves supplied width; labels remain legible. |
| 4 / 4 | Yes | U-Net plate expands spatial fusion through four pool/down stages, bottom and up-convolutions, all four copy/crop paths and concat nodes, dimensions and channel transitions, paired-valid-convolution legend and final 1x1 mapping. Caption distinguishes s and C. No clipped content or overlapping text. |

Independent render identities are in `final-reader-evidence/render_manifest.json`; page-level coverage is in `final-reader-evidence/page_coverage.jsonl`. All four full-page images were actually opened individually with `view_image`. The prose, references and captions are readable; no unresolved visual or scientific finding was identified within the supplied-source scope.

## Scientific consistency

Page 1 supplies a coherent comparison of receiving operations rather than treating every connection as equivalent. Transformer post-norm order, decoder query origin and final encoder memory reuse agree with the supplied method. ResNet correctly retains same-shape identity paths and places ReLU after addition, with the final BN-to-addition boundary explained. U-Net describes valid-convolution shrinkage, all four exact crop sizes and concatenation rather than summation. Diagram-specific captions support these mechanisms. Citation metadata and locators agree with the frozen method files. Audit and build material stay in delivery_notes.md. No unsupported experiment, result or novelty is introduced.

## Independent technical checks

All 15 input hashes match handoff.json; the three copied PDFs are byte-identical to inputs. LaTeX explicitly embeds widths 180 / 85 / 180 mm. PDF placement scales of 1.00005 / 1.00002 / 1.00005 yield approximately 180.009 / 85.0017 / 180.009 mm, normal TeX/PDF precision, without size reduction. Minimum embedded diagram text is 8.5004 / 8.0002 / 8.0041 pt; every source figure text span is retained and embedded figures remain vector.

The source and figures were copied to `final-reader-evidence/isolated-build`. Two direct pdflatex invocations returned 0, produced four pages with no warning/overfull/underfull/undefined diagnostics, and yielded 150-dpi renders pixel-identical to all four collected pages. See `final-reader-evidence/independent-checks.json` and `independent-build.log`. All 19 collected output hashes were checked before review and rechecked before grade delivery.

## Remaining limits and next owner

This is an independent check of the bounded section against supplied frozen methods and figures, not a fresh retrieval of the original research papers, model execution, venue acceptance decision or whole-manuscript scientific review. No physical print, color-vision simulation or external citation-link availability check was performed. Display density is device dependent. There are no open defects requiring manuscript edits; root owns acceptance ingestion and final reporting. Exact rubric decisions and collection output_hashes are in `figure-writing-1-independent-grade.json`.
