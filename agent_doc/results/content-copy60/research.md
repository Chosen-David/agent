# Research application

Original source: [Agent Memory: Characterization and System Implications of Stateful Long-Horizon Workloads](https://arxiv.org/html/2606.06448), v2 dated 2026-09-22; read methods and results through discussion during this run. Its phase-specific profiling motivates measuring complete context assembly separately from retrieval and generation. Construction cost and freshness are separate axes; its five-history systems subset and model/prompt adaptations constrain generalization. This run applies phase attribution, not its GPU results or a new memory algorithm. Reusing immutable strings is our implementation hypothesis, not a contribution claimed by that paper.

The ten prior original-paper readings in read-boundary56/research_a.md and research_b.md remain background; they are not ten new reads in this run. No live model quality or end-to-end inference claim follows from this CPU experiment.

Prior-result search: result_store query `context JSON copy materialization`, limit5,max-scan300 returned broad communication/advice/cluster candidates, not matching this implementation. Missing historical record.json errors prevent treating search as exhaustive. Directly inspected context-metadata35 and ingest-scope58 for methodology; their old timings are not reused as current evidence.
