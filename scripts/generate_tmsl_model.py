"""
Generate valid Tabular Model Schema (TMSL) model.bim for Power BI Desktop PBIP
"""

import json
import os
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POWERBI_DIR = os.path.join(ROOT_DIR, "powerbi")
CSV_DIR = os.path.join(ROOT_DIR, "data", "processed", "powerbi").replace('\\', '\\\\')

tables_def = [
    {
        "name": "DimTransactionType",
        "csv": "DimTransactionType.csv",
        "columns": [
            {"name": "transaction_type", "dataType": "string", "sourceColumn": "transaction_type"},
            {"name": "channel_category", "dataType": "string", "sourceColumn": "channel_category"},
            {"name": "is_fraud_eligible", "dataType": "int64", "sourceColumn": "is_fraud_eligible"},
            {"name": "inherent_risk_rating", "dataType": "string", "sourceColumn": "inherent_risk_rating"}
        ],
        "types_m": '{"transaction_type", type text}, {"channel_category", type text}, {"is_fraud_eligible", Int64.Type}, {"inherent_risk_rating", type text}'
    },
    {
        "name": "DimTime",
        "csv": "DimTime.csv",
        "columns": [
            {"name": "step", "dataType": "int64", "sourceColumn": "step"},
            {"name": "transaction_hour", "dataType": "int64", "sourceColumn": "transaction_hour"},
            {"name": "transaction_day", "dataType": "int64", "sourceColumn": "transaction_day"},
            {"name": "time_of_day_bracket", "dataType": "string", "sourceColumn": "time_of_day_bracket"},
            {"name": "is_business_hours", "dataType": "int64", "sourceColumn": "is_business_hours"}
        ],
        "types_m": '{"step", Int64.Type}, {"transaction_hour", Int64.Type}, {"transaction_day", Int64.Type}, {"time_of_day_bracket", type text}, {"is_business_hours", Int64.Type}'
    },
    {
        "name": "DimRiskTier",
        "csv": "DimRiskTier.csv",
        "columns": [
            {"name": "risk_category", "dataType": "string", "sourceColumn": "risk_category"},
            {"name": "score_min", "dataType": "int64", "sourceColumn": "score_min"},
            {"name": "score_max", "dataType": "int64", "sourceColumn": "score_max"},
            {"name": "sla_tier", "dataType": "string", "sourceColumn": "sla_tier"},
            {"name": "action_code", "dataType": "string", "sourceColumn": "action_code"}
        ],
        "types_m": '{"risk_category", type text}, {"score_min", Int64.Type}, {"score_max", Int64.Type}, {"sla_tier", type text}, {"action_code", type text}'
    },
    {
        "name": "Summary_Channel_KPIs",
        "csv": "Summary_Channel_KPIs.csv",
        "columns": [
            {"name": "transaction_type", "dataType": "string", "sourceColumn": "transaction_type"},
            {"name": "total_transactions", "dataType": "int64", "sourceColumn": "total_transactions"},
            {"name": "total_volume_usd", "dataType": "double", "sourceColumn": "total_volume_usd"},
            {"name": "avg_transaction_amount", "dataType": "double", "sourceColumn": "avg_transaction_amount"},
            {"name": "fraud_transactions", "dataType": "int64", "sourceColumn": "fraud_transactions"},
            {"name": "fraud_exposure_usd", "dataType": "double", "sourceColumn": "fraud_exposure_usd"},
            {"name": "fraud_rate_pct", "dataType": "double", "sourceColumn": "fraud_rate_pct"},
            {"name": "legitimate_transactions", "dataType": "int64", "sourceColumn": "legitimate_transactions"},
            {"name": "legitimate_volume_usd", "dataType": "double", "sourceColumn": "legitimate_volume_usd"},
            {"name": "avg_fraud_amount", "dataType": "double", "sourceColumn": "avg_fraud_amount"},
            {"name": "avg_legitimate_amount", "dataType": "double", "sourceColumn": "avg_legitimate_amount"},
            {"name": "flagged_fraud_count", "dataType": "int64", "sourceColumn": "flagged_fraud_count"},
            {"name": "true_positives", "dataType": "int64", "sourceColumn": "true_positives"},
            {"name": "false_positives", "dataType": "int64", "sourceColumn": "false_positives"},
            {"name": "false_negatives", "dataType": "int64", "sourceColumn": "false_negatives"},
            {"name": "true_negatives", "dataType": "int64", "sourceColumn": "true_negatives"}
        ],
        "types_m": '{"transaction_type", type text}, {"total_transactions", Int64.Type}, {"total_volume_usd", Currency.Type}, {"avg_transaction_amount", Currency.Type}, {"fraud_transactions", Int64.Type}, {"fraud_exposure_usd", Currency.Type}, {"fraud_rate_pct", type number}, {"legitimate_transactions", Int64.Type}, {"legitimate_volume_usd", Currency.Type}, {"avg_fraud_amount", Currency.Type}, {"avg_legitimate_amount", Currency.Type}, {"flagged_fraud_count", Int64.Type}, {"true_positives", Int64.Type}, {"false_positives", Int64.Type}, {"false_negatives", Int64.Type}, {"true_negatives", Int64.Type}'
    },
    {
        "name": "Summary_Hourly_Temporal",
        "csv": "Summary_Hourly_Temporal.csv",
        "columns": [
            {"name": "step", "dataType": "int64", "sourceColumn": "step"},
            {"name": "transaction_hour", "dataType": "int64", "sourceColumn": "transaction_hour"},
            {"name": "transaction_day", "dataType": "int64", "sourceColumn": "transaction_day"},
            {"name": "transaction_type", "dataType": "string", "sourceColumn": "transaction_type"},
            {"name": "total_transactions", "dataType": "int64", "sourceColumn": "total_transactions"},
            {"name": "total_volume_usd", "dataType": "double", "sourceColumn": "total_volume_usd"},
            {"name": "fraud_transactions", "dataType": "int64", "sourceColumn": "fraud_transactions"},
            {"name": "fraud_exposure_usd", "dataType": "double", "sourceColumn": "fraud_exposure_usd"}
        ],
        "types_m": '{"step", Int64.Type}, {"transaction_hour", Int64.Type}, {"transaction_day", Int64.Type}, {"transaction_type", type text}, {"total_transactions", Int64.Type}, {"total_volume_usd", Currency.Type}, {"fraud_transactions", Int64.Type}, {"fraud_exposure_usd", Currency.Type}'
    },
    {
        "name": "Summary_Amount_Bands",
        "csv": "Summary_Amount_Bands.csv",
        "columns": [
            {"name": "amount_band", "dataType": "string", "sourceColumn": "amount_band"},
            {"name": "total_transactions", "dataType": "int64", "sourceColumn": "total_transactions"},
            {"name": "total_volume_usd", "dataType": "double", "sourceColumn": "total_volume_usd"},
            {"name": "fraud_transactions", "dataType": "int64", "sourceColumn": "fraud_transactions"},
            {"name": "fraud_exposure_usd", "dataType": "double", "sourceColumn": "fraud_exposure_usd"},
            {"name": "fraud_rate_pct", "dataType": "double", "sourceColumn": "fraud_rate_pct"}
        ],
        "types_m": '{"amount_band", type text}, {"total_transactions", Int64.Type}, {"total_volume_usd", Currency.Type}, {"fraud_transactions", Int64.Type}, {"fraud_exposure_usd", Currency.Type}, {"fraud_rate_pct", type number}'
    },
    {
        "name": "Summary_Account_Risk",
        "csv": "Summary_Account_Risk.csv",
        "columns": [
            {"name": "risk_category", "dataType": "string", "sourceColumn": "risk_category"},
            {"name": "total_accounts", "dataType": "int64", "sourceColumn": "total_accounts"},
            {"name": "fraud_associated_accounts", "dataType": "int64", "sourceColumn": "fraud_associated_accounts"},
            {"name": "account_fraud_rate_pct", "dataType": "double", "sourceColumn": "account_fraud_rate_pct"},
            {"name": "total_volume_usd", "dataType": "double", "sourceColumn": "total_volume_usd"}
        ],
        "types_m": '{"risk_category", type text}, {"total_accounts", Int64.Type}, {"fraud_associated_accounts", Int64.Type}, {"account_fraud_rate_pct", type number}, {"total_volume_usd", Currency.Type}'
    },
    {
        "name": "FactFraudInvestigation_Extract",
        "csv": "FactFraudInvestigation_Extract.csv",
        "columns": [
            {"name": "transaction_id", "dataType": "int64", "sourceColumn": "transaction_id"},
            {"name": "step", "dataType": "int64", "sourceColumn": "step"},
            {"name": "transaction_type", "dataType": "string", "sourceColumn": "transaction_type"},
            {"name": "amount", "dataType": "double", "sourceColumn": "amount"},
            {"name": "origin_account", "dataType": "string", "sourceColumn": "origin_account"},
            {"name": "orig_old_balance", "dataType": "double", "sourceColumn": "orig_old_balance"},
            {"name": "orig_new_balance", "dataType": "double", "sourceColumn": "orig_new_balance"},
            {"name": "dest_account", "dataType": "string", "sourceColumn": "dest_account"},
            {"name": "dest_old_balance", "dataType": "double", "sourceColumn": "dest_old_balance"},
            {"name": "dest_new_balance", "dataType": "double", "sourceColumn": "dest_new_balance"},
            {"name": "is_fraud", "dataType": "int64", "sourceColumn": "is_fraud"},
            {"name": "is_flagged_fraud", "dataType": "int64", "sourceColumn": "is_flagged_fraud"},
            {"name": "transaction_hour", "dataType": "int64", "sourceColumn": "transaction_hour"},
            {"name": "transaction_day", "dataType": "int64", "sourceColumn": "transaction_day"},
            {"name": "orig_balance_error", "dataType": "double", "sourceColumn": "orig_balance_error"},
            {"name": "dest_balance_error", "dataType": "double", "sourceColumn": "dest_balance_error"},
            {"name": "amount_band", "dataType": "string", "sourceColumn": "amount_band"},
            {"name": "is_drainage", "dataType": "int64", "sourceColumn": "is_drainage"},
            {"name": "risk_score", "dataType": "int64", "sourceColumn": "risk_score"},
            {"name": "risk_category", "dataType": "string", "sourceColumn": "risk_category"},
            {"name": "investigation_typology", "dataType": "string", "sourceColumn": "investigation_typology"}
        ],
        "types_m": '{"transaction_id", Int64.Type}, {"step", Int64.Type}, {"transaction_type", type text}, {"amount", Currency.Type}, {"origin_account", type text}, {"orig_old_balance", Currency.Type}, {"orig_new_balance", Currency.Type}, {"dest_account", type text}, {"dest_old_balance", Currency.Type}, {"dest_new_balance", Currency.Type}, {"is_fraud", Int64.Type}, {"is_flagged_fraud", Int64.Type}, {"transaction_hour", Int64.Type}, {"transaction_day", Int64.Type}, {"orig_balance_error", Currency.Type}, {"dest_balance_error", Currency.Type}, {"amount_band", type text}, {"is_drainage", Int64.Type}, {"risk_score", Int64.Type}, {"risk_category", type text}, {"investigation_typology", type text}'
    },
    {
        "name": "Summary_ML_Model_Comparison",
        "csv": "Summary_ML_Model_Comparison.csv",
        "columns": [
            {"name": "Model", "dataType": "string", "sourceColumn": "Model"},
            {"name": "Threshold", "dataType": "double", "sourceColumn": "Threshold"},
            {"name": "Precision", "dataType": "double", "sourceColumn": "Precision"},
            {"name": "Recall", "dataType": "double", "sourceColumn": "Recall"},
            {"name": "F1_Score", "dataType": "double", "sourceColumn": "F1_Score"},
            {"name": "ROC_AUC", "dataType": "double", "sourceColumn": "ROC_AUC"},
            {"name": "PR_AUC", "dataType": "double", "sourceColumn": "PR_AUC"},
            {"name": "True_Positives", "dataType": "int64", "sourceColumn": "True_Positives"},
            {"name": "False_Positives", "dataType": "int64", "sourceColumn": "False_Positives"},
            {"name": "False_Negatives", "dataType": "int64", "sourceColumn": "False_Negatives"},
            {"name": "True_Negatives", "dataType": "int64", "sourceColumn": "True_Negatives"},
            {"name": "Tuned_Threshold", "dataType": "double", "sourceColumn": "Tuned_Threshold"},
            {"name": "Tuned_Precision", "dataType": "double", "sourceColumn": "Tuned_Precision"},
            {"name": "Tuned_Recall", "dataType": "double", "sourceColumn": "Tuned_Recall"},
            {"name": "Tuned_F1_Score", "dataType": "double", "sourceColumn": "Tuned_F1_Score"},
            {"name": "Tuned_TP", "dataType": "int64", "sourceColumn": "Tuned_TP"},
            {"name": "Tuned_FP", "dataType": "int64", "sourceColumn": "Tuned_FP"},
            {"name": "Tuned_FN", "dataType": "int64", "sourceColumn": "Tuned_FN"},
            {"name": "Tuned_TN", "dataType": "int64", "sourceColumn": "Tuned_TN"}
        ],
        "types_m": '{"Model", type text}, {"Threshold", type number}, {"Precision", type number}, {"Recall", type number}, {"F1_Score", type number}, {"ROC_AUC", type number}, {"PR_AUC", type number}, {"True_Positives", Int64.Type}, {"False_Positives", Int64.Type}, {"False_Negatives", Int64.Type}, {"True_Negatives", Int64.Type}, {"Tuned_Threshold", type number}, {"Tuned_Precision", type number}, {"Tuned_Recall", type number}, {"Tuned_F1_Score", type number}, {"Tuned_TP", Int64.Type}, {"Tuned_FP", Int64.Type}, {"Tuned_FN", Int64.Type}, {"Tuned_TN", Int64.Type}'
    },
    {
        "name": "Summary_ML_Confusion_Matrices",
        "csv": "Summary_ML_Confusion_Matrices.csv",
        "columns": [
            {"name": "Model", "dataType": "string", "sourceColumn": "Model"},
            {"name": "Threshold_Type", "dataType": "string", "sourceColumn": "Threshold_Type"},
            {"name": "Actual_Class", "dataType": "string", "sourceColumn": "Actual_Class"},
            {"name": "Predicted_Class", "dataType": "string", "sourceColumn": "Predicted_Class"},
            {"name": "Count", "dataType": "int64", "sourceColumn": "Count"},
            {"name": "Metric_Type", "dataType": "string", "sourceColumn": "Metric_Type"}
        ],
        "types_m": '{"Model", type text}, {"Threshold_Type", type text}, {"Actual_Class", type text}, {"Predicted_Class", type text}, {"Count", Int64.Type}, {"Metric_Type", type text}'
    },
    {
        "name": "Summary_ML_Feature_Importance",
        "csv": "Summary_ML_Feature_Importance.csv",
        "columns": [
            {"name": "feature", "dataType": "string", "sourceColumn": "feature"},
            {"name": "importance_score", "dataType": "double", "sourceColumn": "importance_score"},
            {"name": "relative_importance_pct", "dataType": "double", "sourceColumn": "relative_importance_pct"},
            {"name": "rank", "dataType": "int64", "sourceColumn": "rank"},
            {"name": "model_type", "dataType": "string", "sourceColumn": "model_type"},
            {"name": "coefficient", "dataType": "double", "sourceColumn": "coefficient"},
            {"name": "odds_ratio", "dataType": "double", "sourceColumn": "odds_ratio"}
        ],
        "types_m": '{"feature", type text}, {"importance_score", type number}, {"relative_importance_pct", type number}, {"rank", Int64.Type}, {"model_type", type text}, {"coefficient", type number}, {"odds_ratio", type number}'
    },
    {
        "name": "Summary_ML_Threshold_Curves",
        "csv": "Summary_ML_Threshold_Curves.csv",
        "columns": [
            {"name": "threshold", "dataType": "double", "sourceColumn": "threshold"},
            {"name": "precision", "dataType": "double", "sourceColumn": "precision"},
            {"name": "recall", "dataType": "double", "sourceColumn": "recall"},
            {"name": "f1_score", "dataType": "double", "sourceColumn": "f1_score"},
            {"name": "true_positives", "dataType": "int64", "sourceColumn": "true_positives"},
            {"name": "false_positives", "dataType": "int64", "sourceColumn": "false_positives"},
            {"name": "false_negatives", "dataType": "int64", "sourceColumn": "false_negatives"},
            {"name": "true_negatives", "dataType": "int64", "sourceColumn": "true_negatives"},
            {"name": "alert_count", "dataType": "int64", "sourceColumn": "alert_count"},
            {"name": "fraud_exposure_recall_pct", "dataType": "double", "sourceColumn": "fraud_exposure_recall_pct"},
            {"name": "flagged_fraud_exposure_usd", "dataType": "double", "sourceColumn": "flagged_fraud_exposure_usd"},
            {"name": "false_alert_volume_usd", "dataType": "double", "sourceColumn": "false_alert_volume_usd"},
            {"name": "model_type", "dataType": "string", "sourceColumn": "model_type"}
        ],
        "types_m": '{"threshold", type number}, {"precision", type number}, {"recall", type number}, {"f1_score", type number}, {"true_positives", Int64.Type}, {"false_positives", Int64.Type}, {"false_negatives", Int64.Type}, {"true_negatives", Int64.Type}, {"alert_count", Int64.Type}, {"fraud_exposure_recall_pct", type number}, {"flagged_fraud_exposure_usd", Currency.Type}, {"false_alert_volume_usd", Currency.Type}, {"model_type", type text}'
    },
    {
        "name": "Summary_Data_Quality",
        "csv": "Summary_Data_Quality.csv",
        "columns": [
            {"name": "Quality_Check", "dataType": "string", "sourceColumn": "Quality_Check"},
            {"name": "Expected_Value", "dataType": "string", "sourceColumn": "Expected_Value"},
            {"name": "Observed_Value", "dataType": "string", "sourceColumn": "Observed_Value"},
            {"name": "Status", "dataType": "string", "sourceColumn": "Status"},
            {"name": "Category", "dataType": "string", "sourceColumn": "Category"}
        ],
        "types_m": '{"Quality_Check", type text}, {"Expected_Value", type text}, {"Observed_Value", type text}, {"Status", type text}, {"Category", type text}'
    }
]

# Build TMSL tables
tmsl_tables = []
for t in tables_def:
    t_name = t["name"]
    t_csv = t["csv"]
    t_cols = t["columns"]
    types_str = t["types_m"]
    
    m_expr = [
        "let",
        f'    Source = Csv.Document(File.Contents("{CSV_DIR}\\\\{t_csv}"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),',
        "    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),",
        f"    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders, {{{types_str}}})",
        "in",
        "    ChangeTypes"
    ]
    
    table_obj = {
        "name": t_name,
        "columns": t_cols,
        "partitions": [
            {
                "name": f"{t_name}-Partition",
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": m_expr
                }
            }
        ]
    }
    tmsl_tables.append(table_obj)

# Load relationships from powerbi_model_schema.json
with open(os.path.join(POWERBI_DIR, "powerbi_model_schema.json"), "r") as f:
    schema = json.load(f)

tmsl_model = {
    "name": "FraudLens_PowerBI_Model",
    "compatibilityLevel": 1550,
    "model": {
        "culture": "en-US",
        "tables": tmsl_tables,
        "relationships": schema["relationships"]
    }
}

# Write out to powerbi/model.bim, FraudLens.Dataset/model.bim, powerbi/FraudLens.Dataset/model.bim
for path in [
    os.path.join(POWERBI_DIR, "model.bim"),
    os.path.join(ROOT_DIR, "FraudLens.Dataset", "model.bim"),
    os.path.join(POWERBI_DIR, "FraudLens.Dataset", "model.bim")
]:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tmsl_model, f, indent=2)
    print(f"Generated compliant TMSL model at: {path}")
