# RoPE coordinate-pair teaching diagram

- Explanation ID: EXPL-ROPE-001
- Input version: v1
- Output revision: final-2
- Route: diagram
- Kind: theoretical teaching schematic, not measured data
- Explanation owner: parent task; user attachment delivery remains with parent.

## Files

- `rope_pairs.png`: final high-resolution PNG, 1440 × 2260 pixels.
- `rope_pairs_preview_720.png`: actual inspected preview, 720 × 1130 pixels.
- `rope_pairs.svg`: editable SVG with vector shapes and text.
- `draw_rope_pairs.py`: editable/reproducible Matplotlib source. Run `python draw_rope_pairs.py` from any directory; outputs stay beside the script.
- `numeric_qa.json`: actual numeric checks and dimensions.

The SVG uses Noto Sans CJK JP and DejaVu Sans font fallback. Chinese text and Unicode subscript digits were checked in the rendered PNG; SVG appearance on other machines depends on compatible fonts. The PNG is the intended display artifact.

## Step-to-panel mapping

- S1 → P1: One angular frequency is attached to each two-coordinate block. The four-dimensional teaching example contains high-frequency pair (x₁,x₂), ω = π/2, and low-frequency pair (x₃,x₄), ω = π/6. Both start at (1,0); one position step turns them 90° and 30°, respectively. The lower-frequency pair is marked for whole-pair retention.
- S2 → P2: The same lower-frequency block rotates (1,0) by 30° to (0.866,0.500). The geometric plot shows both components and the one-coordinate projection. Retaining only x₃ does not retain the complete original two-dimensional RoPE rotation block.
- S3 → P3: Ordinary NoPE channels have no predefined RoPE angular-frequency table; channel numbering does not identify low-frequency dimensions.

## Caption

从上往下看：RoPE 把同一个 token 的两个通道作为一个旋转块，两维共享一个频率。低频块从 (1,0) 转 30° 后得到 (0.866,0.500)；只留第一维，剩下的是投影。NoPE 没有这张预设频率表，因此不能直接按通道编号挑低频。图中频率仅用于手算演示。

## Alt text

三段中文教学图。第一段把四个通道分成高频对 x₁、x₂ 与低频对 x₃、x₄；两个圆中的向量从相同起点分别转 90 度和 30 度，低频对标注整对保留。第二段显示低频二维向量 (1,0) 旋转为 (0.866,0.500)，虚线把终点投影到 x₃ 轴；只留 x₃ 得到 0.866，失去另一坐标。第三段把 NoPE 的四个通道并排展示，说明其没有预设的高低频排序。

## Encodings

- Green: lower-frequency RoPE pair and the retained complete block.
- Gray-blue: higher-frequency example and neutral channels.
- Labels “高频对”“低频对”“整对保留” provide redundancy to color.
- Arrows from circle/plot origins: vectors in coordinate planes.
- Gray dashed horizontal vector in P1: initial (1,0) vector.
- Curved line in P1: rotation angle.
- Horizontal arrow between the numeric boxes in P2: the 30° rotation operation.
- Dashed lines in P2: coordinate projection guides.
- Each pair consists of coordinates within one token, not two tokens.

## Semantic and numeric QA

Pass, checked separately from visual review.

- General mechanism supplied and verified by the explanation owner against RoFormer, §3.2.1 Eq. 13 and §3.2.2 Eq. 15–16: https://arxiv.org/html/2104.09864v5
- Explicitly a hand-calculable teaching example, not default RoPE parameter values or experimental evidence.
- Direct Python computation gives cos(π/6) = 0.8660254037844387 and sin(π/6) = 0.49999999999999994.
- Both off-diagonal rotation entries are nonzero; at 30°, each output coordinate depends on both input coordinates.
- The complete pair has squared norm 1.0; its one-coordinate projection has squared magnitude 0.7500000000000001.
- The plotted geometric end point is computed using those same cosine and sine values, not manually placed.
- π/2 and π/6 convert to 90° and 30° in the executed checks.
- “成对保留” is scoped to preserving the original complete RoPE rotation block. The diagram does not claim all single-coordinate pruning is forbidden.
- The NoPE panel says no predefined table; it does not claim NoPE cannot implicitly learn position.
- Optional empirical spectrum analysis along sequence positions is intentionally left to the explanation outside the image, since it requires a separate definition.

## Visual QA

Pass for the final PNG preview, based on actually opening `rope_pairs_preview_720.png` at its native 720 × 1130 size with the image-viewing tool.

- Three vertically numbered panels match the intended S1/P1 → S2/P2 → S3/P3 reading order.
- Chinese, Greek symbols and all four subscript digits render visibly.
- The original single-font rendering lacked subscript glyphs; a two-font fallback repaired this and rerendering emitted no missing-glyph warnings.
- The original 30° annotation touched the vector. It was moved above the diagonal arrow; the final preview was reopened and checked.
- On owner review, “保留 x₃ + x₄” was revised to “保留 (x₃, x₄)” to remove the possible interpretation of summing the coordinates. The final PNG was regenerated and actually reopened at 720 × 1130; the label fits and is readable.
- Final labels, boxes, panel titles and footer fit without clipping or overlapping.
- Dashed projection guides terminate on the correct vector endpoint and x₃-axis point.
- Light background / green and blue-gray colors remain distinguishable, with text redundancy.
- Core labels are 17–23 display pixels; headline is 28 pixels; footer is 15 pixels at the inspected 720-pixel width.
- The final 1440-pixel-wide PNG uses the same composition at twice the linear resolution.

## Remaining step

The explanation owner must inspect the returned preview, decide whether the wording fits the final explanation, and hand files to the parent for native attachment delivery. No claim is made here that the user has received or viewed an attachment.

## Final file hashes (SHA-256)

- rope_pairs.png: `4e597b6f1ff6d5ee977779ec7db0836a372eacb09cfdf9de8b1b4a9d553191e2`
- rope_pairs.svg: `088b613a7fba3f63b522a298a9eaed21a62e9be91af9fb47d1dcc29968fc9b40`
- rope_pairs_preview_720.png: `7487849549ce81235b8b52cb32e9ecd69a8e37602728ec41140e3c38f0281c84`
