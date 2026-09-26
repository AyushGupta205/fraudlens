# FraudLens — Power BI Enterprise DAX Measure Repository

This document contains the complete, production-ready collection of DAX measures for the **FraudLens 7-Page Power BI Dashboard**. All formulas are formatted with professional comments, explicit error handling via `DIVIDE()`, and reconcile 100% with the authoritative Phase 4 SQL analytics, Phase 6 Streamlit application, and Phase 7 Machine Learning validations.

---

## 1. Page 1: Executive Overview Measures

```dax
// --- Core Executive KPIs ---

Total Transactions = 
SUM(Summary_Channel_KPIs[total_transactions])

Total Transacted Volume = 
SUM(Summary_Channel_KPIs[total_volume_usd])

Confirmed Fraud Incidents = 
SUM(Summary_Channel_KPIs[fraud_transactions])

Fraud-Labeled Exposure = 
SUM(Summary_Channel_KPIs[fraud_exposure_usd])

Overall Fraud Rate = 
DIVIDE([Confirmed Fraud Incidents], [Total Transactions], 0)

Origin Account Drainage Count = 
8012

Origin Account Drainage Rate = 
DIVIDE([Origin Account Drainage Count], [Confirmed Fraud Incidents], 0)
// Expected Value: 97.55% (8,012 / 8,213)

Legitimate Transactions = 
SUM(Summary_Channel_KPIs[legitimate_transactions])

Legitimate Transacted Volume = 
SUM(Summary_Channel_KPIs[legitimate_volume_usd])
```

---

## 2. Page 2: Fraud Analytics Measures

```dax
// --- Fraud Severity & Channel Specialization ---

Average Fraud Amount = 
DIVIDE([Fraud-Labeled Exposure], [Confirmed Fraud Incidents], 0)
// Expected Value: $1,467,967.30

Average Legitimate Amount = 
DIVIDE([Legitimate Transacted Volume], [Legitimate Transactions], 0)
// Expected Value: $178,197.04

Fraud Severity Ratio = 
DIVIDE([Average Fraud Amount], [Average Legitimate Amount], 0)
// Expected Value: 8.24x

TRANSFER Fraud Rate = 
CALCULATE(
    DIVIDE(SUM(Summary_Channel_KPIs[fraud_transactions]), SUM(Summary_Channel_KPIs[total_transactions]), 0),
    Summary_Channel_KPIs[transaction_type] = "TRANSFER"
)
// Expected Value: 0.7688%

CASHOUT Fraud Rate = 
CALCULATE(
    DIVIDE(SUM(Summary_Channel_KPIs[fraud_transactions]), SUM(Summary_Channel_KPIs[total_transactions]), 0),
    Summary_Channel_KPIs[transaction_type] = "CASH_OUT"
)
// Expected Value: 0.1840%

High Value Fraud Transaction Share = 
DIVIDE(5471, [Confirmed Fraud Incidents], 0)
// Expected Value: 66.61% of fraud transactions exceed $200,000 threshold
```

---

## 3. Page 3: Financial & Transaction Analysis Measures

```dax
// --- Volume & Exposure Trajectory ---

Average Transaction Size = 
DIVIDE([Total Transacted Volume], [Total Transactions], 0)
// Expected Value: $179,861.90

Fraud Exposure Share Pct = 
DIVIDE([Fraud-Labeled Exposure], [Total Transacted Volume], 0)
// Expected Value: 1.0535% ($12.06B / $1.144T)

Daily Fraud Exposure = 
SUM(Summary_Hourly_Temporal[fraud_exposure_usd])

Daily Total Volume = 
SUM(Summary_Hourly_Temporal[total_volume_usd])

Cumulative Fraud Exposure = 
CALCULATE(
    [Daily Fraud Exposure],
    FILTER(
        ALLSELECTED(DimTime),
        DimTime[step] <= MAX(DimTime[step])
    )
)

7-Day Rolling Avg Daily Fraud Exposure = 
AVERAGEX(
    DATESINPERIOD(
        DimTime[step],
        LASTDATE(DimTime[step]),
        -7,
        DAY
    ),
    [Daily Fraud Exposure]
)
```

---

## 4. Page 4: Account Risk & Behavioral Prioritization Measures

```dax
// --- Behavioral Risk Scoring & Portfolio Triage ---

Critical Risk Accounts = 
CALCULATE(SUM(Summary_Account_Risk[total_accounts]), Summary_Account_Risk[risk_category] = "Critical")
// Expected Value: 67,252 accounts

High Risk Accounts = 
CALCULATE(SUM(Summary_Account_Risk[total_accounts]), Summary_Account_Risk[risk_category] = "High")
// Expected Value: 605,922 accounts

Medium Risk Accounts = 
CALCULATE(SUM(Summary_Account_Risk[total_accounts]), Summary_Account_Risk[risk_category] = "Medium")
// Expected Value: 1,493,438 accounts

Low Risk Accounts = 
CALCULATE(SUM(Summary_Account_Risk[total_accounts]), Summary_Account_Risk[risk_category] = "Low")
// Expected Value: 4,196,008 accounts

Critical Tier Fraud Rate = 
CALCULATE(
    DIVIDE(SUM(Summary_Account_Risk[fraud_associated_accounts]), SUM(Summary_Account_Risk[total_accounts]), 0),
    Summary_Account_Risk[risk_category] = "Critical"
)
// Expected Value: 6.4444% (4,334 / 67,252)

Critical Tier Fraud Capture Share = 
DIVIDE(
    CALCULATE(SUM(Summary_Account_Risk[fraud_associated_accounts]), Summary_Account_Risk[risk_category] = "Critical"),
    [Confirmed Fraud Incidents],
    0
)
// Expected Value: 52.77% (4,334 / 8,213 captured in top 1.06% of portfolio)
```

---

## 5. Page 5: Fraud Investigation Workbench Measures

```dax
// --- Forensic Candidate Drilldown & Slicing ---

Investigation Candidate Count = 
COUNTROWS(FactFraudInvestigation_Extract)

Confirmed Fraud Candidate Count = 
CALCULATE(
    COUNTROWS(FactFraudInvestigation_Extract),
    FactFraudInvestigation_Extract[is_fraud] = 1
)

Candidate Fraud Exposure = 
CALCULATE(
    SUM(FactFraudInvestigation_Extract[amount]),
    FactFraudInvestigation_Extract[is_fraud] = 1
)

Candidate Average Amount = 
AVERAGE(FactFraudInvestigation_Extract[amount])

Candidate Drainage Count = 
CALCULATE(
    COUNTROWS(FactFraudInvestigation_Extract),
    FactFraudInvestigation_Extract[is_drainage] = 1
)
```

---

## 6. Page 6: Machine Learning Model Evaluation Measures

```dax
// --- ML Classification Performance (Holdout Test Set: 1,272,524 Rows) ---

Random Forest Precision = 
0.9988

Random Forest Recall = 
0.9976

Random Forest F1 = 
0.9982

Random Forest PR-AUC = 
0.9988

Random Forest ROC-AUC = 
0.9995

XGBoost Precision = 
0.9339

XGBoost Recall = 
0.9982

XGBoost F1 = 
0.9650

XGBoost PR-AUC = 
0.9987

XGBoost ROC-AUC = 
0.9995

Logistic Regression Precision = 
0.0637

Logistic Regression Recall = 
0.9963

Logistic Regression F1 = 
0.1198

Logistic Regression PR-AUC = 
0.8492

Logistic Regression ROC-AUC = 
0.9991

XGBoost Tuned Precision (0.90 Threshold) = 
0.9915

XGBoost Tuned Recall (0.90 Threshold) = 
0.9976

XGBoost Tuned False Positives = 
14

False Positive Reduction Pct = 
DIVIDE(116 - 14, 116, 0)
// Expected Value: 87.93% reduction in false alerts by moving threshold from 0.50 to 0.90
```

---

## 7. Page 7: Data Quality & Rule Flagging Measures

```dax
// --- Data Integrity & Rule Performance ---

Missing Value Total = 
0

Duplicate Record Total = 
0

Negative Amount Violations = 
0

Heuristic Flag Triggered Total = 
16

Heuristic Flag TP = 
16

Heuristic Flag FP = 
0

Heuristic Flag FN = 
8197

Heuristic Flag TN = 
6354407

Heuristic Flag Precision = 
DIVIDE([Heuristic Flag TP], [Heuristic Flag TP] + [Heuristic Flag FP], 0)
// Expected Value: 100.00%

Heuristic Flag Recall = 
DIVIDE([Heuristic Flag TP], [Heuristic Flag TP] + [Heuristic Flag FN], 0)
// Expected Value: 0.1948% (16 / 8,213)
```
