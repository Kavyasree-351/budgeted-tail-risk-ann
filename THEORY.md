# Proposed cap-and-tail setup: properties and limits

This is a candidate optimization extension, NOT an established novel contribution. Learn-then-Test (LTT) already supplies the statistical machinery below. A greedy allocation path is a hypothesis to test against strong matched-guarantee paths, not a new theorem by renaming.

## 1. Prefix-class feasibility characterization
Fix the corpus, IVF index and nearest-centroid list order. Let C(q,p)=64+number of corpus vectors in the first p lists; p=0 returns no neighbors and has FNR=1. For a total distance cap B, define p_B(q)=max{p:C(q,p)<=B}. It uses list sizes and query routing, not exact neighbors. Let L_B(q)=L(q,p_B(q)).

**Proposition 1 (deterministic cap and floor).** For ANY query-dependent prefix policy pi respecting B, L(q,pi(q))>=L_B(q), for every q. The same inequality holds for any nondecreasing severity transform, and for conditional mean, exceedance probability, VaR and CVaR whenever defined. Conversely p_B is itself feasible in compute and attains this pointwise minimum.

Proof: C increases with the prefix, so pi(q)<=p_B(q). Prefix candidate sets are nested; every global true neighbor found in a smaller prefix remains found in a larger prefix under consistent distance/ID ties and exact-within-list retrieval. Thus FNR is nonincreasing. Apply any nondecreasing transform and condition/integrate. p_B fits the cap by definition. QED.

Consequences: if the population floor violates any target, NO prefix policy under this cap can solve the all-query problem. For a finite, fully evaluated pilot workload the same conclusion is DETERMINISTIC about that finite workload when its empirical floor violates a target. It is not a population claim. It also does not cover non-prefix, graph, partial-list, learned-probe-order or quantized ANN algorithms.

## 2. Mean-and-tail groups, not input-decile CVaR
For every fixed group g, require E[L|g]<=.10, Pr(L>.20|g)<=.10, and Pr(L>.50|g)<=.05. The latter imply VaR90(L|g)<=.20 and VaR95(L|g)<=.50, including discrete losses. These are three risks on each of fifteen overlapping query groups. A query may contribute to multiple groups; no partition into intersections of all groups is necessary. Each group's effective sample count still matters.

## 3. Prospective finite-sample selected-policy guarantee
Assume fresh calibration queries IID within the fixed group definitions; index/groups/path are independent of their calibration outcomes. For a fixed candidate theta and constraint j=(g,severity), let n_j be group count, z_j its observed bounded mean, and a_j its target. Use p_j(theta)=exp(-n_j KL(z_j||a_j)) when z_j<a_j and n_j>0, otherwise 1. The bounded-variable Chernoff argument makes this a valid one-sided p-value for H_j:R_j(theta)>a_j (possibly conservative).

**Proposition 2 (simultaneous selected-policy safety, standard LTT specialization).** Let p(theta)=max_j p_j(theta). In a path fixed independently of calibration, test from safest to cheapest at level delta_plus, stopping on the first p>delta_plus. Any returned last-passing policy satisfies ALL 45 mean/tail constraints with probability >=1-delta_plus.

Proof: under the null that some constraint is unsafe, fix a truly unsafe j; {max_j p_j<=u} is a subset of {p_j<=u}, so the maximum is a valid p-value (intersection-union test). In fixed-sequence testing, any incorrect acceptance requires rejecting the first true unsafe null in the predetermined sequence, which has probability <=delta_plus. No independence across overlapping groups/tests is required. This does not require a Bonferroni penalty over groups or path length, but also does not produce simultaneous confidence intervals for every candidate. QED.

This is already covered by LTT's multi-risk/fixed-sequence results; it is NOT claimed as original. Structural full search can bypass statistical testing only if it applies to ALL feature cells, respects B, and therefore has deterministically zero risk, not because calibration happened to show zero errors.

The implemented fresh calibration is a uniform sample WITHOUT replacement from a fixed train-query source bank, excluding corpus rows. Conditional on each group's count, its observations are a simple random sample from that source-bank group. Hoeffding's convex-order reduction transfers the with-replacement Chernoff bound to this setting; see [Bardenet and Maillard, 2015, Lemma 1.1](https://arxiv.org/pdf/1309.4029). Thus the same tests can target the finite SOURCE-BANK group means for a fixed independently chosen path. Transferring that certificate to official-test or production queries still requires a shared within-group query law. It does not follow from holding out filenames alone.

## 4. Feasible / infeasible / unknown
For the maximum feasible prefix, use reverse one-sided tests p_j^minus=exp(-n_j KL(z_j||a_j)) when z_j>a_j, else 1, for H_j:R_j(floor)<=a_j. If any p_j^minus<=delta_minus/45, issue an infeasibility witness. If a candidate passes Proposition 2, issue it. Otherwise return UNKNOWN. Set delta_plus=delta_minus=.025. At a fixed cap/algorithm, the chance of a wrong safety or wrong infeasibility statement is at most .05 by union bounding the two directions, under fresh-calibration assumptions. This is pointwise in cap/method, not an all-caps/all-methods guarantee. A statistically unproven constraint is not evidence of infeasibility.

## 5. Small-group obstruction
For a severity event with target beta=.05, zero observed exceedances yield p=(1-beta)^n. At delta_plus=.025, even zero observations of a catastrophe cannot pass this count-based test unless n>=ceil(log(.025)/log(.95))=72. This is an information requirement, not solved by renaming calibration multivalid. In a distribution-free Bernoulli-count test, accepting whenever all n observations are zero at smaller n would exceed the test size under the boundary distribution. Structural exactness or additional assumptions may change the problem; unsupported pooling does not establish the original fine-group guarantee.

The number 72 is a requirement of the implemented conservative Chernoff test, not a universal minimum for every finite-population method. Exact finite-population corrections or structural information can improve it; the IID Bernoulli argument explains why arbitrary fine-group guarantees cannot be made free of sample requirements.

## 6. Candidate policy-path optimization
Policy cells are ambiguity quintile x near/far geometry (ten cells). For design queries, precompute each cell/budget's contribution to all normalized mean/tail risks and average work. Starting at zero probes, greedily raise one cell's budget by the jump maximizing (decrease in sum_j design risk_j/a_j)/(increase in average corpus distances), ignoring zero-benefit jumps. Complete the nested path by common increments to all-64, then calibrate with Proposition 2 after query-wise clipping to p_B. This construction cannot violate the cap; its work optimality is NOT guaranteed.

Uniform LTT and a design-cell-CRC-template plus offset LTT use the SAME groups, targets, confidence, caps and tests. Ablations remove tail or overlap terms only from design optimization; calibration still enforces every constraint. A gain over ordinary expected-risk Group CRC alone is not sufficient evidence.

## 7. Calibration reuse caveat
The method and design/pilot bank depend on earlier experiments. Before new pilot performance, calibration was amended to 5,000 fresh TRAIN rows excluded from the corpus, with a 1,000-prefix ablation; no reserved official TEST query is opened. This restores algorithm-level separation from this study's calibration outcomes, assuming the relevant within-group query law is shared by the fresh calibration source and future queries. It does not make previously inspected pilot queries independent confirmation, or prove train-derived and arbitrary production/OOD query distributions equal. Statuses remain labeled NOMINAL to avoid an unverified deployment claim. Fresh TEST confirmation and completed novelty review are pending. Proposition 1 and finite-workload cap/floor statements are deterministic despite adaptive research reuse.

## Closest primary work, checked 28 October 2026
- [Learn then Test](https://arxiv.org/abs/2110.01052), [author-hosted paper](https://people.eecs.berkeley.edu/~angelopoulos/publications/downloads/ltt.pdf): fixed-sequence testing and multi-risk maximum-p construction are established. Must not be sold as a new calibration theorem.
- [Conformal Risk Control](https://people.csail.mit.edu/tals/publication/conformal_risk/): its extensions ALREADY include quantile and multiple risk control. Merely thresholding an FNR loss to certify a quantile is not novel.
- [Fair Risk Control: A Generalized Framework for Calibrating Multi-group Fairness Risks](https://openreview.net/pdf?id=6KtXzUUEp4): existing generalized multi-group risk/multicalibration work; generic overlapping-group calibration is not new.
- [Conformal Tail Risk Control for Large Language Models](https://openreview.net/pdf?id=MMDVf8RsHz): existing tail/distortion-risk control. Its objective is not the same as the current prefix feasibility setup; no faithful reproduction is claimed.
- [Risk-Averse Evaluation of Conformal Scores through CVaR, COPA 2026](https://proceedings.mlr.press/v329/narteni26a.html): existing CVaR-based evaluation/score selection, distinct from claiming a fresh CVaR certificate.
- [Conformal Thinking](https://arxiv.org/abs/2602.03814): existing risk/compute calibration for reasoning; compute-aware risk control as a broad idea is not new.
- [ConANN](https://www.vldb.org/pvldb/vol19/p29-horchidan.pdf): existing adaptive ANN recall calibration; current prototype is not a faithful author-code reproduction.

Publication novelty remains UNESTABLISHED. The research question is whether the specific overlap-aware allocation/frontier yields a distinct, reproducible benefit beyond these known tools and strong matched baselines. Failure is permitted; no metric threshold will be adjusted after inspection.
