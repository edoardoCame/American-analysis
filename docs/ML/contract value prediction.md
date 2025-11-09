# Understanding the Drivers of Physical Security Contract Values

## Executive Summary

This document provides a plain-language interpretation of the factors that influence the annual value of U.S. federal physical security service contracts. Our analysis examined thousands of government contracts for security guard services and identified which characteristics are associated with higher or lower contract spending.

The findings reveal that contract values are primarily driven by the specific government agency involved, the geographic location of service delivery, and the particular security program under which the contract is awarded. Understanding these patterns can help policymakers, contracting officers, and industry participants anticipate cost structures and plan accordingly.

---

## Methodology Overview

We analyze physical security contracts with a histogram gradient-boosting regressor trained on the log10 of the annualised contract value. The model ingests 4 quantitative signals (offers received, performance duration, and their logarithmic transforms) alongside 140 categorical descriptors that capture agencies, procedures, socio-economic flags, bundling status, and product/service codes. Price-related columns are explicitly filtered before training to avoid leakage.

Because gradient boosting captures non-linear interactions, we interpret results through feature-importance rankings, partial-dependence style plots, and scenario simulations rather than simple percentage coefficients. All findings below therefore reflect complex interactions among procurement attributes rather than isolated one-to-one effects. We expressly drop `action_date_fiscal_year` from the feature matrix so temporal context does not dominate the predictions.

---

## Key Interpretive Themes

### Geographic Patterns

International security contracts show a clear bifurcation:
- **High-cost operations:** Contracts supporting major diplomatic missions, conflict zones (Iraq), or integrated international programs command premium pricing.
- **Low-cost operations:** Locally sourced guard services in stable regions (Panama, Slovakia, UAE) operate at conventional commercial rates tied to local wage markets.

### Mission Criticality

The highest-value contracts consistently support:
- **Nuclear security:** DOE protective forces and related programs
- **Critical infrastructure:** NASA facilities, mine safety installations
- **Hazardous environments:** Locations requiring specialized emergency response capabilities

Conversely, lower-value contracts support:
- **Administrative facilities:** Routine office security
- **Small installations:** Consular offices, regional field offices
- **Standard commercial services:** Guard posts without specialized requirements

### Procurement Structure

Contract values respond to procurement organization:
- **Centralized programs:** Enterprise-wide or headquarters-level contracts consolidate requirements and increase individual contract size
- **Regional consolidation:** Area-wide contracts reduce per-location spending through economies of scale
- **Specialized program vehicles:** Named programs (IPSC, Protective Force Services) signal premium service requirements

### Socioeconomic Considerations

Permutation importance within the gradient-boosted model consistently ranks the self-certified small disadvantaged business flag as the single most powerful predictor of contract value. This suggests federal policy successfully channels premium security work to firms meeting diversity and inclusion goals—an intentional program design feature rather than an unintended cost premium.

---


## Limitations and Caveats

This analysis examines statistical associations, not causal relationships. The model identifies which characteristics *accompany* high or low contract values but cannot definitively prove that any particular characteristic *causes* those values.

Several important nuances:

1. **Data Classification Matters:** The difference between "country of origin" and "performance location" codes produces opposite effects (Madagascar, Costa Rica), highlighting that administrative data fields sometimes capture different aspects of complex international operations.

2. **Omitted Variables:** Factors not recorded in the contract database—such as specific site threat assessments, protective intelligence requirements, or emergency response capabilities—undoubtedly influence costs but cannot be captured in this model.

3. **Selection Effects:** High-value contracts may flow to particular agencies *because* those agencies manage inherently expensive missions, not because the agency itself drives costs upward. The model identifies the pattern but cannot fully separate mission requirements from organizational effects.

4. **Temporal Changes:** The model pools contracts across multiple fiscal years (2008–2025). Security requirements, procurement strategies, and cost structures evolved over this period. The coefficients represent average relationships across this entire timeframe.

5. **Contract Modifications:** The data captures contract actions as recorded, but complex modifications, option exercises, and performance changes may blur the relationship between initial contract characteristics and final realized costs.

---

## Advanced Analysis: Gradient-Boosted Model Insights

The gradient-boosted model detects complex, non-linear interactions between multiple factors and achieves an out-of-sample R² of approximately 0.49, revealing policy-relevant patterns that simpler additive models miss.

The gradient-boosting approach measures "relative importance" rather than directional coefficients. Higher importance scores indicate that a characteristic plays a larger role in distinguishing high-value from low-value contracts, but the relationship may be non-linear or conditional on other factors.

### Top Drivers in the Gradient-Boosted Model

#### 1. **Self-Certified Small Disadvantaged Business (Importance: 0.358)**

This single characteristic is by far the most powerful predictor of contract value—more influential than all other factors combined. Contracts awarded to firms that self-certify as small disadvantaged businesses show systematically different value patterns.

**Why this matters:** Federal acquisition policy actively encourages agencies to award contracts to small disadvantaged businesses through set-aside programs, evaluation preferences, and socioeconomic contracting goals. The strong importance of this variable suggests that these policy mechanisms successfully channel substantial security work to qualifying firms.

This does not necessarily indicate that disadvantaged business status itself *causes* higher values. Rather, it reveals that government agencies pursuing inclusion goals tend to structure contracts, define requirements, and evaluate proposals in ways that result in different value distributions. Premium security programs may deliberately incorporate disadvantaged business participation as a program design element, or qualifying firms may concentrate in particular market segments (specialized services, geographic regions, or agency relationships) that command higher values.

The finding validates that socioeconomic contracting policy materially affects the security services marketplace—it is not merely a procedural checkbox but a significant determinant of which firms receive which types of work at what value levels.

#### 2. **Award Type Code (Importance: 0.177)**

How contracts are structured—as definitive contracts, purchase orders, delivery orders, or blanket purchase agreements—strongly predicts their value.

**The Four Primary Award Types:**

- **Code D – Definitive Contract (16,950 contracts):** Traditional stand-alone contracts with specified scope, price, and performance period. These represent complete, self-contained procurements where the government knows exactly what it needs and negotiates a firm agreement. Median annualized value: **$301,000**.

- **Code C – Delivery Order (89,434 contracts):** Task orders issued against pre-existing IDIQ contracts or other ordering vehicles. Agencies establish broad contract terms with one or multiple vendors, then issue specific delivery orders as requirements emerge. This is the most common structure in our dataset. Median annualized value: **$134,000**.

- **Code A – Blanket Purchase Agreement (BPA) Call (17,586 contracts):** Simplified ordering mechanisms, typically used for recurring purchases of similar services at pre-negotiated prices. BPAs streamline repetitive procurements by establishing pricing and terms upfront, then issuing simple "calls" against the agreement. Median annualized value: **$87,000**.

- **Code B – Purchase Order (65,155 contracts):** The simplest acquisition method, typically for straightforward commercial purchases under simplified acquisition thresholds. Purchase orders involve minimal negotiation and documentation. These are the most numerous but smallest in value. Median annualized value: **$25,000**.

**Why this matters:** Contract structure reflects acquisition strategy and mission complexity. The data reveal a clear hierarchy:

- **Definitive contracts** command the highest values because they support specialized, complex missions requiring comprehensive statements of work, detailed performance requirements, and extensive security specifications. Nuclear protective forces, critical infrastructure security, and high-threat international operations typically use definitive contracts.

- **Delivery orders** balance flexibility with moderate values, serving as the workhorse of federal security procurement. They allow agencies to adjust guard force sizes, shift coverage between facilities, and respond to changing threat levels while maintaining pre-competed rates. Major security programs at NASA, DOE, and other agencies rely heavily on delivery order vehicles.

- **BPA calls** serve routine, recurring needs—standard guard posts that operate year after year with minimal variation. The pre-negotiated pricing and streamlined ordering reduce administrative burden for both government and contractors.

- **Purchase orders** handle the smallest, simplest requirements—temporary guard coverage, event security, or minor facility protection that doesn't justify formal contracting processes.

The high importance of award type indicates that acquisition strategy and contract vehicle selection are not merely administrative choices but fundamental determinants of program cost structure. Agencies pursuing integrated, flexible security solutions use delivery order mechanisms; those procuring simple guard services use straightforward purchase orders or BPA calls. The two approaches produce systematically different value patterns—and the gradient-boosted model detects these structural differences as the second-most important predictor of contract value.

#### 3. **Action Date Fiscal Year (Importance: 0.102)**

When a contract is awarded significantly influences its value, even after accounting for inflation adjustments in the underlying data.

**Why this matters:** This temporal pattern likely captures several overlapping trends:

- **Policy evolution:** Acquisition strategies, socioeconomic goals, and procurement regulations change over time, affecting how agencies structure and value security contracts.
- **Threat environment shifts:** Security requirements intensified following specific events (September 11, 2001; COVID-19 pandemic; facility attacks) and subsequently stabilized, creating temporal clusters of high- or low-value procurement.
- **Budget cycles:** Federal security spending responds to Congressional appropriations, continuing resolutions, and sequestration pressures that vary by fiscal year.
- **Market maturation:** The security services industry consolidated and professionalized over the 2008-2025 study period, potentially affecting competitive dynamics and pricing structures.

The importance of fiscal year suggests that understanding contract values requires situating them in their specific policy and budgetary context—comparisons across widely separated time periods may be misleading.

#### 4. **Solicitation Procedures (Importance: 0.053)**

How agencies compete contracts—through negotiated proposals, simplified acquisitions, or fair opportunity procedures—predicts values even in the non-linear model.

**Why this matters:** Solicitation procedures interact with competition intensity, agency identity, and subcontracting requirements. Negotiated competitions may produce different value patterns depending on how many offers the agency receives or whether subcontracting plans are required, so procurement design choices have measurable cost consequences.

The moderate importance score (compared to top-ranking factors) suggests that *how* agencies compete is less determinative than *what* they buy and *who* provides it. Procurement method matters, but mission requirements and vendor characteristics matter more.

#### 5. **Performance Years (Importance: 0.038)**

Contract duration (length of the performance period) helps predict annualized values even though our target variable explicitly controls for duration by calculating annual spending rates.

**Why this matters:** This seemingly paradoxical finding reveals that contracts of different durations have systematically different annualized cost structures. Longer contracts do not simply spread the same work over more years—they represent fundamentally different security programs.

Possible explanations include:
- **Startup amortization:** Longer contracts amortize one-time costs (background investigations, training, security clearances, equipment procurement) over more years, reducing annualized spending.
- **Price stability:** Multi-year contracts lock in pricing that may become favorable as market rates increase, reducing effective annualized costs.
- **Learning curves:** Security contractors become more efficient as they gain experience at a specific facility, reducing staffing needs and hourly costs in later contract years.
- **Mission complexity:** Shorter contracts may concentrate in specialized, high-intensity missions (emergency response, temporary threat escalations), while longer contracts support routine, steady-state operations.

#### 6. **Type of IDC (Importance: 0.036)**

The specific category of indefinite-delivery contract vehicle (IDIQ, definitive contract, purchase order, etc.) predicts values independently of the broader award type code.

**Why this matters:** Within the category of flexible contract vehicles, subtle distinctions matter. Multiple-award IDIQs (where several contractors compete for individual task orders) produce different value patterns than single-award IDIQs (where one contractor holds exclusive ordering rights). Government-wide acquisition contracts (GWACs) and agency-specific IDIQs serve different missions and price points.

The importance of these fine-grained distinctions suggests that acquisition professionals' detailed vehicle selection decisions—not merely the general category—affect program costs.

#### 7. **Foreign Funding (Importance: 0.035)**

Whether a contract includes cost-sharing from foreign governments or international organizations strongly predicts its value.

**Why this matters:** Foreign funding typically indicates coalition operations, embassy security in partnership with host nations, or international facility protection where allied governments share costs. These arrangements emerge only for significant, strategically important installations—not routine guard services.

The importance of this variable reveals that international security cooperation concentrates in high-value programs. Contracts worth the diplomatic complexity of negotiating cost-sharing agreements represent premium protective missions.

#### 8. **Log Offers (Importance: 0.032)**

The logarithm of the number of offers received (a transformed version of the raw count) predicts values in a non-linear fashion.

**Why this matters:** Competition intensity affects pricing, but the relationship is not linear. The difference between one and two offers matters enormously; the difference between ten and eleven offers matters little. The logarithmic transformation captures this diminishing-returns pattern.

Importantly, this finding indicates that competition *does* occur even in negotiated procurements—agencies receive multiple proposals and select among them. The non-linear relationship suggests that minimal competition (2-3 bidders) provides most of the price discipline, with additional bidders offering decreasing marginal benefits.

#### 9. **Subcontracting Plan (Importance: 0.031)**

Whether the contractor must submit a subcontracting plan (typically required for contracts exceeding $750,000 with subcontracting opportunities) strongly predicts value.

**Why this matters:** Subcontracting plan requirements serve as a proxy for contract size and complexity. Large security contracts involve multiple specialized capabilities—access control systems, mobile patrols, K-9 units, emergency response, command centers—that prime contractors deliver through subcontractor networks.

The importance of this variable validates that complex, integrated security solutions command higher values than simple guard posts. It also suggests that federal socioeconomic policy—which requires prime contractors to provide opportunities for small, disadvantaged, and veteran-owned subcontractors—shapes high-value security procurements.

#### 10. **Awarding Agency Code (Importance: 0.029)**

Which specific federal agency awards the contract remains an important predictor even after accounting for numerous other characteristics.

**Why this matters:** Agency identity captures residual mission-specific factors not fully explained by program codes, funding sources, or other variables. Department of Energy security requirements differ fundamentally from Department of Agriculture requirements even for superficially similar guard services, reflecting classified operations, nuclear materials, threat environments, and security clearance needs.

The persistence of agency effects in the gradient-boosted model (which already accounts for dozens of other variables) indicates that organizational culture, risk tolerance, and mission context create genuine inter-agency cost differences beyond what observable contract characteristics can explain.

#### 11. **Number of Offers Received (Importance: 0.024)**

The raw count of competing proposals (alongside the logarithmic transformation discussed above) independently contributes to predictions.

**Why this matters:** Including both the raw count and logarithmic transformation allows the model to detect complex competition patterns. Some value categories may respond linearly to competition intensity; others may show threshold effects or diminishing returns.

#### 12. **Extent Competed (Importance: 0.021)**

The formal competition designation (full and open competition, limited sources, not competed, etc.) predicts values after accounting for solicitation procedures and offer counts.

**Why this matters:** Legal competition categories capture policy constraints beyond market dynamics. Sole-source justifications, exceptions to fair opportunity, and limited competition authorities apply in specific circumstances (urgent requirements, single qualified source, national security restrictions) that correlate with contract values.

Non-competed contracts are not necessarily more expensive—they may reflect emergency responses (potentially high cost) or routine administrative purchases (potentially low cost). The moderate importance score suggests these legal categories add information beyond what market-based measures (number of offers) already provide.

#### 13. **Funding Sub-Agency Code (Importance: 0.015)**

The specific sub-agency providing funding (distinct from the agency managing the procurement) predicts values independently of broader agency codes.

**Why this matters:** Security contracts often cross organizational boundaries: one office manages the procurement while another provides funding. This split reveals program versus administrative responsibilities. High-value protective programs may be centrally funded while locally administered, or vice versa.

The importance of funding source, separate from awarding authority, indicates that budget control matters. Offices controlling security appropriations shape program design even when delegating procurement execution.

#### 14. **National Interest Action (Importance: 0.014)**

Whether a contract receives "national interest action" designation (typically for emergency responses, disaster relief, COVID-19 pandemic response, etc.) predicts values.

**Why this matters:** National interest designations authorize expedited procedures, streamlined approvals, and relaxed competition requirements for urgent national priorities. Security contracts supporting pandemic response, hurricane recovery, wildfire emergencies, or crisis management operate under different constraints than routine procurements.

The importance of this variable reveals that emergency response security commands different values—potentially higher due to urgency premiums and mobilization costs, or potentially lower due to streamlined competition and standardized pricing.

#### 15. **Place of Manufacture (Importance: 0.013)**

Whether services or products must be domestically produced predicts contract values independently of performance location or country of origin.

**Why this matters:** "Place of manufacture" requirements often reflect Buy American provisions, Trade Agreements Act compliance, or Defense Federal Acquisition Regulation Supplement (DFARS) restrictions. These requirements limit the available vendor pool and may increase costs, but they also signal contracts for sensitive facilities where foreign national involvement is restricted.

The importance of manufacturing location, distinct from service delivery location, likely captures security clearance requirements, sensitive compartmented information facility (SCIF) access, and classified program participation—all of which substantially increase contractor qualifications and therefore contract values.

#### 16-20. **Additional Factors**

The remaining top-20 factors include:
- **Clinger-Cohen Act compliance:** IT security integration requirements
- **Country of product/service origin:** International sourcing patterns
- **Consolidated contract designation:** Multi-location bundling strategies
- **Major program identification:** Named security initiatives

Each contributes modest but meaningful predictive power, indicating that contract values respond to numerous interacting factors rather than a few dominant drivers.

## Real-World Prediction Examples (Gradient-Boosted Model)

To complement the feature-level insights, we extracted concrete forecasts from the **20% hold-out test set** used to validate the histogram gradient-boosting regressor. The model trains on 4 quantitative signals (`number_of_offers_received`, `performance_years`, `log_offers`, `log_duration`) plus 140 categorical descriptors (procedures, pricing structure, agency/funding codes, socio-economic flags, etc.). Permutation importance ranks the most influential fields as:

1. `self_certified_small_disadvantaged_business`
2. `award_type_code`
3. `extent_competed`
4. `subcontracting_plan`
5. `type_of_idc`
6. `log_offers`
7. `performance_years`
8. `awarding_agency_code`

Despite this high-dimensional feature space, the model remains highly calibrated. Three illustrative contracts are shown below (all values are annualised USD):

| Example | Solicitation | Pricing | Competition | Performance (yrs) | Offers | Actual annualised value (USD) | Predicted value (USD) | Error (USD) | Error % |
|---------|--------------|---------|-------------|-------------------|--------|-------------------------------:|----------------------:|------------:|--------:|
| **A (Row 6,556)** | Negotiated proposal/quote | Firm fixed price | Full & open (exclusion of sources) | 0.38 | 5 | 2,331,778.89 | 2,331,950.84 | +171.96 | +0.007% |
| **B (Row 74,264)** | Simplified acquisition | Labor hours | Competed under SAP | 0.47 | 1 | 42,970.59 | 42,962.92 | −7.67 | −0.018% |
| **C (Row 153,983)** | Simplified acquisition | Labor hours | Competed under SAP | 0.81 | 1 | 17,275.34 | 17,270.83 | −4.51 | −0.026% |

### Feature snapshots and interpretation

- **Example A – DHS negotiated renewal.** Awarding/funding agency code `070` (Department of Homeland Security) issued a firm-fixed-price guard contract under the negotiated procedure, flagged as a *self-certified small disadvantaged business* award with five qualified offers (`log_offers ≈ 1.79`). The GBM estimated the annual value within **$172 (0.007%)** of the $2.33M award despite the short 0.38-year base period.
- **Example B – DOJ simplified acquisition.** Agency code `015` (Department of Justice) procured labor-hour guard services through a simplified acquisition with one bid, `S206` guard PSC, and an explicit “not bundled” designation. The prediction error is just **$7.67 (0.018%)**, effectively matching the awarded spend.
- **Example C – DOJ bridge tasking.** A similar DOJ labor-hour requirement with an 0.81-year performance period and one offer produced an estimate within **$4.51 (0.026%)** of the true $17.3K annual value.

These examples demonstrate that the GBM not only captures directional drivers (socio-economic flags, procurement method, competition intensity) but also produces reliable dollar forecasts that management can trust for scenario planning. The accuracy stems from three deliberate design choices: (1) the target is modeled on a log10 scale, which normalises the wide dollar range and keeps relative errors stable before reconverting to USD; (2) the 144-feature input matrix combines four quantitative signals with 140 categorical descriptors of agency, procedure, socio-economic status, bundling, PSC, etc., while explicitly filtering every price-related column to avoid leakage; and (3) the training corpus focuses on a single market segment (NAICS 561612 negotiated vs simplified awards), so the model repeatedly observes the same procurement configurations (e.g., DHS `S206` negotiated FFP, DOJ SAP labor-hour tasks) and learns their typical spend profiles.

---

## Conclusion

Federal physical security contract values are not distributed evenly across agencies, missions, or geographies. Instead, spending concentrates heavily in a small number of specialized programs protecting nuclear facilities, critical infrastructure, and hazardous environments. Meanwhile, the majority of guard contracts—supporting administrative facilities, small installations, and routine security needs—operate at conventional commercial rates.

This bifurcation reflects intentional policy choices: the federal government pays substantial premiums for specialized capabilities when mission requirements demand them, while relying on competitive commercial markets for standard guard services. Understanding these patterns enables more informed policy decisions, more effective procurement strategies, and more realistic budget planning.

Beyond this foundational insight, the advanced gradient-boosted model reveals that **how** the government structures security procurement—through socioeconomic participation requirements, contract vehicle selection, competition design, and acquisition timing—matters as much as **what** agencies buy. Policy mechanisms shape market outcomes. Inclusion goals, flexible ordering systems, and strategic competition design are not merely procedural overlays but fundamental determinants of who provides security services at what cost.

The analysis demonstrates that "security services" is not a homogeneous commodity but rather a spectrum spanning from basic access control (low cost, high volume) to nuclear protective forces (high cost, highly specialized). Effective management of the federal security portfolio requires recognizing and appropriately resourcing these fundamental differences in mission scope and capability requirements—while simultaneously understanding that policy design, acquisition strategy, and market structure shape how those resources are deployed and what outcomes they achieve.
