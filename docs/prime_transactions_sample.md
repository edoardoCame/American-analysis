# Prime Transactions — Esempio record

Panoramica dataset filtrato (NAICS 561612, escluso DoD):
- Contracts_PrimeTransactions: 220,528 righe
- Contracts_Subawards: 120 righe
- Totale: 220,648 righe

Questo estratto mostra i primi 5 record utili per comprendere come vengono descritte le transazioni nel file `Contracts_PrimeTransactions_2025-10-22_H14M09S33_1.csv`, importato in `db/prime_transactions.sqlite`.
Le stesse query funzionano identiche su `db/prime_transactions_filtered.sqlite`,
che contiene solo i record con `naics_code = 561612`.

## Query utilizzata
```sql
SELECT
  contract_transaction_unique_key AS transaction_key,
  award_id_piid AS award_id,
  naics_code,
  naics_description,
  transaction_description,
  prime_award_base_transaction_description AS award_summary
FROM contracts_primetransactions_2025_10_22_h14m09s33_1
WHERE naics_description IS NOT NULL
  AND transaction_description IS NOT NULL
LIMIT 5;
```

## Anteprima (testo troncato a 80 caratteri)
| transaction_key | award_id | naics_code | naics_description | transaction_description | award_summary |
|---|---|---|---|---|---|
| 0559_-NONE-_05GA0A19A0006_P00012_-NONE-_-NONE- | 05GA0A19A0006 | 561612 | SECURITY GUARDS AND PATROL SERVICES | EXTEND THE MASTER BPA (CLINS 0501 - 0516) ENDING PERIOD OF PERFORMANCE FROM 1... | VENDOR: AMERICAN SECURITY PROGRAMS INC. CONTRACT #: 05GA0A19A0006  ARMED GUAR... |
| 0559_-NONE-_05GA0A19A0006_P00014_-NONE-_-NONE- | 05GA0A19A0006 | 561612 | SECURITY GUARDS AND PATROL SERVICES | THE PURPOSE OF THIS NO-COST MODIFICATION IS TO EXTEND THE MASTER BPA (CLINS 0... | VENDOR: AMERICAN SECURITY PROGRAMS INC. CONTRACT #: 05GA0A19A0006  ARMED GUAR... |
| 0559_-NONE-_GAO10CO0003_23_-NONE-_-NONE- | GAO10CO0003 | 561612 | SECURITY GUARDS AND PATROL SERVICES | G4S GOVERNMENT SOLUTIONS INC | GUARD SERVICES |
| 0559_-NONE-_GAO10CO0003_31_-NONE-_-NONE- | GAO10CO0003 | 561612 | SECURITY GUARDS AND PATROL SERVICES | REQ FOR MOD - STEP 1 OF 2 STEP PROCESS TO CORRECT FUNDING STRING - WRONG ORG ... | GUARD SERVICES |
| 0559_0559_05GA0A19K0024_0_05GA0A18A0002_0 | 05GA0A19K0024 | 561612 | SECURITY GUARDS AND PATROL SERVICES | PROPOSAL -REVISION #1 (B8G-029-001) TECHNICAL SURVEILLANCE COUNTERMEASURES SE... | PROPOSAL -REVISION #1 (B8G-029-001) TECHNICAL SURVEILLANCE COUNTERMEASURES SE... |

In particolare, le colonne:
- `transaction_description` riporta il motivo operativo o la descrizione libera dell’azione (estensioni, modifiche, proposte).
- `award_summary` (alias `prime_award_base_transaction_description`) sintetizza la descrizione dell’award originale, spesso includendo fornitore e tipologia di servizio.

## Descrizioni complete (primi esempi)
- **Transaction** `0559_-NONE-_05GA0A19A0006_P00012_-NONE-_-NONE-`  
  - `transaction_description`: EXTEND THE MASTER BPA (CLINS 0501 - 0516) ENDING PERIOD OF PERFORMANCE FROM 12/31/2024 THROUGH 2/28/2025.  
  - `award_summary`: VENDOR: AMERICAN SECURITY PROGRAMS INC. CONTRACT #: 05GA0A19A0006  ARMED GUARD FORCE SERVICES - POP 9/01/19 - 8/31/24
- **Transaction** `0559_-NONE-_05GA0A19A0006_P00014_-NONE-_-NONE-`  
  - `transaction_description`: THE PURPOSE OF THIS NO-COST MODIFICATION IS TO EXTEND THE MASTER BPA (CLINS 0501 - 0516) PERIOD OF PERFORMANCE FROM 2/28/2024 -  3/31/2025.  
  - `award_summary`: VENDOR: AMERICAN SECURITY PROGRAMS INC. CONTRACT #: 05GA0A19A0006  ARMED GUARD FORCE SERVICES - POP 9/01/19 - 8/31/24
- **Transaction** `0559_-NONE-_GAO10CO0003_31_-NONE-_-NONE-`  
  - `transaction_description`: REQ FOR MOD - STEP 1 OF 2 STEP PROCESS TO CORRECT FUNDING STRING - WRONG ORG CODE WAS USED ON PREVIOUS RFM (1785BAA000 INSTEAD OF 1795BAA000).  
  - `award_summary`: GUARD SERVICES
- **Transaction** `0559_0559_05GA0A19K0024_0_05GA0A18A0002_0`  
  - `transaction_description`: PROPOSAL -REVISION #1 (B8G-029-001) TECHNICAL SURVEILLANCE COUNTERMEASURES SERVICES TASK#GAO1911200002  
  - `award_summary`: PROPOSAL -REVISION #1 (B8G-029-001) TECHNICAL SURVEILLANCE COUNTERMEASURES SERVICES TASK#GAO1911200002

## Cos’è `prime_award_base_transaction_description`?
È la descrizione testuale dell’award di base a cui la transazione fa riferimento: riporta contesto della gara, fornitore, condizioni economiche e clausole principali. L’esempio più esteso trovato nel dataset:

> **Transaction** `4732_4730_GSFPNBKP3052_0_GS07F5500R_0`  
> VENDOR: TRINITY PROTECTION SERVICES – *estratto completo:*  
> THIS ORDER IS BEING ISSUED AGAINST TRINITY PROTECTION SERVICES' S MULTIPLE AWARD SCHEDULE (MAS) CONTRACT, GS-07F-5500R. IN ACCORDANCE WITH QUOTE, DATED JUNE 18, 2012, AND CLARIFIED ON JULY 16, 2012, FROM MR. CAMERON COLLINS - DIRECTOR OF BUSINESS DEVELOPMENT, SUBMITTED IN RESPONSE TO THE GSA RFQ FOR ARMED GUARD SERVICES FOR THE DRMSC, ISSUED ON MAY 31, 2012, THE ABOVE DOCUMENTS ARE HEREBY INCORPORATED AND MADE PART OF THIS ORDER. THIS FIRM-FIXED PRICE ORDER IS FOR ONE-YEAR OF ARMED GUARD SERVICES, WITH FOUR, ONE-YEAR OPTION PERIODS. [...] FAR CLAUSE 52.222-54, EMPLOYMENT ELIGIBILITY VERIFICATION (JAN 2009), INCLUDED IN THE RFQ, IS HEREBY INCORPORATED INTO THE PURCHASE ORDER. FUNDING FOR THIS ORDER IS PROVIDED VIA MIPR NO. HQ068121160001.

## Cos’è `solicitation_procedures`?
È la descrizione testuale del codice `solicitation_procedures_code`, cioè la procedura di gara utilizzata (es. gara negoziata, acquisto semplificato, singola fonte). Prime occorrenze nel database:

| solicitation_procedures_code | solicitation_procedures          | Esempio transaction_key                                  |
|---|---|---|
| `MAFO` | SUBJECT TO MULTIPLE AWARD FAIR OPPORTUNITY | `0559_-NONE-_05GA0A19A0006_P00012_-NONE-_-NONE-` |
| `NP`   | NEGOTIATED PROPOSAL/QUOTE                 | `0559_-NONE-_GAO10CO0003_23_-NONE-_-NONE-` |
| `SP1`  | SIMPLIFIED ACQUISITION                    | `0559_0559_05GA0A19K0024_0_05GA0A18A0002_0` |
| `SSS`  | ONLY ONE SOURCE                           | `0574_4730_GSVWXQ212088_0_47QSHA20A002E_0` |
| `SB`   | SEALED BID/FORMAL ADVERTISING             | `0473_4700_47QMCA21K001R_0_47QMCA19D000P_0` |

Questi valori chiariscono se la solicitation è stata negoziata, affidata a fonte unica, soggetta a fair opportunity tra più award, ecc.
