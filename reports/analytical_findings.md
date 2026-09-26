# Detailed Analytical Findings & Statistical Report ? FraudLens

## 1. Statistical Overview of Transaction Dynamics

### Amount Distribution & Skewness
- **Legitimate Transactions**: Highly right-skewed ($	ext{Skewness} > 30.0$), with 75th percentile at $\,000$ and median at $\,640.89$.
- **Fraudulent Transactions**: Median at $\,423.44$, with maximum transaction capping at $\,000,000.00$ (representing the system's hard transaction limit per API call).
- **Kurtosis**: Extremely high kurtosis indicating heavy tail risk where catastrophic loss is driven by fewer than 1% of transactions.

---

## 2. Channel Breakdown & Loss Attribution

`
+-----------+--------------------+-------------------+--------------------+------------------+------------------+
| Channel   | Total Transactions | Total Volume ($)  | Fraud Transactions | Fraud Loss ($)   | Loss Share (%)   |
+-----------+--------------------+-------------------+--------------------+------------------+------------------+
| TRANSFER  |             28,490 | 25,690,480,480.00 |              4,097 | 6,067,213,000.00 |           50.32% |
| CASH_OUT  |            106,717 | 18,574,890,230.00 |              4,116 | 5,989,202,427.84 |           49.68% |
| PAYMENT   |             99,042 |  1,297,377,200.00 |                  0 |             0.00 |            0.00% |
| CASH_IN   |             63,820 | 10,818,340,110.00 |                  0 |             0.00 |            0.00% |
| DEBIT     |              1,931 |     10,014,350.00 |                  0 |             0.00 |            0.00% |
+-----------+--------------------+-------------------+--------------------+------------------+------------------+
`

### Analytical Insights:
- PAYMENT, CASH_IN, and DEBIT demonstrated **0.00% empirical fraud** across the dataset.
- Anti-fraud infrastructure should prioritize inspection latency budget on TRANSFER and CASH_OUT pipelines.

---

## 3. Customer Risk Tier Segmentation Summary

- **Critical Risk (2.52% of customer base)**: Accounts responsible for **.05 Billion** in confirmed fraud volume (average risk score 88.4).
- **High Risk (20.55%)**: High velocity / large volume commercial accounts without confirmed fraud incidents.
- **Medium Risk (30.43%)**: Standard retail accounts utilizing transfer channels with balanced inflows/outflows.
- **Low Risk (46.51%)**: Routine small-ticket payment and debit users.

---

## 4. Machine Learning Model Benchmark

`
+--------------------+-----------+--------+----------+---------+---------+
| Model Architecture | Precision | Recall | F1-Score | PR-AUC  | ROC-AUC |
+--------------------+-----------+--------+----------+---------+---------+
| Logistic Regression|    68.14% | 99.45% |   80.87% |  0.9809 |  0.9986 |
| Random Forest      |    99.94% | 99.51% |   99.73% |  0.9977 |  0.9992 |
| XGBoost Classifier |    99.51% | 99.51% |   99.51% |  0.9971 |  0.9992 |
+--------------------+-----------+--------+----------+---------+---------+
`

### Cost-Benefit Analysis:
- In testing on a 60,000-transaction holdout set (containing 1,643 frauds):
  - **False Negatives**: 8 transactions missed ($pprox \.7	ext{M}$ unmitigated loss).
  - **False Positives**: 1 false alert ($\$ investigation cost).
  - **Prevented Fraud Volume**: Over **.41 Billion** in saved transaction loss.
