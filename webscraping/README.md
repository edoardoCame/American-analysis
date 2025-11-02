# Web Scraping utilities

## `sam_attachment_scraper.py`

Download the "Download All" attachment bundles for archived opportunities whose
links are already stored inside `db/sam_archived_opportunities_filtered.sqlite`.
The script relies on Playwright to mimic your manual workflow: it opens each
`Link`, switches to the **Attachments/Links** tab, and clicks the **Download All**
button with a small randomized delay between records.

### Prerequisites

```bash
pip install playwright
playwright install chromium
```

### Example

```bash
python webscraping/sam_attachment_scraper.py \
  --keyword "security guard" \
  --tables fy2025_archived_opportunities fy2026_archived_opportunities \
  --pages 1 \
  --output-dir webscraping/downloads \
  --headless
```

Key flags:

- `--keyword` filters the Title column (case-insensitive substring match).
- `--pages` × `--page-size` controls how many links are processed (default page
  size matches the SAM.gov UI: 25 notices).
- `--tables` accepts multiple fiscal-year tables and stops once the desired
  number of links is collected.
- `--headless` toggles Chromium headless mode; omit it if you want to watch the
  browser for debugging.
- `--throttle-min/--throttle-max` slow things down (defaults 2.5–5.5 s) to avoid
  hammering the site.

Downloads are saved as ZIP files named `{NoticeId}_{suggested_name}.zip` under
`webscraping/downloads/` by default. Logged output lists successes and failures
(e.g., notices with no attachments).
