# USAspending Physical Security Analysis – Methodology Journal

## 2025-11-02 – Initial setup

- Imported helper utilities into `scripts/usaspending_utils.py` so that notebooks stay lean and rely on reusable functions.
- Restricted all dataset pulls to NAICS codes explicitly maintained in `NAICs.md` (currently 561612) to align with the scope defined by the research team.
- Implemented a quality scoring heuristic anchored in `solicitation_procedures` guidance:
  - Awards with **Negotiated** or other FAR Part 15 trade-off language receive strong positive weighting.
  - Entries marked as **Sealed Bid**, **Simplified Acquisition**, or similar price-first procedures receive a penalty.
  - Additional signals (performance-based service acquisitions, incentive fee pricing, limited competition, single-offer events) provide incremental adjustments to the score.
- Generated a head-of-table snapshot (`data/prime_transactions_head80.csv`) capturing the first 80 rows from `db/prime_transactions_filtered.sqlite` to support field inspection and validation.

Subsequent notebook work will reference this journal to document refinements, assumptions, and deviations from plan.
