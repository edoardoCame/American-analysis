# Analisi Strategiche per Aziende nel Settore Security (NAICS 561612)

**Data:** 8 novembre 2025  
**Dataset:** USAspending - Contracts_PrimeTransactions (238,078 contratti, 297 colonne)  
**Contesto:** Oltre la semplice predizione dei costi, queste analisi rispondono a domande strategiche che un'azienda di security services si pone per ottimizzare la partecipazione a gare federali.

---

## 1. Competition Intensity Prediction (Analisi della Competitività)

### Campo chiave
- `number_of_offers_received`

### Obiettivo strategico
Predire **quanti competitor parteciperanno** a una gara prima di investire risorse nella proposta.

### Valore per l'azienda
- **Decisione go/no-go:** Evitare gare troppo affollate con basse probabilità di vittoria
- **Calibrazione offerta:** Aggressività del pricing basata sulla competizione attesa
- **Identificazione nicchie:** Trovare opportunità a bassa competizione ma alto valore
- **Allocazione risorse:** Concentrare effort commerciale su gare più promettenti

### Approccio analitico
1. **Regressione/Classificazione:** Predire `number_of_offers_received` usando:
   - `awarding_agency_code` (alcune agenzie attraggono più competitor)
   - `extent_competed` (full & open vs limited competition)
   - `type_of_set_aside` (set-aside riducono pool competitor)
   - `solicitation_procedures` (negotiated vs simplified)
   - `base_and_all_options_value` (contratti più grandi = più competitor)
   - `product_or_service_code` (specificità del servizio)

2. **Segmentazione:** Cluster di gare "low-competition" (≤3 offer) vs "high-competition" (>5 offer)

3. **Time-series:** Trend di competitività per agenzia nel tempo

### Metriche di successo
- **R² > 0.4** nella predizione del numero di offer
- **Precision > 70%** nell'identificare gare low-competition

---

## 2. Contract Modification Risk Analysis (Rischio di Variazioni Contrattuali)

### Campi chiave
- `modification_number`
- `current_total_value_of_award` vs `base_and_exercised_options_value`
- `parent_award_id_piid` (tracking storico modifiche)
- `action_type_code` (tipo di modifica)

### Obiettivo strategico
Predire **quali contratti subiranno modifiche** (scope changes, budget cuts, estensioni) per gestire rischio operativo e opportunità di upselling.

### Valore per l'azienda
- **Risk assessment:** Identificare agenzie/clienti volatili che cambiano spesso contratti
- **Opportunità upselling:** Modifiche positive = revenue addizionale inatteso
- **Cash flow planning:** Modifiche negative = necessità di riallocazione risorse
- **Pricing strategy:** Includere buffer per contratti ad alto rischio modifica

### Approccio analitico
1. **Classificazione binaria:** Predire se contratto subirà modifiche (`modification_number > 0`)
   - Features: `awarding_agency_code`, `type_of_contract_pricing`, `extent_competed`, `performance_based_service_acquisition`

2. **Regressione:** Predire **quante** modifiche avrà un contratto
   - Aggregare storico per `parent_award_id_piid`

3. **Survival analysis:** Tempo medio alla prima modifica (`action_date` delta tra base e mod 1)

4. **Value change analysis:** Predire se modifiche aumenteranno/diminuiranno il valore
   - Target: `current_total_value_of_award - base_and_exercised_options_value`

### Metriche di successo
- **AUC > 0.75** nella predizione di modifiche
- **MAE < 1.5** nella predizione del numero di modifiche

---

## 3. Agency-Specific Winning Patterns (Strategie per Agenzia)

### Campi chiave
- `awarding_agency_code` + `awarding_agency_name`
- `recipient_name` + `recipient_uei`
- `type_of_set_aside`
- `extent_competed`
- `type_of_contract_pricing`
- `solicitation_procedures`

### Obiettivo strategico
Decodificare le **preferenze di acquisto specifiche** di ciascuna agenzia federale per adattare la strategia commerciale.

### Valore per l'azienda
- **Targeting mirato:** Identificare quali agenzie favoriscono certi tipi di vendor
- **Incumbent identification:** Scoprire chi vince ripetutamente presso ciascuna agenzia
- **Procurement pattern:** Capire se un'agenzia preferisce T&M vs FFP, set-aside vs open
- **Partnership strategy:** Identificare possibili teaming partner basati su co-occorrenze

### Approccio analitico
1. **Descriptive profiling:** Per ogni agenzia calcolare:
   - Top 10 recipient per `total_dollars_obligated`
   - % contratti per `type_of_set_aside`
   - % contratti per `extent_competed`
   - Median contract value
   - Preferred `type_of_contract_pricing`

2. **Network analysis:** 
   - Grafo bipartito agenzia → vincitore ricorrente
   - Metriche di concentrazione (Herfindahl index per distribuzione vendor)

3. **Association rule mining:** Pattern tipo:
   - "Se agenzia=DHS + set_aside=8(a) + NAICS=561612 → vincitore è sempre tra questi 5 vendor"

4. **Agency clustering:** Raggruppare agenzie per comportamento di acquisto simile (K-means su feature aggregate)

### Metriche di successo
- Identificare **incumbent advantage** (% rinnovi per stesso vendor)
- **Concentration ratio** (% di spending controllato dai top 5 vendor per agenzia)

---

## 4. Set-Aside Opportunity Scoring (Ottimizzazione Certificazioni)

### Campi chiave
- `type_of_set_aside` + `type_of_set_aside_code`
- `service_disabled_veteran_owned_business`
- `woman_owned_business`
- `women_owned_small_business`
- `economically_disadvantaged_women_owned_small_business`
- `self_certified_small_disadvantaged_business`
- `minority_owned_business`
- `veteran_owned_business`
- `contracting_officers_determination_of_business_size`

### Obiettivo strategico
Calcolare il **ROI** di ogni certificazione socioeconomica per decidere dove investire tempo/costi di acquisizione.

### Valore per l'azienda
- **Investment prioritization:** Quale certificazione porta più valore?
- **Market sizing:** Quanti contratti security sono riservati a ciascuna categoria?
- **Competitive landscape:** Quanti competitor hanno già ciascuna certificazione?
- **Agency preferences:** Quali agenzie usano di più ciascun set-aside?

### Approccio analitico
1. **Opportunity quantification:**
   - Numero contratti per `type_of_set_aside`
   - Valore totale (`sum(federal_action_obligation)`)
   - Valore mediano per contratto
   - Trend temporale (ultimi 5 anni)

2. **Certification ROI model:**
   ```
   ROI_score = (accessible_contracts_value × win_probability) / certification_cost
   ```
   - `accessible_contracts_value`: Contratti riservati a quella certificazione
   - `win_probability`: Basata su `number_of_offers_received` storico
   - `certification_cost`: Stima esterna (tempo + consulenza)

3. **Agency-certification matrix:** Heatmap di spending per incrocio agenzia × set-aside

4. **Scenario modeling:** "Se otteniamo certificazione SDVOSB, a quanti contratti in più potremmo accedere?"
   - Filter dataset per `service_disabled_veteran_owned_business = True`
   - Calcolare TAM (Total Addressable Market)

### Metriche di successo
- **Ranking certificazioni** per valore opportunità
- **Break-even analysis** per ciascuna certificazione

---

## 5. Performance-Based vs Traditional Contracting Outcomes

### Campi chiave
- `performance_based_service_acquisition` (boolean)
- `type_of_contract_pricing` (FFP, T&M, Cost Plus, ecc.)
- `modification_number`
- `current_total_value_of_award`
- `period_of_performance_current_end_date - period_of_performance_start_date` (duration)

### Obiettivo strategico
Capire se i contratti **performance-based** (pagamento legato a KPI) sono più vantaggiosi/rischiosi dei tradizionali.

### Valore per l'azienda
- **Risk profiling:** I contratti PB hanno più modifiche (instabilità)?
- **Pricing strategy:** Il valore medio è diverso? Serve premium per KPI risk?
- **Agency targeting:** Quali agenzie preferiscono PB contracting?
- **Operational planning:** I contratti PB durano di più o meno?

### Approccio analitico
1. **Comparative analysis:** Confrontare metriche tra PB e non-PB:
   - Median `current_total_value_of_award`
   - Average `modification_number`
   - Contract duration distribution
   - `number_of_offers_received` (competitività)

2. **Propensity score matching:** Isolare effetto causale controllando per:
   - `awarding_agency_code`
   - `base_and_all_options_value`
   - `type_of_contract_pricing`

3. **Regression analysis:** 
   - DV: `current_total_value_of_award`
   - IV: `performance_based_service_acquisition` (dummy)
   - Controls: agency, duration, competition

4. **Interaction effects:** 
   - `performance_based × type_of_contract_pricing`
   - `performance_based × extent_competed`

### Metriche di successo
- **Statistical significance** (p < 0.05) delle differenze
- **Effect size** (Cohen's d) per magnitude differenze

---

## 6. Geographic Market Concentration (Analisi Geografica)

### Campi chiave
- `primary_place_of_performance_state_code`
- `primary_place_of_performance_county_name`
- `recipient_state_code`
- `awarding_agency_code`
- `awarding_office_name`
- `federal_action_obligation`

### Obiettivo strategico
Identificare **dove** concentrare presenza operativa per massimizzare opportunità di contratti federali security.

### Valore per l'azienda
- **Expansion planning:** Dove aprire nuove sedi/branch?
- **Low-competition markets:** Stati/contee con poca presenza competitor
- **Local preference:** Le agenzie favoriscono vendor locali?
- **Federal presence correlation:** Vicinanza a basi militari/uffici federali

### Approccio analitico
1. **Geographic heatmap:**
   - Contratti per stato (count + `sum(federal_action_obligation)`)
   - Visualizzazione choropleth map

2. **Local preference analysis:**
   ```
   local_preference_rate = count(recipient_state = performance_state) / total_contracts
   ```
   - Calcolare per ogni stato
   - Identificare stati con alta preferenza locale (>70%)

3. **Market concentration metrics:**
   - Herfindahl-Hirschman Index per stato (concentrazione vendor)
   - Gini coefficient per distribuzione geografica spending

4. **Time-series regionale:**
   - Crescita YoY spending per stato
   - Emerging markets (stati con >20% crescita negli ultimi 3 anni)

5. **Agency clustering geografico:**
   - Dove si concentrano gli uffici delle agenzie top spender?
   - Correlazione tra `awarding_office_name` e geography

### Metriche di successo
- **Market opportunity score** per stato: `(total_value × growth_rate) / local_competition`
- Identificare top 5 **underserved markets**

---

## 7. Contract Duration & Renewal Probability (Stabilità Revenue)

### Campi chiave
- `period_of_performance_start_date`
- `period_of_performance_current_end_date`
- `period_of_performance_potential_end_date`
- `parent_award_id_piid` (link rinnovi)
- `action_type` + `action_type_code` (NEW, RENEWAL, EXERCISE_OPTION)
- `base_and_all_options_value` (opzioni non esercitate)
- `ordering_period_end_date` (per IDV)

### Obiettivo strategico
Predire la **lifetime** di un contratto e la probabilità di **rinnovo** per pianificare revenue stream e hiring.

### Valore per l'azienda
- **Revenue forecasting:** Contratti lunghi = cash flow prevedibile
- **Workforce planning:** Assumere solo se contratto ha alta probabilità rinnovo
- **Incumbent advantage quantification:** Chi vince tende a rinnovare?
- **Option exercise prediction:** Quali opzioni contrattuali saranno esercitate?

### Approccio analitico
1. **Survival analysis (Kaplan-Meier):**
   - Event: Contratto termina senza rinnovo
   - Censored: Contratto ancora attivo
   - Stratificare per `awarding_agency_code`, `type_of_contract_pricing`

2. **Renewal prediction (classificazione binaria):**
   - Linkare contratti via `parent_award_id_piid`
   - Label: 1 se esiste action_type=RENEWAL dopo end_date, 0 altrimenti
   - Features: duration, modifications, agency, incumbent performance (proxy via value stability)

3. **Duration regression:**
   - Target: `period_of_performance_current_end_date - period_of_performance_start_date`
   - Features: `base_and_all_options_value`, `type_of_contract_pricing`, `awarding_agency_code`

4. **Option exercise analysis:**
   - Calcolare `option_utilization_rate = base_and_exercised_options_value / base_and_all_options_value`
   - Predire quali contratti eserciteranno >80% opzioni

5. **Incumbent analysis:**
   - Per ogni `parent_award_id_piid`, tracciare se `recipient_uei` rimane costante nei rinnovi
   - Calcolare `incumbent_retention_rate` per agenzia

### Metriche di successo
- **Median survival time** per categoria contratto
- **AUC > 0.70** nella predizione renewal
- **Incumbent retention rate** complessivo

---

## 8. Prime vs Subcontractor Strategy (Decisione Strategica)

### Campi chiave
- **Tabella Contracts_PrimeTransactions:**
  - `contract_award_unique_key`
  - `recipient_name` + `recipient_uei` (prime contractor)
  - `subcontracting_plan` + `subcontracting_plan_code`
  - `total_dollars_obligated`

- **Tabella Contracts_Subawards:**
  - `prime_award_unique_key` (link a prime)
  - `subawardee_name` + `subawardee_uei`
  - `subaward_amount`
  - `subaward_description`

### Obiettivo strategico
Decidere quando conviene partecipare come **prime contractor** vs **subcontractor** per massimizzare probabilità di vittoria e margini.

### Valore per l'azienda
- **Channel strategy:** Identificare prime contractor che subappaltano frequentemente
- **Margin analysis:** I subcontratti hanno ROI migliori/peggiori?
- **Capability gaps:** Quali servizi i prime esternalizzano di più?
- **Partnership identification:** Chi sono i migliori prime per teaming agreements?

### Approccio analitico
1. **Prime-Sub network analysis:**
   - JOIN `Contracts_PrimeTransactions.contract_award_unique_key = Contracts_Subawards.prime_award_unique_key`
   - Grafo diretto: prime → sub
   - Metriche di centralità: Quali prime danno più subcontratti?

2. **Subcontracting propensity:**
   - Per ogni prime contractor, calcolare:
     ```
     subcontracting_rate = sum(subaward_amount) / sum(total_dollars_obligated)
     ```
   - Identificare prime con >30% subcontracting rate

3. **Value flow analysis:**
   - Average `subaward_amount` per prime
   - Distribution of subaward sizes (small vs large chunks)

4. **Service specialization:**
   - Text mining su `subaward_description` per identificare patterns (es. "patrol services", "access control")
   - Quali servizi security sono più subappaltati?

5. **Margin proxy (indirect):**
   - Confrontare `federal_action_obligation` (prime) vs `subaward_amount` (sub)
   - Assumption: Prime keeps delta come margin + overhead

6. **Strategic positioning:**
   - Classificare aziende security in 3 categorie:
     - **Pure prime:** >80% revenue da contratti diretti
     - **Hybrid:** 20-80% mix
     - **Pure sub:** >80% revenue da subcontratti
   - Analizzare profitability proxy per categoria

### Metriche di successo
- **Subcontracting network map** (top 20 prime + loro sub preferiti)
- **Average subcontracting rate** per agenzia/tipo contratto
- **Subcontract opportunity size** per security services

---

## Priorità di Implementazione

### High Impact + Complessità Bassa (Quick Wins)
1. **Competition Intensity Prediction** (#1)
   - Dati già disponibili, modello supervised standard
   - Output: Probability score per ogni opportunity
   
2. **Agency-Specific Winning Patterns** (#3)
   - Analisi descrittiva + clustering
   - Output: Agency profile report

3. **Set-Aside Opportunity Scoring** (#4)
   - Calcoli aggregati + ranking
   - Output: ROI table per certificazione

4. **Geographic Market Concentration** (#6)
   - Aggregazioni + visualizzazioni map
   - Output: State opportunity heatmap

### Complessità Media (2-3 settimane)
5. **Contract Modification Risk Analysis** (#2)
   - Richiede tracking temporale con `parent_award_id_piid`
   - Output: Risk score per contratto

6. **Performance-Based vs Traditional Contracting** (#5)
   - Statistical testing + propensity matching
   - Output: Comparative report

### Complessità Alta (1-2 mesi)
7. **Contract Duration & Renewal Probability** (#7)
   - Survival analysis + link temporale complesso
   - Output: Renewal probability model

8. **Prime vs Subcontractor Strategy** (#8)
   - Richiede join tra tabelle + network analysis
   - Output: Subcontracting opportunity map

---

## Note Tecniche

### Limitazioni Dataset USAspending
- **NO win/loss data:** Solo contratti assegnati, nessuna info su bid persi
- **NO pricing details:** Nessun breakdown costi (labor, materials, overhead)
- **NO performance metrics:** Nessun dato su CPARS ratings, past performance
- **Lag temporale:** Dati pubblicati con 30-90 giorni di ritardo

### Dati Complementari Suggeriti
- **SAM.gov Opportunities:** Per analisi pre-award (intent to bid, solicitation text)
- **FPDS-NG:** Source originale con maggior granularità
- **CPARS:** Contract Performance Assessment Reporting System (richiede accesso gov)
- **GovWin IQ / Bloomberg Government:** Commercial data augmentation

### Stack Tecnologico Consigliato
- **Python:** pandas, scikit-learn, statsmodels, networkx
- **Visualization:** matplotlib, seaborn, plotly, folium (mappe)
- **Database:** SQLite attuale OK, PostgreSQL per scaling
- **ML Ops:** MLflow per tracking esperimenti
- **Reporting:** Jupyter notebooks + Streamlit dashboard

---

## Prossimi Passi

1. **Prioritizzare:** Scegliere 1-2 analisi dal tier "High Impact + Bassa Complessità"
2. **Proof of concept:** Implementare in notebook separato
3. **Validazione:** Confrontare output con domain expert security industry
4. **Productization:** Creare dashboard automatizzato
5. **Iterazione:** Aggiungere analisi più complesse incrementalmente

---

**Documento creato:** 8 novembre 2025  
**Autore:** GitHub Copilot (Claude Sonnet 4.5)  
**Dataset:** USAspending Contracts_PrimeTransactions (NAICS 561612)  
**Version:** 1.0
