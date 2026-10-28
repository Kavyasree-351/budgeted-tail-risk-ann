# Direction B — verified exploratory findings

**A subgroup gap is observed on GloVe, but the predefined >=18% primary failure gate is not met. Groupwise CRC is useful engineering here; a novel publishable method is not established.**

Completed 10 dataset/seed runs, two calibration scenarios, ten methods and 2800 subgroup/method conditions. All use the previously explored public query bank. Reserved final queries remain unevaluated. No paper or full benchmark has been generated.

## Primary result: unchanged query mixture

| Dataset | Global marginal FNR | Global top-two-decile FNR | Group CRC top-two-decile FNR | G-CRC/global total-work ratio | Primary passing seeds |
|---|---:|---:|---:|---:|---|
| glove | 0.0873 | 0.1508 | 0.0905 | 0.988 | [] |
| fashion | 0.0470 | 0.0950 | 0.0843 | 0.814 | [] |

Means above average five fitted runs, not independent production datasets. Seed SD and conditional query-bootstrap intervals are in summary.csv/results.csv. A pooled top-two-decile mean is not an individual decile guarantee. The lower 15% secondary criterion was prespecified and is reported in gate.json; it does not replace the failed 18% primary criterion.

## Matched-query method and ablation comparison

Total query distance work includes the common 64 centroid comparisons; exact search does not need centroids. Work ratio is relative to global CRC on the same seed, pilot and scenario. Empirical violating-decile fraction counts observed decile mean FNR>.10 and is NOT a formal violation probability.

| Dataset | Scenario | Method | Marginal FNR mean ± SD | Hard-pair FNR mean ± SD | Work ratio mean ± SD | Empirical violating-decile fraction |
|---|---|---|---:|---:|---:|---:|
| glove | iid | exact | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 8.830 ± 0.541 | 0.00 |
| glove | iid | global_crc | 0.0873 ± 0.0019 | 0.1508 ± 0.0185 | 1.000 ± 0.000 | 0.42 |
| glove | iid | group_crc10 | 0.0806 ± 0.0072 | 0.0905 ± 0.0178 | 0.988 ± 0.066 | 0.22 |
| glove | iid | group_crc2 | 0.0897 ± 0.0122 | 0.0960 ± 0.0177 | 0.969 ± 0.090 | 0.42 |
| glove | iid | group_crc5 | 0.0827 ± 0.0073 | 0.0960 ± 0.0177 | 0.973 ± 0.065 | 0.26 |
| glove | iid | group_kl10 | 0.0039 ± 0.0013 | 0.0048 ± 0.0025 | 5.165 ± 0.485 | 0.00 |
| glove | iid | monotone_crc10 | 0.0786 ± 0.0086 | 0.0875 ± 0.0194 | 1.003 ± 0.081 | 0.18 |
| glove | iid | ood_exact_fallback | 0.0873 ± 0.0019 | 0.1508 ± 0.0185 | 1.000 ± 0.000 | 0.42 |
| glove | iid | shuffled_crc10 | 0.0832 ± 0.0080 | 0.1461 ± 0.0256 | 1.052 ± 0.064 | 0.38 |
| glove | iid | worst_uniform | 0.0466 ± 0.0082 | 0.0812 ± 0.0197 | 1.503 ± 0.139 | 0.04 |
| glove | heldout_cells | exact | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 8.830 ± 0.541 | 0.00 |
| glove | heldout_cells | global_crc | 0.0873 ± 0.0019 | 0.1508 ± 0.0185 | 1.000 ± 0.000 | 0.42 |
| glove | heldout_cells | group_crc10 | 0.0754 ± 0.0060 | 0.0859 ± 0.0148 | 1.032 ± 0.064 | 0.12 |
| glove | heldout_cells | group_crc2 | 0.0827 ± 0.0106 | 0.0918 ± 0.0227 | 1.018 ± 0.085 | 0.38 |
| glove | heldout_cells | group_crc5 | 0.0797 ± 0.0071 | 0.0918 ± 0.0227 | 1.004 ± 0.074 | 0.20 |
| glove | heldout_cells | group_kl10 | 0.0005 ± 0.0005 | 0.0003 ± 0.0004 | 7.668 ± 0.539 | 0.00 |
| glove | heldout_cells | monotone_crc10 | 0.0727 ± 0.0088 | 0.0802 ± 0.0170 | 1.061 ± 0.095 | 0.06 |
| glove | heldout_cells | ood_exact_fallback | 0.0691 ± 0.0043 | 0.1210 ± 0.0215 | 2.598 ± 0.212 | 0.24 |
| glove | heldout_cells | shuffled_crc10 | 0.0803 ± 0.0070 | 0.1430 ± 0.0234 | 1.086 ± 0.059 | 0.38 |
| glove | heldout_cells | worst_uniform | 0.0452 ± 0.0076 | 0.0778 ± 0.0164 | 1.529 ± 0.127 | 0.02 |
| fashion | iid | exact | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 16.273 ± 0.392 | 0.00 |
| fashion | iid | global_crc | 0.0470 ± 0.0063 | 0.0950 ± 0.0070 | 1.000 ± 0.000 | 0.10 |
| fashion | iid | group_crc10 | 0.0653 ± 0.0073 | 0.0843 ± 0.0240 | 0.814 ± 0.038 | 0.10 |
| fashion | iid | group_crc2 | 0.0788 ± 0.0152 | 0.0843 ± 0.0240 | 0.821 ± 0.105 | 0.36 |
| fashion | iid | group_crc5 | 0.0645 ± 0.0105 | 0.0843 ± 0.0240 | 0.822 ± 0.053 | 0.12 |
| fashion | iid | group_kl10 | 0.0039 ± 0.0020 | 0.0039 ± 0.0037 | 5.293 ± 0.768 | 0.00 |
| fashion | iid | monotone_crc10 | 0.0653 ± 0.0073 | 0.0843 ± 0.0240 | 0.814 ± 0.038 | 0.10 |
| fashion | iid | ood_exact_fallback | 0.0470 ± 0.0063 | 0.0950 ± 0.0070 | 1.000 ± 0.000 | 0.10 |
| fashion | iid | shuffled_crc10 | 0.0530 ± 0.0092 | 0.1076 ± 0.0197 | 0.969 ± 0.039 | 0.14 |
| fashion | iid | worst_uniform | 0.0421 ± 0.0128 | 0.0843 ± 0.0240 | 1.056 ± 0.126 | 0.08 |
| fashion | heldout_cells | exact | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 16.273 ± 0.392 | 0.00 |
| fashion | heldout_cells | global_crc | 0.0470 ± 0.0063 | 0.0950 ± 0.0070 | 1.000 ± 0.000 | 0.10 |
| fashion | heldout_cells | group_crc10 | 0.0626 ± 0.0033 | 0.0673 ± 0.0235 | 0.830 ± 0.025 | 0.08 |
| fashion | heldout_cells | group_crc2 | 0.0788 ± 0.0152 | 0.0843 ± 0.0240 | 0.821 ± 0.105 | 0.36 |
| fashion | heldout_cells | group_crc5 | 0.0645 ± 0.0105 | 0.0843 ± 0.0240 | 0.822 ± 0.053 | 0.12 |
| fashion | heldout_cells | group_kl10 | 0.0010 ± 0.0010 | 0.0003 ± 0.0004 | 12.275 ± 1.546 | 0.00 |
| fashion | heldout_cells | monotone_crc10 | 0.0608 ± 0.0021 | 0.0581 ± 0.0275 | 0.842 ± 0.035 | 0.08 |
| fashion | heldout_cells | ood_exact_fallback | 0.0390 ± 0.0059 | 0.0817 ± 0.0098 | 3.973 ± 0.651 | 0.02 |
| fashion | heldout_cells | shuffled_crc10 | 0.0542 ± 0.0115 | 0.1079 ± 0.0204 | 0.967 ± 0.042 | 0.14 |
| fashion | heldout_cells | worst_uniform | 0.0264 ± 0.0125 | 0.0527 ± 0.0289 | 1.230 ± 0.129 | 0.04 |

## Per-seed efficiency and residual risk

| Dataset | Seed | G-CRC/global work ratio | Paired mean work difference [95% bootstrap interval] | Observed violating-decile fraction |
|---|---:|---:|---:|---:|
| fashion | 0 | 0.787 | -133.6 [-146.6, -121.1] | 0.10 |
| fashion | 1 | 0.776 | -140.7 [-154.0, -128.0] | 0.10 |
| fashion | 2 | 0.837 | -96.2 [-108.6, -84.6] | 0.10 |
| fashion | 3 | 0.868 | -81.5 [-97.1, -65.2] | 0.00 |
| fashion | 4 | 0.802 | -121.3 [-135.2, -108.1] | 0.20 |
| glove | 0 | 1.037 | 84.3 [6.4, 163.4] | 0.20 |
| glove | 1 | 0.946 | -126.8 [-196.0, -53.3] | 0.30 |
| glove | 2 | 0.934 | -155.7 [-226.9, -88.0] | 0.30 |
| glove | 3 | 1.079 | 161.5 [93.1, 227.6] | 0.10 |
| glove | 4 | 0.944 | -130.2 [-200.3, -63.6] | 0.20 |

The GloVe mean work ratio is slightly below one, but individual seeds include increases: an averaged saving is not evidence of no inflation for each run. Group CRC also leaves some realized pilot deciles above .10; its theorem is expected mean-risk control over calibration randomness, not a simultaneous certificate for every realized decile. The KL control is the simultaneous-confidence alternative and incurs much larger work.

## Held-out coarse-cell diagnostic

| Dataset | Method | Held-cell FNR mean | Seen-cell FNR mean |
|---|---|---:|---:|
| glove | global_crc | 0.0903 | 0.0866 |
| glove | group_crc10 | 0.0801 | 0.0742 |
| glove | group_kl10 | 0.0013 | 0.0003 |
| glove | ood_exact_fallback | 0.0000 | 0.0866 |
| fashion | global_crc | 0.0410 | 0.0484 |
| fashion | group_crc10 | 0.0549 | 0.0643 |
| fashion | group_kl10 | 0.0004 | 0.0011 |
| fashion | ood_exact_fallback | 0.0000 | 0.0484 |

Held cells are geometric exclusions, not semantic domain/OOD labels. Group CRC calibrated on other cells does not gain an unseen-support guarantee merely by sharing ambiguity bins. OOD exact fallback is explicitly conservative. These already explored query IDs are not fresh OOD confirmation.

## Feature and fitting overhead

| Dataset | Seed | Median feature/bin time per query (microseconds, 600-query batch) | Shared exact calibration-truth/curve time (seconds) |
|---|---:|---:|---:|
| fashion | 0 | 0.657 | 2.415 |
| fashion | 1 | 0.427 | 2.595 |
| fashion | 2 | 0.414 | 2.807 |
| fashion | 3 | 0.912 | 2.660 |
| fashion | 4 | 0.692 | 2.481 |
| glove | 0 | 0.428 | 0.612 |
| glove | 1 | 0.428 | 0.768 |
| glove | 2 | 0.493 | 0.708 |
| glove | 3 | 0.597 | 1.020 |
| glove | 4 | 0.425 | 0.682 |

All methods reuse identical calibration labels. Feature timing reuses existing centroid distances; it is not complete serving latency. Selection is O(nlist) CPU plus O(log 10) lookup, with zero extra corpus distances, not literal O(1) in index size. Fit times for both scenarios are in each metrics JSON.

## Novelty and limits

- The numerical assumption of 25–35% hard/OOD risk was not established. A marginal/subgroup gap is not a defect in the original marginal CRC theorem or proof of broken exchangeability.
- Groupwise/Mondrian calibration and conditional risk control already exist, including the closely related HG-CRC preprint. Applying them to this ANN prototype is not a defensible new algorithm or theorem.
- Ten calibration deciles have roughly 100 queries each. Do not claim simultaneous high-probability group safety from ordinary CRC, merge cells and claim leaf safety, or manufacture calibration examples for absent groups.
- Raw Fashion pixels and GloVe-25 subsamples are not modern production multimodal/MS-MARCO embeddings. This is fixed-probe IVF, not faithful adaptive ConANN, Quake, DARTH+, HNSW or RAG task evaluation.
- Data/group definitions and thresholds were frozen before pilot outcomes. No features, seeds or buckets were selected to force the gate. All individual D9/D10 rows, OOD controls, grouping ablations and unfavorable results are retained.
- Final queries remain untouched. A positive paper would require distinct capability beyond known groupwise calibration, reproducible effect under faithful strong baselines, matched-risk compute comparison, fresh queries and independent index/dataset replication.

See PROTOCOL.md and THEORY_AND_PRIOR_WORK.md for assumptions, primary-source links and the elementary counterexample showing that subgroup safety cannot universally be free in compute.
