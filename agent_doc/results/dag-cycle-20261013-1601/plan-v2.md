# Revised plan v2: defer sparse topology construction until depth observed

Keep plan.md scope, baseline, correctness and exact numerical gates. Preserve producer.json as failed candidate v1: star512 regression 21.29% exceeds 10%, so v1 is rejected, not published. No measurement rerun of v1 to select a better sample.

Change: execute two original scan rounds first. Shallow stars/no-dependency graphs finish without adjacency allocation. On third round only, remaining>=64, deduplicated original edges<=4V, exact builtin str remaining/visited/dependencies and all deps in remaining or visited admit Kahn. Subtract already visited deps when computing residual indegrees; exact set operations have no custom callbacks. Others continue original scan. Admission is depth/density structure, not an input-ID/timing shortcut. Preserve legacy validation order/construction/final packed.

New measured version v2 requires new producer-v2.json, one independent run, same 2 warmups/9 pairs, >=20% chain512/1000 and <=10% other regression. Also add shallow-star, residual-root edges, two peeled roots, cycles with removable prefix and density fallback boundaries. Independent reviewer must approve v2 before implementation. No deployed protected plan/supervisor/host adapter claim.
