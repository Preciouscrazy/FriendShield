# FriendShield — reproducible validation

**Scope:** Offline advisory-review scoring against fabricated, labeled scenarios. These are not verified bot labels, real account records, or estimates of real-world performance.

## Baseline
- On the original `main` branch, [GitHub Actions run #42587127011](https://github.com/Preciouscrazy/FriendShield/actions/runs/42587127011) completed successfully on Ubuntu with Python 3.10, 3.11 and 3.12.
- The baseline included **23 test methods** and two versioned demonstration artifacts: [JSON evaluation](sample-evaluation.json) and [offline HTML dashboard](sample-dashboard.html).

## Final cleanup and regression scope
- Adds **six focused CLI/evidence tests** while preserving scoring rules and the existing 12-row fixture.
- Validates that report/dashboard output paths cannot overwrite the input CSV, either directly or through existing hard links; report/dashboard hard-link collisions are rejected before any writes.
- Checks the generated synthetic evaluation report against the committed golden JSON structure.
- GitHub Actions runs all tests and a synthetic evaluation/dashboard smoke command across **Windows and Ubuntu** with Python **3.10–3.12**.

## Expected synthetic result
At threshold 60 on `examples/labeled_requests.csv`, the 12 fabricated examples produce **TP=4, FP=2, TN=4, FN=2** (precision and recall both 66.7%). These fixed fixture outcomes are not field validation of any automated bot-identification capability.

## Reproduce
```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m friendshield --evaluate examples/labeled_requests.csv --threshold 60 --output evaluation-report.json --dashboard evaluation-dashboard.html
```

## GitHub-hosted verification

| Environment | Python 3.10 | Python 3.11 | Python 3.12 |
| --- | --- | --- | --- |
| Ubuntu 24.04 | Pending | Pending | Pending |
| Windows latest | Pending | Pending | Pending |

**Not yet verified on the upgrade branch.** This table will be updated only after the final commit's hosted workflows complete successfully.
