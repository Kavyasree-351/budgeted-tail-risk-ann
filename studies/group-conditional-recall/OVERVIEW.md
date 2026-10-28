# Direction B — verified exploratory findings

**A subgroup gap is observed on GloVe, but the predefined >=18% primary failure gate is not met. Groupwise CRC is useful engineering here; a novel publishable method is not established.**

Completed 10 dataset/seed runs, two calibration scenarios, ten methods and 2800 subgroup/method conditions. All use the previously explored public query bank. Reserved final queries remain unevaluated. No paper or full benchmark has been generated.

## Primary result: unchanged query mixture

| Dataset | Global marginal FNR | Global top-two-decile FNR | Group CRC top-two-decile FNR | G-CRC/global total-work ratio | Primary passing seeds |
|---|---:|---:|---:|---:|---|
| glove | 0.0873 | 0.1508 | 0.0905 | 0.988 | [] |
| fashion | 0.0470 | 0.0950 | 0.0843 | 0.814 | [] |

The complete report includes all seed uncertainty, calibration counts, known groupwise baselines, grouping/monotonicity/shuffled-feature ablations, confidence-bound comparison, held-out-cell tests and post-routing feature timings.

**Decision:** no full/fresh-query run or paper. The primary >=18% replicated failure gate failed on both datasets; G-CRC does not establish all-decile realized safety or consistently free compute. Its observed engineering benefit is useful but uses established methods.
