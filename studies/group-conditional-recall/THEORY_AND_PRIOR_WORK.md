# Scientific interpretation and closest work

## What this study can establish
The prior Direction-A pilot did not establish a replicated failure in its tested settings; it did not prove that global CRC remains valid under all index mutations. This pivot tests a different, bounded hypothesis, not a mathematically guaranteed numerical failure.

For fixed corpus/index I and k=10, let L(q,p)=1-Recall@k(q,p), with nested search budgets p. The target is R_g(p)=E[L(Q,p)|G(Q)=g], while global CRC controls R(p)=sum_g Pr(G=g)R_g(p). R(p)<=.10 does not imply R_g(p)<=.10. This is an estimand mismatch even for IID exchangeable queries; the condition P(Y|X_hard)!=P(Y) is not itself an exchangeability violation. Actual support/mixture shift is a separate scenario. Neither situation mathematically forces numerical recall failure.

The group label is a design-fixed centroid-ambiguity interval. It is a proxy to test, not a proven measure of semantic topic difficulty, OOD, long-tail queries or multi-hop reasoning. ANN neighbor fidelity also does not directly bound RAG answer error or semantic relevance.

## Requested G-CRC as an existing conditional extension
Independently fix G using the index and design queries. In calibration group g, select

    p_g = min{p : [1+sum_{i:G(Q_i)=g} L(Q_i,p)]/(n_g+1)<=alpha}.

For empty/small groups without a certificate, search exactly. Under exchangeability within each fixed group and independence of the policy family/group design from calibration outcomes, the original CRC argument applies separately, yielding expected mean-risk control for each group. This averages over calibration randomness and a fresh within-group query; it does not promise every observed pilot group is below .10. This argument is a direct conditional application of existing CRC, not a new theorem.

The monotone curve p_mono(g)=max_{h<=g}p_h never underserves any certified group, so it preserves that expected-risk property at potentially increased work. The uniform control p_max=max_g p_g dominates every group rule. Coarser 2/5-group ablations certify only their own groups; shuffled groups do not certify ambiguity groups.

For simultaneous confidence over all 10 groups and 64 budgets, the bounded-loss Chernoff/KL control requires

    mean_g(p)<=alpha and n_g*KL(mean_g(p)||alpha)>=log(640/delta).

Union bounding the fixed family yields a population-risk confidence statement under the stated sampling assumptions, with exact fallback where insufficient. Losses are bounded QUERY-level FNRs: do not pretend the k neighbor indicators are independent samples or apply binomial counts to n*k observations. This alternative has a different guarantee from expected-risk CRC.

## Why no-inflation cannot be a universal guarantee
An elementary counterexample (not a novelty claim): 80% easy queries have zero loss at the minimum one-probe budget; 20% hard queries have loss .45 at one probe and zero at two. Global loss=.09, so global CRC with n=100 can accept one probe: (9+1)/101<.10. Group control requires two probes for the hard group; easy queries cannot be made cheaper than one. Average work becomes 1.2 probe units versus 1.0 globally. A uniform two-probe repair costs 2.0. Group control helps versus the conservative uniform repair, but cannot match global work in this example. Real IVF lists vary in population, so the pilot uses actual corpus-vector distance counts, not just probe counts.

## OOD limitation
Withholding 13 coarse cells removes their calibration labels. An ambiguity bin can still contain both seen and unseen cells. A certificate for the seen-cell mixture within that bin is NOT a certificate for the unseen cells. Only the explicitly marked exact fallback provides deterministic zero FNR on unknown-support cells in this implementation. No semantic/OOD-topic guarantee is asserted. The within-study exclusion diagnostic is exploratory; the queries were in the previously inspected public bank, not newly collected OOD data.

## Feature cost
IVF already computes query-centroid distances to select lists. Reuse them for the nearest/second-nearest ratio and design-bin lookup: no extra corpus-distance evaluations, 64 common centroid comparisons per query. Additional feature work is O(nlist), and lookup is O(log 10); it is not literally O(1) as dimension or index size changes. The benchmark measures this post-routing CPU time on a 600-query batch, not full serving latency.

## Primary sources inspected on 28 October 2026
- [Conformal Risk Control, ICLR 2024](https://research.google/pubs/conformal-risk-control/): established bounded monotone-loss expected-risk calibration. The small correction used here comes from this framework.
- [Conformal Prediction With Conditional Guarantees](https://arxiv.org/abs/2305.12616), Gibbs, Cherian and Candes; [JRSS-B publication](https://academic.oup.com/jrsssb/article/87/4/1100/8058684). Established conditional/group inference. Prediction-set coverage is not identical to fractional ANN FNR, but group-conditional calibration is not a new research concept.
- [Hierarchical Group-Conditional Conformal Risk Control for Selective Prediction in Language Models](https://arxiv.org/abs/2607.24562); [full HTML](https://arxiv.org/html/2607.24562v1). Directly relevant existing group-risk calibration, hierarchical policies, simultaneous confidence and group-mixture-shift experiments. It studies a different selective-prediction loss/policy; no faithful implementation or theorem transfer is claimed. This preprint alone makes a generic renamed 'G-CRC' originality claim untenable without a distinct mechanism.
- [ConANN, PVLDB 19(1)](https://www.vldb.org/pvldb/vol19/p29-horchidan.pdf): existing query-adaptive ANN recall control. Our integer-probe prototype is simpler, can leave risk slack, and does not reproduce ConANN's stopping score. No counterexample to its theorem is claimed.
- [MAPIE conditional-guarantee documentation](https://github.com/scikit-learn-contrib/MAPIE/blob/master/doc/content/conformal-prediction/conditional-guarantees.md): official implementation documentation describing established Mondrian groupwise calibration and conditional methods.

## Remaining publication requirements
Meeting the subgroup failure gate would establish a concrete empirical problem, not originality. A publishable method must beat strong groupwise/conditional controls with a distinct capability or mechanism. Sparse-group calibration, unseen support and routing-efficiency tradeoffs are possible research questions but are not declared unresolved by this pilot. Fresh queries, another index family, a faithful adaptive ANN baseline, larger/modern embeddings and downstream retrieval tasks are pending. No full experiment or paper is justified simply by observing that marginal and conditional guarantees differ.
