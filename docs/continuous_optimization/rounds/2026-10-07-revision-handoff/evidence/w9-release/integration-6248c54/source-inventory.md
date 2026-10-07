# External source inventory

Public metadata only. Seven third-party PDF/fulltext/page-image caches are excluded from the archive and restored privately for cache-assisted evidence validation. No full-paper reading or new scientific execution claimed.

The ZIP omits every source listed below. Full replay used exact authorized local cache copies outside the extracted run; it is not self-contained. Frozen files were not rewritten.

| Relative cache path | Version / source URL | SHA-256 | Bytes |
|---|---|---|---|
| `writing-exemplars/b/flash.pdf` | NeurIPS 2022 official extended supplemental, 35-page PDF; distinct from arXiv 2205.14135v2 34-page historical source · https://proceedings.neurips.cc/paper_files/paper/2022/file/67d57c32e20fd0a7a302cb81d36e40d5-Supplemental-Conference.pdf | `6b0fcf9037095c8a10453267cd48d125652deb171b64d3ec9397a563ff5d93ca` | 2153751 |
| `writing-exemplars/b/flash.txt` | NeurIPS 2022 official extended supplemental, 35-page PDF; distinct from arXiv 2205.14135v2 34-page historical source · https://proceedings.neurips.cc/paper_files/paper/2022/file/67d57c32e20fd0a7a302cb81d36e40d5-Supplemental-Conference.pdf | `dc128681fd8f86a599f03cf59b261717d314944f306c37db582a7c764b579e65` | 125337 |
| `writing-exemplars/b/flash-p04.png` | NeurIPS 2022 official extended supplemental, 35-page PDF; distinct from arXiv 2205.14135v2 34-page historical source · https://proceedings.neurips.cc/paper_files/paper/2022/file/67d57c32e20fd0a7a302cb81d36e40d5-Supplemental-Conference.pdf | `3a9870354152bf00556488a6d5b253a4bb60e3cc72134d3254a34510ddbfaa47` | 248417 |
| `writing-exemplars/b/flash-p05.png` | NeurIPS 2022 official extended supplemental, 35-page PDF; distinct from arXiv 2205.14135v2 34-page historical source · https://proceedings.neurips.cc/paper_files/paper/2022/file/67d57c32e20fd0a7a302cb81d36e40d5-Supplemental-Conference.pdf | `34b93bd8fd9762b7cec2f4ee7ceab828fd519a58f3283a1469a32459d2f2a5fc` | 241132 |
| `writing-exemplars/b/flash-p22.png` | NeurIPS 2022 official extended supplemental, 35-page PDF; distinct from arXiv 2205.14135v2 34-page historical source · https://proceedings.neurips.cc/paper_files/paper/2022/file/67d57c32e20fd0a7a302cb81d36e40d5-Supplemental-Conference.pdf | `188d46faebab078a8730df68f6626f2d146b977a746eecf3fd874e999329925c` | 227464 |
| `architecture-sources/unet/paper.pdf` | arXiv:1505.04597v1, 8-page PDF · https://arxiv.org/pdf/1505.04597v1 | `a3172b2124f38e260dc2c7ed968d87c31bc94dbc19a42a7ab3dcbd7534319c44` | 1648684 |
| `architecture-sources/unet/paper.txt` | arXiv:1505.04597v1, 8-page PDF · https://arxiv.org/pdf/1505.04597v1 | `50d152f3b9ad4805b8fe612e2a4388134ee1043f89d8999a80c063f6170fd6e9` | 19830 |

## Original absolute paths → relocation

Observed private extraction root: `/workspace/scratch/c12f3d9f92bd/w9-final-private-relocated-54szcply`. `${EXTRACT_ROOT}` denotes an arbitrary clean extraction directory.

- `/workspace/scratch/c12f3d9f92bd/writing-exemplars/b/flash.pdf` → `${EXTRACT_ROOT}/writing-exemplars/b/flash.pdf`; inspected location: official NeurIPS2022 extended supplemental35-page PDF: physical4§3.1,5Algorithm1/Theorem1,22AppendixC induction.
- `/workspace/scratch/c12f3d9f92bd/writing-exemplars/b/flash.txt` → `${EXTRACT_ROOT}/writing-exemplars/b/flash.txt`; inspected location: text contains ===PAGE N=== markers; pages4/5/22.
- `/workspace/scratch/c12f3d9f92bd/writing-exemplars/b/flash-p04.png` → `${EXTRACT_ROOT}/writing-exemplars/b/flash-p04.png`; inspected location: existing original page4 raster.
- `/workspace/scratch/c12f3d9f92bd/writing-exemplars/b/flash-p05.png` → `${EXTRACT_ROOT}/writing-exemplars/b/flash-p05.png`; inspected location: existing original page5 raster.
- `/workspace/scratch/c12f3d9f92bd/writing-exemplars/b/flash-p22.png` → `${EXTRACT_ROOT}/writing-exemplars/b/flash-p22.png`; inspected location: existing original page22 raster.
- `/workspace/scratch/c12f3d9f92bd/architecture-sources/unet/paper.pdf` → `${EXTRACT_ROOT}/architecture-sources/unet/paper.pdf`; inspected location: arXiv1505.04597v1,8pages; physical2Fig1,3Fig2,4§2.
- `/workspace/scratch/c12f3d9f92bd/architecture-sources/unet/paper.txt` → `${EXTRACT_ROOT}/architecture-sources/unet/paper.txt`; inspected location: corresponding local extract.

All seven restored hashes matched. Exact TXT/PNG regeneration recipes and tool versions were not established; this replay copied existing authorized derivatives and did not rerender them. The machine-readable inventory includes the actual private paths, purpose, URLs and byte counts.

Source-free package inventory passed; source-free pipeline report exited 1 with missing-cache dependencies (0/4 accepted). After private restoration, the same pipeline command exited 0, 4/4 accepted, matching the root report. These operations validate recorded evidence and do not re-execute the four roles.
