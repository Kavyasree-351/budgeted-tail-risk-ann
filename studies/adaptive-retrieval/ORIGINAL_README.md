> Historical workspace instructions. Use README.md for this standalone repository.

# Adaptive retrieval research pilot

**Outcome: no novelty established.** Read [REPORT.md](REPORT.md), [PROTOCOL.md](PROTOCOL.md) and `gate.json` before interpreting results. Completed: correctness smoke tests; two public datasets; five index seeds each; eight selector controls/robustness variants; six calibration/search methods; conditional query-bootstrap intervals; exact within-list recall checks; efficiency by vector-distance counts. Reserved queries were not evaluated. No full benchmark, online-latency study, new theorem or IEEE manuscript is claimed.

This is a small CPU IVF prototype, **not** ConANN/DARTH author-code reproduction. The useful tested solution is standard selector-specific conformal calibration; it is included as a strong known baseline rather than renamed as a new method. The main adaptive-k failure hypothesis did not meet its predefined pilot threshold, so the scientific stop rule forbids promoting this into a positive research paper.

## Reproduce on Windows PowerShell

From the original workspace root (the directory containing `outputs` and `work`):

```powershell
python -m venv work/ann-venv
work/ann-venv/Scripts/python.exe -m pip install -r outputs/adaptive-retrieval/requirements.txt
work/ann-venv/Scripts/python.exe outputs/adaptive-retrieval/download.py
work/ann-venv/Scripts/python.exe outputs/adaptive-retrieval/research.py smoke
work/ann-venv/Scripts/python.exe outputs/adaptive-retrieval/research.py pilot --seeds 0 1 2 3 4
work/ann-venv/Scripts/python.exe outputs/adaptive-retrieval/precision_audit.py
work/ann-venv/Scripts/python.exe outputs/adaptive-retrieval/research.py aggregate
work/ann-venv/Scripts/python.exe outputs/adaptive-retrieval/validate_results.py
work/ann-venv/Scripts/python.exe outputs/adaptive-retrieval/make_report.py
```

The original run used Python 3.12.6, with the listed scientific packages in `work/deps`. To reproduce using that existing installation without duplicating dependencies:

```powershell
$env:PYTHONPATH = (Resolve-Path work/deps).Path
python outputs/adaptive-retrieval/research.py smoke
python outputs/adaptive-retrieval/research.py pilot --seeds 0 1 2 3 4
python outputs/adaptive-retrieval/precision_audit.py
python outputs/adaptive-retrieval/research.py aggregate
python outputs/adaptive-retrieval/validate_results.py
python outputs/adaptive-retrieval/make_report.py
```

When relocating, preserve `outputs/adaptive-retrieval` under a workspace folder, or pass `--data PATH` to the download, pilot and precision-audit commands. Raw downloads require about 160 MB; leave additional space for libraries and results. The ZIP deliberately excludes raw datasets, which remain in `work/adaptive-retrieval`. Downloads verify saved SHA256 values; a changed upstream file fails rather than silently changing the experiment.

No `full` command is supplied: the full-experiment gate failed. Rerunning more seeds on the same pilot queries is not fresh confirmation. Designing an independently justified next study requires a new frozen protocol, distinct contribution and separate evaluation data; there are no pending full jobs here.

## Outputs

- `results.csv`: all 480 conditions, per-run bootstrap intervals, budgets, selector counts, work and FNR.
- `results/*_pilot.npz`: individual pilot query losses and work for paired reanalysis. Query ordering follows the provenance file.
- `results/*_metrics.json`: metrics, build and offline trace timing. Host scheduling affects these values; they are not serving latency measurements.
- `results/*_provenance.json`: input checksums and exact split IDs; reserved IDs never enter evaluation.
- `smoke.json`, `precision_audit.json`: actual correctness audit outcomes.
- `pilot.png`, `pilot.pdf`: descriptive across-seed primary comparison; each plotted point averages five indexes, not five independent datasets.
- `pilot_table.tex`: table of verified pilot results, usable in a later report. This is a table fragment, not a complete paper.
- `manifest.json`: checksums of top-level deliverables; per-dataset hashes are in provenance files.

The simultaneous Hoeffding control bounds per-query worst-over-k loss uniformly over the design-fixed scaled-budget family. Simultaneous marginal k-risk bounds alone would not protect query-dependent k. CRC controls expected marginal loss under its assumptions; neither guarantees every query. The question and known repairs are documented with primary-source links in the report. Review of DARTH+ full text remains incomplete, so no novelty conclusion against it is possible.
