# Direction B: frozen pilot protocol, 28 October 2026

## Question and corrections
Does a global fixed-probe CRC policy achieve empirical marginal mean FNR<=.10 while mean FNR in the top two AMBIGUITY deciles is >=.18? Does group calibration fix that without increasing mean work? Neither the subgroup effect nor compute parity is guaranteed. Do not assert 25–35% errors before observing them.

A marginal-vs-conditional risk gap does NOT require broken exchangeability: it can occur under IID queries. Restricting to a group or changing group mixture is a different deployment target. E[FNR|G=g]<=alpha is a mean-risk statement, not P(FNR|G)<=alpha. Ordinary groupwise CRC is an established conditional extension, not a new algorithm. Adding ANN as an application does not establish novelty. Unknown-support OOD cannot be certified from an empty subgroup without assumptions or safe fallback.

## Data, frozen groups and compute
Public GloVe-25 (20k corpus) and Fashion raw pixels (10k corpus), input hashes as previous studies. Seeds 0..4 vary corpus sample, 64-centroid IVF construction and exploratory query partition. Same previously explored 2,000-query bank ONLY: 400 design, 1,000 calibration, 600 pilot. The other 8,000 official query IDs remain reserved and unevaluated. These are exploratory observations, not fresh replication. Queries in earlier studies have already been inspected; no claim of independent confirmation.

Fixed corpus/index, k=10, alpha=.10. Group edges are .1,.2,...,.9 quantiles of DESIGN-only feature values. Feature=sqrt(squared-distance to nearest centroid / squared-distance to second-nearest centroid). High ratios mean ambiguous coarse assignment, not necessarily harder retrieval. Test data never set decile edges. Counts can differ from exactly 10% at calibration/pilot time. Tie boundaries use deterministic searchsorted(side=right). No oracle kNN features, prompt-length claim, semantic labels or tuning over features. No additional feature is substituted if this one fails.

Use already-required IVF centroid distances for the ratio; report 64 common centroid comparisons per query. Post-routing ratio/partition and group lookup have no additional corpus-distance evaluations; they cost O(nlist) CPU plus O(log(10)) lookup, NOT absolute O(1) in dimension/index size. Measure this extra feature/assignment time separately from centroid computation. Distance counts are trace replay; not actual serving latency.

## Scenarios
1. PRIMARY `iid`: all calibration queries; fixed design-derived ambiguity groups; unchanged pilot mixture.
2. SECONDARY `heldout_cells`: withhold 13/64 centroid-cell IDs selected by RNG(seed+801) from calibration based on nearest centroid. Pilot retains all query cells, with held-out and seen subsets separately reported. This creates a query-support diagnostic. Cells are geometric, NOT validated semantic topics; no claim of MS-MARCO/domain OOD. Design features may cover the unlabeled cells, but no held-out-cell calibration labels are used. Binwise calibration from other cells does not guarantee risk inside excluded cells, even if they share ambiguity bins. Safe OOD fallback probes all lists in held-out cells.

## Methods, all with identical label access
- Global CRC: smallest probe count p with (sum losses+1)/(n+1)<=.10; exact fallback.
- Group CRC-10 (requested G-CRC): separate standard CRC in each design-defined decile, exact fallback for empty/small groups. This is a KNOWN baseline/application.
- Monotone G-CRC-10: prefix maximum of the ten certified probe budgets. This never lowers any budget, preserving its expected-risk guarantee at extra work; does not invent a new guarantee.
- Worst-uniform: maximum of the ten group CRC budgets, used for every query. Same underlying expected group-risk scope, conservative uniform budget.
- Group CRC-5 and Group CRC-2: prespecified pooling ablations (pairs of deciles; lowest eight vs highest two). They certify their OWN coarser groups, not each original decile.
- Shuffled-group CRC-10: seeded query-ID hash groups unrelated to difficulty. Negative feature-information control; certifies random groups, not ambiguity deciles.
- Group KL-10: bounded-loss Chernoff/KL upper bound, union-corrected over 10 groups x 64 candidate budgets at delta=.05. If empirical mean<=alpha and n*KL(mean||alpha)>=log(640/.05), certify; exact fallback otherwise. This is a strong known simultaneous-confidence control, a different guarantee from mean-risk CRC.
- OOD-exact fallback: global CRC on seen cells, exact search on cells absent by construction from calibration; group IDs known at query time.
- Full exact search.

All methods share calibration labels and index; no pilot-driven hyperparameter selection. No shrinking/pooling into a parent followed by an unsupported claim of leaf-group safety. Model fitting on design is unnecessary for these bucketed baselines.

## Gate and uncertainty
Predefined PRIMARY gate per seed: global empirical marginal mean FNR<=.10 AND pooled deciles 9–10 mean FNR>=.18 AND its percentile-bootstrap lower 95% endpoint>.10. Require >=4/5 seeds on EACH dataset for a replicated opportunity. Report both individual D9/D10 and the pooled group; none can replace the primary group after outcomes. Secondary >=.15 and OOD findings are exploratory and cannot silently replace the gate. Empty pilot groups are missing, not zero risk.

2,000 query bootstrap draws per condition. Group intervals resample within the group; marginal intervals resample all pilot queries. Paired whole-query bootstrap for G-CRC/global work difference; common pilot query identities across methods. Across-seed sample SD, all seeds retained. Record group sizes, budgets, calibration count and corrected empirical criterion. A 100-query calibration decile is small: CRC controls expected mean risk over calibration randomness, NOT a simultaneous high-probability statement that every realized group's true risk or empirical pilot FNR is <=.10. Group KL is the confidence alternative. Do not interpret a group violation fraction as a formal error probability.

Opportunity for the proposed efficiency claim requires the primary failure gate, credible group-risk control AND <=1.00 mean TOTAL distance work ratio to global in >=4/5 seeds on both datasets; report paired uncertainty rather than conceal added work. A method that spends more can still fix a group problem, but fails the requested no-inflation claim. Passing these does not establish novelty; closest conditional/group CRC work must still be surpassed with a distinct mechanism. Full/fresh-query runs and paper drafting remain blocked until both contribution and pilot gates clear.

Smoke: trace vs direct candidate recall; deterministic design bins unaffected by pilot; CRC fallback for empty/small groups; analytic known marginal/subgroup positive control; monotone budget domination; bounded-KL certificate; exact-search loss zero; split separation; feature has no pilot labels.
