"""
FraudLens — Phase 8: Power BI Dashboard Automated Validation Tests
Tests the data staging integrity, star-schema relationships, DAX formulas,
KPI reconciliation, Power Query importer scripts, 7-page visual specifications,
report.json layout integrity, and standalone HTML preview validation.
"""

import os
import json
import zipfile
import pytest
import pandas as pd
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POWERBI_DIR = "data/processed/powerbi"
POWERBI_DOCS = "powerbi"
REPORTS_DIR = "reports"


def test_1_all_13_staging_tables_exist_and_non_empty():
    """Verify all 13 CSV staging tables exist and contain required minimum rows."""
    expected_tables = {
        "DimTransactionType.csv": 5,
        "DimTime.csv": 743,
        "DimRiskTier.csv": 4,
        "Summary_Channel_KPIs.csv": 5,
        "Summary_Hourly_Temporal.csv": 2729,
        "Summary_Amount_Bands.csv": 6,
        "Summary_Account_Risk.csv": 4,
        "FactFraudInvestigation_Extract.csv": 20865,
        "Summary_ML_Model_Comparison.csv": 3,
        "Summary_ML_Confusion_Matrices.csv": 12,
        "Summary_ML_Feature_Importance.csv": 60,
        "Summary_ML_Threshold_Curves.csv": 27,
        "Summary_Data_Quality.csv": 10,
    }
    for filename, min_rows in expected_tables.items():
        filepath = os.path.join(POWERBI_DIR, filename)
        assert os.path.exists(filepath), f"Missing table: {filepath}"
        df = pd.read_csv(filepath)
        assert len(df) == min_rows, f"Table {filename} row mismatch: expected {min_rows}, got {len(df)}"


def test_2_model_schema_and_star_schema_relationships():
    """Verify star-schema JSON specification defines 13 tables and 7 valid 1-to-many relationships."""
    schema_path = os.path.join(POWERBI_DOCS, "powerbi_model_schema.json")
    bim_path = os.path.join(POWERBI_DOCS, "model.bim")
    assert os.path.exists(schema_path), f"Missing {schema_path}"
    assert os.path.exists(bim_path), f"Missing {bim_path}"

    with open(schema_path, "r") as f:
        schema = json.load(f)

    assert len(schema["tables"]) == 13, f"Expected 13 tables, found {len(schema['tables'])}"
    assert len(schema["relationships"]) == 7, f"Expected 7 relationships, found {len(schema['relationships'])}"

    for rel in schema["relationships"]:
        assert rel["cardinality"] == "manyToOne"
        assert rel["crossFilteringBehavior"] == "oneDirection"
        assert "fromTable" in rel and "toTable" in rel


def test_3_power_query_importers_file_complete():
    """Verify power_query_importers.m exists and contains definitions for all 13 tables."""
    m_path = os.path.join(POWERBI_DOCS, "power_query_importers.m")
    assert os.path.exists(m_path), f"Missing {m_path}"
    with open(m_path, "r", encoding="utf-8") as f:
        content = f.read()

    tables = [
        "DimTransactionType", "DimTime", "DimRiskTier",
        "Summary_Channel_KPIs", "Summary_Hourly_Temporal", "Summary_Amount_Bands",
        "Summary_Account_Risk", "FactFraudInvestigation_Extract",
        "Summary_ML_Model_Comparison", "Summary_ML_Confusion_Matrices",
        "Summary_ML_Feature_Importance", "Summary_ML_Threshold_Curves",
        "Summary_Data_Quality"
    ]
    for table in tables:
        assert table in content, f"Table {table} missing from power_query_importers.m"


def test_4_dax_measures_file_complete():
    """Verify dax_measures.dax exists and covers all core measure definitions."""
    dax_path = os.path.join(POWERBI_DOCS, "dax_measures.dax")
    assert os.path.exists(dax_path), f"Missing {dax_path}"
    with open(dax_path, "r", encoding="utf-8") as f:
        content = f.read()

    expected_measures = [
        "Total Transactions",
        "Total Transacted Volume",
        "Confirmed Fraud Incidents",
        "Fraud-Labeled Exposure",
        "Overall Fraud Rate",
        "Origin Account Drainage Rate",
        "Average Fraud Amount",
        "Average Legitimate Amount",
        "Fraud Severity Ratio",
        "TRANSFER Fraud Rate",
        "CASHOUT Fraud Rate",
        "Average Transaction Size",
        "Fraud Exposure Share Pct",
        "Daily Fraud Exposure",
        "Cumulative Fraud Exposure",
        "7-Day Rolling Avg Daily Fraud Exposure",
        "Critical Risk Accounts",
        "High Risk Accounts",
        "Critical Tier Fraud Rate",
        "Critical Tier Fraud Capture Share",
        "Investigation Candidate Count",
        "Confirmed Fraud Candidate Count",
        "Candidate Fraud Exposure",
        "Random Forest Precision",
        "Random Forest Recall",
        "XGBoost Precision",
        "XGBoost Recall",
        "Logistic Regression Precision",
        "Heuristic Flag Recall"
    ]
    for m in expected_measures:
        assert m in content, f"Measure {m} missing from dax_measures.dax"


def test_5_authoritative_macro_kpis_reconciliation():
    """Verify all 12 authoritative project KPIs match exactly."""
    df_channel = pd.read_csv(os.path.join(POWERBI_DIR, "Summary_Channel_KPIs.csv"))
    df_ml = pd.read_csv(os.path.join(POWERBI_DIR, "Summary_ML_Model_Comparison.csv"))
    df_extract = pd.read_csv(os.path.join(POWERBI_DIR, "FactFraudInvestigation_Extract.csv"))

    # 1. Total Transactions
    total_tx = df_channel["total_transactions"].sum()
    assert total_tx == 6362620, f"Total transactions mismatch: {total_tx}"

    # 2. Total Volume
    total_vol = df_channel["total_volume_usd"].sum()
    assert abs(total_vol - 1144392944759.77) < 1.0, f"Total volume mismatch: {total_vol}"

    # 3. Fraud Transactions
    fraud_tx = df_channel["fraud_transactions"].sum()
    assert fraud_tx == 8213, f"Fraud transactions mismatch: {fraud_tx}"

    # 4. Fraud Rate
    fraud_rate = (fraud_tx / total_tx) * 100
    assert abs(fraud_rate - 0.129082) < 0.001, f"Fraud rate mismatch: {fraud_rate}"

    # 5. Fraud Exposure
    fraud_exp = df_channel["fraud_exposure_usd"].sum()
    assert abs(fraud_exp - 12056415427.84) < 1.0, f"Fraud exposure mismatch: {fraud_exp}"

    # 6. Origin Account Drainage
    fraud_drainage = df_extract[(df_extract["is_fraud"] == 1) & (df_extract["is_drainage"] == 1)]
    assert len(fraud_drainage) == 8012, f"Fraud drainage mismatch: {len(fraud_drainage)}"
    drainage_rate = len(fraud_drainage) / 8213 * 100
    assert abs(drainage_rate - 97.55266) < 0.01, f"Drainage rate mismatch: {drainage_rate}"

    # 7. Heuristic Flag Count & Recall
    tp = df_channel["true_positives"].sum()
    fp = df_channel["false_positives"].sum()
    fn = df_channel["false_negatives"].sum()
    assert tp + fp == 16, f"Heuristic flag count mismatch: {tp + fp}"
    assert tp == 16 and fp == 0, "Heuristic precision must be 100%"
    heuristic_recall = tp / (tp + fn) * 100
    assert abs(heuristic_recall - 0.194813) < 0.001, f"Heuristic recall mismatch: {heuristic_recall}"

    # 8. ML Test Partition Size & Fraud
    rf_row = df_ml[df_ml["Model"] == "RandomForest"].iloc[0]
    test_size = rf_row["True_Positives"] + rf_row["False_Positives"] + rf_row["False_Negatives"] + rf_row["True_Negatives"]
    test_fraud = rf_row["True_Positives"] + rf_row["False_Negatives"]
    assert test_size == 1272524, f"ML test set size mismatch: {test_size}"
    assert test_fraud == 1643, f"ML test fraud mismatch: {test_fraud}"

    # 9. Exposure Share
    exp_share = (fraud_exp / total_vol) * 100
    assert abs(exp_share - 1.05352) < 0.001, f"Exposure share mismatch: {exp_share}"


def test_6_forensic_extract_recall():
    """Verify FactFraudInvestigation_Extract has 20,865 rows and captures 100% of fraud incidents."""
    path = os.path.join(POWERBI_DIR, "FactFraudInvestigation_Extract.csv")
    df = pd.read_csv(path)
    assert len(df) == 20865, f"Expected 20,865 rows, got {len(df)}"
    frauds = df[df["is_fraud"] == 1]
    assert len(frauds) == 8213, f"Expected 8,213 frauds in extract, got {len(frauds)}"


def test_7_detailed_visual_specs_exist():
    """Verify powerbi/visual_specifications_detailed.md exists and contains specifications for all 7 pages."""
    spec_path = os.path.join(POWERBI_DOCS, "visual_specifications_detailed.md")
    assert os.path.exists(spec_path), f"Missing {spec_path}"
    with open(spec_path, "r", encoding="utf-8") as f:
        content = f.read()

    pages = [
        "Executive Overview",
        "Fraud Analytics",
        "Financial & Transaction Analysis",
        "Account Risk & Behavioral Prioritization",
        "Fraud Investigation Workbench",
        "Machine Learning Model Analysis",
        "Data Quality, Architecture & Governance"
    ]
    for page in pages:
        assert page in content, f"Page '{page}' missing from visual_specifications_detailed.md"


def test_8_pbix_and_report_json_contain_all_8_pages():
    """Verify that both PBIX and report.json define all 8 report pages including the new Executive Risk Dashboard."""
    report_json_path = os.path.join(ROOT_DIR, "FraudLens.Report", "report.json")
    assert os.path.exists(report_json_path), f"Missing {report_json_path}"
    with open(report_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["sections"]) == 8, f"Expected 8 sections, got {len(data['sections'])}"
    section_names = [s["displayName"] for s in data["sections"]]
    assert "FraudLens — Executive Risk Dashboard" in section_names, "New page missing"
    assert "Executive Overview" in section_names, "Existing Page 1 missing"
    assert "Fraud Analytics" in section_names, "Existing Page 2 missing"
    total_visuals = sum(len(s["visualContainers"]) for s in data["sections"])
    assert total_visuals >= 60, f"Expected >= 60 visuals across 8 pages, found {total_visuals}"

    pbix_path = os.path.join(ROOT_DIR, "FraudLens_Analytics_Platform.pbix")
    assert os.path.exists(pbix_path), f"Missing {pbix_path}"
    with zipfile.ZipFile(pbix_path, "r") as z:
        layout = json.loads(z.read("Report/Layout").decode("utf-16-le"))
        assert len(layout["sections"]) == 8, f"Expected 8 sections in PBIX, got {len(layout['sections'])}"


def test_9_html_dashboard_preview_and_screenshot_exist():
    """Verify that the interactive visual dashboard preview HTML and PNG screenshot exist and are populated."""
    html_path = os.path.join(REPORTS_DIR, "powerbi_dashboard_preview.html")
    assert os.path.exists(html_path), f"Missing {html_path}"
    assert os.path.getsize(html_path) > 10000, "HTML preview is incomplete or too small"
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Executive Overview" in content
    assert "Fraud Analytics" in content
    assert "Executive Risk Dashboard" in content
    assert "Cohen's d = 2.1422" in content
    assert "$1.144 T" in content
    assert "67,252" in content

    screenshot_path = os.path.join(REPORTS_DIR, "executive_risk_dashboard_screenshot.png")
    assert os.path.exists(screenshot_path), f"Missing {screenshot_path}"
    assert os.path.getsize(screenshot_path) > 50000, "Screenshot file is too small or incomplete"


def test_10_pbip_project_settings_valid():
    """Verify FraudLens.pbip does not contain invalid enableAutoAuth property."""
    for p in ["FraudLens.pbip", os.path.join(POWERBI_DOCS, "FraudLens.pbip")]:
        with open(p, "r", encoding="utf-8") as f:
            meta = json.load(f)
        assert "enableAutoAuth" not in meta.get("settings", {}), f"Invalid enableAutoAuth found in {p}"
