# FraudLens — Detailed Page-by-Page Visual Specification & Power BI Authoring Guide

This specification provides the exact, production-ready blueprint for assembling all 7 report pages in Microsoft Power BI Desktop using the staged star-schema datasets (`data/processed/powerbi/`) and DAX measures repository (`powerbi/dax_measures.dax`).

---

## Global Report Canvas & Theme Settings

- **Canvas Page Size**: 16:9 Widescreen (1920 px width x 1080 px height).
- **Background Color**: Canvas Background `#F8FAFC` (Slate 50), 0% Transparency.
- **Card / Visual Container Style**: 
  - Fill: `#FFFFFF` (Pure White).
  - Border: 1 px solid `#E2E8F0` (Slate 200).
  - Corner Radius: 6 px rounded corners.
  - Drop Shadow: Outside bottom-right subtle shadow (`#000000`, 5% opacity, blur 4 px).
- **Color Palette**:
  - Primary Brand Navy: `#0F172A`
  - High Risk / Fraud Crimson: `#DC2626`
  - Financial Volume Electric Blue: `#2563EB`
  - Legitimate / Low Risk Emerald: `#10B981`
  - Medium Risk Amber: `#F59E0B`
  - High Risk Orange: `#EA580C`
  - Neutral Muted Gray: `#64748B`
- **Global Header Banner (Y: 0 to 80 px, Width: 1920 px)**:
  - Left: Title *"FraudLens — Financial Fraud Analytics & Investigation Platform"* (Segoe UI Bold, 20 pt, `#0F172A`).
  - Right: Page Navigation Buttons (Executive Overview, Fraud Analytics, Financial Analysis, Account Risk, Fraud Investigation, ML Model Analysis, Data Quality).

---

## Page 1: Executive Overview

**Primary Purpose**: Executive risk visibility into portfolio scale, fraud-labeled exposure, channel concentration, and origin drainage.

### 1. Top KPI Row (Y: 95 px, Height: 110 px, 6 Equal Width Cards)
1. **Total Transactions**:
   - Visual: Card (New)
   - Measure: `[Total Transactions]`
   - Formatted Value: `6.36M` (Display Units: Millions, Tooltip: `6,362,620`)
   - Accent: Neutral Slate `#0F172A`
2. **Total Transacted Volume**:
   - Visual: Card (New)
   - Measure: `[Total Transacted Volume]`
   - Formatted Value: `$1.144 T` (Display Units: Trillions, Tooltip: `$1,144,392,944,759.77`)
   - Accent: Blue `#2563EB`
3. **Confirmed Fraud Incidents**:
   - Visual: Card (New)
   - Measure: `[Confirmed Fraud Incidents]`
   - Formatted Value: `8,213` (Integer with comma)
   - Accent: Crimson `#DC2626`
4. **Fraud-Labeled Exposure**:
   - Visual: Card (New)
   - Measure: `[Fraud-Labeled Exposure]`
   - Formatted Value: `$12.06 B` (Display Units: Billions, Tooltip: `$12,056,415,427.84`)
   - Accent: Crimson `#DC2626`
5. **Overall Fraud Rate**:
   - Visual: Card (New)
   - Measure: `[Overall Fraud Rate]`
   - Formatted Value: `0.1291%` (4 decimal places)
   - Subtitle: *"Macro Portfolio Incident Frequency"*
6. **Origin Account Drainage %**:
   - Visual: Card (New)
   - Measure: `[Origin Account Drainage Rate]`
   - Formatted Value: `97.55%` (Subtitle: *"8,012 / 8,213 incidents emptied to $0.00"*)
   - Accent: Alert Red `#DC2626`

### 2. Main Visual Grid (Y: 220 px to 1020 px)
- **Visual 1 (X: 30, Y: 220, W: 600, H: 400): Channel Breakdown — Volume vs. Exposure**
  - Type: Clustered Column & Line Chart (Combo Chart)
  - Table: `Summary_Channel_KPIs`
  - X-Axis: `transaction_type` (TRANSFER, CASH_OUT, PAYMENT, CASH_IN, DEBIT)
  - Column Y-Axis: `total_volume_usd` (Bar Color `#2563EB`)
  - Line Y-Axis: `fraud_exposure_usd` (Line Color `#DC2626`, Width 3 px, Markers ON)
  - Data Labels: On for both series
  - Sort: By `total_volume_usd` Descending
  - Insight Highlight: Demonstrates that while `CASH_IN` and `PAYMENT` carry billions in volume, 100% of fraud exposure ($12.06B) is isolated to `TRANSFER` and `CASH_OUT`.

- **Visual 2 (X: 650, Y: 220, W: 780, H: 400): 31-Day Fraud Exposure Trajectory & 7-Day Moving Avg**
  - Type: Line Chart
  - Table: `Summary_Hourly_Temporal` & `DimTime`
  - X-Axis: `transaction_day` (Days 1 to 31)
  - Y-Axis: `Daily Fraud Exposure` (`#DC2626`, dashed line) and `7-Day Rolling Avg Daily Fraud Exposure` (`#0F172A`, solid 3 px line)
  - Tooltips: `transaction_day`, `Daily Fraud Exposure`, `Daily Total Volume`
  - Insight Highlight: Shows consistent, systematic daily fraud extraction across the entire 31-day simulation period without sudden multi-day pauses.

- **Visual 3 (X: 1450, Y: 220, W: 440, H: 400): Amount Band Risk Sizing**
  - Type: Horizontal Bar Chart
  - Table: `Summary_Amount_Bands`
  - Y-Axis: `amount_band` (<10k, 10k-100k, 100k-500k, 500k-1M, 1M-5M, 5M+)
  - X-Axis: `fraud_exposure_usd` (Fill: Crimson `#DC2626`)
  - Tooltip: `total_transactions`, `fraud_transactions`, `fraud_rate_pct`
  - Sort: Logical ticket size ascending
  - Insight Highlight: 66.61% of fraud exposure occurs in tickets > $200k, with the highest concentration in the 1M–5M and 5M+ tiers.

- **Visual 4 (X: 30, Y: 640, W: 900, H: 380): Heuristic Flag (isFlaggedFraud) Confusion Matrix**
  - Type: Matrix / Table Visual
  - Columns: Ground Truth (Fraud vs Legitimate)
  - Rows: Rule Flag (Flagged vs Not Flagged)
  - Values: Count (`TP=16`, `FP=0`, `FN=8,197`, `TN=6,354,407`)
  - Formatting: Conditional heatmap fill.
  - Accompanying Callout Box: *"Legacy Heuristic Failure: The rule-based threshold of amount > $200k in TRANSFER triggered exactly 16 times (Precision: 100%), but missed 8,197 fraud cases (Recall: 0.1948%). 99.81% of fraud slipped past the legacy rule."*

- **Visual 5 (X: 950, Y: 640, W: 940, H: 380): Executive Key Findings & Portfolio Recommendations**
  - Type: Multi-card / Rich Text Callout Container
  - Content:
    1. **Channel Exclusivity**: 100% of fraud attacks are executed exclusively via `TRANSFER` ($6.07B) and `CASH_OUT` ($5.99B).
    2. **Origin Account Liquidation**: In 97.55% of fraud cases, the perpetrator drains the origin balance completely to $0.00.
    3. **Heuristic Inefficiency**: Legacy rule recall of 0.1948% necessitates modern supervised machine learning.
    4. **Capital Exposure**: Total exposure of $12.06B accounts for 1.0535% of total transacted volume.

---

## Page 2: Fraud Analytics

**Primary Purpose**: Deep-dive statistical and temporal decomposition of fraud behavioral patterns.

### 1. KPI Cards (Y: 95 px, 5 Cards)
- **Confirmed Frauds**: `8,213`
- **Fraud Rate**: `0.1291%`
- **Fraud Exposure**: `$12.06 B`
- **Mean Fraud Ticket**: `$1,467,967.30`
- **Mean Legitimate Ticket**: `$178,197.04` (Severity Multiplier: `8.24x`)

### 2. Main Visual Grid
- **Visual 1: Channel Fraud Rates Comparison**
  - Type: Clustered Bar Chart
  - Y-Axis: `transaction_type` (TRANSFER vs CASH_OUT)
  - X-Axis: `fraud_rate_pct`
  - Values: `TRANSFER: 0.7688%`, `CASH_OUT: 0.1840%` (TRANSFER is 4.18x more fraud-dense).
  - Bar Color: `#DC2626`

- **Visual 2: Diurnal Fraud Curve & Simulation Hour Trajectory**
  - Type: Dual-Axis Line & Column Chart
  - Table: `DimTime` and `Summary_Hourly_Temporal`
  - X-Axis: `transaction_hour` (0 to 23)
  - Column Values: Legitimate transaction volume (showing strong daytime peak 09:00 to 18:00)
  - Line Values: Fraud transaction frequency and fraud exposure (showing uniform round-the-clock occurrence, especially elevated during night/off-peak hours).

- **Visual 3: Ticket Size Distribution (Fraud vs Legitimate)**
  - Type: Box Plot / Distribution Column
  - Comparison of Median and 75th percentile amounts.
  - Fraud Median: `$441,423.44` vs Legitimate Median: `$74,871.94`.

- **Visual 4: Statistical Significance & Effect Size Card**
  - Type: Metric Callout Card
  - Metrics:
    - Independent Two-Sample Welch's t-test: $p < 10^{-15}$ (Extreme statistical significance).
    - Cohen's $d$: `2.1422` (Huge effect size, indicating fraud origin balance errors and ticket sizes operate in an entirely distinct statistical distribution from legitimate transactions).

---

## Page 3: Financial & Transaction Analysis

**Primary Purpose**: Portfolio liquidity flows, cumulative exposure accumulation, and daily liquidity-to-exposure dual-axis tracking.

### 1. KPI Cards (Y: 95 px)
- **Gross Volume**: `$1.144 T`
- **Fraud-Labeled Exposure**: `$12.06 B`
- **Exposure Share**: `1.0535%`
- **Average Ticket Size**: `$179,861.90`

### 2. Main Visual Grid
- **Visual 1: Portfolio Channel Volume Distribution**
  - Type: Donut Chart
  - Table: `Summary_Channel_KPIs`
  - Legend: `transaction_type`
  - Values: `total_volume_usd`
  - Breakdown: `TRANSFER` ($485.2B, 42.4%), `CASH_OUT` ($394.4B, 34.5%), `CASH_IN` ($236.4B, 20.7%), `PAYMENT` ($28.0B, 2.4%), `DEBIT` ($227M, 0.02%).

- **Visual 2: Cumulative Fraud Exposure Growth Curve**
  - Type: Area Chart
  - Table: `Summary_Hourly_Temporal` & `DimTime`
  - X-Axis: `step` (1 to 743)
  - Y-Axis: `[Cumulative Fraud Exposure]`
  - Fill: Gradient Crimson (`#DC2626` to `#FCA5A5`)
  - Insight Highlight: Linear, steady rise from $0 to $12.06B, demonstrating an active, continuous attack pattern across all 31 days.

- **Visual 3: Daily Volume vs Daily Exposure Dual-Axis Trajectory**
  - Type: Line and Clustered Column Chart
  - X-Axis: `transaction_day` (1 to 31)
  - Column Y-Axis: `Daily Total Volume` (Blue `#2563EB`)
  - Line Y-Axis: `Daily Fraud Exposure` (Crimson `#DC2626`)

- **Visual 4: Volume & Fraud Exposure by Ticket Size Bands**
  - Table: `Summary_Amount_Bands`
  - Clustered Bar: Total Volume vs Fraud Volume across the 6 amount tiers.

---

## Page 4: Account Risk & Behavioral Prioritization

**Primary Purpose**: Operational triage workbench displaying the 0–100 behavioral risk score distribution, risk tiers, and origin drainage metrics.

### 1. Risk Tier Cards (Y: 95 px, 4 Cohort Cards + Capture Share)
- **Critical (Score 76–100)**: `67,252 accounts` (1.06% of portfolio | 6.44% fraud rate)
- **High (Score 51–75)**: `605,922 accounts` (9.52% of portfolio)
- **Medium (Score 26–50)**: `1,493,438 accounts` (23.47% of portfolio)
- **Low (Score 0–25)**: `4,196,008 accounts` (65.95% of portfolio)
- **Critical Tier Capture Share**: `52.77%` (4,334 of 8,213 frauds captured in top 1.06% of accounts)

### 2. Main Visual Grid
- **Visual 1: Account Portfolio Distribution by Risk Tier**
  - Type: Donut Chart
  - Table: `Summary_Account_Risk`
  - Legend: `risk_category`
  - Values: `total_accounts`
  - Colors: Critical `#DC2626`, High `#EA580C`, Medium `#F59E0B`, Low `#10B981`

- **Visual 2: Fraud Rate by Risk Tier**
  - Type: Column Chart
  - X-Axis: `risk_category` (Critical, High, Medium, Low)
  - Y-Axis: `account_fraud_rate_pct`
  - Data Labels: `Critical: 6.44%`, `High: 0.58%`, `Medium: 0.02%`, `Low: 0.0004%`
  - Risk Concentration: Critical tier is over 16,000x more concentrated with fraud than Low tier.

- **Visual 3: Origin Drainage Ratio Donut Chart**
  - Values: `Drained to $0.00: 8,012 (97.55%)` vs `Non-Zero Balance: 201 (2.45%)`
  - Colors: Crimson `#DC2626` vs Gray `#94A3B8`

- **Visual 4: SLA & Operational Triage Matrix**
  - Table: `DimRiskTier` & `Summary_Account_Risk`
  - Columns: Risk Category, Score Range, Total Accounts, Fraud Cases, SLA Tier, Action Code.

---

## Page 5: Fraud Investigation Workbench

**Primary Purpose**: Case investigator workstation operating over `FactFraudInvestigation_Extract` (20,865 rows, capturing 100% of the 8,213 fraud incidents).

### 1. Multi-Criteria Slicer Panel (Top Row, Y: 95 px to 175 px)
- **Slicer 1 (Dropdown)**: `transaction_type` (All, TRANSFER, CASH_OUT, PAYMENT, CASH_IN, DEBIT)
- **Slicer 2 (Radio Buttons)**: `is_fraud` (All, Confirmed Fraud [1], Legitimate Benchmark [0])
- **Slicer 3 (Dropdown)**: `risk_category` (All, Critical, High, Medium, Low)
- **Slicer 4 (Numeric Range Slider)**: `amount` ($0 to $10,000,000)
- **Slicer 5 (Numeric Range Slider)**: `risk_score` (0 to 100)
- **Slicer 6 (Search Box)**: `origin_account` / `dest_account`

### 2. Investigation KPI Summary (Y: 185 px, 4 Cards)
- **Candidate Transactions**: `COUNTROWS(FactFraudInvestigation_Extract)` (Default: `20,865`)
- **Confirmed Fraud Cases**: `[Confirmed Fraud Candidate Count]` (Default: `8,213`)
- **Filtered Volume**: `SUM(amount)` (Default: `$14.28 B`)
- **Mean Transaction Size**: `[Candidate Average Amount]` (Default: `$684,310.20`)

### 3. Forensic Investigation Grid (Y: 280 px to 1020 px, Full Width)
- Visual: Table Visual with Conditional Formatting
- Data Columns:
  1. `transaction_id` (Integer)
  2. `step` (Simulation Hour)
  3. `transaction_type` (Channel)
  4. `amount` (Currency format `$#,##0.00`)
  5. `origin_account` (Masked Account ID)
  6. `orig_old_balance` (Currency)
  7. `orig_new_balance` (Currency)
  8. `orig_balance_error` (Discrepancy Amount)
  9. `dest_account` (Recipient ID)
  10. `dest_old_balance` (Currency)
  11. `dest_new_balance` (Currency)
  12. `dest_balance_error` (Discrepancy Amount)
  13. `is_drainage` (1 / 0 Flag)
  14. `risk_score` (0–100 Score, conditional bar fill)
  15. `risk_category` (Critical, High, Medium, Low)
  16. `investigation_typology` (Drainage & Laundering, Synthetic Transfer, etc.)
  17. `is_fraud` (1 = Confirmed Alert `#DC2626`, 0 = Cleared `#10B981`)

---

## Page 6: Machine Learning Model Analysis

**Primary Purpose**: Rigorous comparative evaluation of Random Forest, XGBoost, and Logistic Regression on the held-out test partition ($N = 1,272,524$).

### 1. Top Callout Banner
- *"DISCLAIMER: Evaluated strictly on the held-out PaySim synthetic test partition (1,272,524 rows, 1,643 fraud cases). Metrics reflect synthetic mobile-money topology and do not claim production deployment readiness on live banking rails."*

### 2. Primary Model Performance Table
- Visual: Table Visual
- Table: `Summary_ML_Model_Comparison`
- Columns:
  - `Model`
  - `Precision` (RF: `99.88%`, XGB: `93.39%`, LogReg: `6.37%`)
  - `Recall` (RF: `99.76%`, XGB: `99.82%`, LogReg: `99.63%`)
  - `F1_Score` (RF: `0.9982`, XGB: `0.9650`, LogReg: `0.1198`)
  - `PR_AUC` (RF: `0.9988`, XGB: `0.9987`, LogReg: `0.8492`)
  - `ROC_AUC` (RF: `0.9995`, XGB: `0.9995`, LogReg: `0.9991`)
  - `True_Positives` (RF: `1,639`, XGB: `1,640`, LogReg: `1,637`)
  - `False_Positives` (RF: `2`, XGB: `116`, LogReg: `24,050`)
  - `False_Negatives` (RF: `4`, XGB: `3`, LogReg: `6`)
  - `True_Negatives` (RF: `1,270,879`, XGB: `1,270,765`, LogReg: `1,246,831`)

### 3. Feature Importance Visual
- Visual: Clustered Horizontal Bar Chart
- Table: `Summary_ML_Feature_Importance` (Filter: `model_type = 'XGBoost'`)
- Y-Axis: `feature`
- X-Axis: `relative_importance_pct`
- Sort: Descending by Importance
- Top Features:
  - `newbalanceOrig`: `49.56%`
  - `orig_balance_error`: `42.07%`
  - `amount`: `3.02%`
  - `origin_balance_change`: `2.30%`
  - `dest_balance_error`: `1.28%`

### 4. Threshold Tuning & Trade-Off Curve Visual
- Visual: Line Chart
- Table: `Summary_ML_Threshold_Curves` (Filter: `model_type = 'XGBoost'`)
- X-Axis: `threshold` (0.10 to 0.90)
- Lines: `precision` (Blue), `recall` (Crimson), `f1_score` (Green)
- Secondary Y-Axis / Callout: `alert_count` and `false_positives`
- Key Callout: Shifting XGBoost threshold from 0.50 to 0.90 reduces false positive alert volume from 116 to 14 (**87.93% reduction in false alerts**) while preserving 99.76% recall (1,639 / 1,643 frauds captured).

---

## Page 7: Data Quality, Architecture & Governance

**Primary Purpose**: Technical credibility, data quality audit trail, heuristic baseline audit, and compliance governance.

### 1. Data Quality Audit Matrix
- Visual: Table Visual
- Table: `Summary_Data_Quality`
- Columns: `Category`, `Quality_Check`, `Expected_Value`, `Observed_Value`, `Status`
- Highlights:
  - Missing Values: `0` (PASS)
  - Duplicate Records: `0` (PASS)
  - Negative Amounts: `0` (PASS)
  - Transaction Type Schema Integrity: 5 distinct types (PASS)
  - Account ID Prefix Standard: C-to-C and C-to-M verified (PASS)

### 2. Heuristic Rule Performance (isFlaggedFraud)
- Visual: Multi-Row Card / Matrix
- Rule Logic: `type = 'TRANSFER' AND amount > 200,000`
- Total Triggers: `16`
- True Positives: `16` (Precision = `100.00%`)
- Missed Frauds (FN): `8,197` (Recall = `0.1948%`)
- Cleared Legitimate (TN): `6,354,407` (Specificity = `100.00%`)
- Audit Finding: Proves deterministic threshold rules are incapable of defending modern payment topologies; supervised ML is mandatory.

### 3. End-to-End Platform Flowchart (Diagrammatic Card)
```
Raw PaySim CSV (6.36M Rows)
       ↓
[Phase 1 & 2]: Ingestion, Cleaning & Feature Engineering (Balance Errors, Drainage Flags)
       ↓
[Phase 3]: Exploratory Data Analysis & Statistical Testing (Cohen's d = 2.1422, p < 1e-15)
       ↓
[Phase 4]: SQLite Analytical Layer & Indexing (10 B-Tree Composite Indices)
       ↓
[Phase 5 & 8]: Power BI 7-Page Star Schema & DAX Intelligence (13 Staging Tables)
       ↓
[Phase 6]: Streamlit Interactive Forensic Investigation Application
       ↓
[Phase 7]: Machine Learning Fraud Classification (Random Forest & XGBoost Models)
```

### 4. Enterprise Regulatory & Governance Disclaimers
1. **Synthetic Data**: PaySim is an agent-based synthetic simulation; patterns reflect simulated behavior and should not be confused with proprietary banking or Indian regulatory datasets.
2. **Exposure vs. Loss**: Fraud amounts represent *fraud-labeled gross exposure*; actual net financial loss depends on chargebacks, reserve recovery, and interbank clawbacks.
3. **Risk Scoring**: Account risk scores (0–100) are designed for compliance case triage and prioritized queuing; they do not constitute legal determinations of guilt.
4. **Attribution**: Feature importance metrics reflect statistical correlation within the tree-based models, not causal proof of criminal intent.
