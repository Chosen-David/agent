# AgentSpec reading 3/10

Haoyu Wang, Christopher M. Poskitt, Jun Sun. arXiv:2503.18666v3,
2025-07-31. Original: https://arxiv.org/html/2503.18666v3
Read §§1–8, Tables1–6, formal definitions, code-rule figures2/3/5–8;
actually viewed Figure4 architecture. Bibliography not systematically checked;
no appendix present in retrieved HTML. ICSE26 metadata appears in this version;
final proceedings/official venue status not separately verified.

Question/mechanism: prevent an unsafe proposed action using explicit
trigger→predicate→enforcement outside the model. §4 hooks LangChain0.3.13
AgentAction/AgentStep/AgentFinish; predicates still require correct implementation.
§5 uses RedCode, SafeAgentBench and FixDrive. Table4 safe completion falls
58.62→54.26%; Table6 generated AV rules handle5/8. §5.3 records example-bound
rules, false positives and missed contexts. §5.5 separates millisecond checks
from human/model/action enforcement latency. §6.3 excludes long-horizon reasoning.
No component-removal ablation establishes this repository's recovery gains.

Own inference: pre-action checks could enforce recipient/receipt intent here,
but a precheck cannot remove an inter-call race or supply durable crash recovery.
Existing Mailbox validators and ownership are stronger than free-form reflection
for exact state facts. Candidate: scoped existing-adapter precondition tests
(`communication.py`, communication workflow; CO-025), low incremental cost;
minimum experiment is frozen conflicting receipt/valid restart controls.
Pending, not adopted. Reject DSL/runtime import: duplicate machinery and no
measured benefit. Paper detection rates/costs do not transfer to our workload.
