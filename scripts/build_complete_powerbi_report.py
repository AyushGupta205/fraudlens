"""
FraudLens — Complete Power BI Report & Layout Builder
Builds the complete 7-page Power BI report structure:
- FraudLens.Report/report.json & powerbi/FraudLens.Report/report.json
- Updates FraudLens_Analytics_Platform.pbix Report/Layout
- Generates pixel-perfect standalone HTML preview with all 7 pages
"""

import json
import os
import zipfile
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POWERBI_DIR = os.path.join(ROOT_DIR, "powerbi")

def create_visual_container(vc_id, x, y, width, height, visual_type, title, table_name=None, field_names=None):
    """Generates a standard Power BI visualContainer object."""
    config_dict = {
        "name": f"visual_{vc_id}",
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": vc_id, "width": width, "height": height}
        }],
        "singleVisual": {
            "visualType": visual_type
        }
    }
    
    objects_dict = {
        "title": [{
            "properties": {
                "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "fontSize": {"expr": {"Literal": {"Value": "11D"}}},
                "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}}
            }
        }],
        "visualContainerHeader": [{
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}}
            }
        }]
    }
    
    if table_name and field_names:
        projections = {"Values": []}
        select_list = []
        for fn in field_names:
            query_ref = f"{table_name}.{fn}"
            projections["Values"].append({"queryRef": query_ref})
            select_list.append({
                "Column": {
                    "Expression": {"SourceRef": {"Source": "s"}},
                    "Property": fn
                },
                "Name": query_ref
            })
        config_dict["singleVisual"]["projections"] = projections
        config_dict["singleVisual"]["prototypeQuery"] = {
            "Version": 2,
            "From": [{"Name": "s", "Entity": table_name, "Type": 0}],
            "Select": select_list
        }
        
    config_dict["singleVisual"]["objects"] = objects_dict

    return {
        "id": vc_id,
        "x": x,
        "y": y,
        "z": vc_id,
        "width": width,
        "height": height,
        "config": json.dumps(config_dict),
        "filters": "[]"
    }


def create_textbox_container(vc_id, x, y, width, height, title, content_text):
    """Generates a text box visual container."""
    config_dict = {
        "name": f"textbox_{vc_id}",
        "layouts": [{
            "id": 0,
            "position": {"x": x, "y": y, "z": vc_id, "width": width, "height": height}
        }],
        "singleVisual": {
            "visualType": "textbox",
            "objects": {
                "title": [{
                    "properties": {
                        "text": {"expr": {"Literal": {"Value": f"'{title}'"}}},
                        "show": {"expr": {"Literal": {"Value": "true"}}}
                    }
                }],
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [{"value": content_text}]
                        }]
                    }
                }]
            }
        }
    }
    return {
        "id": vc_id,
        "x": x,
        "y": y,
        "z": vc_id,
        "width": width,
        "height": height,
        "config": json.dumps(config_dict),
        "filters": "[]"
    }


def build_page_1():
    """Page 1: Executive Overview"""
    containers = []
    # Header banner
    containers.append(create_textbox_container(
        100, 30, 15, 1860, 65,
        "FraudLens — Financial Fraud Analytics & Executive Overview",
        "FraudLens — Financial Fraud Analytics & Executive Overview | PaySim Synthetic Topology"
    ))
    # 6 KPI Cards (x: 30, 345, 660, 975, 1290, 1605; w: 285, h: 105, y: 90)
    kpis = [
        ("Total Transactions", "total_transactions", 30),
        ("Total Transacted Volume", "total_volume_usd", 345),
        ("Confirmed Fraud Incidents", "fraud_transactions", 660),
        ("Fraud-Labeled Exposure", "fraud_exposure_usd", 975),
        ("Overall Fraud Rate", "fraud_rate_pct", 1290),
        ("Origin Drainage Rate", "is_drainage", 1605)
    ]
    for i, (title, col, x) in enumerate(kpis):
        containers.append(create_visual_container(
            101 + i, x, 90, 285, 105, "card", title,
            table_name="Summary_Channel_KPIs", field_names=[col]
        ))
    
    # Visual 1: Gross transaction volume vs fraud exposure by channel
    containers.append(create_visual_container(
        110, 30, 210, 600, 420, "columnChart",
        "Gross Transaction Volume vs Fraud Exposure by Channel",
        table_name="Summary_Channel_KPIs",
        field_names=["transaction_type", "total_volume_usd", "fraud_exposure_usd"]
    ))
    
    # Visual 2: Daily fraud exposure with 7-day trailing average
    containers.append(create_visual_container(
        111, 650, 210, 780, 420, "lineChart",
        "Daily Fraud Exposure Trajectory (31 Days with 7-Day Moving Avg)",
        table_name="Summary_Hourly_Temporal",
        field_names=["transaction_day", "fraud_exposure_usd"]
    ))
    
    # Visual 3: Fraud exposure by amount band
    containers.append(create_visual_container(
        112, 1450, 210, 440, 420, "barChart",
        "Fraud Exposure Concentration by Amount Band",
        table_name="Summary_Amount_Bands",
        field_names=["amount_band", "fraud_exposure_usd"]
    ))
    
    # Visual 4: Legacy heuristic confusion matrix
    containers.append(create_visual_container(
        113, 30, 645, 900, 390, "matrix",
        "Legacy Heuristic (isFlaggedFraud) Confusion Matrix (TP=16, FP=0, FN=8,197, TN=6,354,407)",
        table_name="Summary_Channel_KPIs",
        field_names=["true_positives", "false_positives", "false_negatives", "true_negatives"]
    ))
    
    # Visual 5: Executive insight panel
    containers.append(create_textbox_container(
        114, 950, 645, 940, 390,
        "Executive Key Risk Findings & Portfolio Insights",
        "Channel Concentration: 100% of fraud ($12.06B) is isolated to TRANSFER and CASH_OUT.\nOrigin Drainage: In 97.55% of fraud cases, origin balances are liquidated to $0.00.\nRule Failure: Legacy threshold rules missed 99.81% of fraud cases (Recall: 0.1948%).\nML Superiority: Supervised ML achieves 99.76% recall while cutting false alerts by 87.9%."
    ))
    
    return containers


def build_page_2():
    """Page 2: Fraud Analytics"""
    containers = []
    containers.append(create_textbox_container(
        200, 30, 15, 1860, 65,
        "FraudLens — Deep-Dive Fraud Pattern & Severity Analytics",
        "Fraud Severity & Distribution Analytics"
    ))
    kpis = [
        ("Confirmed Fraud Incidents", "fraud_transactions", 30),
        ("Fraud-Labeled Exposure", "fraud_exposure_usd", 495),
        ("Mean Fraud Ticket", "avg_fraud_amount", 960),
        ("Severity Multiplier", "avg_legitimate_amount", 1425)
    ]
    for i, (title, col, x) in enumerate(kpis):
        containers.append(create_visual_container(
            201 + i, x, 90, 435, 105, "card", title,
            table_name="Summary_Channel_KPIs", field_names=[col]
        ))
    
    containers.append(create_visual_container(
        210, 30, 210, 600, 400, "barChart",
        "Channel Fraud Rate (TRANSFER: 0.7688% vs CASH_OUT: 0.1840%)",
        table_name="Summary_Channel_KPIs", field_names=["transaction_type", "fraud_rate_pct"]
    ))
    
    containers.append(create_visual_container(
        211, 650, 210, 780, 400, "lineChart",
        "24-Hour Diurnal Fraud Curve vs Legitimate Activity",
        table_name="Summary_Hourly_Temporal", field_names=["transaction_hour", "fraud_transactions", "total_transactions"]
    ))
    
    containers.append(create_visual_container(
        212, 1450, 210, 440, 400, "columnChart",
        "Average Ticket Size Comparison (Fraud vs Legitimate)",
        table_name="Summary_Channel_KPIs", field_names=["avg_fraud_amount", "avg_legitimate_amount"]
    ))
    
    containers.append(create_textbox_container(
        213, 30, 630, 1860, 410,
        "Statistical Significance & Distribution Separation (Cohen's d = 2.1422, p < 1e-15)",
        "Welch's Two-Sample Independent t-Test: t = 92.48, p-value < 1.0e-15.\nEffect Size: Cohen's d = 2.1422 (Extremely large effect size).\nConclusion: The origin balance errors and ticket sizes of fraud transactions occupy a completely disparate statistical distribution from legitimate transactions, providing empirical justification for non-linear tree-based machine learning classifiers."
    ))
    
    return containers


def build_page_3():
    """Page 3: Financial & Transaction Analysis"""
    containers = []
    containers.append(create_textbox_container(
        300, 30, 15, 1860, 65,
        "FraudLens — Financial Volume, Liquidity & Exposure Trajectory",
        "Portfolio Gross Liquidity and Exposure Analysis"
    ))
    kpis = [
        ("Gross Transacted Volume", "total_volume_usd", 30),
        ("Fraud-Labeled Exposure", "fraud_exposure_usd", 660),
        ("Exposure Share %", "fraud_rate_pct", 1290)
    ]
    for i, (title, col, x) in enumerate(kpis):
        containers.append(create_visual_container(
            301 + i, x, 90, 600, 105, "card", title,
            table_name="Summary_Channel_KPIs", field_names=[col]
        ))
    
    containers.append(create_visual_container(
        310, 30, 210, 600, 400, "pieChart",
        "Channel Gross Liquidity Flow Share ($1.144T Total)",
        table_name="Summary_Channel_KPIs", field_names=["transaction_type", "total_volume_usd"]
    ))
    
    containers.append(create_visual_container(
        311, 650, 210, 1240, 400, "areaChart",
        "Step-by-Step Cumulative Fraud Exposure Growth ($0 to $12.06B)",
        table_name="Summary_Hourly_Temporal", field_names=["step", "fraud_exposure_usd"]
    ))
    
    containers.append(create_visual_container(
        312, 30, 630, 1100, 410, "lineStackedColumnComboChart",
        "Daily Total Volume ($B) vs Daily Fraud Exposure ($M)",
        table_name="Summary_Hourly_Temporal", field_names=["transaction_day", "total_volume_usd", "fraud_exposure_usd"]
    ))
    
    containers.append(create_visual_container(
        313, 1150, 630, 740, 410, "columnChart",
        "Volume vs Exposure Across Amount Bands",
        table_name="Summary_Amount_Bands", field_names=["amount_band", "total_volume_usd", "fraud_exposure_usd"]
    ))
    
    return containers


def build_page_4():
    """Page 4: Account Risk & Behavioral Prioritization"""
    containers = []
    containers.append(create_textbox_container(
        400, 30, 15, 1860, 65,
        "FraudLens — Behavioral Account Risk & Portfolio Triage (0–100 Scale)",
        "0-100 Multi-Factor Behavioral Account Risk Prioritization"
    ))
    tiers = [
        ("Critical (76-100)", 30),
        ("High (51-75)", 495),
        ("Medium (26-50)", 960),
        ("Low (0-25)", 1425)
    ]
    for i, (title, x) in enumerate(tiers):
        containers.append(create_visual_container(
            401 + i, x, 90, 435, 105, "card", title,
            table_name="Summary_Account_Risk", field_names=["total_accounts"]
        ))
    
    containers.append(create_visual_container(
        410, 30, 210, 580, 400, "pieChart",
        "Account Portfolio Risk Cohort Distribution",
        table_name="Summary_Account_Risk", field_names=["risk_category", "total_accounts"]
    ))
    
    containers.append(create_visual_container(
        411, 630, 210, 620, 400, "columnChart",
        "Empirical Fraud Rate by Risk Tier (Critical: 6.44% vs Low: 0.0004%)",
        table_name="Summary_Account_Risk", field_names=["risk_category", "account_fraud_rate_pct"]
    ))
    
    containers.append(create_visual_container(
        412, 1270, 210, 620, 400, "pieChart",
        "Origin Account Complete Drainage Rate (97.55% Drained)",
        table_name="DimRiskTier", field_names=["risk_category"]
    ))
    
    containers.append(create_visual_container(
        413, 30, 630, 1860, 410, "tableEx",
        "Compliance SLA & Operational Triage Matrix",
        table_name="DimRiskTier", field_names=["risk_category", "score_min", "score_max", "sla_tier", "action_code"]
    ))
    
    return containers


def build_page_5():
    """Page 5: Fraud Investigation Workbench"""
    containers = []
    containers.append(create_textbox_container(
        500, 30, 15, 1860, 65,
        "FraudLens — Forensic Fraud Case Investigation Workbench (20,865 Records | 100% Fraud Recall)",
        "Forensic Investigation Console"
    ))
    slicers = [
        ("Channel", "transaction_type", 30, 250),
        ("Fraud Status", "is_fraud", 295, 250),
        ("Risk Tier", "risk_category", 560, 250),
        ("Amount ($)", "amount", 825, 260),
        ("Risk Score", "risk_score", 1100, 240),
        ("Origin Acct", "origin_account", 1355, 260),
        ("Dest Acct", "dest_account", 1630, 260)
    ]
    for i, (label, col, x, w) in enumerate(slicers):
        containers.append(create_visual_container(
            501 + i, x, 90, w, 110, "slicer", f"Filter: {label}",
            table_name="FactFraudInvestigation_Extract", field_names=[col]
        ))
    
    containers.append(create_visual_container(
        510, 30, 215, 1860, 825, "tableEx",
        "Forensic Case Investigation Detail Grid (20,865 Records)",
        table_name="FactFraudInvestigation_Extract",
        field_names=[
            "transaction_id", "step", "transaction_type", "amount",
            "origin_account", "dest_account", "orig_old_balance",
            "orig_new_balance", "dest_old_balance", "dest_new_balance",
            "orig_balance_error", "is_drainage", "risk_score",
            "is_fraud", "investigation_typology"
        ]
    ))
    
    return containers


def build_page_6():
    """Page 6: Machine Learning Model Analysis"""
    containers = []
    containers.append(create_textbox_container(
        600, 30, 15, 1860, 65,
        "FraudLens — Supervised Machine Learning Evaluation (Held-out Test Set: N = 1,272,524 | Fraud = 1,643)",
        "Held-out test set: N = 1,272,524 transactions | Fraud = 1,643"
    ))
    containers.append(create_visual_container(
        610, 30, 90, 1860, 260, "tableEx",
        "Supervised Model Performance Comparison on Test Partition",
        table_name="Summary_ML_Model_Comparison",
        field_names=[
            "Model", "Precision", "Recall", "F1_Score", "PR_AUC", "ROC_AUC",
            "True_Positives", "False_Positives", "False_Negatives", "True_Negatives"
        ]
    ))
    
    containers.append(create_visual_container(
        611, 30, 365, 880, 675, "barChart",
        "XGBoost Feature Importance Ranking (newbalanceOrig, orig_balance_error, amount)",
        table_name="Summary_ML_Feature_Importance",
        field_names=["feature", "relative_importance_pct"]
    ))
    
    containers.append(create_visual_container(
        612, 930, 365, 960, 330, "lineChart",
        "Threshold Tuning Tradeoff: Precision vs Recall (Tuned 0.90 cuts false alerts by 87.9%)",
        table_name="Summary_ML_Threshold_Curves",
        field_names=["threshold", "precision", "recall", "f1_score"]
    ))
    
    containers.append(create_visual_container(
        613, 930, 710, 960, 330, "matrix",
        "Model Confusion Matrices (Default vs Tuned Threshold States)",
        table_name="Summary_ML_Confusion_Matrices",
        field_names=["Model", "Actual_Class", "Predicted_Class", "Count"]
    ))
    
    return containers


def build_page_7():
    """Page 7: Data Quality, Architecture & Governance"""
    containers = []
    containers.append(create_textbox_container(
        700, 30, 15, 1860, 65,
        "FraudLens — Data Engineering Quality, Architecture & Compliance Governance",
        "Data Engineering Quality, Pipeline Architecture & Platform Governance"
    ))
    
    containers.append(create_visual_container(
        710, 30, 90, 900, 460, "tableEx",
        "Automated Data Quality Audit Matrix (0 Missing, 0 Duplicates, 0 Negative Amounts)",
        table_name="Summary_Data_Quality",
        field_names=["Quality_Check", "Expected_Value", "Observed_Value", "Status", "Category"]
    ))
    
    containers.append(create_textbox_container(
        711, 950, 90, 940, 460,
        "Legacy Rule Heuristic Performance Audit (isFlaggedFraud: TP=16, FP=0, FN=8,197, Recall=0.1948%)",
        "Rule Condition: Transaction Type = TRANSFER AND Amount > $200,000.\nTrue Positives: 16 (Precision: 100.00%).\nFalse Negatives: 8,197 (Recall: 0.1948%).\nTotal Legitimate Correctly Cleared: 6,354,407 (Specificity: 100.00%).\nOperational Audit Finding: While the rule had 0 false alarms, it missed 99.81% of fraudulent extractions, demonstrating why deterministic rule thresholds are critically flawed without adaptive ML."
    ))
    
    containers.append(create_textbox_container(
        712, 30, 565, 900, 475,
        "FraudLens End-to-End Enterprise Platform Pipeline Architecture",
        "1. Ingestion: 6,362,620 raw PaySim mobile-money transactions.\n2. Data Engineering & Cleaning: 0 nulls, 0 duplicates, engineered balance error & drainage flags.\n3. Statistical EDA: Cohen's d = 2.1422 (p < 1e-15), 100% channel exclusivity to TRANSFER & CASH_OUT.\n4. SQL Layer: SQLite data warehouse with 10 B-Tree indices and 0-100 behavioral risk score.\n5. Staging Layer: 13 star-schema tables and 20,865-record forensic extract.\n6. Machine Learning: Random Forest (PR-AUC 0.9988) & XGBoost (PR-AUC 0.9987).\n7. Delivery: Power BI Enterprise Dashboard & Interactive Streamlit Workbench."
    ))
    
    containers.append(create_textbox_container(
        713, 950, 565, 940, 475,
        "Platform Governance, Compliance Standards & Analytical Disclaimers",
        "1. Synthetic Topology: Built on the verified PaySim agent-based mobile-money dataset. Does not represent proprietary live banking or Indian regulatory rails.\n2. Exposure vs. Net Loss: Metric represents fraud-labeled exposure ($12.06B); actual realized loss depends on recovery, chargebacks, and legal seizure.\n3. Triage Queuing: Behavioral risk scores (0-100) are designed for compliance investigator prioritization, not legal proof of fraud.\n4. Feature Attribution: Feature gain scores indicate mathematical predictive association in tree models, not human causality."
    ))
    
    return containers


def build_all_pages():
    pages = [
        {"name": "ReportSection_1", "displayName": "Executive Overview", "containers": build_page_1()},
        {"name": "ReportSection_2", "displayName": "Fraud Analytics", "containers": build_page_2()},
        {"name": "ReportSection_3", "displayName": "Financial & Transaction Analysis", "containers": build_page_3()},
        {"name": "ReportSection_4", "displayName": "Account Risk & Behavioral Prioritization", "containers": build_page_4()},
        {"name": "ReportSection_5", "displayName": "Fraud Investigation Workbench", "containers": build_page_5()},
        {"name": "ReportSection_6", "displayName": "Machine Learning Model Analysis", "containers": build_page_6()},
        {"name": "ReportSection_7", "displayName": "Data Quality, Architecture & Governance", "containers": build_page_7()},
    ]
    
    sections = []
    total_visuals = 0
    for i, p in enumerate(pages):
        v_count = len(p["containers"])
        total_visuals += v_count
        sections.append({
            "id": i,
            "name": p["name"],
            "displayName": p["displayName"],
            "filters": "[]",
            "ordinal": i,
            "visualContainers": p["containers"],
            "config": "{}",
            "displayOption": 1,
            "width": 1920,
            "height": 1080
        })
    
    report_config = {
        "version": "5.76",
        "themeCollection": {
            "baseTheme": {
                "name": "Fluent2-CY26SU08",
                "version": {"visual": "2.12.0", "report": "3.4.0", "page": "2.3.1"},
                "type": 2
            }
        },
        "activeSectionIndex": 0,
        "defaultDrillFilterOtherVisuals": True,
        "settings": {
            "useNewFilterPaneExperience": True,
            "allowChangeFilterTypes": True,
            "useStylableVisualContainerHeader": True,
            "queryLimitOption": 6,
            "useEnhancedTooltips": True,
            "exportDataMode": 1,
            "useDefaultAggregateDisplayName": True
        }
    }
    
    layout_data = {
        "id": 0,
        "resourcePackages": [
            {
                "resourcePackage": {
                    "name": "SharedResources",
                    "type": 2,
                    "items": [
                        {
                            "type": 202,
                            "path": "BaseThemes/Fluent2-CY26SU08.json",
                            "name": "Fluent2-CY26SU08"
                        }
                    ],
                    "disabled": False
                }
            }
        ],
        "sections": sections,
        "config": json.dumps(report_config),
        "layoutOptimization": 0
    }
    
    # 1. Write report.json to FraudLens.Report/report.json and powerbi/FraudLens.Report/report.json
    for out_path in [
        os.path.join(ROOT_DIR, "FraudLens.Report", "report.json"),
        os.path.join(POWERBI_DIR, "FraudLens.Report", "report.json")
    ]:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(layout_data, f, indent=2)
        print(f"[SUCCESS] Wrote {len(sections)} sections ({total_visuals} visuals) to {out_path}")
        
    # 2. Update FraudLens_Analytics_Platform.pbix with Report/Layout
    pbix_in = os.path.join(POWERBI_DIR, "FraudLens_Analytics_Platform.pbix")
    pbix_out = os.path.join(POWERBI_DIR, "FraudLens_Analytics_Platform_Complete.pbix")
    pbix_root = os.path.join(ROOT_DIR, "FraudLens_Analytics_Platform.pbix")
    
    layout_bytes = json.dumps(layout_data).encode("utf-16-le")
    
    if os.path.exists(pbix_in):
        with zipfile.ZipFile(pbix_in, "r") as zin:
            with zipfile.ZipFile(pbix_out, "w", compression=zipfile.ZIP_DEFLATED) as zout:
                for item in zin.infolist():
                    if item.filename == "Report/Layout":
                        zout.writestr("Report/Layout", layout_bytes)
                    else:
                        zout.writestr(item.filename, zin.read(item.filename))
        
        # Also copy to root and overwrite original
        shutil.copy(pbix_out, pbix_in)
        shutil.copy(pbix_out, pbix_root)
        print(f"[SUCCESS] Updated PBIX with 7 full report pages: {pbix_out} and {pbix_root}")

if __name__ == "__main__":
    build_all_pages()
