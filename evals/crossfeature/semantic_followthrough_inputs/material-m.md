# Stable Group Summaries on Constructed Integer Lists

## Abstract
We examine whether grouping adjacent equal symbols preserves total multiplicity. For [2,2,5,5,5,9], the grouped representation is [(2,2),(5,3),(9,1)] and reconstructs six elements. This is a deterministic mechanism example, not a benchmark or novelty claim.

## Introduction
A compact representation must distinguish the number of groups from the number of elements. Our question is whether a group-count consumer can stand in for an element-count consumer. We provide a counterexample and an explicit invariant.

## Related work
Only the supplied synthetic source note is available. No published-source learning or comparison to literature has been performed; citation and submission readiness remain unverified.

## Method
Traverse the integer sequence in order. Extend the last group when the symbol matches; otherwise append a new group of count one. Reconstruction repeats each symbol by its count. The sum of group counts equals input length; the number of groups generally does not.

## Evaluation
For the six input elements above, counts sum to 2+3+1=6 while there are three groups. For the separate boundary [4,4], there is one group of count two. Empty input yields no groups and zero elements. These exact outputs support the invariant in these examples only; an implementation proof or broad test suite is not supplied.

## Limitations
All inputs are tiny synthetic integer lists. There is no measured speed, uncertainty estimate, real workload or production implementation. No graphical figure is requested for this text-only mechanism brief. A manuscript prepared for submission would require its own template, full reference learning and independent delivery checks.

## Conclusion
For the constructed examples, grouped storage can preserve multiplicity only when consumers sum counts. Counting groups alone loses that quantity.
