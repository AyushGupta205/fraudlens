"""
FraudLens — Phase 5: Power BI Automated Validation Tests
Tests the data integrity, star-schema staging tables, reconciliation against SQL ground truth,
ML evaluation staging, and documentation completeness for the 7-page Power BI dashboard.
"""

import os
import pytest
import pandas as pd
import numpy as np

POWERBI_DIR = "data/processed/powerbi"
REPORTS_DIR = "reports"
DOCS_DIR = "powerbi"


def test_1_powerbi_export_files_exist():
    """Verifies that all 13 Power BI star schema staging datasets exist and are non-empty."""
    expected_files = [
        "DimTransactionType.csv",
        "DimTime.csv",
        "DimRiskTier.csv",
        "Summary_Channel_KPIs.csv",
        "Summary_Hourly_Temporal.csv",
        "Summary_Amount_Bands.csv",
        "Summary_Account_Risk.csv",
        "FactFraudInvestigation_Extract.csv",
        "Summary_ML_Model_Comparison.csv",
        "Summary_ML_Confusion_Matrices.csv",
        "Summary_ML_Feature_Importance.csv",
        "Summary_ML_Threshold_Curves.csv",
        "Summary_Data_Quality.csv"
    ]
    for filename in expected_files:
        path = os.path.join(POWERBI_DIR, filename)
        assert os.path.exists(path), f"Missing Power BI export file: {path}"
        assert os.path.getsize(path) > 0, f"Export file is empty: {path}"


def test_2_summary_channel_kpis_reconciliation():
    """Verifies that Summary_Channel_KPIs reconciles 100% with Phase 4 SQL ground truth."""
    path = os.path.join(POWERBI_DIR, "Summary_Channel_KPIs.csv")
    df = pd.read_csv(path)
    
    total_tx = df["total_transactions"].sum()
    total_vol = df["total_volume_usd"].sum()
    total_fraud = df["fraud_transactions"].sum()
    total_exposure = df["fraud_exposure_usd"].sum()
    overall_fraud_rate = total_fraud / total_tx * 100

    assert total_tx == 6362620, f"Total transactions mismatch: {total_tx}"
    assert total_fraud == 8213, f"Fraud transactions mismatch: {total_fraud}"
    assert abs(overall_fraud_rate - 0.129082) < 0.001, f"Fraud rate mismatch: {overall_fraud_rate}"
    assert abs(total_vol - 1144392944759.77) < 1.0, f"Total volume mismatch: {total_vol}"
    assert abs(total_exposure - 12056415427.84) < 1.0, f"Fraud exposure mismatch: {total_exposure}"


def test_3_transaction_type_channel_reconciliation():
    """Verifies that channel transaction counts and fraud incidents match Phase 4 SQL exact figures."""
    path = os.path.join(POWERBI_DIR, "Summary_Channel_KPIs.csv")
    df = pd.read_csv(path).set_index("transaction_type")
    
    assert df.loc["TRANSFER", "total_transactions"] == 532909
    assert df.loc["TRANSFER", "fraud_transactions"] == 4097
    assert df.loc["CASH_OUT", "total_transactions"] == 2237500
    assert df.loc["CASH_OUT", "fraud_transactions"] == 4116
    assert df.loc["PAYMENT", "total_transactions"] == 2151495
    assert df.loc["PAYMENT", "fraud_transactions"] == 0
    assert df.loc["CASH_IN", "total_transactions"] == 1399284
    assert df.loc["CASH_IN", "fraud_transactions"] == 0
    assert df.loc["DEBIT", "total_transactions"] == 41432
    assert df.loc["DEBIT", "fraud_transactions"] == 0


def test_4_heuristic_flagged_fraud_confusion_matrix():
    """Verifies that isFlaggedFraud confusion matrix metrics match Phase 4 exactly."""
    path = os.path.join(POWERBI_DIR, "Summary_Channel_KPIs.csv")
    df = pd.read_csv(path)
    
    tp = df["true_positives"].sum()
    fp = df["false_positives"].sum()
    fn = df["false_negatives"].sum()
    tn = df["true_negatives"].sum()
    
    assert tp == 16, f"TP mismatch: {tp}"
    assert fp == 0, f"FP mismatch: {fp}"
    assert fn == 8197, f"FN mismatch: {fn}"
    assert tn == 6354407, f"TN mismatch: {tn}"
    assert (tp + fp + fn + tn) == 6362620, "Confusion matrix sum does not equal total transactions"


def test_5_summary_amount_bands_reconciliation():
    """Verifies that Summary_Amount_Bands matches total transaction counts and exposure."""
    path = os.path.join(POWERBI_DIR, "Summary_Amount_Bands.csv")
    df = pd.read_csv(path)
    
    assert len(df) == 6, f"Expected 6 amount bands, got {len(df)}"
    assert df["total_transactions"].sum() == 6362620
    assert df["fraud_transactions"].sum() == 8213
    assert abs(df["fraud_exposure_usd"].sum() - 12056415427.84) < 1.0


def test_6_summary_account_risk_reconciliation():
    """Verifies that behavioral risk tiers in Summary_Account_Risk match Phase 4 SQL numbers."""
    path = os.path.join(POWERBI_DIR, "Summary_Account_Risk.csv")
    df = pd.read_csv(path).set_index("risk_category")
    
    assert len(df) == 4, f"Expected 4 risk categories, got {len(df)}"
    assert df["total_accounts"].sum() == 6362620
    assert df["fraud_associated_accounts"].sum() == 8213
    assert df.loc["Critical", "total_accounts"] == 67252
    assert df.loc["Critical", "fraud_associated_accounts"] == 4334
    assert df.loc["High", "total_accounts"] == 605922
    assert df.loc["High", "fraud_associated_accounts"] == 2890


def test_7_fact_fraud_investigation_extract_coverage():
    """Verifies that FactFraudInvestigation_Extract.csv contains 100% of confirmed fraud transactions."""
    path = os.path.join(POWERBI_DIR, "FactFraudInvestigation_Extract.csv")
    df = pd.read_csv(path)
    
    fraud_count = df["is_fraud"].sum()
    assert fraud_count == 8213, f"Investigation extract missing frauds: found {fraud_count} / 8213"
    assert "transaction_id" in df.columns
    assert "amount" in df.columns
    assert "risk_score" in df.columns
    assert "risk_category" in df.columns
    assert "is_drainage" in df.columns


def test_8_dimension_tables_integrity():
    """Verifies that dimension tables are properly formatted and populated."""
    dim_type = pd.read_csv(os.path.join(POWERBI_DIR, "DimTransactionType.csv"))
    assert len(dim_type) == 5
    assert set(dim_type["transaction_type"]) == {"TRANSFER", "CASH_OUT", "PAYMENT", "CASH_IN", "DEBIT"}

    dim_time = pd.read_csv(os.path.join(POWERBI_DIR, "DimTime.csv"))
    assert len(dim_time) == 743
    assert dim_time["step"].min() == 1
    assert dim_time["step"].max() == 743

    dim_risk = pd.read_csv(os.path.join(POWERBI_DIR, "DimRiskTier.csv"))
    assert len(dim_risk) == 4
    assert set(dim_risk["risk_category"]) == {"Critical", "High", "Medium", "Low"}


def test_9_documentation_files_exist():
    """Verifies that all Power BI documentation and design files exist and are populated."""
    docs = [
        os.path.join(DOCS_DIR, "data_dictionary.md"),
        os.path.join(DOCS_DIR, "dax_measures.md"),
        os.path.join(DOCS_DIR, "dashboard_design.md"),
        os.path.join(DOCS_DIR, "powerbi_model_schema.json"),
        os.path.join(REPORTS_DIR, "phase5_powerbi_validation.md"),
        os.path.join(REPORTS_DIR, "powerbi_dashboard_report.md"),
    ]
    for doc in docs:
        assert os.path.exists(doc), f"Missing documentation file: {doc}"
        assert os.path.getsize(doc) > 100, f"Documentation file too small: {doc}"


def test_10_ml_summary_staging_reconciliation():
    """Verifies that ML summary tables in Power BI staging match Phase 7 ground truth."""
    comp_path = os.path.join(POWERBI_DIR, "Summary_ML_Model_Comparison.csv")
    df_comp = pd.read_csv(comp_path).set_index("Model")
    assert len(df_comp) == 3
    assert abs(df_comp.loc["RandomForest", "Precision"] - 0.9988) < 1e-3
    assert abs(df_comp.loc["RandomForest", "Recall"] - 0.9976) < 1e-3
    assert abs(df_comp.loc["RandomForest", "F1_Score"] - 0.9982) < 1e-3
    assert abs(df_comp.loc["XGBoost", "PR_AUC"] - 0.9987) < 1e-3

    cm_path = os.path.join(POWERBI_DIR, "Summary_ML_Confusion_Matrices.csv")
    df_cm = pd.read_csv(cm_path)
    assert len(df_cm) == 12

    feat_path = os.path.join(POWERBI_DIR, "Summary_ML_Feature_Importance.csv")
    df_feat = pd.read_csv(feat_path)
    assert len(df_feat) >= 8


def test_11_data_quality_staging_integrity():
    """Verifies that Summary_Data_Quality.csv contains passing validation checks."""
    dq_path = os.path.join(POWERBI_DIR, "Summary_Data_Quality.csv")
    df_dq = pd.read_csv(dq_path)
    assert len(df_dq) == 10
    assert (df_dq["Status"].str.startswith("PASS")).all()
