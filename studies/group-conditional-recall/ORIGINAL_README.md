> Historical workspace instructions. Use README.md for this standalone repository.

# Direction B: group-conditional ANN recall pilot

Read `OVERVIEW.md` for outcomes, `FINDINGS.md` for all comparisons, `PROTOCOL.md` for the frozen gates and `THEORY_AND_PRIOR_WORK.md` for assumptions/novelty limits. This is a **complete exploratory pilot**, not a novel-method paper or a completed full benchmark.

## Reproduction commands (Windows PowerShell)

Run from the workspace containing `outputs` and `work`:

```powershell
python -m venv work/group-venv
work/group-venv/Scripts/python.exe -m pip install -r outputs/group-recall/requirements.txt
work/group-venv/Scripts/python.exe outputs/group-recall/download.py
work/group-venv/Scripts/python.exe outputs/group-recall/experiment.py smoke
work/group-venv/Scripts/python.exe outputs/group-recall/experiment.py pilot --seeds 0 1 2 3 4
work/group-venv/Scripts/python.exe outputs/group-recall/validate.py
work/group-venv/Scripts/python.exe outputs/group-recall/report.py
```

Use the existing dependency installation from this study:

```powershell
$env:PYTHONPATH = (Resolve-Path work/deps).Path
python outputs/group-recall/experiment.py smoke
python outputs/group-recall/experiment.py pilot --datasets glove fashion --seeds 0 1 2 3 4
python outputs/group-recall/validate.py
python outputs/group-recall/report.py
```

Python 3.12.6 and pinned requirements were used. `download.py` verifies the original public source hashes; existing data are reused in `work/adaptive-retrieval`. About 160 MB raw download storage plus libraries is required. Pass `--data ABSOLUTE_PATH` to downloader/pilot when relocating. Preserve the `outputs/group-recall` directory structure; the `inputs` files supply public split/hash definitions without depending on earlier source code. ZIP excludes raw datasets and bytecode.

The full-stage command is intentionally blocked:

```powershell
python outputs/group-recall/experiment.py full
```

It exits before loading any reserved query. No independent full benchmark is implemented or claimed complete because the primary failure/efficiency/novelty gates have not cleared. A later full study requires a distinct contribution, a frozen method and independent confirmation protocol. This is a scientific stop rule, not a permission request.

## Contents and conditions

- `data.py` / `download.py`: verified public inputs; only the already explored 2,000-query bank is repartitioned. The other 8,000 query IDs remain reserved.
- `index.py`: exact-within-list IVF and deterministic exact top-k ground truth. Copied/reused research infrastructure; no HNSW or faithful ConANN implementation is claimed.
- `methods.py`: global/groupwise CRC, monotone envelope, coarser grouping, random-group control and a bounded-KL simultaneous-confidence alternative.
- `experiment.py`: design-only decile edges; IID and calibration-excluded coarse-cell scenarios; paired observations and feature timing.
- `validate.py`: checks all 2,800 conditions and subgroup calibration criteria, raw data agreement and safe fallbacks.
- `report.py`: aggregation, predefined gate, Markdown, four LaTeX table fragments and PNG/PDF plots.

Ten methods x two scenarios x fourteen reported scopes x five seeds x two datasets = 2,800 conditions. These share pilot queries and are NOT 2,800 independent experiments. Scopes are marginal, ten individual deciles, pooled D9â€“10, held cells and seen cells. OOD cells are geometric, not semantic labels; random held cells are only OOD-relative-to-calibration in the exclusion scenario.

## Result files

`results.csv` has every group's FNR, size and 2,000-resample percentile-bootstrap interval. `summary.csv` gives five-seed mean and sample SD. `paired_work.csv` includes each seed's total-work ratio, paired work-difference interval and empirical violating-decile fraction. `policies.csv` records actual calibrated budgets, group sample counts and exact calibration IDs used. NPZ files contain paired pilot losses/budgets/work, calibration/pilot loss curves and frozen group memberships. Provenance records all corpus/query IDs and input hashes.

Work counts include corpus distances and the common 64 centroid comparisons (except pure exact search). Additional ratio/bin lookup timing is measured using already-computed centroid distances. It has zero extra corpus-distance calls but nonzero O(nlist) CPU work; do not call complete feature extraction absolute O(1). No actual serving-latency or total peak-memory measurement is claimed by this pilot.

Group CRC is an established application of CRC within fixed groups. Its guarantee averages over calibration randomness; it does not certify that every realized decile is below alpha. The KL method has a different simultaneous-confidence guarantee under its assumptions. Held-out support invalidates guarantees transferred from a different within-bin population; only the explicit exact fallback is deterministically safe there. Do not mistake fewer empirical group violations for a formal simultaneous certificate.

Paper-ready table fragments report exploratory values only. No paper draft is included because passing an empirical subgroup test would still not make generic groupwise calibration novel.
