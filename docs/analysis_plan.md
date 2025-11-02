
Got it—no binary “quality flag,” no inference. We’ll answer each of the 7 items **only** with observable fields, using **`solicitation_procedures`** (its labels) as the primary axis for “quality vs. low-bid” analysis. All fields below come from USAspending **Contracts Prime Transactions**. 

---

### 1) Changes over time

**What to compute (by fiscal year):**

* Count of awards and sum of dollars **by `solicitation_procedures` label**.
* Optionally also by `extent_competed` and `number_of_offers_received`.
  **Fields:** `action_date_fiscal_year`, `solicitation_procedures`, `extent_competed`, `number_of_offers_received`, `federal_action_obligation` (flow), `base_and_all_options_value` (ceiling).
 

### 2) Does including “quality criteria” add cost?

**No inference—just stratify cost by procedure label.**

* Compare **award size** and **annualized value** **across `solicitation_procedures` labels**.
* Annualize using performance dates: value ÷ contract years.
  **Fields:** `solicitation_procedures`, `federal_action_obligation`, `base_and_exercised_options_value`, `base_and_all_options_value`, `current_total_value_of_award`, `potential_total_value_of_award`, `total_outlayed_amount_for_overall_award`, `period_of_performance_start_date`, `period_of_performance_current_end_date`/`_potential_end_date`. 

### 3) Do contracts under certain procedure labels have less turnover?

**Observable turnover proxy (no latent tagging):**

* Build “streams” by (agency × NAICS/PSC × geography) and check **vendor changes** between successive awards; then report turnover **by `solicitation_procedures`**.
  **Fields:** `awarding_agency_name`, `awarding_sub_agency_name`, `recipient_uei`/`recipient_name`, `naics_code`/`product_or_service_code`, `primary_place_of_performance_state_name`, performance dates, `solicitation_procedures`. 

### 4) Are certain procedures more/less present by size, value, or method?

**What to compute:**

* Cross-tabs of **`solicitation_procedures` × value buckets** (`base_and_all_options_value`).
* **`solicitation_procedures` × duration** (years from performance dates).
* **`solicitation_procedures` × pricing/competition/vehicle**: `type_of_contract_pricing`, `extent_competed`, `award_or_idv_flag`, `type_of_idc`, `multiple_or_single_award_idv`, `type_of_set_aside`.
  All are direct group-bys—no scoring. 

### 5) Do procurement strategies correlate with certain procedure labels?

**Descriptive associations only (no modeling required):**

* Show distributions of strategy fields **within each `solicitation_procedures` label**:
  `extent_competed`, `number_of_offers_received`, `type_of_set_aside`, `evaluated_preference`, `contract_bundling`, `fair_opportunity_limited_sources`, `commercial_item_acquisition_procedures`, `simplified_procedures_for_certain_commercial_items`, `undefinitized_action`, `type_of_contract_pricing`.
  Simple cross-tabs or χ²/Cramér’s V are fine as descriptive stats.

### 6) Other cuts that reveal when procedure choices are helped/blocked

**Straight group-bys—again, no inference:**

* **Competition:** distribution of `number_of_offers_received` by `solicitation_procedures`.
* **Agency/office:** `awarding_agency_name`, `awarding_office_name` by `solicitation_procedures`.
* **Geography:** `primary_place_of_performance_state_name`/country by `solicitation_procedures`.
* **Vehicle structure:** `award_or_idv_flag`, `type_of_idc`, `multiple_or_single_award_idv`, `fair_opportunity_limited_sources` by `solicitation_procedures`. 

---





# Additioanl infos on certain data fields
 
 | **Field name (in USAspending)** | **What it represents** | **How it helps infer awarding logic** |
|----------------------------------|-------------------------|----------------------------------------|
| solicitation_procedures | Describes how bids were solicited (e.g., Sealed Bid, Negotiated, Simplified Acquisition). | “Sealed Bid” corresponds almost always to lowest-price technically acceptable (LPTA) awards. “Negotiated” (FAR Part 15) allows best-value tradeoff (price + quality). |
| extent_competed | Indicates how much competition occurred (e.g., Full and Open Competition, Not Competed). | If fully competed → likely price-sensitive. If limited or not competed → selection may depend on technical/quality factors or urgent need. |
| other_than_full_and_open_competition | Lists statutory exceptions to open competition. | Helps identify sole-source or restricted awards — these often rely on qualitative or capability-based justification (not price competition). |
| fair_opportunity_limited_sources | Used under multi-award IDVs to note if the opportunity was limited. | Indicates non-competitive awards, implying that technical quality or mission fit drove selection. |
| number_of_offers_received | Total bids received for the solicitation. | Fewer offers = weaker price competition → quality or technical capacity may have weighed more heavily. |
| type_of_contract_pricing | Defines the pricing mechanism (e.g., Firm Fixed Price, Cost Plus Award Fee, Incentive Fee). | “Firm Fixed Price” → typically price-based. “Cost Plus Award Fee” or “Incentive Fee” → includes performance or quality incentives (thus quality-based). |
| performance_based_service_acquisition | Flag indicating if service requirements were defined in terms of measurable outcomes. | “Y” = contract evaluated and monitored by results → strong proxy for quality-based or outcome-oriented criteria. |
| contract_bundling | Whether multiple requirements were bundled. | Complex, bundled contracts are more likely to include performance or quality factors (vs. small, price-only tasks). |
| solicitation_identifier | ID linking to the original solicitation on SAM.gov. | You can use it to retrieve the Evaluation Factors for Award section — the only direct source of price vs. quality criteria. |
| extent_competed_code, solicitation_procedures_code, etc. | Numeric versions of the above text fields. | Useful for coding and quantitative analysis of procurement method. |
| type_of_set_aside | Indicates preference programs (e.g., Small Business Set-Aside). | Some set-asides use best-value even under low-price context; interesting to test for correlation. |
| evaluated_preference | Notes statutory evaluation preferences (e.g., Buy American, Small Disadvantaged Business). | These preferences can modify the pure price ranking — introducing non-price criteria (policy-based weighting). |
| price_evaluation_adjustment_preference_percent_difference | Adjustment percentage applied for evaluation preferences. | Quantifies the extent to which non-price factors (e.g., domestic preference) affect final evaluation. |
| simplified_procedures_for_certain_commercial_items | Indicates if simplified acquisition methods were used. | Simplified methods typically imply price-driven decisions with less formal quality evaluation. |
| commercial_item_acquisition_procedures | Whether commercial item acquisition rules apply. | If “Commercial” and “Simplified,” then price is usually the dominant criterion. |
| type_of_idc / multiple_or_single_award_idv | Contract structure (Indefinite Delivery / Multiple Award). | In multi-award IDVs, task orders may later be competed using best-value or price-only rules — can signal a two-step evaluation. |
| undefinitized_action | Indicates if terms were finalized after performance began. | Often linked to urgent or specialized awards where technical performance dominates price competition. |
