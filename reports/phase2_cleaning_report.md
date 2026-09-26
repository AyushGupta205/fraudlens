# Phase 2: Data Cleaning & Quality Report

**Platform**: FraudLens ? Financial Fraud Analytics & Detection Platform  
**Report Type**: Phase 2 Reproducible Data Cleaning & Quality Audit  
**Dataset**: PaySim Synthetic Financial Dataset for Fraud Detection  
**Audit Date**: 2026-09-09  

---

## 1. Cleaning Objective
To construct a reproducible, memory-conscious data-cleaning and feature engineering pipeline for the 6.36M-row PaySim dataset without silently dropping records, while mathematically validating balance transitions and establishing ground truth targets.

---

## 2. Input Dataset
- **Raw File**: data/raw/PS_20174392719_1491204439457_log.csv (Preserved Untouched)
- **Input Dimensions**: 6,362,620 rows x 11 columns
- **Input Memory**: ~534.4 MB

---

## 3. Missing Values
- **Missing Value Count**: 0
- **Action Taken**: None required (0 missing values present)

---

## 4. Duplicate Analysis
- **Exact Duplicate Rows**: 0
- **Action Taken**: No duplicate removal required.

---

## 5. Data Type Validation
- Standardized `step` to `int32`, `isFraud` & `isFlaggedFraud` to `int8`.
- Standardized `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest` to `float64`.
- Standardized string identifier and category fields (`type`, `nameOrig`, `nameDest`).

---

## 6. Category Validation
- **Observed Categories**: PAYMENT, TRANSFER, CASH_OUT, DEBIT, CASH_IN
- **Unexpected Categories**: 0
- **Status**: Complete alignment with domain schema.

---

## 7. Numerical Validation
- **Negative Transaction Amounts**: 0
- **Negative Account Balances**: 0
- **Infinite / NaN Values**: 0
- **Zero-Value Transactions**: 16

---

## 8. Zero-Amount Transactions Investigation
- Exactly **16 records** possess an `amount == 0.00`.
- **Modus Operandi**: All 16 transactions belong to `type == CASH_OUT` and are confirmed frauds (`isFraud == 1`).
- **Data Decision**: Retained in analytical dataset as legitimate fraud signals representing attempted post-drain cashout operations.

---

## 9. Balance Consistency Analysis

**Mathematical Formulas Applied:**
- `orig_balance_error = newbalanceOrig + amount - oldbalanceOrg`
- `dest_balance_error = newbalanceDest - oldbalanceDest - amount`

**Classification (Tolerance = $0.01 to account for floating-point precision):**
- **Consistent (|error| <= 0.01)**: 1,281,436 (20.14%)
- **Small Rounding Difference (0.01 < |error| <= 1.0)**: 80,400 (1.26%)
- **Material Inconsistency (|error| > 1.0)**: 5,000,784 (78.60%)

*Domain Note*: In PaySim, fraudulent operations exhibit **99.45% mathematical consistency** on origin balance liquidation, whereas legitimate non-outbound operations (e.g. `CASH_IN` and `PAYMENT` to merchant accounts) exhibit expected structural discrepancies.

---

## 10. Fraud Target Validation
- **Target Variable**: `isFraud in {0, 1}`
- **Confirmed Fraud Incidents**: 8,213 (0.1291%)
- **Confirmed Legitimate Transactions**: 6,354,407 (99.8709%)
- **Target Integrity**: 100% preserved.

---

## 11. Flagged Fraud Analysis (`isFlaggedFraud`)
- **System-Flagged Transactions**: 16
- **True Positive Flagged Frauds**: 16
- **Flagged Capture Recall**: 0.1948%
- *Analytical Finding*: The naive single-rule benchmark captures < 0.20% of total fraud, highlighting the critical necessity for multi-factor behavioral heuristics and machine learning.

---

## 12. Features Created in Analytical Dataset
1. `transaction_hour`: Hour of transaction (0 to 23).
2. `transaction_day`: Calendar simulation day (1 to 31).
3. `origin_balance_change`: `oldbalanceOrg - newbalanceOrig`.
4. `destination_balance_change`: `newbalanceDest - oldbalanceDest`.
5. `orig_balance_error`: Origin balance mathematical discrepancy.
6. `dest_balance_error`: Destination balance mathematical discrepancy.
7. `orig_balance_consistency`: Categorical consistency status (`Consistent`, `Small Rounding Difference`, `Material Inconsistency`).
8. `amount_to_origin_balance_ratio`: Ratio of transacted amount relative to pre-existing origin balance.
9. `amount_to_destination_balance_ratio`: Ratio of transacted amount relative to destination balance.
10. `zero_balance_origin_after_transaction`: Boolean flag indicating complete origin account drainage.
11. `zero_balance_destination_after_transaction`: Boolean flag indicating zero ending destination balance.

---

## 13. Records Removed & Retained
- **Records Removed**: **0** (0.00%)
- **Records Retained**: **6,362,620** (100.00%)

---

## 14. Data Quality Before vs After Comparison

| Metric | Before Cleaning | After Cleaning | Change / Decision |
| :--- | ---: | ---: | :--- |
| **Total Rows** | 6,362,620 | 6,362,620 | No records silently dropped |
| **Total Columns** | 11 | 22 | +11 analytical features engineered |
| **Missing Values** | 0 | 0 | 100% complete |
| **Exact Duplicates** | 0 | 0 | 0 duplicates |
| **Invalid Numerics** | 0 | 0 | All negative/inf values verified zero |
| **Invalid Categories** | 0 | 0 | 100% valid domain channels |
| **Fraud Transactions** | 8,213 | 8,213 | Ground truth preserved |
| **Legitimate Transactions** | 6,354,407 | 6,354,407 | Ground truth preserved |

---

## 15. Final Validation Summary
- [x] Raw data preserved untouched
- [x] Processed dataset saved to `data/processed/paysim_clean.parquet`
- [x] Balance errors mathematically categorized
- [x] Zero-amount transactions documented and retained
- [x] Automated unit tests passing

---

## PHASE 2 STATUS: PASS