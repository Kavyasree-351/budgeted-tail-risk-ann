# Cap-constrained simultaneous mean/tail control — findings

**New setup tested:** a hard per-query distance cap, fifteen overlapping groups, three mean/severity risks, and feasible/infeasible/unknown decisions. This does not reuse the old subgroup-FNR failure gate. No publication novelty is established.

Completed 10 dataset/seed runs, 320 policy/cap conditions and 4800 group rows (three risks each). Calibration uses 5,000 fresh TRAIN vectors excluded from the index; all methods share labels. The old 400-design/600-pilot queries remain exploratory. The final 8,000 official query IDs remain unopened.

## Targets and theorem scope

For every declared group: mean FNR<=.10, Pr(FNR>.20)<=.10 and Pr(FNR>.50)<=.05. These imply 90th/95th-percentile bounds, not CVaR control. Theory.md proves deterministic cap compliance and the prefix-class floor; selected-policy and infeasibility properties specialize existing LTT/Chernoff machinery under a shared fresh-query law. Certificates remain labeled nominal: the pilot was previously inspected, and arbitrary production/OOD shift is outside the theorem.

## Feasibility profile (candidate; all five seeds retained)

| Dataset | Corpus-work cap +64 centroids | Nominally issued | Infeasibility witnesses | Insufficient evidence | Empirically infeasible finite pilot workloads |
|---|---:|---:|---:|---:|---:|
| fashion | 10% | 5/5 | 0/5 | 0/5 | 0/5 |
| fashion | 25% | 5/5 | 0/5 | 0/5 | 0/5 |
| fashion | 50% | 5/5 | 0/5 | 0/5 | 0/5 |
| fashion | 100% | 5/5 | 0/5 | 0/5 | 0/5 |
| glove | 10% | 0/5 | 5/5 | 0/5 | 5/5 |
| glove | 25% | 5/5 | 0/5 | 0/5 | 0/5 |
| glove | 50% | 5/5 | 0/5 | 0/5 | 0/5 |
| glove | 100% | 5/5 | 0/5 | 0/5 | 0/5 |

Infeasibility concerns exact-within-list PREFIX IVF under this distance counter; it is not an impossibility theorem for arbitrary ANN methods. Unknown is not rejected feasibility. When no policy is issued, diagnostic loss/work fields describe the maximum feasible prefix, NOT a deployed/certified output. Guarantees are pointwise per cap/method; choosing among all displayed caps using this calibration is not covered. A heuristic profile is not a proven optimal Pareto frontier.

## Primary 25% cap: matched-guarantee comparisons

| Dataset | Method | Issued | Mean FNR ± seed SD (issued only) | Mean total distances ± SD (issued only) | Maximum observed query distances | Empirical target-violation runs |
|---|---|---:|---:|---:|---:|---:|
| glove | overlap_repair | 5/5 | 0.0404 ± 0.0089 | 3287.3 ± 318.5 | 5064 | 0/5 |
| glove | uniform_ltt | 5/5 | 0.0341 ± 0.0056 | 4086.6 ± 256.9 | 5064 | 1/5 |
| glove | cell_shift_ltt | 5/5 | 0.0382 ± 0.0029 | 3361.5 ± 90.8 | 5064 | 0/5 |
| glove | no_overlap | 5/5 | 0.0394 ± 0.0088 | 3362.7 ± 335.3 | 5064 | 0/5 |
| glove | no_tail | 5/5 | 0.0405 ± 0.0088 | 3319.0 ± 294.1 | 5064 | 0/5 |
| glove | cap_max | 5/5 | 0.0238 ± 0.0023 | 4891.1 ± 7.3 | 5064 | 0/5 |
| glove | group_crc_capped | 0/5 | not issued | not issued | None | 0/0 |
| glove | group_crc_uncapped | 0/5 | not issued | not issued | None | 0/0 |
| fashion | overlap_repair | 5/5 | 0.0313 ± 0.0068 | 658.9 ± 42.5 | 1670 | 1/5 |
| fashion | uniform_ltt | 5/5 | 0.0195 ± 0.0059 | 825.1 ± 76.3 | 1648 | 1/5 |
| fashion | cell_shift_ltt | 5/5 | 0.0219 ± 0.0047 | 731.6 ± 29.4 | 1670 | 0/5 |
| fashion | no_overlap | 5/5 | 0.0319 ± 0.0053 | 655.5 ± 29.6 | 1670 | 1/5 |
| fashion | no_tail | 5/5 | 0.0290 ± 0.0073 | 693.7 ± 84.3 | 1951 | 0/5 |
| fashion | cap_max | 5/5 | 0.0003 ± 0.0002 | 2462.0 ± 7.4 | 2564 | 0/5 |
| fashion | group_crc_capped | 0/5 | not issued | not issued | None | 0/0 |
| fashion | group_crc_uncapped | 0/5 | not issued | not issued | None | 0/0 |

Ordinary Group CRC references are deliberately unissued for this stronger objective; their real diagnostic outcomes and cap violations remain in policy_metrics.csv/group_risks.csv. Do not compare their cheaper work as if they supplied the same tail/confidence/cap guarantee. Issued-policy empirical group violations remain possible from finite pilot variation even when a population-risk confidence theorem applies.

## Candidate versus strongest simple path, seed by seed

| Dataset | Seed | Better uniform/template baseline | Candidate/baseline work ratio | Paired work-difference upper 95% endpoint |
|---|---:|---|---:|---:|
| glove | 0 | cell_shift_ltt | 1.079 | 306.2 |
| glove | 1 | cell_shift_ltt | 0.979 | -42.2 |
| glove | 2 | cell_shift_ltt | 0.880 | -355.2 |
| glove | 3 | cell_shift_ltt | 1.043 | 184.3 |
| glove | 4 | cell_shift_ltt | 0.908 | -277.5 |
| fashion | 0 | cell_shift_ltt | 0.951 | -26.4 |
| fashion | 1 | cell_shift_ltt | 0.916 | -56.7 |
| fashion | 2 | cell_shift_ltt | 0.907 | -56.7 |
| fashion | 3 | cell_shift_ltt | 0.834 | -114.8 |
| fashion | 4 | cell_shift_ltt | 0.895 | -64.9 |

Primary gate (>=10% saving, paired upper endpoint<0, observed targets and cap all met, >=4/5 seeds on BOTH datasets): False. No threshold was relaxed after inspection. Ablation evidence counts are descriptive in gate.json; a match or loss against an ablation is retained, not hidden.

## Calibration-size ablation at primary cap

| Dataset | Method | Fresh calibration count | Nominally issued | Infeasible | Unknown |
|---|---|---:|---:|---:|---:|
| glove | overlap_repair | 1000 | 0/5 | 0/5 | 5/5 |
| glove | overlap_repair | 5000 | 5/5 | 0/5 | 0/5 |
| glove | uniform_ltt | 1000 | 0/5 | 0/5 | 5/5 |
| glove | uniform_ltt | 5000 | 5/5 | 0/5 | 0/5 |
| glove | cell_shift_ltt | 1000 | 0/5 | 0/5 | 5/5 |
| glove | cell_shift_ltt | 5000 | 5/5 | 0/5 | 0/5 |
| fashion | overlap_repair | 1000 | 5/5 | 0/5 | 0/5 |
| fashion | overlap_repair | 5000 | 5/5 | 0/5 | 0/5 |
| fashion | uniform_ltt | 1000 | 5/5 | 0/5 | 0/5 |
| fashion | uniform_ltt | 5000 | 5/5 | 0/5 | 0/5 |
| fashion | cell_shift_ltt | 1000 | 5/5 | 0/5 | 0/5 |
| fashion | cell_shift_ltt | 5000 | 5/5 | 0/5 | 0/5 |

5,000 calibration examples are additional supervision, not a free algorithmic cure for fragmentation. At 5% tail risk and .025 test level, a zero-exceedance count requires at least 72 examples in a group. The 1,000-example ablation uses a prefix of the same fresh pool; it never retunes group definitions.

## Cost, uncertainty and limits

- Every comparison uses the same corpus, labels, groups, targets, cap and confidence procedure. The calibration family is learned only on 400 design queries. Fresh calibration source rows are excluded from corpus IDs; shared train/test query-law assumptions are explicit, not guaranteed by a filename.
- Exact labeling computes distances for 400 design + 5000 calibration + 600 pilot queries. This supervision cost is shared by all methods, but is substantially larger than prior 1000-query studies. Stored truth_curve_seconds times the combined preparation, NOT calibration alone.
- path_learning_seconds covers all three design-repair variants at that cap. The recorded calibration_selection_seconds includes the 1000-prefix calibration ablation and metadata construction for path methods; it is diagnostic rather than a clean deployment-only timing.
- Query counts bound vector-distance evaluations, not wall-clock latency, memory, GPU operations or all CPU instructions. Group/cell routing and cap-prefix lookup have additional small CPU work. Zero-prefix queries incur FNR=1; no abstention is scored as success.
- Bootstrap CIs are conditional exploratory query resamples. Seed SD is descriptive; seed runs share public datasets and can share source queries. Pilot queries were seen in earlier research. No fresh official TEST confirmation is claimed.
- The maximum-p/FST multiple-risk theorem is established LTT, quantile CRC already exists, and the basic feasibility lemma is elementary monotonicity. Greedy overlap-aware allocation is a candidate heuristic without global optimality. Better numbers alone would not establish novelty.
- Full publication claims require a distinctive capability beyond known cost-aware LTT/Pareto testing, stronger ANN systems and larger/modern embedding workloads, a frozen independent confirmation run, and actual latency/memory measurements. No paper/full experiment was produced.

## Attempt ledger

1. Defined a new hard-cap and mean/tail problem plus proofs BEFORE running its pilot; did not lower the old 18% threshold.
2. Before pilot outcomes, amended calibration to 5000 fresh non-corpus TRAIN queries after deriving the small-group sample threshold. Added a 1000-prefix ablation; kept all risk/confidence/cost gates unchanged.
3. Initial process failed before the first result due memory allocation pressure. Replaced full HDF5/image/corpus float64 reads with bounded-memory streaming and verified blocked top-k against direct sorting. Archived only an old public download cache with decompressed SHA verification; previous experiment outputs were retained.
4. An intermediate process accumulated bootstrap matrices and failed before Fashion runs. Cleared the cache per seed and stored compact exact multinomial bootstrap counts; reran ALL seeds. Scientific losses, policies and targets were unchanged.
5. Retained infeasible, unknown, bad baselines, work increases and missing component improvements. Final test-query touch count remains zero.


## Finalization note

All scientific outputs and validation completed before further host-memory pressure prevented an optional final plotting rerun. The retained plots were successfully generated from the same completed metrics. Text/packaging was finalized using standard-library tools; no scientific numbers, gates or policies were changed. See THEORY.md for the source-bank sampling-without-replacement clarification.
