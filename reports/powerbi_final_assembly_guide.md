# FraudLens — Final Power BI Desktop Assembly Guide

## Purpose and scope

This guide turns the prepared FraudLens assets into the real, viewable seven-page Power BI report. It intentionally does **not** use `powerbi/FraudLens_Analytics_Platform.pbix`: that package is a small scaffold containing empty report pages, not the finished dashboard.

Use the prepared summaries and the forensic extract only. Do not load `transactions_clean.parquet`, `transactions_analytical.parquet`, or any other 6.36 million-row raw transaction source.

## Inputs and expected result

Open the project file:

`D:\financial_Analytics\FraudLens.pbip`

The report must connect to the sibling dataset project at `D:\financial_Analytics\FraudLens.Dataset`. Save the completed report as:

`D:\financial_Analytics\FraudLens_Analytics_Platform.pbix`

The required source assets are:

| Asset | Use |
| --- | --- |
| `powerbi/power_query_importers.m` | Thirteen typed CSV-import queries; each numbered `let … in` block is one query. |
| `powerbi/model.bim` | Tabular model table/partition and relationship reference. |
| `powerbi/powerbi_model_schema.json` | Human-readable authoritative model map. |
| `powerbi/dax_measures.dax` | DAX measure definitions and intended formats. |
| `powerbi/visual_specifications_detailed.md` | Visual geometry, colors, field bindings, values, and narrative copy. |
| `data/processed/powerbi/*.csv` | The 13 prepared inputs. |

## 1. Open and import the prepared tables

1. Start Power BI Desktop (the installed version is 2.156.951.0 or later) and choose **File > Open report**. Open `D:\financial_Analytics\FraudLens.pbip`.
2. If the dataset reference cannot be resolved, open `D:\financial_Analytics\FraudLens.Report\definition.pbir` and verify its relative path remains `../FraudLens.Dataset`; keep the three project folders together.
3. Choose **Transform data > New source > Blank query > Advanced Editor**. Create each query listed below. Paste **only** the corresponding numbered `let … in` block from `powerbi/power_query_importers.m`, name the query exactly as shown, and leave load enabled.
4. In Power Query, verify every query shows its expected row count before selecting **Close & Apply**. The import path is already absolute: `D:\financial_Analytics\data\processed\powerbi\`. If the project is moved, replace that directory consistently in all 13 source expressions.

| # | Query name | Expected rows |
| ---: | --- | ---: |
| 1 | `DimTransactionType` | 5 |
| 2 | `DimTime` | 743 |
| 3 | `DimRiskTier` | 4 |
| 4 | `Summary_Channel_KPIs` | 5 |
| 5 | `Summary_Hourly_Temporal` | 2,729 |
| 6 | `Summary_Amount_Bands` | 6 |
| 7 | `Summary_Account_Risk` | 4 |
| 8 | `FactFraudInvestigation_Extract` | 20,865 |
| 9 | `Summary_ML_Model_Comparison` | 3 |
| 10 | `Summary_ML_Confusion_Matrices` | 12 |
| 11 | `Summary_ML_Feature_Importance` | 60 |
| 12 | `Summary_ML_Threshold_Curves` | 27 |
| 13 | `Summary_Data_Quality` | 10 |

The three `Dim*` queries are dimensions; `FactFraudInvestigation_Extract` is the only detail fact. All other `Summary_*` tables are deliberately small aggregate/reference tables.

## 2. Configure and validate the model

Use Model view. Confirm these are the **only** active relationships. Every relationship is `*:1`, single direction, with the dimension on the `1` side. Do not enable bidirectional filtering.

| Fact/summary column | Dimension column |
| --- | --- |
| `Summary_Channel_KPIs[transaction_type]` | `DimTransactionType[transaction_type]` |
| `Summary_Hourly_Temporal[step]` | `DimTime[step]` |
| `Summary_Hourly_Temporal[transaction_type]` | `DimTransactionType[transaction_type]` |
| `Summary_Account_Risk[risk_category]` | `DimRiskTier[risk_category]` |
| `FactFraudInvestigation_Extract[step]` | `DimTime[step]` |
| `FactFraudInvestigation_Extract[transaction_type]` | `DimTransactionType[transaction_type]` |
| `FactFraudInvestigation_Extract[risk_category]` | `DimRiskTier[risk_category]` |

There must be seven relationships, no inactive duplicates, no circular route, and no relationship from one summary table to another. Keep the supplied data types: money columns as Fixed decimal/Currency; IDs, counts, steps, hours, days and risk score as Whole number; rates, scores and model metrics as Decimal number; labels/accounts/categories as Text.

## 3. Load DAX measures

`powerbi/model.bim` defines table partitions and relationships; it does not contain the DAX library. In Data or Report view select `Summary_Channel_KPIs`, then choose **New measure**. For every declaration in `powerbi/dax_measures.dax`, paste its complete expression (from `Measure Name =` through the final expression), press Enter, and set the format written immediately below it in the source file. Use display folders exactly as the source comment headings: `01_Executive_KPIs`, `02_Fraud_Analytics`, `03_Financial_Analysis`, `04_Account_Risk`, `05_Fraud_Investigation`, `06_ML_Model_Evaluation`, and `07_Data_Governance`.

The measure library contains 60 declarations. Do not change a formula while loading it. The core executive measures to pin and reconcile first are:

`Total Transactions`; `Total Transacted Volume`; `Confirmed Fraud Incidents`; `Fraud-Labeled Exposure`; `Overall Fraud Rate`; `Origin Account Drainage Rate`; `Heuristic Flag Triggered Total`; `Heuristic Flag Recall`; `Random Forest PR-AUC`; `XGBoost PR-AUC`; `Cohen's d` is a fixed visual callout (2.1422), not a supplied DAX measure.

For the rate fields loaded directly from CSV, format `fraud_rate_pct`, `account_fraud_rate_pct`, `Precision`, `Recall`, `PR_AUC`, `ROC_AUC`, `relative_importance_pct`, `precision`, `recall`, and `f1_score` appropriately as percentages only where their stored scale is fractional. Verify after formatting; never multiply an already percentage-scaled source value.

## 4. Shared visual design and interactions

Set every page to 16:9 custom canvas, 1920 × 1080, background `#F8FAFC`, with a full-width header from Y=0–80. Use dark slate `#0F172A` for headers, blue `#2563EB` for normal volume/neutral series, crimson `#DC2626` only for fraud/risk emphasis, and the contained green/amber risk colors where indicated in the detailed specification. Use white visual containers, restrained borders, consistent titles, aligned margins, and no gradients except the optional area fill in Page 3.

Add page-navigation buttons for all seven pages. Use slicers and chart cross-filtering on their own analytic scope. For Executive Overview, edit interactions so channel/time slicers do not turn the macro baseline cards into misleading partial-portfolio totals. The Workbench slicers should filter its KPI cards and grid.

## 5. Build the seven pages

Use `powerbi/visual_specifications_detailed.md` as the placement source of truth. The bindings below are the required field wells; apply the specified titles, colors, labels and numerical callouts from that file.

### 1. Executive Overview

- Six cards: `[Total Transactions]`, `[Total Transacted Volume]`, `[Confirmed Fraud Incidents]`, `[Fraud-Labeled Exposure]`, `[Overall Fraud Rate]`, `[Origin Account Drainage Rate]`.
- Clustered column chart: Axis `Summary_Channel_KPIs[transaction_type]`; column values `total_volume_usd` and `fraud_exposure_usd`.
- Line chart: Axis `DimTime[transaction_day]`; values `[Daily Fraud Exposure]` and `[7-Day Rolling Avg Daily Fraud Exposure]`.
- Column chart: Axis `Summary_Amount_Bands[amount_band]`; values `fraud_exposure_usd` and `fraud_transactions`.
- Matrix: rows `Summary_Channel_KPIs[transaction_type]`; values `true_positives`, `false_positives`, `false_negatives`, `true_negatives`.
- Narrative callout must say exactly: **Legacy heuristic recall = 0.1948%; approximately 99.8052% of fraud-labeled transactions were not detected.** It must not describe this as an exposure miss rate.

### 2. Fraud Analytics

- Cards: `[Confirmed Fraud Incidents]`, `[Overall Fraud Rate]`, `[Fraud-Labeled Exposure]`, `[Average Fraud Amount]`, `[Average Legitimate Amount]`; show the severity ratio `[Fraud Severity Ratio]` in the ticket-size card/callout.
- Clustered bar: Axis `Summary_Channel_KPIs[transaction_type]`; value `fraud_rate_pct`; filter to TRANSFER and CASH_OUT.
- Line/column combo: Axis `DimTime[transaction_hour]`; columns `Summary_Hourly_Temporal[total_volume_usd]`; line `fraud_transactions` and/or `fraud_exposure_usd` as specified.
- Distribution comparison: use `FactFraudInvestigation_Extract[amount]` with `is_fraud` as legend (or a supported box-plot visual); label it fraud versus legitimate.
- Static statistical callout: `Cohen's d = 2.1422` and `p < 10^-15`.

### 3. Financial & Transaction Analysis

- Cards: `[Total Transacted Volume]`, `[Fraud-Labeled Exposure]`, `[Fraud Exposure Share Pct]`, `[Average Transaction Size]`.
- Donut: legend `Summary_Channel_KPIs[transaction_type]`, values `total_volume_usd`.
- Area chart: axis `DimTime[step]`, value `[Cumulative Fraud Exposure]`.
- Line/clustered-column chart: axis `DimTime[transaction_day]`; columns `[Daily Total Volume]`; line `[Daily Fraud Exposure]`.
- Clustered bar: axis `Summary_Amount_Bands[amount_band]`; values `total_volume_usd` and `fraud_exposure_usd`.

### 4. Account Risk & Behavioral Prioritization

- Cards: `[Critical Risk Accounts]`, `[High Risk Accounts]`, `[Medium Risk Accounts]`, `[Low Risk Accounts]`, `[Critical Tier Fraud Capture Share]`.
- Donut: legend `Summary_Account_Risk[risk_category]`, values `total_accounts`; apply Critical `#DC2626`, High `#EA580C`, Medium `#F59E0B`, Low `#10B981`.
- Column chart: axis `risk_category`, values `account_fraud_rate_pct`.
- Drainage donut: use a two-value helper/category visual showing drained 8,012 / 97.55% and non-zero 201 / 2.45%; source the headline from `[Origin Account Drainage Count]` and `[Origin Account Drainage Rate]`.
- Matrix: `DimRiskTier[risk_category]`, `score_min`, `score_max`, `sla_tier`, `action_code`, plus `Summary_Account_Risk[total_accounts]` and `fraud_associated_accounts`.

### 5. Fraud Investigation Workbench

- Use only `FactFraudInvestigation_Extract`. Add slicers for `transaction_type`, `is_fraud`, `risk_category`, numeric range `amount`, numeric range `risk_score`, and searchable `origin_account` and `dest_account`.
- Cards: `[Investigation Candidate Count]`, `[Confirmed Fraud Candidate Count]`, `[Candidate Fraud Exposure]`, `[Candidate Average Amount]`.
- Full-width table fields: `transaction_id`, `step`, `transaction_type`, `amount`, `origin_account`, `dest_account`, `orig_old_balance`, `orig_new_balance`, `dest_old_balance`, `dest_new_balance`, `orig_balance_error`, `dest_balance_error`, `is_drainage`, `risk_score`, `risk_category`, `investigation_typology`, `is_fraud`.
- Apply currency formatting to financial fields; conditional bars to `risk_score`; red/green conditional formatting to `is_fraud`. Before saving, filter `is_fraud = 1` and confirm the grid count is 8,213.

### 6. Machine Learning Model Analysis

- Banner text: **Evaluated strictly on the held-out PaySim synthetic test partition: N = 1,272,524; fraud count = 1,643. Metrics do not claim production deployment readiness on live banking rails.**
- Table fields from `Summary_ML_Model_Comparison`: `Model`, `Precision`, `Recall`, `F1_Score`, `PR_AUC`, `ROC_AUC`, `True_Positives`, `False_Positives`, `False_Negatives`, `True_Negatives`, with Random Forest, XGBoost, and Logistic Regression shown.
- Confusion-matrix matrix: rows `Actual_Class`, columns `Predicted_Class`, values `Count`; slicers `Model` and `Threshold_Type` from `Summary_ML_Confusion_Matrices`.
- Horizontal bar: axis `feature`, value `relative_importance_pct`, filter `model_type = XGBoost`, sort descending.
- Line chart: axis `threshold`, values `precision`, `recall`, `f1_score`; filter `model_type = XGBoost`; pair with `alert_count`/`false_positives` callout.

### 7. Data Quality, Architecture & Governance

- Audit table: `Category`, `Quality_Check`, `Expected_Value`, `Observed_Value`, `Status` from `Summary_Data_Quality`.
- Heuristic matrix/card values: `[Heuristic Flag Triggered Total]`, `[Heuristic Flag TP]`, `[Heuristic Flag FP]`, `[Heuristic Flag FN]`, `[Heuristic Flag TN]`, `[Heuristic Flag Precision]`, `[Heuristic Flag Recall]`.
- Include the platform flow diagram and governance notes from the Page 7 section of `powerbi/visual_specifications_detailed.md`.
- Include this disclaimer verbatim in substance: **PaySim is a synthetic mobile-money topology. Fraud-labeled exposure is gross flagged transaction value and must not automatically be interpreted as recovered funds or actual financial loss.**

## 6. KPI reconciliation checklist

After **Refresh**, place the following measures/values in a temporary validation table or cards and compare against this exact baseline. Do not save a result with a non-zero variance unless its cause is documented in the report.

| KPI | Expected |
| --- | ---: |
| Total Transactions | 6,362,620 |
| Total Transaction Volume | $1,144,392,944,759.77 |
| Confirmed Fraud Incidents | 8,213 |
| Fraud-Labeled Exposure | $12,056,415,427.84 |
| Overall Fraud Rate | 0.1291% |
| Origin Account Drainage Rate | 97.55% |
| Heuristic Alerts | 16 |
| Heuristic Recall | 0.1948% |
| ML Holdout Set | 1,272,524 |
| ML Holdout Fraud Count | 1,643 |
| Cohen's d | 2.1422 |

Also validate the Workbench: 20,865 default candidates; 8,213 after fraud filter. Verify 13 loaded tables, seven active relationships, no ambiguous/circular routes, and all seven pages.

## 7. Visual QA and final save

1. On each page, use **View > Actual size** and inspect all visuals for clipped labels, overlaps, blank visuals, unreadable tables, wrong legends, or unexpected filter context.
2. Exercise every slicer, reset it, and confirm the intended cards/charts respond while protected macro KPIs remain stable on the Executive page.
3. Confirm page navigation works in Reading view.
4. Optionally export the complete report to PDF and inspect all seven pages at full page size. This is the required visual QA evidence when Desktop access is available.
5. Select **File > Save As**, choose `D:\financial_Analytics\FraudLens_Analytics_Platform.pbix`, then close and reopen that exact file. Confirm seven populated pages, 13 tables and the reconciled KPI values remain available.

The final PBIX is genuine only after this Power BI Desktop save-and-reopen check succeeds.
