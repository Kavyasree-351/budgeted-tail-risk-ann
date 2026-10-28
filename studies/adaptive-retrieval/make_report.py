"""Generate honest pilot report and reusable LaTeX table from saved results."""
import csv,json
import numpy as np
import research as r
rows=list(csv.DictReader(open(r.ROOT/'results.csv',newline='')))
methods=['naive_per_k','selector_common_crc','selector_scaled_crc','envelope_crc','simultaneous_hoeffding','exact']
names=['Separate per-k CRC (marginal only)','Selector-specific common CRC','Selector-specific scaled CRC',
       'Worst-over-k CRC','Simultaneous Hoeffding','Exact search']
lines=['# Adaptive retrieval pilot: no novelty established','',
 'Five index seeds on each of two public vector datasets completed. Smoke tests and the design-only float32/float64 neighbor-set audit passed. The predefined practical-failure gate failed on both datasets (0/5 qualifying seeds each). Full experiments and an IEEE research paper are therefore not justified by this study.','',
 'These are controlled IVF feasibility experiments, not faithful reproductions or refutations of ConANN or DARTH+. No new algorithm, new theorem, deployment-grade guarantee or independently replicated discovery has been established.','',
 '## Primary selector results','',
 'Mean FNR is one minus mean recall, not the fraction of queries with any error. Values below are mean and range across five fitted indexes/calibration outcomes on shared pilot queries; the range is not a confidence interval. Per-run conditional query-bootstrap intervals are in results.csv. Costs count corpus-vector distances, with 64 common centroid distances additional for IVF.','',
 '| Dataset | Method | Mean FNR | Seed range | Mean distances |','|---|---|---:|---:|---:|']
tex=['% Verified pilot outcomes only; no novel-method result. Seed ranges are descriptive.',
 '\\begin{tabular}{llrr}','\\hline','Dataset & Method & Mean FNR & Distances \\\\','\\hline']
for d in ['glove','fashion']:
    for method,label in zip(methods,names):
        rr=[x for x in rows if x['dataset']==d and x['selector']=='ambiguity_q0.5' and x['method']==method]
        v=np.array([float(x['fnr']) for x in rr]);w=np.mean([float(x['distances']) for x in rr])
        lines.append(f'| {d} | {label} | {v.mean():.4f} | {v.min():.4f}–{v.max():.4f} | {w:.0f} |')
        tex.append(f'{d} & {label} & {v.mean():.4f} & {w:.0f} \\\\')
tex+=['\\hline','\\end{tabular}']
lines+=['','## Robustness and component checks','',
 'All prespecified selector variants were retained. The following are mean FNR values for the naive per-k control; no secondary result replaces the primary gate.','',
 '| Selector | GloVe | Fashion |','|---|---:|---:|']
for s in ['ambiguity_q0.25','ambiguity_q0.5','ambiguity_q0.75','inverse_q0.5','uniform','constant_1','constant_10','constant_50']:
    vals=[np.mean([float(x['fnr']) for x in rows if x['dataset']==d and x['selector']==s and x['method']=='naive_per_k']) for d in ['glove','fashion']]
    lines.append(f'| {s} | {vals[0]:.4f} | {vals[1]:.4f} |')
lines+=['','The common-versus-scaled CRC comparison isolates the design-fitted per-k template. The envelope-versus-selector-specific comparison measures the work cost of protecting arbitrary k selection. These are ablations of known calibration choices, not evidence of a novel component. Different risks make raw work differences unsuitable as matched-risk superiority claims. No downstream retrieval utility was measured, so a lower FNR alone does not establish better RAG answers.','',
 '## What the negative result means','',
 'The specific natural selector and controlled IVF settings did not expose the hypothesized practically material calibration failure. This rejects the current primary empirical claim; it does not prove all adaptive-k policies are safe. A toy selection counterexample remains mathematically valid but does not establish a publishable ANN discovery. Standard selector-specific calibration remains a strong and sufficient comparator here. More seeds or larger datasets cannot by themselves create methodological novelty.','',
 '## Limits and evidence still needed','',
 '- Subsampled corpora and raw image pixels; no large-scale production embeddings, downstream RAG evaluation, query drift, HNSW or faithful author-code reproduction.',
 '- Query-bootstrap intervals condition on fitted indexes/calibration. Index seeds share queries and are not independent external replications. Mean-risk CRC does not promise every query or every realized calibration sample meets the target.',
 '- The Hoeffding comparator bounds per-query worst-over-k loss uniformly over the design-fixed scaled-budget family. Simultaneous marginal bounds alone would not protect query-dependent k. It has a different high-probability risk guarantee; full-search fallback is safe by construction.',
 '- No serving-latency benchmark was run. Offline trace and build wall times are diagnostic, depend on host scheduling, and must not be treated as serving or stable training-throughput measurements.',
 '- Zero-distance query counts were zero in all recorded traces. Smoke and 20-design-query-per-dataset precision audits found no recall-code/neighbor-set disagreement; this is not a comprehensive floating-point proof.',
 '- Remaining public query vectors were not evaluated. Fashion archive decompression reads bytes for the full archive, but reserved images never enter fitting, traces, calibration, performance inspection or selection.',
 '- DARTH+ complete theorem/implementation comparison remains pending because the public document endpoint was access denied. The current results cannot establish a gap over it.',
 '- Before any positive paper: identify a distinct unresolved mechanism, reproduce closest methods, obtain matched-risk efficiency improvements, confirm on fresh queries and another index family, measure actual serving latency/memory, and establish independence of the claimed discovery. These items are pending, not silently assumed complete.','',
 '## Attempt ledger','',
 '1. Kept the previous routing/acquisition failures unchanged; narrowed this run to adaptive retrieval.',
 '2. Public SIFT small download failed TLS hostname verification. ANN-Benchmarks direct downloads returned HTTP 403. Used a public GloVe mirror, pinned by downloaded-file SHA256; independent Fashion data came from the dataset authors.',
 '3. Fashion HDF5 download ran out of disk space. Removed only that incomplete task-created file, switched to official compressed raw images before any retrieval outcome was observed.',
 '4. Smoke correctness checks passed before the pilot.',
 '5. During implementation review the Hoeffding baseline required two repairs: accounting for calibration-selected budgets, and bounding per-query worst-over-k loss rather than merely simultaneous marginal k-risks. All ten runs were regenerated after the final repair; primary naive-policy results, splits and gate were unchanged. No favorable seed was dropped.',
 '6. Completed five seeds, eight selectors and six methods per dataset (480 recorded conditions). Design-only precision audit passed. Primary gate failed; no pilot-driven selector search, confirmation opening or full experiment followed.',
 '7. No complete IEEE paper was written because the user explicitly conditioned it on achieving novelty. This report, code, raw pilot losses, table and figure are the verified deliverables.','',
 '## Closest sources','',
 '- [ConANN paper](https://www.vldb.org/pvldb/vol19/p29-horchidan.pdf): existing IVF conformal recall control; our budget prototype is simpler than its query-adaptive stopping rule.',
 '- [ConANN author repository](https://github.com/soniahorchidan/conann): already discusses variable-k calibration and reports variable-k experiments. This is an acknowledged scope issue, not a newly found theorem flaw.',
 '- [DARTH/DARTH+ author overview](https://mchatzakis.github.io/declarative-recall/): existing learned early termination, with DARTH+ describing optional probabilistic quality guarantees.',
 '- [Conformal Risk Control](https://arxiv.org/abs/2208.02814): underlying generic mean-risk machinery, not invented here.',
 '- [ANN-Benchmarks datasets](https://github.com/erikbern/ann-benchmarks): source benchmark format; original full-corpus ground truths were not used.',
 '- [Fashion-MNIST authors](https://github.com/zalandoresearch/fashion-mnist): independent raw image benchmark.',
 '- [ESANN](https://www.esann.org/): machine-learning scope is relevant, but scope fit does not establish novelty. IEEE format would be a separate requested manuscript format, not an assertion about ESANN submission requirements.']
(r.ROOT/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(r.ROOT/'pilot_table.tex').write_text('\n'.join(tex)+'\n',encoding='utf-8')
r.save(r.ROOT/'manifest.json',{p.name:r.sha(p) for p in r.ROOT.iterdir() if p.is_file() and p.name!='manifest.json'})
print('Report, verified LaTeX table and manifest written.')
