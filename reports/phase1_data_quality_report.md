# Phase 1: Initial Data Quality & Inspection Report

**Platform**: FraudLens ? Financial Fraud Analytics & Detection Platform  
**Report Type**: Phase 1 Dataset Verification & Structural Integrity Audit  
**Dataset**: PaySim Synthetic Financial Dataset for Fraud Detection  
**Audit Date**: 2026-09-09  

---

## 1. Dataset Overview
- **Raw File Name**: `PS_20174392719_1491204439457_log.csv`
- **File Size**: ~481.9 MB (0.46 GB)
- **Total Records (Rows)**: 6,362,620
- **Total Features (Columns)**: 11
- **Temporal Span**: 1 to 744 steps (30-day simulation cycle)

---

## 2. Row & Column Count Summary

| Metric | Measured Value |
| :--- | :--- |
| Total Rows | **6,362,620** |
| Total Columns | **11** |
| Memory Usage | ~534.4 MB |
| Total Data Cells | 69,988,820 |

---

## 3. Missing Values & Completeness

| Column | Non-Null Count | Missing Count | Missing Percentage | Integrity Status |
| :--- | :--- | :--- | :--- | :--- |
| `step` | 6,362,620 | 0 | 0.0000% | Complete |
| `type` | 6,362,620 | 0 | 0.0000% | Complete |
| `amount` | 6,362,620 | 0 | 0.0000% | Complete |
| `nameOrig` | 6,362,620 | 0 | 0.0000% | Complete |
| `oldbalanceOrg` | 6,362,620 | 0 | 0.0000% | Complete |
| `newbalanceOrig` | 6,362,620 | 0 | 0.0000% | Complete |
| `nameDest` | 6,362,620 | 0 | 0.0000% | Complete |
| `oldbalanceDest` | 6,362,620 | 0 | 0.0000% | Complete |
| `newbalanceDest` | 6,362,620 | 0 | 0.0000% | Complete |
| `isFraud` | 6,362,620 | 0 | 0.0000% | Complete |
| `isFlaggedFraud` | 6,362,620 | 0 | 0.0000% | Complete |

*Assessment*: The dataset has **0 missing values** across all 11 features (100.0% data completeness).

---

## 4. Duplicate Records
- **Exact Duplicate Rows**: **0** (0.00%)
- *Assessment*: No row-level duplication detected in the raw transactions.

---

## 5. Column Data Types

- **Integer (`int64`)**: `step`, `isFraud`, `isFlaggedFraud` (3 columns)
- **Floating Point (`float64`)**: `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest` (5 columns)
- **String / Object (`object`)**: `type`, `nameOrig`, `nameDest` (3 columns)

---

## 6. Fraud Target Distribution (`isFraud`)

| Category | Record Count | Percentage of Total |
| :--- | :--- | :--- |
| **Legitimate Transactions (0)** | 6,354,407 | 99.8709% |
| **Fraudulent Transactions (1)** | 8,213 | 0.1291% |
| **Total** | 6,362,620 | 100.0000% |

*Analytical Note*: The target is severely imbalanced with a natural fraud occurrence rate of **0.1291%** (~1 fraud per 775 transactions).

---

## 7. Transaction Type Breakdown & Fraud Concentration

| Transaction Type | Total Transactions | Volume Share (%) | Fraud Incidents | Fraud Rate (%) |
| :--- | :--- | :--- | :--- | :--- |
| `CASH_OUT` | 2,237,500 | 35.1663% | 4,116 | 0.1840% |
| `PAYMENT` | 2,151,495 | 33.8146% | 0 | 0.0000% |
| `CASH_IN` | 1,399,284 | 21.9923% | 0 | 0.0000% |
| `TRANSFER` | 532,909 | 8.3756% | 4,097 | 0.7688% |
| `DEBIT` | 41,432 | 0.6512% | 0 | 0.0000% |
| **Total** | **6,362,620** | **100.0000%** | **8,213** | **0.1291%** |

*Critical Observation*: **100.0% of all confirmed fraud cases occur exclusively within `TRANSFER` and `CASH_OUT` channels.**

---

## 8. Potential Data Issues & Edge Cases Identified

1. **Zero Amount Transactions**:
   - Exactly **16 records** have `amount == 0.0`.
   - All 16 zero-amount transactions are labeled `isFraud = 1` and `isFlaggedFraud = 1` (cancelling or attempted illicit operations).
2. **Negative Values**:
   - Negative amounts: **0**
   - Negative balances: **0**
3. **Balance Accounting Discrepancies**:
   - Several legitimate transactions have merchant destination accounts where recipient balances are recorded as `0.0` (PaySim simulator artifact for merchant entities).

---

## 9. Structural & Logical Validation Summary

- [x] Dataset file located and readable
- [x] All 11 expected columns present
- [x] Data types conform to numerical and categorical schemas
- [x] No missing or null values
- [x] Target column contains strictly `{0, 1}` values
- [x] No negative transaction values

---

## PHASE 1 STATUS: PASS
