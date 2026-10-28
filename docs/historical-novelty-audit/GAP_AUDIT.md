# Gap-first research audit

26 October 2026. **No new contribution has been established and no new model-training experiment is authorized by the novelty gate yet.** This audit is an actual screening result, not a paper proposal presented as verified originality.

## Research standard

Before an experiment, identify a concrete unsupported condition, read the closest method and its later extensions, and check whether general statistical machinery already solves the proposed claim. Choose ONE primary contribution: a genuinely distinct method, a nontrivial new theorem, or an independently replicated consequential empirical discovery. A new application of standard calibration, a new name or more benchmarks is insufficient.

No original held-out data are opened during this audit. Previous negative experiments remain unchanged. The user has authorized autonomous research; the following gates are scientific criteria, not requests for additional permission.

## Screening ledger

| Candidate | Closest evidence found | Decision |
|---|---|---|
| Upfront cost and deployment payback | SaveRouter already charges supervision and defines amortized payback | Reject broad novelty claim; previously tested |
| Joint predictor/label allocation | AM-PPI already jointly optimizes predictor subsets, labels and weights | Reject broad claim; previous pilots failed |
| Dependence-aware model-set routing | CopRoute explicitly models complementary failures; RACER already controls model-set risk | Reject generic dependence/calibration combination |
| Cache-aware session routing | Stateful routing and model-switch/KV-cache work already studies the mechanism | Reject generic cache-aware router |
| Reuse calibration after cost-setting changes | CR2 handles operating-point-specific calibration; finite-family simultaneous testing already permits arbitrary later cost-based selection | Reject the simple claim; any continuum/sample-efficiency result requires a genuinely new argument |
| Conformal approximate retrieval | ConANN already provides IVF recall-risk control; DARTH/DARTH+ address runtime recall prediction | Reject generic 'conformal ANN' as a new method |
| Post-calibration query-dependent retrieval size | ConANN authors explicitly qualify variable-k guarantees; a query-dependent policy selected after calibration is different from a fixed or independently randomized k | Retain as a PROVISIONAL empirical question; not novelty-cleared |

## Why price adaptation alone is not a new theorem

Suppose K router policies are fixed independently of n IID calibration observations, each loss is in [a,b], and the empirical mean of policy j is Rhat_j. Hoeffding plus a union bound gives, simultaneously for all j, with probability >=1-delta:

    R_j <= Rhat_j + (b-a)*sqrt(log(K/delta)/(2*n)).

After that event holds, an operator can choose any certified policy using any sequence of price vectors or budget preferences. The safety statement survives those choices. This is an elementary instance of uniform testing/risk control, not a new contribution. It requires unchanged data-generating distribution, losses, policy family and model outputs. It does not solve continuum-policy efficiency, distribution drift, changed model versions or selective missing feedback.

Thus, 'prices change, but do not buy new labels' is not enough as a novelty claim. The current literature screening did not establish a nontrivial improvement over these existing tools.

## Most concrete remaining lead: selection after retrieval calibration

Engineering setting: a vector-search/RAG application changes the number k of returned neighbors according to the query or inexpensive search trace. An ANN recall certificate obtained separately for each fixed k may not survive a newly selected query-dependent k policy.

Closest primary-source observation: ConANN's official repository reports variable-k experiments but explicitly states that fixed-k calibration does not automatically establish formal validity for varying-k test queries, and that out-of-range k can break the guarantee. This is an acknowledged scope limitation, NOT evidence of a defect in the authors' theorem.

The narrowly stated question is:

> Is the distinction between fixed-k marginal recall control and post-calibration query-dependent k consequential in realistic ANN workloads, and can existing selection-safe baselines preserve the target without eliminating the speed advantage?

The main contribution, if supported, would be an **empirical discovery with a demonstrated mechanism and independent replication**, not claiming to invent selection bias or conformal calibration.

### Why the lead has not cleared the gate

1. Generic selection-safe calibration and a worst-over-k loss envelope already offer standard repairs. Applying them to retrieval is not automatically a new algorithm.
2. DARTH+ advertises probabilistic recall guarantees. Its complete assumptions and adaptive-k behavior must be checked before claiming a gap over it. The author-hosted HAL landing page was access denied during this audit; the author overview and original DARTH paper are available. No claim is made about an unread theorem.
3. Guaranteed adaptive-K recommendation and selection-safe early exits are adjacent prior work and must be compared explicitly. Changing the domain alone is insufficient.
4. A worst-case toy counterexample establishes only that marginal statements do not imply a selected-policy statement. It does not establish a practical ANN failure or an original theorem.

### Required baselines if the literature gate clears

- Fixed-k ConANN and the authors' variable-k implementation.
- Calibration using the EXACT deployed k-selector, selected before independent calibration. This may already solve the practical problem; do not omit it.
- Simultaneous finite-grid testing over k and a worst-over-k risk envelope.
- DARTH+, with its actual guarantee and implementation reproduced faithfully where feasible.
- Standard IVF/HNSW with separately tuned per-k search effort, matched recall targets and wall-clock measurements.

### Pre-experiment opportunity criteria

Freeze these before any retrieval performance outcomes are examined. Use separate design, calibration, pilot, confirmation and final query pools. A selector may use only query/trace information available before returning results; it must not inspect exact neighbors or recall at inference. Test natural selectors first. A deliberately adversarial selector is a labeled stress test, not the headline result.

An opportunity requires a practically material recall-risk discrepancy on at least two independently sourced vector datasets, across five index/calibration seeds; intervals must distinguish it from target slack. Existing selector-specific calibration and simultaneous/envelope baselines must be tested at matched risk. A proposed efficiency improvement must preserve recall, retain a material latency/probe advantage, and survive confirmation with a frozen selector on another index family or query distribution. Exact thresholds must be selected after reading the remaining closest method, BEFORE running the pilot; they are not yet frozen here because the comparison set is incomplete.

If these baselines eliminate the claimed gap or the effect is only visible for an oracle selector, reject the direction. Do not create a new-method paper from it.

## Primary sources inspected or explicitly pending

- SaveRouter: https://arxiv.org/abs/2609.37402 ; primary full text was read in the previous lifecycle study.
- AM-PPI: https://arxiv.org/abs/2605.08429 ; primary full text was read in the previous acquisition study.
- RACER: https://proceedings.mlr.press/v306/hao26c.html ; https://arxiv.org/html/2603.06616v1 . Set-level routing risk is already studied.
- CR2: https://arxiv.org/html/2605.12001v1 . Cost-aware routing and operating-point calibration are already studied.
- CopRoute: https://arxiv.org/abs/2610.13276 . Dependence-aware calibrated model-set routing is already proposed.
- Stateful routing: https://arxiv.org/abs/2610.19292 ; https://arxiv.org/abs/2508.11291 . Screening sources; full algorithm reproduction is not claimed.
- Learn then Test: https://arxiv.org/abs/2110.01052 . General simultaneous testing is established.
- ConANN: https://www.vldb.org/pvldb/vol19/p29-horchidan.pdf ; https://github.com/soniahorchidan/conann . Read paper excerpts and official variable-k discussion.
- DARTH: https://arxiv.org/abs/2505.19001 ; author overview https://mchatzakis.github.io/declarative-recall/ . Original runtime recall prediction is established.
- DARTH+: https://hal.science/hal-05566027 . Full-text theorem audit PENDING because this landing page returned access denied. Do not treat the missing review as absence of prior work.
- Selection-safe early exit: https://arxiv.org/abs/2610.20773 . Adjacent generic selection-safe principle; direct transfer is not novelty.

## Outcome of this stage

The audit has filtered out several ideas BEFORE another model sweep. One retrieval question remains a concrete lead, but it has not passed the novelty gate. No training or retrieval performance result is claimed. Next dependent work is the remaining closest-paper/theorem audit, followed by a frozen protocol only if that audit clears. This is a bounded gap-screening deliverable, not a claim that every possible AI-engineering topic has been exhausted.
