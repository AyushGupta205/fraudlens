// ============================================================================
// FraudLens — Power BI Power Query (M) Automated Import Scripts
// Project Root: D:\financial_Analytics\data\processed\powerbi
// All 13 Staging Tables with Strictly Enforced Data Types and Column Headers
// ============================================================================

// ----------------------------------------------------------------------------
// Shared Base Path Parameter (Adjust if project folder moves)
// ----------------------------------------------------------------------------
let
    DataDirectory = "D:\financial_Analytics\data\processed\powerbi\"
in
    DataDirectory

// ----------------------------------------------------------------------------
// 1. DimTransactionType (5 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\DimTransactionType.csv"), [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"transaction_type", type text},
        {"channel_category", type text},
        {"is_fraud_eligible", Int64.Type},
        {"inherent_risk_rating", type text}
    })
in
    ChangeTypes

// ----------------------------------------------------------------------------
// 2. DimTime (743 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\DimTime.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"step", Int64.Type},
        {"transaction_hour", Int64.Type},
        {"transaction_day", Int64.Type},
        {"time_of_day_bracket", type text},
        {"is_business_hours", Int64.Type}
    })
in
    ChangeTypes

// ----------------------------------------------------------------------------
// 3. DimRiskTier (4 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\DimRiskTier.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"risk_category", type text},
        {"score_min", Int64.Type},
        {"score_max", Int64.Type},
        {"sla_tier", type text},
        {"action_code", type text}
    })
in
    ChangeTypes

// ----------------------------------------------------------------------------
// 4. Summary_Channel_KPIs (5 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\Summary_Channel_KPIs.csv"), [Delimiter=",", Columns=16, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"transaction_type", type text},
        {"total_transactions", Int64.Type},
        {"total_volume_usd", Currency.Type},
        {"avg_transaction_amount", Currency.Type},
        {"fraud_transactions", Int64.Type},
        {"fraud_exposure_usd", Currency.Type},
        {"fraud_rate_pct", type number},
        {"legitimate_transactions", Int64.Type},
        {"legitimate_volume_usd", Currency.Type},
        {"avg_fraud_amount", Currency.Type},
        {"avg_legitimate_amount", Currency.Type},
        {"flagged_fraud_count", Int64.Type},
        {"true_positives", Int64.Type},
        {"false_positives", Int64.Type},
        {"false_negatives", Int64.Type},
        {"true_negatives", Int64.Type}
    })
in
    ChangeTypes

// ----------------------------------------------------------------------------
// 5. Summary_Hourly_Temporal (2,729 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\Summary_Hourly_Temporal.csv"), [Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"step", Int64.Type},
        {"transaction_hour", Int64.Type},
        {"transaction_day", Int64.Type},
        {"transaction_type", type text},
        {"total_transactions", Int64.Type},
        {"total_volume_usd", Currency.Type},
        {"fraud_transactions", Int64.Type},
        {"fraud_exposure_usd", Currency.Type}
    })
in
    ChangeTypes

// ----------------------------------------------------------------------------
// 6. Summary_Amount_Bands (6 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\Summary_Amount_Bands.csv"), [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"amount_band", type text},
        {"total_transactions", Int64.Type},
        {"total_volume_usd", Currency.Type},
        {"fraud_transactions", Int64.Type},
        {"fraud_exposure_usd", Currency.Type},
        {"fraud_rate_pct", type number}
    })
in
    ChangeTypes

// ----------------------------------------------------------------------------
// 7. Summary_Account_Risk (4 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\Summary_Account_Risk.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"risk_category", type text},
        {"total_accounts", Int64.Type},
        {"fraud_associated_accounts", Int64.Type},
        {"account_fraud_rate_pct", type number},
        {"total_volume_usd", Currency.Type}
    })
in
    ChangeTypes

// ----------------------------------------------------------------------------
// 8. FactFraudInvestigation_Extract (20,865 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\FactFraudInvestigation_Extract.csv"), [Delimiter=",", Columns=21, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"transaction_id", Int64.Type},
        {"step", Int64.Type},
        {"transaction_type", type text},
        {"amount", Currency.Type},
        {"origin_account", type text},
        {"orig_old_balance", Currency.Type},
        {"orig_new_balance", Currency.Type},
        {"dest_account", type text},
        {"dest_old_balance", Currency.Type},
        {"dest_new_balance", Currency.Type},
        {"is_fraud", Int64.Type},
        {"is_flagged_fraud", Int64.Type},
        {"transaction_hour", Int64.Type},
        {"transaction_day", Int64.Type},
        {"orig_balance_error", Currency.Type},
        {"dest_balance_error", Currency.Type},
        {"amount_band", type text},
        {"is_drainage", Int64.Type},
        {"risk_score", Int64.Type},
        {"risk_category", type text},
        {"investigation_typology", type text}
    })
in
    ChangeTypes

// ----------------------------------------------------------------------------
// 9. Summary_ML_Model_Comparison (3 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\Summary_ML_Model_Comparison.csv"), [Delimiter=",", Columns=19, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"Model", type text},
        {"Threshold", type number},
        {"Precision", type number},
        {"Recall", type number},
        {"F1_Score", type number},
        {"ROC_AUC", type number},
        {"PR_AUC", type number},
        {"True_Positives", Int64.Type},
        {"False_Positives", Int64.Type},
        {"False_Negatives", Int64.Type},
        {"True_Negatives", Int64.Type},
        {"Tuned_Threshold", type number},
        {"Tuned_Precision", type number},
        {"Tuned_Recall", type number},
        {"Tuned_F1_Score", type number},
        {"Tuned_TP", Int64.Type},
        {"Tuned_FP", Int64.Type},
        {"Tuned_FN", Int64.Type},
        {"Tuned_TN", Int64.Type}
    })
in
    ChangeTypes

// ----------------------------------------------------------------------------
// 10. Summary_ML_Confusion_Matrices (12 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\Summary_ML_Confusion_Matrices.csv"), [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"Model", type text},
        {"Threshold_Type", type text},
        {"Actual_Class", type text},
        {"Predicted_Class", type text},
        {"Count", Int64.Type},
        {"Metric_Type", type text}
    })
in
    ChangeTypes

// ----------------------------------------------------------------------------
// 11. Summary_ML_Feature_Importance (60 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\Summary_ML_Feature_Importance.csv"), [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"feature", type text},
        {"importance_score", type number},
        {"relative_importance_pct", type number},
        {"rank", Int64.Type},
        {"model_type", type text},
        {"coefficient", type number},
        {"odds_ratio", type number}
    })
in
    ChangeTypes

// ----------------------------------------------------------------------------
// 12. Summary_ML_Threshold_Curves (27 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\Summary_ML_Threshold_Curves.csv"), [Delimiter=",", Columns=13, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"threshold", type number},
        {"precision", type number},
        {"recall", type number},
        {"f1_score", type number},
        {"true_positives", Int64.Type},
        {"false_positives", Int64.Type},
        {"false_negatives", Int64.Type},
        {"true_negatives", Int64.Type},
        {"alert_count", Int64.Type},
        {"fraud_exposure_recall_pct", type number},
        {"flagged_fraud_exposure_usd", Currency.Type},
        {"false_alert_volume_usd", Currency.Type},
        {"model_type", type text}
    })
in
    ChangeTypes

// ----------------------------------------------------------------------------
// 13. Summary_Data_Quality (10 rows)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(File.Contents("D:\financial_Analytics\data\processed\powerbi\Summary_Data_Quality.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"Quality_Check", type text},
        {"Expected_Value", type text},
        {"Observed_Value", type text},
        {"Status", type text},
        {"Category", type text}
    })
in
    ChangeTypes
