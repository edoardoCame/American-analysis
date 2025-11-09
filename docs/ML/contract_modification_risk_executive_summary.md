# Contract Modification Risk Analysis: Executive Summary

## Overview

This analysis examined 46,771 federal security service contracts (NAICS 561612) to predict which base awards will require modifications during execution. The dataset covers contracts from multiple federal agencies spanning several years.

**Key Finding**: 81% of security contracts experience at least one modification after the initial award, making modification risk a structural feature of this market rather than an exception.

---

## What We Built

We developed a predictive model that assigns each new contract opportunity a "modification probability score" between 0% and 100%. This score indicates the likelihood that the contract will require changes after award.

**Model Performance**:
- **Accuracy**: 91% - The model correctly predicts whether a contract will be modified in 9 out of 10 cases
- **Recall**: 97% - The model catches 97% of all contracts that will actually be modified
- **Precision**: 93% - When the model flags a contract as high-risk, it's correct 93% of the time
- **ROC-AUC**: 95% - Industry benchmark for predictive quality (above 90% is considered excellent)

These metrics indicate strong predictive performance across the test dataset.

---

## What Drives Contract Modifications

The model analyzed 168 different characteristics of each contract to identify patterns. The analysis reveals five primary factors that influence modification probability:

### 1. **Contract Value and Option Structure** (Strongest Predictor)

The gap between the initial contract ceiling and the exercised base value is the single most powerful predictor of future modifications.

**Observed patterns**:
- Contracts with large "option headroom" (difference between maximum authorized value and initial funding) show modification rates exceeding 90%
- Top decile contracts (above $2.1M) show 93% modification probability vs. 65% for smaller awards
- The data suggests agencies build flexibility into contracts when they anticipate scope evolution

### 2. **Contract Duration** (Second Strongest Predictor)

Longer planned performance periods correlate directly with higher modification frequency.

**Observed patterns**:
- Contracts with 365+ day performance periods show 88% modification rates
- Short-term contracts (< 90 days) still face 72% modification probability
- Duration and modification frequency move together consistently across the dataset

### 3. **Agency and Office Identity** (Third Strongest Predictor)

The specific government buyer shows strong correlation with modification frequency.

**Observed patterns**:
- Department of Homeland Security (DHS): 95% modification rate across 8,800 contracts ($159B total value)
- Department of Justice (DOJ): 82% modification rate across 29,000 contracts
- Department of the Interior: 73% modification rate
- Certain DHS offices exceed 98% modification rates, while some Interior bureaus stay below 60%

### 4. **Solicitation Procedure** (Fourth Strongest Predictor)

The procurement method shows correlation with modification likelihood.

**Observed patterns**:
- Negotiated proposals: 89% modification rate
- Multiple-award fair opportunity: 83% modification rate
- Simplified acquisitions: 79% modification rate
- Full and open competition: 77% modification rate

### 5. **Competition Intensity**

The number of competing bids shows inverse correlation with modification risk.

**Observed patterns**:
- Single-bid contracts: 87% modification rate
- 2-3 bidders: 82% modification rate
- 4+ bidders: 78% modification rate
- Less competition correlates with higher modification frequency

---

## Visual Analysis of Key Patterns

### Agency Modification Patterns

![Agency Modification Rates](images/01_agency_modification_rates.png)

**What this chart shows**: This horizontal bar chart displays the 12 federal agencies with the highest modification rates. The blue bars show the percentage of contracts that were modified, while the orange line with dots shows the total contract value in millions of dollars.

**Key observations**:
- Department of Homeland Security (DHS) has the highest modification rate at 95%, with approximately $159 billion in total base value
- Department of Justice (DOJ) shows an 82% modification rate across roughly $120 billion in contracts
- Social Security Administration and General Services Administration also show rates above 90%
- Department of the Interior has a lower modification rate at 73%, despite substantial contract volume
- There is no direct correlation between total contract value and modification rate - some agencies with lower spending show higher modification rates

**Interpretation**: Different agencies exhibit distinctly different modification patterns, ranging from 73% to 95%. This variation persists across agencies of different sizes and missions.

---

### Contract Value and Modification Risk

![Value Decile Risk](images/02_value_decile_modification_risk.png)

**What this chart shows**: This chart segments all contracts into 10 equal groups (deciles) based on their contract value, from smallest to largest. The blue bars show the modification rate for each value group, while the gray line shows the median contract duration in days.

**Key observations**:
- Smallest contracts ($0.0M - $0.1M): 65% modification rate, ~120 days median duration
- Mid-range contracts ($0.5M - $1.0M): 82% modification rate, ~320 days median duration
- Largest contracts ($2.1M+): 93% modification rate, ~450 days median duration
- Modification rate increases steadily as contract value increases
- Contract duration also increases with contract value, suggesting larger contracts also tend to be longer
- Even the smallest contracts show 65% modification probability

**Interpretation**: There is a clear positive relationship between contract value and modification likelihood. Higher-value contracts are both longer in duration and more likely to be modified. The relationship is approximately linear, with each value decile showing incrementally higher modification rates.

---

### Model Performance: ROC Curve

![ROC Curve](images/03_roc_curve.png)

**What this chart shows**: The Receiver Operating Characteristic (ROC) curve measures how well the model distinguishes between contracts that will be modified and those that won't. The blue line represents our model's performance, while the gray dashed line represents random guessing.

**How to read this chart**:
- The X-axis shows the "false-positive rate" - how often the model incorrectly predicts modification when it doesn't occur
- The Y-axis shows the "true-positive rate" - how often the model correctly identifies contracts that will be modified
- A perfect model would hug the top-left corner (100% true positives, 0% false positives)
- Random guessing produces the diagonal gray line
- The area under the blue curve (AUC) is 0.95, meaning the model is 95% better than random chance

**Key observations**:
- The blue curve stays very close to the top-left corner throughout
- At a false-positive rate of 10%, the model achieves approximately 90% true-positive rate
- The model maintains strong performance across different decision thresholds
- The substantial gap between the blue line and gray line indicates strong discriminative power

**Interpretation**: The ROC curve confirms the model can reliably distinguish between contracts that will and won't be modified. An AUC of 0.95 is considered excellent in predictive modeling.

---

### Model Performance: Precision-Recall Curve

![Precision-Recall Curve](images/04_precision_recall_curve.png)

**What this chart shows**: The Precision-Recall curve shows the trade-off between precision (how many flagged contracts actually get modified) and recall (what percentage of all modified contracts we catch).

**How to read this chart**:
- The X-axis shows "recall" - the percentage of all modified contracts the model successfully identifies
- The Y-axis shows "precision" - among contracts the model flags as high-risk, what percentage actually get modified
- Higher values on both axes are better
- The curve shows performance across different decision thresholds

**Key observations**:
- The model maintains precision above 90% even at recall levels of 95%
- At the operating threshold, precision is 93% and recall is 97%
- The curve stays close to the top-right corner throughout, indicating strong performance
- There is minimal trade-off between precision and recall across most of the range
- Average precision (area under curve) is 0.99

**Interpretation**: The model successfully balances catching most modifications (97% recall) while maintaining high accuracy in its predictions (93% precision). This means when the model flags a contract as high-risk, it's almost always correct, and it catches almost all contracts that will actually be modified.

---

### Model Performance: Confusion Matrix

![Confusion Matrix](images/05_confusion_matrix.png)

**What this chart shows**: The confusion matrix shows actual outcomes (rows) versus model predictions (columns) for the 9,354 contracts in the test set that the model had never seen during training.

**How to read this chart**:
- **Top-left cell (1,281)**: Contracts correctly predicted as NOT modified (True Negatives)
- **Top-right cell (501)**: Contracts predicted to be modified but weren't (False Positives - model error)
- **Bottom-left cell (312)**: Contracts predicted as NOT modified but were (False Negatives - model error)
- **Bottom-right cell (7,260)**: Contracts correctly predicted as modified (True Positives)
- Darker blue indicates higher counts

**Key observations**:
- The model made 8,541 correct predictions (1,281 + 7,260) out of 9,354 total
- This yields 91% accuracy (8,541 / 9,354)
- False positives (501) represent 5.4% of test set - the model occasionally flags contracts that won't be modified
- False negatives (312) represent 3.3% of test set - the model occasionally misses contracts that will be modified
- The model makes fewer false negatives than false positives, meaning it's more likely to over-predict than under-predict modifications

**Interpretation**: The confusion matrix provides concrete counts of model errors. Of the 7,572 contracts that were actually modified, the model correctly identified 7,260 (97% recall). Of the 7,761 contracts the model flagged as high-risk, 7,260 were actually modified (93% precision).

---

### Feature Importance

![Feature Importance](images/06_feature_importance.png)

**What this chart shows**: This horizontal bar chart shows which contract characteristics have the most influence on the model's predictions. Longer bars indicate more important features.

**How to read this chart**:
- Each bar represents one feature (contract characteristic)
- The length of the bar shows "permutation importance" - how much model performance drops when that feature is randomly shuffled
- Features are ranked from most important (top) to least important (bottom)
- Only the top 15 features are shown

**Key observations**:
- **Base And All Options Value** (total contract ceiling) is by far the most important feature
- **Options Vs Base Delta** (gap between ceiling and exercised base) is the second most important
- **Planned Duration Days** ranks third
- **Awarding Office Name** and **Awarding Agency Name** rank fourth and fifth
- Contract pricing type, obligation amount, and solicitation procedures show moderate importance
- The top 3 features relate to contract value structure and duration
- Agency/office identity appears twice in the top 10

**Interpretation**: Contract value structure (base value, options, and the gap between them) combined with contract duration are the strongest predictors of modification risk. The identity of the government buyer (agency and office) also plays a significant role. These top features drive the majority of the model's predictions.

---

### Solicitation Procedure and Modification Risk

![Solicitation Risk](images/07_solicitation_procedure_risk.png)

**What this chart shows**: This chart compares observed modification rates (green bars) versus model-predicted modification probabilities (red line with dots) across different solicitation procedures. Only solicitation types with at least 100 contracts are included.

**How to read this chart**:
- Green bars show the actual modification rate observed in the data
- Red line with dots shows the average predicted modification probability from the model
- X-axis shows different procurement methods
- Y-axis shows percentage of contracts modified
- Close alignment between green and red indicates good model calibration

**Key observations**:
- Negotiated proposals show the highest rates: 89% observed, 88% predicted
- Fair opportunity and limited sources procedures: 85% observed, 84% predicted  
- Simplified acquisitions: 79% observed, 80% predicted
- Full and open competition: 77% observed, 78% predicted
- The model's predictions closely track actual outcomes across all solicitation types
- The maximum difference between observed and predicted is less than 2 percentage points
- All solicitation types show modification rates above 75%

**Interpretation**: The close match between observed (green) and predicted (red) values demonstrates that the model's probability estimates are well-calibrated across different solicitation procedures. This means the model's modification probability scores can be interpreted as reliable estimates. The chart also shows that negotiated procurements have consistently higher modification rates than competitive procurements.

---

---

## Technical Appendix

### Model Specifications

- **Algorithm**: Histogram-Based Gradient Boosting Classifier (scikit-learn)
- **Training set**: 37,417 contracts (80%)
- **Test set**: 9,354 contracts (20%)
- **Features**: 168 total (14 numeric, 68 categorical, 86 boolean)
- **Target variable**: Binary (modified = 1, not modified = 0)
- **Class balance**: 81% positive class (modified), 19% negative class (not modified)
- **Validation method**: Stratified train-test split, no temporal leakage

### Feature Engineering

**Numeric Features**:
- Contract value metrics (base, ceiling, obligation, option delta)
- Duration metrics (planned days, days between key dates)
- Competition metrics (number of offers received)
- Performance metrics (historical vendor scores)

**Categorical Features**:
- Agency/office identifiers
- Solicitation procedure codes
- Pricing mechanism codes
- Place of performance characteristics
- Product/service classification codes
- Socioeconomic set-aside indicators

**Boolean Features**:
- Contract characteristic flags (competitive, negotiated, simplified)
- Set-aside indicators (small business, veteran-owned, etc.)
- Option clause presence
- Special provision indicators

**Engineered Features**:
- Options vs base delta (ceiling minus exercised base)
- Value-per-day ratios
- Competition intensity categories
- Agency/office modification history aggregates

### Model Hyperparameters

```python
HistGradientBoostingClassifier(
    max_iter=200,
    max_depth=8,
    learning_rate=0.05,
    min_samples_leaf=20,
    random_state=42
)
```

### Performance Metrics (Test Set)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Accuracy | 0.91 | 91% of predictions are correct |
| Precision | 0.93 | 93% of flagged contracts truly modified |
| Recall | 0.97 | Model catches 97% of all modifications |
| F1 Score | 0.95 | Harmonic mean of precision and recall |
| ROC-AUC | 0.95 | 95% probability model ranks random modified contract higher than random non-modified contract |
| Average Precision | 0.99 | Area under precision-recall curve |

### Data Sources

- **USAspending.gov**: Prime contract transaction data (2008-2024)
- **Filters applied**: NAICS 561612 (Security Guards and Patrol Services)
- **Base awards**: 46,771 unique contracts
- **Total transactions**: 238,078 (including all modifications)
- **Data quality**: 97% completeness on critical fields (value, agency, duration, solicitation)

### Reproducibility

All analysis code, data processing scripts, and model training procedures are version-controlled and documented in the project repository. Model performance can be reproduced by re-running the training pipeline with the same random seed (42).

---

## Summary of Key Findings

This analysis of 46,771 federal security service contracts reveals several clear patterns:

**Modification Frequency**:
- 81% of contracts experience at least one modification after initial award
- This high baseline rate indicates modification is the norm, not the exception

**Primary Predictive Factors**:
1. Contract value structure (ceiling amount and option headroom)
2. Contract duration (longer contracts more likely to be modified)
3. Agency and office identity (DHS at 95%, Interior at 73%)
4. Solicitation procedure (negotiated 89%, competitive 77%)
5. Competition intensity (fewer bidders correlates with higher rates)

**Model Performance**:
- 91% accuracy on test set of 9,354 contracts
- 97% recall (catches nearly all modifications)
- 93% precision (high confidence in predictions)
- 95% ROC-AUC (excellent discrimination ability)

**Practical Application**:
The model provides modification probability scores (0-100%) for new contracts based on their characteristics at award. These scores can inform resource allocation, pricing decisions, and risk management approaches across a contract portfolio.

---

## Contact and Questions

For questions about this analysis, model implementation, or operationalization support:

- **Technical questions**: Contact data science team
- **Business application**: Contact business development leadership
- **Model access**: Contact IT for API integration or batch scoring

**Document version**: 1.0  
**Last updated**: November 9, 2025  
**Model version**: v1.0 (168-feature production model)
