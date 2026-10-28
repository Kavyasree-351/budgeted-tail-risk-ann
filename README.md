# Budgeted Tail-Risk ANN

A CPU research-engineering prototype for **hard per-query distance caps**, simultaneous mean/tail-risk constraints across overlapping query groups, and explicit feasible/infeasible/unknown outcomes in prefix-IVF search.

Includes a design-learned allocation path, strong Learn-then-Test controls, component ablations, exact counter checks, fresh calibration outside the index, frozen protocols and retained negative findings. **A consistent new-method advantage is not established.** The proofs specialize known statistical tools; no original A* theorem or completed paper is claimed.

Read [OVERVIEW.md](OVERVIEW.md), [FINDINGS.md](FINDINGS.md), [THEORY.md](THEORY.md) and [PROTOCOL.md](PROTOCOL.md).

## Standalone quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_checks.py
.\.venv\Scripts\python.exe download.py
.\.venv\Scripts\python.exe experiment.py pilot --seeds 0 1 2 3 4
.\.venv\Scripts\python.exe validate.py
.\.venv\Scripts\python.exe report.py
```

Run from this repository root. Linux/macOS: use `.venv/bin/python`. Inputs download to the ignored, repository-local `work/datasets` folder; `--data PATH` overrides it. Bounded checks use synthetic inputs or existing result traces and require no dataset download. Python 3.12 and exact scientific-library pins were used. Full/final experiments are gated and have not been completed; do not weaken gates or relabel explored queries as fresh data.

## Earlier studies included here

| Folder | Question |
|---|---|
| [studies/adaptive-retrieval](studies/adaptive-retrieval) | Query-dependent retrieval size and calibration |
| [studies/group-conditional-recall](studies/group-conditional-recall) | Marginal versus group-conditional ANN recall |
| [docs/historical-novelty-audit](docs/historical-novelty-audit) | Dated literature/gap screening; not a current novelty claim |

`run_checks.py` checks the main prototype and both earlier studies in separate processes. They share the same repository-local download cache. To rerun earlier pilots:

```powershell
.\.venv\Scripts\python.exe studies/adaptive-retrieval/research.py pilot
.\.venv\Scripts\python.exe studies/group-conditional-recall/experiment.py pilot
```

Their READMEs contain independent aggregation commands; no new final data are needed to inspect existing results. Main outputs retain all 320 policy/cap conditions and 4800 group rows. Counts bound vector-distance evaluations, not wall-clock latency. Certificates target the stated source-query law and assumptions; previously inspected pilots are not fresh confirmation. No failed query or abstention is counted as free success.

See [PUBLICATION.md](PUBLICATION.md) for scope/license status and [THIRD_PARTY.md](THIRD_PARTY.md) for attribution. `ORIGINAL_README.md` preserves historical workspace instructions.
