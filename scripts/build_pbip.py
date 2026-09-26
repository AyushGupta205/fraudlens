"""
FraudLens — Build Power BI Project (.pbip) Artifact
Generates the FraudLens.pbip project structure with all 7 pages,
model.bim, partitions, M transformations, and relationships.
"""

import os
import json
import shutil

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POWERBI_DATA = os.path.join(ROOT_DIR, "data", "processed", "powerbi")

def build_pbip():
    # 1. Root .pbip
    pbip_data = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "FraudLens.Report"
                }
            }
        ],
        "settings": {
            "enableAutoAuth": True
        }
    }
    with open(os.path.join(ROOT_DIR, "FraudLens.pbip"), "w", encoding="utf-8") as f:
        json.dump(pbip_data, f, indent=2)

    # 2. Report structure
    os.makedirs(os.path.join(ROOT_DIR, "FraudLens.Report"), exist_ok=True)
    pbir_data = {
        "version": "1.0",
        "datasetReference": {
            "byPath": {
                "path": "../FraudLens.Dataset"
            },
            "byConnection": None
        }
    }
    with open(os.path.join(ROOT_DIR, "FraudLens.Report", "definition.pbir"), "w", encoding="utf-8") as f:
        json.dump(pbir_data, f, indent=2)

    # 7 Report pages
    pages = [
        "Executive Overview",
        "Fraud Analytics",
        "Financial & Transaction Analysis",
        "Account Risk",
        "Fraud Investigation",
        "ML Model Analysis",
        "Data Quality & Methodology"
    ]
    sections = []
    for i, name in enumerate(pages):
        sections.append({
            "name": f"ReportSection_{i+1}",
            "displayName": name,
            "filters": "[]",
            "ordinal": i,
            "width": 1920,
            "height": 1080,
            "visualContainers": []
        })

    report_config = {
        "version": "5.50",
        "themeCollection": {
            "baseTheme": {
                "name": "CY24SU06",
                "version": "5.55",
                "type": 2
            }
        },
        "activeSectionIndex": 0,
        "defaultDrillFilterOtherVisuals": True
    }

    report_data = {
        "config": json.dumps(report_config),
        "layoutOptimization": 0,
        "sections": sections
    }
    with open(os.path.join(ROOT_DIR, "FraudLens.Report", "report.json"), "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

    # 3. Dataset structure
    os.makedirs(os.path.join(ROOT_DIR, "FraudLens.Dataset"), exist_ok=True)
    pbism_data = {"version": "1.0"}
    with open(os.path.join(ROOT_DIR, "FraudLens.Dataset", "definition.pbism"), "w", encoding="utf-8") as f:
        json.dump(pbism_data, f, indent=2)

    # Copy / update model.bim into FraudLens.Dataset
    shutil.copy(os.path.join(ROOT_DIR, "powerbi", "model.bim"), os.path.join(ROOT_DIR, "FraudLens.Dataset", "model.bim"))
    
    print("[SUCCESS] FraudLens.pbip and project structure generated at D:\\financial_Analytics\\FraudLens.pbip")

if __name__ == "__main__":
    build_pbip()
