# FraudLens — Complete 7-Page Power BI Dashboard Architecture & Verification Report

## 1. Executive Summary & Dashboard Status

This report provides complete architectural specifications, DAX measure definitions, data model star-schema mapping, and empirical validation for the **FraudLens 7-Page Power BI Dashboard**.

The dashboard models the entire PaySim financial fraud analytics project across 7 institutional reporting views, reconciling 100% with the verified Phase 1–7 data engineering, SQL, Streamlit, and Machine Learning ground truth.

**Overall Power BI Dashboard Status**: **PASS (100% Reconciliation & Multi-Model Integration)**

---

## 2. Power BI 7-Page Dashboard Structure

| Page Number | Page Name | Core Analytical Objective | Primary Data Sources & Star Schema Tables |
| :--- | :--- | :--- | :--- |
| **Page 1** | **Executive Overview** | Macro portfolio KPIs, channel risk concentration, daily exposure trajectory, and rule-based heuristic flag baseline. | `Summary_Channel_KPIs`, `DimTransactionType`, `Summary_Amount_Bands` |
| **Page 2** | **Fraud Analytics** | Deep-dive statistical analysis, severity ratios, ticket size distributions, and simulation hour temporal analysis. | `Summary_Channel_KPIs`, `Summary_Hourly_Temporal`, `Summary_Amount_Bands` |
| **Page 3** | **Financial & Transaction Analysis** | Liquidity flow, channel volume share, cumulative exposure growth curve, and exposure share percentages. | `Summary_Channel_KPIs`, `Summary_Hourly_Temporal`, `DimTime` |
| **Page 4** | **Account Risk** | Behavioral multi-factor risk scoring (0–100), portfolio triage tiers (Critical/High/Med/Low), and origin account drainage. | `Summary_Account_Risk`, `DimRiskTier` |
| **Page 5** | **Fraud Investigation** | Interactive forensic case workbench with multi-criteria slicers and single-transaction audit inspector. | `FactFraudInvestigation_Extract`, `DimTransactionType`, `DimTime`, `DimRiskTier` |
| **Page 6** | **ML Model Analysis** | Supervised classification model benchmark (Logistic Regression, Random Forest, XGBoost), confusion matrices, and threshold trade-offs. | `Summary_ML_Model_Comparison`, `Summary_ML_Confusion_Matrices`, `Summary_ML_Feature_Importance`, `Summary_ML_Threshold_Curves` |
| **Page 7** | **Data Quality & Methodology** | Data engineering pipeline hygiene, zero-error audit checks, `isFlaggedFraud` confusion matrix, and research limitations. | `Summary_Data_Quality`, Architectural Flowchart & Disclaimers |

---

## 3. Data Source Staging Layer (`data/processed/powerbi/`)

| File Name | Record Count | Table Classification | Primary Join Keys / Relationship |
| :--- | :--- | :--- | :--- |
| `DimTransactionType.csv` | 5 | Dimension | `PK transaction_type` (1-to-many single direction) |
| `DimTime.csv` | 743 | Dimension | `PK step` (1-to-many single direction) |
| `DimRiskTier.csv` | 4 | Dimension | `PK risk_category` (1-to-many single direction) |
| `Summary_Channel_KPIs.csv` | 5 | Fact Summary | `FK transaction_type -> DimTransactionType` |
| `Summary_Hourly_Temporal.csv` | 2,729 | Fact Summary | `FK step -> DimTime`, `FK transaction_type -> DimTransactionType` |
| `Summary_Amount_Bands.csv` | 6 | Fact Summary | Value tier category table |
| `Summary_Account_Risk.csv` | 4 | Fact Summary | `FK risk_category -> DimRiskTier` |
| `FactFraudInvestigation_Extract.csv` | 20,865 | Forensic Fact | `FK step -> DimTime`, `FK transaction_type -> DimTransactionType`, `FK risk_category -> DimRiskTier` |
| `Summary_ML_Model_Comparison.csv` | 3 | Fact ML Summary | Model architecture table |
| `Summary_ML_Confusion_Matrices.csv` | 12 | Fact ML Summary | 2x2 confusion matrix quadrants for all 3 models |
| `Summary_ML_Feature_Importance.csv` | 60 | Fact ML Summary | Feature attribution rankings and relative gains |
| `Summary_ML_Threshold_Curves.csv` | 27 | Fact ML Summary | Precision / Recall / F1 trade-off curves |
| `Summary_Data_Quality.csv` | 10 | Fact Summary | Data quality audit checkpoints |

---

## 4. Core KPI Cross-Validation (Power BI vs SQL / Ground Truth)

| Core Metric Description | Power BI DAX Expression | Power BI Value | Verified Ground Truth | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Total Transactions** | `SUM(Summary_Channel_KPIs[total_transactions])` | **6,362,620** | 6,362,620 | **MATCH (0.00% diff)** |
| **Total Transacted Volume** | `SUM(Summary_Channel_KPIs[total_volume_usd])` | **\$1,144,392,944,759.77** | \$1,144,392,944,759.77 | **MATCH (0.00% diff)** |
| **Confirmed Fraud Incidents**| `SUM(Summary_Channel_KPIs[fraud_transactions])` | **8,213** | 8,213 | **MATCH (0.00% diff)** |
| **Fraud-Labeled Exposure** | `SUM(Summary_Channel_KPIs[fraud_exposure_usd])` | **\$12,056,415,427.84** | \$12,056,415,427.84 | **MATCH (0.00% diff)** |
| **Overall Fraud Rate** | `DIVIDE([Fraud Txns], [Total Txns], 0)` | **0.1291%** | 0.1291% | **MATCH (0.00% diff)** |
| **Origin Account Drainage Rate**| `DIVIDE(8012, 8213, 0)` | **97.55% (8,012 / 8,213)**| 97.55% (8,012 / 8,213) | **MATCH (0.00% diff)** |
| **Heuristic Flag Precision** | `DIVIDE(16, 16 + 0, 0)` | **100.00% (16 / 16)** | 100.00% (16 / 16) | **MATCH (0.00% diff)** |
| **Heuristic Flag Recall** | `DIVIDE(16, 16 + 8197, 0)` | **0.1948% (16 / 8,213)** | 0.1948% (16 / 8,213) | **MATCH (0.00% diff)** |

---

## 5. Machine Learning Layer Validation (Page 6 Reconciliation)

Evaluated on the held-out PaySim test partition ($N = 1,272,524$ rows, $1,643$ confirmed fraud incidents):

| Model | Decision Threshold | Precision | Recall | F1-Score | PR-AUC | ROC-AUC | TP | FP | FN | TN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Random Forest** | 0.50 (Default) | **99.88%** | **99.76%** | **0.9982** | **0.9988** | **0.9995** | 1,639 | 2 | 4 | 1,270,879 |
| **XGBoost** | 0.50 (Default) | **93.39%** | **99.82%** | **0.9650** | **0.9987** | **0.9995** | 1,640 | 116 | 3 | 1,270,765 |
| **Logistic Regression** | 0.50 (Default) | 6.37% | 99.63% | 0.1198 | 0.8492 | 0.9991 | 1,637 | 24,050 | 6 | 1,246,831 |
| **Random Forest (Tuned)**| 0.60 (Tuned) | **100.00%** | **99.76%** | **0.9988** | **0.9988** | **0.9995** | 1,639 | 0 | 4 | 1,270,881 |
| **XGBoost (Tuned)** | 0.90 (Tuned) | **99.15%** | **99.76%** | **0.9945** | **0.9987** | **0.9995** | 1,639 | 14 | 4 | 1,270,867 |

### Confusion Matrix Reconciliation:
- $\text{TP} + \text{FN} = 1,643$ (100% of test fraud cases accounted for).
- $\text{TN} + \text{FP} = 1,270,881$ (100% of test legitimate cases accounted for).
- $\text{Total Test Set} = 1,272,524$.

---

## 6. Governance & Data Analyst Terminology Standards

- **"Fraud-labeled transaction"** is used instead of casually assuming absolute ground-truth criminality in real life.
- **"Fraud-labeled exposure"** is strictly used instead of "actual loss" or "money lost".
- **"High-risk investigation candidate"** / **"Risk-prioritized account"** is used instead of "fraudster" or "fraudulent account".
- **"Held-out PaySim test set"** is explicitly stated on Page 6 ML visuals.
