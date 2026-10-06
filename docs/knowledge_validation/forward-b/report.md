# Forward task B: relabeling and dimensional modeling

Task ID: `knowledge-forward-b`. Task refs: `report.md`, `refs.json`, `evidence.txt` in `/tmp/knowledge-forward-b`.

Equal current queue lengths do **not** justify worker interchangeability. Static optimization can preserve its optimal value under a genuine symmetry of the complete constrained problem. Dynamic merging additionally requires equivalent possible futures. The proposed oscillator formula `T = length/gravity` has dimensions of time squared and therefore cannot be a period when gravity means acceleration.

## Model and actual retrieval

For scheduling, let a candidate x contain job assignments and scheduling decisions, F the feasible candidates, and f(x) the makespan (or another explicitly chosen objective). Worker data include speeds, dataset permissions, execution compatibility, communication costs, and queue contents. The proposed candidate structure is a permutation group acting on worker labels. For dynamics, a state must include everything needed to determine future actions, transitions, costs, and termination; queue counts alone need not be Markov sufficient.

For the oscillator, use positive period T, positive characteristic length l, positive gravitational acceleration g, and, when relevant, dimensionless angular amplitude a. A pendulum interpretation is a **conditional modeling choice**: the phrase “ideal oscillator” alone does not establish that l and g are its complete governing parameters.

Actual read-only queries against `skill/assets/knowledge` were:

- `worker relabeling permutation equal queues optimization symmetry dynamic transition state merging` (limit 5).
- `period length gravity units dimensional analysis dimensionless amplitude oscillator` (limit 5).

The first retrieved `math.symmetry-quotient` and the unrelated `math.topk-margin`; only the former was read and used. The second retrieved `physics.dimensionless`, which was read and used. Relevance scores were treated only as lexical candidate ranking. Both used entries report `requires: []`, so there are no further strong dependencies to read. Exact command output and full entry reads are in `evidence.txt`.

## Assumptions mapped to the problem

| Required condition | Task evidence | Judgment |
|---|---|---|
| A permutation group acts on complete candidate solutions | Three worker labels exist, but the proposed action was not fully specified | Must define the action, not just sort counts |
| Feasibility is preserved in both directions | Only one worker can access the dataset | Generally fails for swaps involving that worker |
| Objective is invariant | One worker executes a job twice as fast | Generally fails when that job is moved to another worker |
| Actions, transitions, costs, and termination correspond | Only current queue equality is given | Not established; counterexample below |
| A physical relation is invariant under changes of units | Intended for a physical period | Required; proposed formula fails |
| Listed variables capture all relevant physical parameters | Only “ideal oscillator,” length, gravity are specified | Unknown; pendulum results are conditional |
| Positive variables for monomial dimensional modeling | l > 0, g > 0, finite positive T assumed | Satisfied in the stated model |

## When static relabeling preserves an optimum

Let G act on F, with `x ∈ F iff πx ∈ F` and `f(πx) = f(x)` for every π in G. Choose one representative per orbit. Every removed feasible candidate has a retained candidate with the same objective; consequently the infimum is unchanged, and if a minimum is attained, an optimal representative exists. This is a sufficient condition, not a claim that no other reduction could work.

For a fixed scheduling instance, permuting assignment labels must preserve worker-specific speeds for relevant jobs, permissions, capacities, network relations, constraints, and every term of the objective. Only permutations preserving that full structure are safe under this argument. Depending on which worker is fast and which has dataset access, some smaller subgroup may survive, or only the identity may survive. Equality of queue counts alone establishes none of these requirements.

A different operation is a consistent renaming of **all** worker records, including speed, permission, queues, topology endpoints, and assignments. That produces an isomorphic representation of the same physical schedule, even for heterogeneous workers; it does not authorize moving a job between two fixed physical workers while leaving their attributes fixed. If all labeled optimal schedules are requested, retaining only representatives also loses requested labeled outputs unless those are reconstructed.

Concrete static counterexample: choose speeds `(2,1,1)` work units/second, with only worker 3 permitted to run dataset job D. Initially all three queues are empty. Generic job A has 2 units and D has 1 unit. Assigning A to worker 1 and D to worker 3 gives makespan `max(2/2,1/1)=1 s`. Swapping workers 1 and 2 in the assignments gives `max(2/1,1/1)=2 s`. Swapping workers 1 and 3 moves D to an unauthorized worker, making the assignment infeasible. Thus a naive representative can remove a better or even feasible solution despite equal initial counts.

## Why dynamic merging needs more

A sufficient deterministic condition is an action bijection `a ↦ πa` between states s and πs, equal stage costs, `P(πs,πa)=πP(s,a)`, and matching terminal status and terminal costs. These conditions make complete future trajectories and accumulated costs correspond, supporting equality of optimal continuation values. For stochastic models, require corresponding transition probability distributions, or an appropriate reward-preserving bisimulation/lumpability condition on the quotient; equality of immediate costs is insufficient. Time, remaining service, future arrival laws, resource permissions, and job identity may all matter.

Independent dynamic example: again use speeds `(2,1,1)`, with dataset access exclusive to worker 3. There are no new arrivals, all jobs are ready, and each worker processes its one assigned job to completion. State s assigns work `(4,1,1)` to workers `(1,2,3)`; the last job requires the dataset. State s' swaps the two generic jobs, giving `(1,4,1)`. Both have queue-count vector `(1,1,1)`, yet their remaining makespans are `max(4/2,1,1)=2 s` and `max(1/2,4,1)=4 s`. Their next completion times also differ: 1 s versus 0.5 s. Hence neither the transition timing nor continuation value is determined by the queue counts. This counterexample does not assume that equal counts imply equal amounts of work.

## Dimensional model and its limits

Use base dimensions L (length) and τ (time). Then `[T]=τ`, `[l]=L`, and `[g]=L τ^-2`. With columns `(T,l,g)` and rows `(L,τ)`, the dimension matrix is

```
D = [[0, 1,  1],
     [1, 0, -2]].
```

It has rank 2 and nullspace dimension 1. The vector `(1,-1/2,1/2)` gives the dimensionless group `Π = T sqrt(g/l)`. Equivalently, a power-law ansatz `T = C l^p g^q` yields `p+q=0`, `-2q=1`, hence `p=1/2`, `q=-1/2`.

If l and g are indeed the complete dimensional inputs and a unique period is defined on the chosen physical branch, dimensional consistency gives `T = C sqrt(l/g)`. It identifies scaling, not C, the governing dynamics, stability, the existence of periodic motion, or completeness of the variable list. A mass-spring oscillator, for example, requires stiffness and mass; “ideal” does not turn it into a gravity pendulum. Damping, forcing, additional lengths, or initial-condition parameters may introduce further groups.

The proposed `l/g` has units τ². At `l=1 m`, `g=9.81 m/s²`, it is `0.101936799 s²`; its square root is `0.319275428 s`. Changing the time unit to milliseconds makes g numerically `9.81×10^-6 m/ms²`. The proposed expression then grows by 10^6, whereas a period's numeric value should grow by 10^3. This directly checks the unit failure.

Adding dimensionless amplitude a appends a zero column to D. Rank stays 2, but with four variables the nullspace dimension becomes 2: use `Π` and a. The model becomes `Π=F(a)`, or `T=sqrt(l/g) F(a)`, when a single-valued period exists. Dimensionless does **not** mean physically irrelevant; dimensional analysis leaves F undetermined. Linearization may predict a constant F, but that is additional dynamical information.

For a concrete conditional calculation, assume an undamped simple pendulum obeying `θ''+(g/l) sin θ=0`. Multiplying by θ' and integrating for turning angle a gives `θ'^2=(2g/l)(cos θ−cos a)`. A quarter-period integral with `sin(θ/2)=sin(a/2) sin u` then yields

`T = 4 sqrt(l/g) ∫₀^(π/2) [1−sin²(a/2) sin²u]^-1/2 du`.

In the small-amplitude limit the integral tends to π/2, giving `C=2π`; that constant follows from the assumed dynamics, not dimensions. For `l=1 m`, `g=9.81 m/s²`, the small-amplitude period is `2.006066681 s`; at amplitude `a=π/3` it is `2.152874667 s`, an increase of about `7.3182%`. Simpson quadrature at 5,000 and 10,000 intervals agreed to displayed floating-point precision. This is numerical evidence, not a rigorous error bound. For pendulum libration require `0<a<π`; the period diverges approaching π, and at exactly zero amplitude the resting solution has no observed oscillation although its limiting linear period is defined.

## Provenance, checks, and limits

Actual used refs (also machine-readable in `refs.json`):

| ID | Version | SHA-256 |
|---|---:|---|
| `math.symmetry-quotient` | 1 | `b6f49f38838a976fdf42589d923d818119438b749049a6a69104449afabf2e57` |
| `physics.dimensionless` | 1 | `06d0c7f8b08727194bb340cae3dc9e31e2606e38a1b59a668b36430311f97dd3` |

Snapshot: `5744245725a198e45a2b5b9c8da7df89617b09930442d2bbd66ae94fb9db46f6`. `check-refs /tmp/knowledge-forward-b/refs.json` passed after writing the refs, including dependency closure. Independent Python assertions checked scheduling costs and the dimensional null vector; numerical outputs and reproducible code are `checks.json` and `run_checks.py`. The unmerged scheduling candidates provide the baseline showing why the proposed reduction changes results.

No external browsing, repository tests, rubrics, other agents' work, formal prover, or scheduling performance benchmark was used. The external MIT sources are provenance recorded in the local entries, not pages independently re-opened in this run. Local retrieval and hash checks establish which knowledge was used, not its scientific correctness. The reasoning is a task-specific mathematical derivation with finite numerical checks; it does not establish practical speedup. The planner must still supply the full worker/job model to certify any nontrivial symmetry subgroup, and the simulator must identify its oscillator dynamics and amplitude regime before assigning a physical period law.
