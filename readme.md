# SAM.gov — Dati organizzati e utility

Raccolta e normalizzazione di dataset pubblici da SAM.gov/USASpending con
strumenti per analisi rapide e download degli allegati dalle opportunità
archiviate.

Se cerchi lo schema dettagliato delle tabelle o l’elenco completo delle colonne
dei CSV, vedi `docs/sam_archived_opportunities_filtered.md` e
`docs/prime_transactions.md`.

## Struttura della repository
- `data/` — CSV grezzi scaricati (quando presenti)
- `db/` — database SQLite pronti per interrogazioni
- `docs/` — documentazione su schemi e campi
- `scripts/` — utility per analisi (Python e shell)
- `webscraping/` — strumenti Playwright per scaricare allegati
- `notebooks/` — analisi esplorative in Jupyter
- `NAICs.md` — note e mapping NAICS rilevanti

## Dataset inclusi

### Archived Opportunities
- CSV consolidati in `data/archived_opportunities/` (FY1970–FY2026, schema
  omogeneo a 47 colonne) — vedi `docs/sam_archived_opportunities_filtered.md`.
- Database:
  - `db/sam_archived_opportunities.sqlite` — replica completa multi‑FY
  - `db/sam_archived_opportunities_filtered.sqlite` — sottoinsieme filtrato per
    `NaicsCode = 561612` (security services) utile per analisi mirate

Colonne principali: `NoticeId`, `Title`, `Sol#`, `Department/Ind.Agency`,
`Sub-Tier`, `PostedDate`, `Type`, `ArchiveType`, `ArchiveDate`, `SetASide*`,
`ResponseDeadLine`, `NaicsCode`, `ClassificationCode`, `Pop*`, `Award*`,
`PrimaryContact*`, `SecondaryContact*`, `OrganizationType`, `State/City/Zip`,
`AdditionalInfoLink`, `Link`, `Description`.

### Prime Transactions & Subawards (estrazione 2025‑10‑22)
- CSV in `data/prime_transactions/`:
  - `Contracts_PrimeTransactions_...csv` — 238.078 righe, 297 colonne
  - `Contracts_Subawards_...csv` — 516 righe, 118 colonne
  - `Assistance_*` — vuoti in questo estratto
- Database:
  - `db/prime_transactions.sqlite` — tabelle importate con indici sulle chiavi
  - `db/prime_transactions_filtered.sqlite` — contiene solo `naics_code = 561612`:
    - `contracts_primetransactions_2025_10_22_h14m09s33_1`: 238.078 righe
    - `contracts_subawards_2025_10_22_h14m19s43_1`: 253 righe
- Dettagli colonne: `docs/prime_transactions.md` e `docs/prime_transactions_sample.md`

## Come iniziare

Requisiti: Python 3.10+, `sqlite3`, `pip`.

1) Ambiente Python

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install pandas playwright
playwright install chromium
```

2) Interrogare i database

```bash
# esempio: conteggio per tabella FY
sqlite3 db/sam_archived_opportunities_filtered.sqlite "\
  SELECT name, (SELECT COUNT(1) FROM '"||name||"') AS rows\n\
  FROM sqlite_master WHERE type='table' AND name LIKE 'fy%_archived_opportunities'\n\
  ORDER BY name;"

# esempio: NAICS più frequenti sulle archiviate filtrate
sqlite3 db/sam_archived_opportunities_filtered.sqlite "\
  SELECT NaicsCode, COUNT(1) c FROM fy2025_archived_opportunities\n\
  GROUP BY NaicsCode ORDER BY c DESC LIMIT 10;"
```

3) Analisi veloce in Python

```python
from scripts.sam_market_analysis import get_connection, load_opportunities, enrich_dataset, yearly_summary

with get_connection("db/sam_archived_opportunities_filtered.sqlite") as conn:
    df = load_opportunities("db/sam_archived_opportunities_filtered.sqlite")
    df = enrich_dataset(df)
    print(yearly_summary(df).head())
```

## Download allegati (Playwright)

Strumenti per scaricare i bundle “Download All” delle opportunità archiviate.
Vedi anche `webscraping/README.md`.

Esempio mirato:
```bash
python webscraping/sam_attachment_scraper.py \
  --keyword "security guard" \
  --tables fy2025_archived_opportunities fy2026_archived_opportunities \
  --pages 1 \
  --output-dir webscraping/downloads \
  --headless
```

Lancio massivo per tutte le tabelle popolate:
```bash
bash scripts/launch_all_tables.sh
```

I file ZIP sono salvati come `{NoticeId}_{nome_suggerito}.zip` sotto
`webscraping/downloads/…`. Il percorso viene registrato nella colonna
`DownloadPath` della tabella sorgente.

## Note e fonti
- Dati provenienti da SAM.gov e USASpending; eventuali anomalie di encoding
  vengono gestite forzando la decodifica UTF‑8 con sostituzione caratteri.
- Le estrazioni possono cambiare nel tempo; i conteggi riportati qui riflettono
  lo stato dei file presenti nella repo.

## Roadmap (breve)
- Aggiungere script di import SQL riproducibili per i CSV Prime/Assistance
- Pubblicare requirements opzionali per analisi (matplotlib/seaborn, duckdb)
- Arricchire i notebooks con visualizzazioni standard
