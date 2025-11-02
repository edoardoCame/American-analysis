# USAspending Physical Security Analysis – Methodology Journal

## 2025-11-02 – Initial setup

- Imported helper utilities into `scripts/usaspending_utils.py` so that notebooks stay lean and rely on reusable functions.
- Restricted all dataset pulls to NAICS codes explicitly maintained in `NAICs.md` (currently 561612) to align with the scope defined by the research team.
- Replaced earlier heuristic scoring with purely descriptive tooling: the refreshed `scripts/usaspending_utils.py` now exposes direct aggregation helpers (counts and obligations by `solicitation_procedures`, offers, competition) without inventing proxy flags.
- Generated a head-of-table snapshot (`data/prime_transactions_head80.csv`) capturing the first 80 rows from `db/prime_transactions_filtered.sqlite` to support field inspection and validation.
- Added a reusable path bootstrap in `notebooks/usaspending.ipynb` to guarantee the repository root (and `scripts` package) is importable when the kernel starts in subdirectories; rewrote and executed the notebook to validate the descriptive solicitation analysis end-to-end.
- Implemented Question 2 of the plan: expanded `scripts/usaspending_utils.py` with cost and duration helpers, updated the notebook with award value summaries and log-scale boxplots by `solicitation_procedures`, and executed the full workflow after the additions.
- Extended the notebook with density/histogram overlays plus a bar chart of median percentage gaps, and documented the complete set of award value fields in both the notebook header and `analysis_plan.md`.

Subsequent notebook work will reference this journal to document refinements, assumptions, and deviations from plan.
