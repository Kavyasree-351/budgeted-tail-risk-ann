> Historical workspace instructions. Use README.md for this standalone repository.

# Hard-cap simultaneous group/tail recall: candidate extension

Read `OVERVIEW.md` for the concise decision, `FINDINGS.md` for every outcome, `PROTOCOL.md` for the new preregistered problem/gates, and `THEORY.md` for propositions/proofs and closest work. This package attempts a **different constrained problem**, not a search for an old metric that passes.

The candidate learns an overlap/severity-aware nested allocation path on design queries. Established Learn-then-Test certifies its clipped policies against 45 group/risk constraints. It can instead report evidence of prefix-class infeasibility or insufficient calibration. The optimization heuristic is not globally optimal, and neither LTT nor quantile/group CRC is claimed as a new invention. Publication novelty remains unestablished.

## Exact commands, Windows PowerShell

From a workspace containing `outputs` and `work`:

```powershell
python -m venv work/cap-venv
work/cap-venv/Scripts/python.exe -m pip install -r outputs/cap-tail/requirements.txt
work/cap-venv/Scripts/python.exe outputs/cap-tail/download.py
work/cap-venv/Scripts/python.exe outputs/cap-tail/experiment.py smoke
work/cap-venv/Scripts/python.exe outputs/cap-tail/experiment.py pilot --datasets glove fashion --seeds 0 1 2 3 4
work/cap-venv/Scripts/python.exe outputs/cap-tail/validate.py
work/cap-venv/Scripts/python.exe outputs/cap-tail/report.py
work/cap-venv/Scripts/python.exe outputs/cap-tail/package.py
```

Using the existing scientific installation (Python 3.12.6):

```powershell
$env:PYTHONPATH = (Resolve-Path work/deps).Path
python outputs/cap-tail/experiment.py smoke
python outputs/cap-tail/experiment.py pilot
python outputs/cap-tail/validate.py
python outputs/cap-tail/report.py
python outputs/cap-tail/package.py
```

Public raw files are shared in `work/adaptive-retrieval`; `download.py` verifies hashes. `--data ABSOLUTE_PATH` is accepted by downloader/pilot when relocating. Preserve the `outputs/cap-tail` package structure. The ZIP includes source, split definitions, all results and table/figure scripts, but excludes raw datasets and bytecode. Inputs total about 160 MB; dependency installation, outputs and OS headroom require additional space.

The full-stage command is deliberately blocked:

```powershell
python outputs/cap-tail/experiment.py full
```

It opens no final queries. Full/fresh official-test experiments and a paper are NOT implemented or claimed complete: the efficiency/component/novelty gates did not clear. This is the scientific stop rule, not a permission request.

## What is new in this experiment's setup

- Strict per-query cap B=64+floor(f*N), primary f=.25; f=.10,.50,1.00 are diagnostic budgets. These constrain distance evaluations, not total runtime/CPU instructions.
- Fifteen overlapping query groups, including ten ambiguity deciles and geometric-distance intersections; no post-hoc group dropping.
- Mean FNR<=.10, Pr(FNR>.20)<=.10 and Pr(FNR>.50)<=.05 in every group. These are 90th/95th-percentile targets. Empirical CVaR90 is descriptive; no CVaR guarantee is claimed.
- A label-free maximum feasible prefix supplies a pointwise risk floor. Infeasible, unknown and issued are separate outcomes; no forced guarantee at an impossible budget.
- All queries count. An empty prefix has FNR=1; neither rejection nor a failed query is scored as a success.

## Fresh calibration without unblinding final tests

The original 400 design / 600 pilot queries are reused exploratory data from the old 2,000-query bank. The old 1,000 calibration queries are NOT used to calibrate this extension. `fresh.py` samples 5,000 new query vectors from TRAIN rows excluded from the index corpus, records source IDs and uses the same fresh labels for every method. The first 1,000 form a calibration-size ablation. No reserved official TEST query is loaded into feature fitting, exact-neighbor evaluation or method selection.

This extra labeling is a real cost, not an algorithmic cure for data fragmentation. Fresh uniform sampling without replacement permits concentration statements about the finite source-query bank; generalizing to official-test/production/OOD queries requires a shared within-group query law. The previously inspected pilot is not independent confirmation. Seed pools may overlap, and five seeds are not five independent external datasets.

## Strong baselines and ablations

- Uniform-prefix and design-cell-CRC-template/offset paths use the SAME LTT test, groups, targets, confidence and caps.
- The no-overlap/no-tail ablations alter only the design-learning objective; calibration still tests every mean/tail constraint. They do not receive weaker guarantees.
- Maximum feasible prefix is the prefix-class best-risk anchor. Ordinary Group CRC, uncapped and naively capped, are reported as uncertified references for the stronger problem.
- The IUT/FST procedure is established LTT. A lower work count versus only expected-risk CRC or a Bonferroni-heavy bound is insufficient novelty evidence.

## Source files

`control.py`: capped-policy evaluation, risk floor, p-values, LTT, greedy path and known baselines.
`fresh.py`, `data.py`, `index.py`: disjoint sampling and low-memory exact IVF/reference kernels.
`experiment.py`: smoke tests, design-only fitting, all caps/methods, calibration-size ablation and paired observations.
`validate.py`: checks saved counters, risk predicates, nominal calibration criteria, witness criteria, split separation and pointwise bounds.
`report.py`: CSV aggregation, seed SD, 2,000-resample conditional/paired bootstrap intervals, preregistered gate, Markdown, LaTeX snippets and PNG/PDF plots.

## Interpreting outputs

`policy_metrics.csv` has all 320 policy/cap conditions; `group_risks.csv` has all 4,800 group rows with three risks and intervals. `paired_comparisons.csv` retains unfavorable work differences. `sample_size_ablation.csv` records 1,000/5,000 calibration statuses. `summary.csv`, `gate.json`, `validation.json`, `smoke.json` and raw NPZ/JSON provide checks and provenance. `table_glove.tex`/`table_fashion.tex` are exploratory table fragments, not a paper.

An unissued candidate's loss/work fields are a DIAGNOSTIC maximum-feasible-prefix profile; they are not a deployed or certified policy. Do not average them with issued outputs as successful deployments. The method's nominal safety statement is pointwise per cap/algorithm, not joint over arbitrary cap/method selection. The feasibility profile is not a proven optimal Pareto frontier; the heuristic can choose different work levels when a cap changes.

Timing caveats: `truth_curve_seconds` includes design, calibration AND pilot reference computation. `path_learning_seconds` includes all three repair variants at a cap. Stored `calibration_selection_seconds` includes the 1,000-prefix ablation/metadata work for path methods. These are diagnostic offline timings, not serving latency or isolated calibration benchmarks. Maximum query distance counts are exact under the declared counter.

## Resource recovery audit

Low commit/disk headroom caused an early allocation failure before the first result, then an intermediate bootstrap-cache accumulation failure before Fashion runs. Kernels were streamed, bootstrap counts compacted/cleared per seed, smoke tests passed, and ALL ten runs were regenerated. Targets, confidence, groups and work gates were not changed after outcomes.

Only the old public RouterBench raw download cache in `work/lifecycle-routing` was losslessly gzip-archived to recover space. Its decompressed SHA256 was verified before removing that uncompressed cache; no previous experiment results were deleted. `resource_recovery.json` records exact paths/hash. To restore when sufficient space is available, decompress that `.pkl.gz` into its original `.pkl` path using Python's gzip/shutil modules. This cache is unrelated to the current ANN inputs.
