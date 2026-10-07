# HANDRAISER

Learning to Interrupt in Language-based Multi-agent Communication.
Authors: Danqing Wang, Da Yin, Ruta Desai, Lei Li, Asli Celikyilmaz, Ansong Ni.
Original: https://arxiv.org/html/2604.06452v2 ; PDF: https://arxiv.org/pdf/2604.06452v2 ; revised 2026-08-14.
Author-reported COLM2026 acceptance; official proceedings unchecked.
Read: §§1–6, equations, Figures1–7, Tables1–8, AppendicesA–G including prompts; PDF pp1–10,15–23; HTML L54–221,276–442. Unchecked: bibliography verification, code/data, independent venue publication.

Mechanism: chunkwise listener interruption; tree-rollout cost/quality labels train Yes/No decisions. Experiments: pictionary100, scheduling50, debate100; three seeds,10 rounds,16-token chunks. Table1 reports 8B scheduling SR .273→.307, tokens1361→1042. Token latency proxy omits measured end-to-end latency; training needs rollouts/SFT. AppendixD.3 shows premature interruption loses subsequent corrections; Table4 preserves .45 SR while messages increase13.39→20.29.

Repository inference: preserve reviewer correction edges and complete finding/evidence/repair conditions. Pending: boundary-safe optional-explanation suppression in communication workflow/eval pipeline. Smallest experiment: paired full versus gated explanations on one correction-after-prefix fixture; count recovery correctness, total tokens, latency, repair rounds, including gate overhead. Low fixture cost; streaming/model costs unknown. Reject mailbox crash-recovery adoption: paper offers no publish/ACK durability evidence. No repository gains inferred.
