# FraudLens — Power BI Enterprise Dashboard Design Specification

## 1. Design Philosophy & Visual Standards

The **FraudLens Power BI Dashboard** is designed as a portfolio-grade, institutional financial intelligence product for risk analysts, AML compliance managers, and executive leadership.

### Global Visual Guidelines:
- **Canvas Resolution**: 1920 x 1080 (16:9 widescreen).
- **Color Theme**:
  - Primary Brand Navy: `#0F172A` (Headers, KPI text, structural frames)
  - Fraud Crimson: `#DC2626` (Fraud exposure, high severity, alerts)
  - Accent Electric Blue: `#2563EB` (Volume bars, primary highlights)
  - Neutral Slate Background: `#F8FAFC` (Canvas background)
  - Card Surface: `#FFFFFF` (Visual containers with subtle drop shadow `#E2E8F0`)
  - Risk Tiers: Critical `#DC2626`, High `#EA580C`, Medium `#F59E0B`, Low `#10B981`
- **Global Navigation Bar (Top Banner)**:
  `[Overview] | [Fraud Analytics] | [Financial Analysis] | [Account Risk] | [Investigation] | [ML Analysis] | [Data Quality & Methodology]`
- **Global Disclaimers**: Explicit label on all pages stating *"PaySim Synthetic Financial Topology — Exposure Analytics & Investigative Prioritization"*.

---

## 2. Page-by-Page Layout & Visual Architecture

### 📊 Page 1: Executive Overview
**Objective**: Provide senior leadership with immediate visibility into portfolio volume, fraud exposure, channel risk concentration, and origin drainage patterns.

```
+---------------------------------------------------------------------------------------------------+
| FraudLens — Financial Fraud Analytics & Executive Overview                      [Navigation Bar] |
+---------------------------------------------------------------------------------------------------+
| [Total Transactions] | [Total Volume]  | [Fraud Incidents] | [Fraud Exposure] | [Fraud Rate] | [Drainage %] |
|     6,362,620        |    $1.144 T     |      8,213        |    $12.06 B      |   0.1291%    |   97.55%     |
+---------------------------------------------------------------------------------------------------+
| [VISUAL 1: Channel Breakdown]                 | [VISUAL 2: Daily Fraud Exposure Trajectory]        |
| Bar/Line: Volume vs. Fraud Exposure by Type   | Line Chart: 31-Day Exposure with 7-Day Moving Avg  |
| (TRANSFER: $6.07B | CASH_OUT: $5.99B)         | (Highlighting consistent daily exposure rate)      |
+---------------------------------------------------------------------------------------------------+
| [VISUAL 3: Amount Band Sizing]                | [VISUAL 4: Executive Key Insights Panel]          |
| Stacked Bar: Volume & Fraud Concentration     | • TRANSFER has highest fraud rate (0.7688%).       |
| (<10k, 10k-100k, 100k-500k, 500k-1M, 1M-5M, 5M+) | • CASH_OUT has highest fraud count (4,116).        |
|                                               | • 97.55% of frauds drain origin account to $0.00.  |
|                                               | • Rule flag (isFlaggedFraud) recall is 0.1948%.    |
+---------------------------------------------------------------------------------------------------+
```

---

### 🔍 Page 2: Fraud Analytics
**Objective**: Deep-dive statistical and temporal analysis of fraud characteristics.

```
+---------------------------------------------------------------------------------------------------+
| FraudLens — Deep-Dive Fraud Pattern & Severity Analytics                        [Navigation Bar] |
+---------------------------------------------------------------------------------------------------+
| [Fraud Count]  | [Fraud Rate]   | [Fraud Exposure] | [Avg Fraud Size] | [Median Fraud] | [> $200k Share] |
|    8,213       |   0.1291%      |    $12.06 B      |   $1,467,967.30  |  $441,423.44   |    66.61%       |
+---------------------------------------------------------------------------------------------------+
| [VISUAL 1: Fraud Rate by Channel]             | [VISUAL 2: Simulation Hour Temporal Curve]        |
| Horizontal Bar: TRANSFER vs CASH_OUT          | Dual-axis Line: Hourly Fraud Count vs. Exposure   |
| (0.7688% vs 0.1840%)                          | (Continuous off-peak fraud presence across hours) |
+---------------------------------------------------------------------------------------------------+
| [VISUAL 3: Ticket Size Distribution]          | [VISUAL 4: Statistical Severity Comparison]       |
| Box Plot / Histogram: Fraud vs Legit Amounts  | Metric Card: Cohen's d = 2.1422 (p < 1e-15)       |
| (Average fraud is 8.24x legitimate average)   | Note: Highly significant disparity in balances.   |
+---------------------------------------------------------------------------------------------------+
```

---

### 💵 Page 3: Financial & Transaction Analysis
**Objective**: Analyze total liquidity flow, channel volume distribution, and cumulative financial exposure.

```
+---------------------------------------------------------------------------------------------------+
| FraudLens — Financial Volume & Exposure Trajectory                              [Navigation Bar] |
+---------------------------------------------------------------------------------------------------+
| [Total Volume] | [Fraud-Labeled Exposure] | [Avg Ticket Size] | [Median Ticket] | [Exposure Share %] |
|   $1.144 T     |        $12.06 B          |    $179,861.90    |   $74,871.94    |      1.0535%       |
+---------------------------------------------------------------------------------------------------+
| [VISUAL 1: Volume Share by Channel]           | [VISUAL 2: Cumulative Exposure Growth Curve]      |
| Donut Chart: TRANSFER ($485B), CASH_OUT ($394B)| Area Chart: Cumulative Step-by-Step Growth        |
| CASH_IN ($236B), PAYMENT ($28B), DEBIT ($227M) | (Linear steady upward cumulative exposure curve)  |
+---------------------------------------------------------------------------------------------------+
| [VISUAL 3: Transacted Volume by Amount Band]  | [VISUAL 4: Daily Volume vs. Exposure Dual-Axis]   |
| Clustered Column: Volume vs. Fraud Band       | Dual-line: Daily Total Liquidity vs Fraud Exposure|
+---------------------------------------------------------------------------------------------------+
```

---

### ⚠️ Page 4: Account Risk & Behavioral Prioritization
**Objective**: Present the multi-factor behavioral risk triage model (0–100 scale) for compliance operations.

```
+---------------------------------------------------------------------------------------------------+
| FraudLens — Behavioral Account Risk & Portfolio Triage                          [Navigation Bar] |
+---------------------------------------------------------------------------------------------------+
| [Critical (76-100)] | [High (51-75)] | [Medium (26-50)] | [Low (0-25)] | [Critical Capture Share] |
|   67,252 (1.06%)    | 605,922 (9.52%)| 1,493,438 (23.5%)| 4,196,008 (66%)|   52.77% (4,334 frauds)  |
+---------------------------------------------------------------------------------------------------+
| [VISUAL 1: Risk Tier Portfolio Distribution]  | [VISUAL 2: Origin Drainage Ratio Donut]           |
| Donut Chart: 4 Risk Cohorts with Fraud Rates  | 97.55% Drained (8,012) vs 2.45% Retained (201)    |
| (Critical: 6.44% fraud rate | Low: 0.0004%)   | (Origin accounts emptied post-transaction)        |
+---------------------------------------------------------------------------------------------------+
| [VISUAL 3: Risk Score vs Volume Matrix]       | [VISUAL 4: Top Prioritized Account Candidates]    |
| Scatter / Bubble: Score vs Amount             | Table: Account ID, Score, Channel, Amount, Triage |
+---------------------------------------------------------------------------------------------------+
```

---

### 🕵️ Page 5: Fraud Investigation Workbench
**Objective**: Interactive forensic search workstation over the 20,865-record extract with multi-criteria filtering.

```
+---------------------------------------------------------------------------------------------------+
| FraudLens — Forensic Fraud Investigation Workbench                              [Navigation Bar] |
+---------------------------------------------------------------------------------------------------+
| [SLICERS: Channel (All) | Fraud Status (All) | Amount Range ($) | Step (1-743) | Risk Tier (All)] |
+---------------------------------------------------------------------------------------------------+
| [Candidate Records] | [Confirmed Fraud Cases] | [Total Filtered Volume] | [Avg Candidate Amount]  |
|      20,865         |         8,213           |        $14.28 B         |       $684,310.20       |
+---------------------------------------------------------------------------------------------------+
| [VISUAL 1: Forensic Case Investigation Grid]                                                      |
| Columns: Txn ID | Step | Channel | Amount ($) | Origin Acct | Orig Bal Old/New | Dest Bal Old/New |
|          Orig Error | Dest Error | Drainage | Risk Score | Risk Tier | Forensic Typology Tag      |
+---------------------------------------------------------------------------------------------------+
```

---

### 🤖 Page 6: Machine Learning Model Analysis
**Objective**: Contrast supervised classification models against rule heuristics on the held-out test set.

```
+---------------------------------------------------------------------------------------------------+
| FraudLens — Machine Learning Fraud Detection & Model Evaluation                 [Navigation Bar] |
+---------------------------------------------------------------------------------------------------+
| DISCLAIMER: Evaluated on held-out PaySim test partition (1,272,524 rows). Not production banking data. |
+---------------------------------------------------------------------------------------------------+
| [RF Precision] | [RF Recall] | [RF F1-Score] | [RF PR-AUC] | [RF ROC-AUC] | [Tuned False Positives]|
|    99.88%      |   99.76%    |    0.9982     |   0.9988    |    0.9995    |      14 (XGB 0.90)     |
+---------------------------------------------------------------------------------------------------+
| [VISUAL 1: Model Comparison Grid]                                                                 |
| Table: Model | Precision | Recall | F1-Score | PR-AUC | ROC-AUC | TP | FP | FN | TN                 |
| Random Forest: 99.88% | 99.76% | 0.9982 | 0.9988 | 0.9995 | 1639 | 2 | 4 | 1270879           |
| XGBoost:       93.39% | 99.82% | 0.9650 | 0.9987 | 0.9995 | 1640 | 116 | 3 | 1270765         |
| Logistic Reg:   6.37% | 99.63% | 0.1198 | 0.8492 | 0.9991 | 1637 | 24050 | 6 | 1246831       |
+---------------------------------------------------------------------------------------------------+
| [VISUAL 2: Feature Importance (XGBoost Gain)] | [VISUAL 3: Precision / Recall Threshold Curve]    |
| Horizontal Bar: newbalanceOrig (49.56%)       | Line Chart: Precision, Recall, F1 across 0.10-0.90|
| orig_balance_error (42.07%), amount (3.02%)   | (Demonstrating 87.9% reduction in false alarms)   |
+---------------------------------------------------------------------------------------------------+
```

---

### 📖 Page 7: Data Quality, Architecture & Methodology
**Objective**: Demonstrate rigorous data engineering, data quality audits, heuristic flag evaluation, and research limitations.

```
+---------------------------------------------------------------------------------------------------+
| FraudLens — Data Quality Auditing, Architecture & Governance                    [Navigation Bar] |
+---------------------------------------------------------------------------------------------------+
| [Total Dataset Rows] | [Cleaned Features] | [Missing Values] | [Exact Duplicates] | [Negative Amounts] |
|     6,362,620        |       22 cols      |       0          |        0           |        0           |
+---------------------------------------------------------------------------------------------------+
| [VISUAL 1: End-to-End Pipeline Architecture]  | [VISUAL 2: Heuristic Rule (isFlaggedFraud) Audit]  |
| Flow: Raw CSV -> Cleaning -> Feature Eng      | Matrix: TP = 16, FP = 0, FN = 8,197, TN = 6,354,407|
|       -> EDA -> SQL Schema -> Power BI /      | Precision = 100.00% | Recall = 0.1948%             |
|       Streamlit -> Machine Learning Pipeline  | Insight: Perfect precision but fails on 99.8% cases|
+---------------------------------------------------------------------------------------------------+
| [VISUAL 3: Platform Governance & Disclaimers]                                                     |
| 1. Synthetic Mobile-Money Topology (PaySim). Not real customer or Indian banking data.            |
| 2. Exposure vs Loss: Metrics represent fraud-labeled exposure, not verified unrecovered loss.      |
| 3. Prioritization: Risk scores serve as triage queuing tools, not definitive proof of guilt.      |
| 4. Attribution: ML feature importances indicate mathematical association, not causation.          |
+---------------------------------------------------------------------------------------------------+
```
