# Hard-cap simultaneous tail control — frozen 28 October 2026

## New problem, not a relaxed old gate
The old >=18% subgroup-FNR gate is retired for this DIFFERENT setup, not lowered until it passes. All queries must count toward loss. Prefix-IVF search has a strict per-query TOTAL distance-computation cap B; no silent exact fallback beyond B, no deleting failed queries, and no calling abstention zero loss. Return one of: nominally certified policy / statistically evidenced infeasible cap / insufficient calibration evidence.

Mean target remains E[FNR|g]<=.10. Additional severity targets for EVERY declared group:

- Pr(FNR>.20|g)<=.10 (90th-percentile FNR<=.20).
- Pr(FNR>.50|g)<=.05 (95th-percentile FNR<=.50).

These are actual loss-tail constraints, distinct from input-difficulty deciles. Empirical CVaR90 is a diagnostic only; no CVaR guarantee is claimed. Targeting a new risk functional does not itself establish novelty.

## Theory and closest baseline
Fixed-sequence Learn-then-Test (LTT), with the maximum of constraint p-values (intersection-union testing), ALREADY controls multiple risks without a group-times-policy Bonferroni penalty. That is a strong baseline and a tool, not an invented theorem. The candidate contribution to investigate is a design-learned overlap/severity-aware, work-efficient NESTED allocation path plus an explicit prefix-class feasibility frontier. Generic multicalibration, quantile CRC and CVaR control already have prior work.

Prove: (i) deterministic hard-cap compliance, (ii) pointwise risk-floor domination by the maximum feasible prefix, (iii) finite-sample simultaneous group/quantile safety of a selected path member under fresh independent calibration, (iv) a valid infeasibility witness or an honest unknown. These are useful specialization properties, not automatically original A* theorems. No claim of unrestricted ANN impossibility.

## Data and blind-data count
Same public GloVe-25/Fashion corpora and the SAME already explored 2,000-query bank, seeds 0..4: 400 design / 1000 calibration / 600 exploratory pilot. Design labels may train the path. Final 8,000 official query IDs remain untouched. NO new test queries opened. Because these calibration/pilot observations have been explored in previous projects, certificates here are NOMINAL exploratory certificates: the prospective theorem assumes independent calibration and does not magically repair adaptive research reuse. Fresh calibration/confirmation is required before a real deployment or positive paper.

Fixed 64-list IVF, k=10. Float64 exact reference distances; deterministic ties. Full-list prefix search only: all vectors in a probed list are evaluated. Vector-distance operation counts include 64 required centroid distances. No GPU/latency claim. A zero-list prefix returns an empty result with FNR=1; it is never treated as free success.

## Fixed features, groups and path family
Design-defined ambiguity deciles: nearest/second-nearest centroid distance ratio. A second feature is nearest-centroid distance, split at its DESIGN median (a geometric-distance proxy, not a verified OOD or density label).

Fifteen overlapping groups: all queries; ten ambiguity deciles; near/far halves; upper-five-decile ambiguity intersected with near/far halves. All are retained even if small; no post-hoc dropping of difficult groups. The policy lookup has ten cells: ambiguity QUINTILE x near/far. Calibration-group overlap reuses observations instead of partitioning into all atoms; this does not eliminate small-group sample complexity.

Candidate path: start with zero probe budgets; using DESIGN labels, greedily increase a policy-cell budget, selecting the largest reduction in the sum of normalized mean/tail risks per added average corpus-distance operation. Jumps may skip budgets with no design benefit. Complete the nested path by common-offset increases through the maximum feasible prefix. Group/risk weights fixed by targets, not tuned. Family built independently of current calibration labels at algorithm level.

Strong baselines with IDENTICAL certification and cap: uniform-budget LTT; design-cell CRC-template plus offset LTT; maximal feasible prefix. Ablations: omit overlapping groups ONLY from the DESIGN objective; omit tail components ONLY from that objective. All paths are still calibrated against ALL fifteen groups and ALL three risks, so guarantees are matched. Also report ordinary uncapped Group CRC and its naively capped version as UNCERTIFIED references, not strong safety competitors.

## Budgets, calibration and status
Primary B=64+floor(.25*N) TOTAL comparisons per query. Secondary cap fractions .10,.50,1.00 are predefined diagnostics; no cap selected after calibration to claim joint frontier safety. Each cap has a pointwise confidence statement, not a simultaneous all-caps guarantee.

Use delta=.05 per fixed method/cap, split .025 to selected-policy false acceptance and .025 to a false infeasibility conclusion. At each fixed path member, test every bounded risk using one-sided KL/Chernoff p-values; their maximum is a valid intersection-union p-value. Test the predetermined path from safest to cheapest, stopping at the first non-rejection. Exact full search may bypass a statistical test only when it is structurally exact for ALL possible feature cells and respects B (the 100% cap). Never infer structural zero risk from zero observed losses.

### Pre-pilot amendment: genuinely fresh calibration, unchanged targets
Frozen AFTER proving the 72-example zero-catastrophe requirement and BEFORE any new pilot performance: primary calibration uses 5,000 previously unused query vectors sampled from TRAIN rows EXCLUDING the index corpus. This does not access any of the 8,000 reserved official TEST queries. Original 400 design/600 exploratory pilot query IDs remain unchanged; the prior 1,000 exploratory calibration queries are NOT used for certificates in this study. A first-1,000 subset of the fresh calibration pool is a predefined calibration-size ablation, not a search over sample sizes after outcomes. All methods get identical fresh labels. Record source-row IDs, disjointness and the real 5,000-query exact-label cost; do not attribute the benefit of more labels to a new algorithm.

This amendment supersedes the old reused-calibration paragraph above. The method/path can depend on earlier research/design queries but is fixed before this fresh calibration sample. Prospective population claims additionally assume train-derived calibration queries and future queries follow the same within-group query law; official train/test splitting does not by itself prove that under arbitrary domain shift. The old pilot remains exploratory/exposed; no independent TEST confirmation is claimed. Across seeds, public calibration pools can overlap; they are not independent external datasets.

Infeasibility: let p_B(q) be the largest whole-list prefix fitting B. Every admissible prefix policy has FNR>=L(q,p_B(q)) pointwise; the same holds for severity events. Reject feasibility only if a lower-confidence test for one floor-risk component excludes its target, corrected over all 45 constraints at .025. Otherwise lack of certification is UNKNOWN, not infeasible. No selected-policy safety statement across arbitrary benchmark-method selection; the prospective theorem concerns a fixed algorithm.

## New preregistered opportunity gate
At the PRIMARY 25% cap, require: zero query cap violations; candidate issued in >=4/5 seeds on BOTH datasets; empirical mean/tail targets met in every OBSERVED group in those issued runs; >=10% mean TOTAL distance-work reduction against the BETTER issued uniform-LTT/template-LTT baseline on matched queries, with paired-bootstrap work-difference upper endpoint<0 in >=4/5 seeds on both datasets. Require component evidence against both ablations, not just versus ordinary expected-risk Group CRC. These strict operational criteria need not pass. No uncertainty or infeasible run silently removed from coverage statistics.

Report all caps, statuses, constraint sample counts, nominal certificates, empirical pilot risk, CVaR90, query bootstrap CIs, mean/SD over seeds, work maxima and selection/learning time. 2000 paired query bootstraps. Group/constraint empty samples are missing/uncertified, not zero. Positive-control smoke tests and deterministic cap/feasibility/path checks precede the pilot. Full/fresh-data experiments and a paper remain pending unless a distinct contribution AND this gate survive.
