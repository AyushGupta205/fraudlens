# FraudLens ? Data Dictionary

This data dictionary documents every field in the authentic **PaySim Synthetic Financial Dataset for Fraud Detection**.

| Column | Data Type | Description | Example | Analytical Role |
| :--- | :--- | :--- | :--- | :--- |
| `step` | `int64` | Discrete unit of simulation time where 1 step corresponds to 1 hour. Total timeline spans 744 steps (30 days). | `1`, `24`, `743` | Temporal feature for time-series analysis, diurnal patterns, and hourly fraud velocity. |
| `type` | `object` (string) | Transaction channel/category: `CASH_OUT`, `PAYMENT`, `CASH_IN`, `TRANSFER`, `DEBIT`. | `TRANSFER`, `CASH_OUT` | Primary categorical dimension for channel risk segmentation and fraud distribution. |
| `amount` | `float64` | Transaction monetary value in local/simulated currency units (USD equivalent). | `9839.64`, `181.00` | Core continuous numerical feature measuring exposure, loss, and transaction scale. |
| `nameOrig` | `object` (string) | Unique identifier of the originating customer account initiating the transaction. | `C1231006815` | Entity key used for customer profiling, transaction frequency, and risk scoring. |
| `oldbalanceOrg` | `float64` | Originating account balance immediately before the transaction occurred. | `170136.00` | Baseline balance feature used to calculate account drain and financial feasibility. |
| `newbalanceOrig` | `float64` | Originating account balance immediately after the transaction completed. | `160296.36`, `0.00` | Post-transaction balance; key indicator for complete account balance liquidation. |
| `nameDest` | `object` (string) | Unique identifier of the recipient account (Customer `C...` or Merchant `M...`). | `M1979787155`, `C553264065` | Destination entity key for mule account analysis and merchant category detection. |
| `oldbalanceDest` | `float64` | Recipient account balance immediately before the transaction occurred. | `0.00`, `21182.00` | Baseline recipient balance; identifies unseeded destination accounts. |
| `newbalanceDest` | `float64` | Recipient account balance immediately after the transaction completed. | `0.00`, `79866.00` | Post-transaction recipient balance; used to identify rapid cash-out and mule routing. |
| `isFraud` | `int64` | Ground truth fraud indicator (1 = Confirmed Fraudulent Transaction, 0 = Legitimate). | `0`, `1` | Primary supervised learning target variable for detection and classification models. |
| `isFlaggedFraud` | `int64` | Simulation heuristic flag marking illegal attempts to transfer > 200,000 in a single operation. | `0`, `1` | Heuristic baseline rule indicator for comparison against advanced ML detection. |
