# FraudLens — Phase 7: Machine Learning Fraud Detection Validation Report

## 1. Executive Summary & Verification Status

This document provides empirical verification, methodology auditing, and cross-validation for the **FraudLens Machine Learning Fraud Detection Layer** (`src/ml/`).

Three distinct classification models were engineered, trained, and evaluated on the verified 6.36M-row PaySim synthetic mobile-money dataset:
1. **L2-Regularized Logistic Regression** (Standardized linear baseline with balanced class weighting)
2. **Balanced Random Forest Classifier** (Non-linear bagging ensemble, 100 estimators, max_depth=12)
3. **Histogram-based Gradient Boosted Trees (XGBoost)** (Extreme gradient boosting with `scale_pos_weight` derived strictly from training data)

**Overall Phase 7 Verification Status**: **PASS (100% Leakage-Free & Mathematically Reconciled)**

---

## 2. Data Leakage Prevention & Feature Classification Audit

A rigorous multi-point leakage audit was executed prior to model fitting to prevent data contamination:

| Column Name | Classification | Inclusion Status | Leakage Prevention Rationale |
| :--- | :--- | :--- | :--- |
| `isFraud` | Target Variable | **EXCLUDED from Features** | Binary ground truth label ($y \in \{0, 1\}$). |
| `isFlaggedFraud` | Rule Flag | **EXCLUDED from Features** | Heuristic rule output; excluded to eliminate circular reasoning and synthetic target leakage. |
| `nameOrig` | Identifier | **EXCLUDED from Features** | High-cardinality raw customer ID ($>6.3M$ unique strings); non-generalizable. |
| `nameDest` | Identifier | **EXCLUDED from Features** | High-cardinality raw recipient ID; parsed into binary merchant indicator `is_dest_merchant`. |
| `type` | Categorical Channel | **Transformed** | Converted to one-hot binary indicators (`is_transfer`, `is_cashout`, `is_payment`). |
| `orig_balance_consistency`| Text Label | **EXCLUDED from Features** | Redundant string label derived directly from `orig_balance_error`. |
| **Selected 20 Features** | Numeric / Binary | **INCLUDED in Matrix $X$** | Temporal steps, amounts, balances, behavioral balance errors, balance changes, and ratios. |

### Preprocessing & Split Safeguards:
- **Feature Scaling**: `StandardScaler` was fitted **strictly on `X_train`** and subsequently applied to transform `X_val` and `X_test`.
- **Class Imbalance Parameter**: `scale_pos_weight = 773.75` was calculated solely from training label counts ($\frac{N_{\text{train, legit}}}{N_{\text{train, fraud}}}$).
- **Holdout Test Set**: The 1,272,524-row test set remained completely untouched until final model scoring.
- **Threshold Selection**: Decision threshold tuning was conducted strictly on an internal validation partition derived from `X_train`.

---

## 3. Train / Test Stratified Split Architecture

To preserve the severe class imbalance ($0.1291\%$ fraud prevalence), stratified partitioning was enforced with `random_state = 42`:

| Partition | Total Transactions | Legitimate (0) | Confirmed Fraud (1) | Fraud Rate (%) | Share of Dataset |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Full Cleaned Dataset** | **6,362,620** | 6,354,407 | 8,213 | **0.1291%** | 100.00% |
| **Training Set (`X_train`)** | **5,090,096** | 5,083,526 | 6,570 | **0.1291%** | 80.00% |
| **Untouched Test Set (`X_test`)** | **1,272,524** | 1,270,881 | 1,643 | **0.1291%** | 20.00% |

---

## 4. Model Comparison & Performance Evaluation

All models were evaluated on the untouched holdout test partition ($N = 1,272,524$, $\text{Fraud} = 1,643$). Because fraud detection is severely class-imbalanced, **PR-AUC (Average Precision)** is the primary ranking metric.

### Model Performance Comparison Table:

| Model Architecture | Threshold | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | True Positives (TP) | False Positives (FP) | False Negatives (FN) | True Negatives (TN) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Random Forest** | 0.50 | **0.9988** | **0.9976** | **0.9982** | **0.9995** | **0.9988** | 1,639 | 2 | 4 | 1,270,879 |
| **XGBoost** | 0.50 | **0.9339** | **0.9982** | **0.9650** | **0.9995** | **0.9987** | 1,640 | 116 | 3 | 1,270,765 |
| **Logistic Regression** | 0.50 | 0.0637 | 0.9963 | 0.1198 | 0.9991 | 0.8492 | 1,637 | 24,050 | 6 | 1,246,831 |

### Tuned Threshold Performance (Selected on Validation Partition):

| Model Architecture | Tuned Threshold | Tuned Precision | Tuned Recall | Tuned F1-Score | Tuned TP | Tuned FP | Tuned FN | Tuned TN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Random Forest** | 0.60 | **1.0000** | 0.9976 | **0.9988** | 1,639 | 0 | 4 | 1,270,881 |
| **XGBoost** | 0.90 | **0.9915** | 0.9976 | **0.9945** | 1,639 | 14 | 4 | 1,270,867 |
| **Logistic Regression** | 0.90 | 0.2881 | 0.9373 | 0.4407 | 1,540 | 3,806 | 103 | 1,267,075 |

---

## 5. Mathematical Confusion Matrix Reconciliation

For all three models on the holdout test set:
- **Total Fraud Matches**: $\text{TP} + \text{FN} = 1,643$ (100% of test fraud cases accounted for).
- **Total Legitimate Matches**: $\text{TN} + \text{FP} = 1,270,881$ (100% of test legitimate cases accounted for).
- **Total Test Records**: $\text{TP} + \text{TN} + \text{FP} + \text{FN} = 1,272,524$ (100% exact match).

---

## 6. Threshold Sensitivity & Investigator Workload Analysis

Operating decision thresholds directly control the trade-off between fraud capture rate and manual investigation volume.

### XGBoost Validation Threshold Sweep ($N_{\text{val}} = 1,017,800$, $\text{Fraud}_{\text{val}} = 1,314$):

| Decision Threshold | Precision | Recall | F1-Score | Total Alerts Generated | False Alerts (FP) | Fraud Exposure Captured ($) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **0.10** | 84.83% | 100.00% | 0.9179 | 1,549 | 235 | \$1,959,696,842.04 |
| **0.30** | 92.08% | 100.00% | 0.9588 | 1,427 | 113 | \$1,959,696,842.04 |
| **0.50 (Default)** | 94.67% | 100.00% | 0.9726 | 1,388 | 74 | \$1,959,696,842.04 |
| **0.70** | 96.62% | 100.00% | 0.9828 | 1,360 | 46 | \$1,959,696,842.04 |
| **0.90 (Tuned)** | **99.32%** | **100.00%** | **0.9966** | **1,323** | **9** | **\$1,959,696,842.04** |

### Analyst Workload Insight:
Moving the decision threshold from $0.50$ to $0.90$ eliminates **87.8% of false alerts** (reducing FP from 74 to 9 in the validation cohort) without losing a single confirmed fraud incident, drastically optimizing operational AML review efficiency.

---

## 7. Feature Importance & Model Attribution

Feature importance was extracted for all three architectures:

### Top Predictive Features in Tree Ensemble (XGBoost):
1. **`newbalanceOrig` (49.56% relative gain)**: The residual origin balance after transaction execution is the single strongest indicator of complete account draining.
2. **`orig_balance_error` (42.07% relative gain)**: Discrepancy between stated balance deductions and transacted amounts.
3. **`amount` (3.02% relative gain)**: Absolute monetary scale of the transfer.
4. **`origin_balance_change` (2.30% relative gain)**: Net change in originating balance.
5. **`is_payment` (0.78% relative gain)**: Channel classification (payment channels have zero fraud history in PaySim).
6. **`amount_to_destination_balance_ratio` (0.50% relative gain)**: Destination balance surge relative to prior account holdings.

> [!NOTE]
> **Data Analyst Phrasing**: Feature attributions represent mathematical associations with model predictions within the PaySim synthetic topology and must not be interpreted as real-world causal mechanisms.

---

## 8. Artifacts & Deliverables

1. **ML Pipeline Modules**:
   - `src/ml/prepare_ml_data.py` (Feature selection, leakage audit, stratified splitting)
   - `src/ml/train_models.py` (Training pipeline for Logistic Regression, Random Forest, XGBoost)
   - `src/ml/evaluate_models.py` (Evaluation metrics, confusion matrices, financial exposure calculation)
   - `src/ml/threshold_analysis.py` (Threshold tuning grids and optimal selector)
   - `src/ml/feature_importance.py` (Tree gain & linear coefficient attribution extractor)
   - `src/ml/predict.py` (Single-transaction and batch scoring interface)
2. **Serialized Model Artifacts**:
   - `data/processed/models/xgboost_model.joblib`
   - `data/processed/models/randomforest_model.joblib`
   - `data/processed/models/logisticregression_model.joblib`
   - `data/processed/models/scaler.joblib`
3. **Exported Evaluation Data**:
   - `data/processed/ml/model_comparison.csv`
   - `data/processed/ml/threshold_grid_xgboost.csv`
   - `data/processed/ml/feature_importance_xgboost.csv`
4. **Interactive Dashboard Integration**:
   - `dashboard/streamlit_app.py` (Page 6: `🤖 ML Model Analysis` with threshold trade-offs and feature attributions)
5. **Automated Test Suite**:
   - `tests/test_phase7.py` (12 automated unit and integration tests, 100% passing)

---

## 9. Test Automation & Cross-Phase Regression Verification

```bash
pytest tests/ -v
```

### Full Test Suite Summary:
- **Phase 1 (Data Loading & Structure)**: 6 / 6 PASSED
- **Phase 2 (Cleaning & Feature Engineering)**: 9 / 9 PASSED
- **Phase 3 (Exploratory Data Analysis)**: 11 / 11 PASSED
- **Phase 4 (SQL Analytics & Schema)**: 13 / 13 PASSED
- **Phase 5 (Power BI Star Schema & DAX)**: 9 / 9 PASSED
- **Phase 6 (Streamlit Analytics Application)**: 12 / 12 PASSED
- **Phase 7 (Machine Learning Fraud Detection)**: 12 / 12 PASSED
- **Core Unit & Regression Tests**: 6 / 6 PASSED
- **Total Tests Passing**: **78 / 78 PASSED (100% Success Rate)**
