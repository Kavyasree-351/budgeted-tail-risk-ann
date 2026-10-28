# Cap-constrained simultaneous mean/tail control — concise outcome

A new setup was tested: strict distance budgets, fifteen overlapping groups, simultaneous mean and 90th/95th-percentile targets, and feasible/infeasible/unknown outcomes. This is not the old 18% failure gate.

Ten dataset/seed runs completed; 320 policy/cap cases and 4800 group rows passed saved-result validation. Calibration used 5000 fresh TRAIN vectors outside the index; 1000-query subsets were an ablation. The official final TEST bank remains unopened.

## Primary 25% cap

| Dataset | Candidate mean distances | Uniform LTT | Template LTT | Candidate issued | Runs meeting all observed pilot targets |
|---|---:|---:|---:|---:|---:|
| glove | 3287 | 4087 | 3362 | 5/5 | 5/5 |
| fashion | 659 | 825 | 732 | 5/5 | 4/5 |

Counts include 64 centroid comparisons. Every capped candidate query respected the bound. Population-risk certificates do not promise that every finite pilot group mean stays below its target.

At the 10%-corpus cap, all five GloVe runs returned infeasibility evidence; all five Fashion runs issued policies. A concrete GloVe witness was a .3312 floor probability of FNR>.20 in the upper-ambiguity/far intersection versus the .10 target (n=1739). This conclusion is restricted to the defined prefix-IVF class and source-query law.

## Decision

The candidate improved over uniform search, but the strongest simple template baseline captured most of that benefit. The preregistered >=10% strong-baseline improvement plus empirical-safety gate passed only 1/5 seeds on each dataset, below the required 4/5. Component evidence was inconsistent. Novelty is not established, and no paper/full-test run was made.

THEORY.md proves cap/floor properties and specializes established LTT for simultaneous quantile-risk selection; these are not claimed as original A* theorems. FINDINGS.md and CSV/JSON/NPZ retain all outcomes, uncertainty, calibration costs and ablations.
