"""
FraudLens ? Dataset Inspection and Validation Module
Performs comprehensive Phase 1 exploratory data auditing, summary calculation, and validation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from typing import Dict, Any
import pandas as pd
import numpy as np
from src.data.load_data import load_dataset

def inspect_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    total_rows, total_cols = df.shape
    
    # 1. Column-level information
    column_info = []
    for col in df.columns:
        non_null_count = int(df[col].notnull().sum())
        missing_count = int(df[col].isnull().sum())
        missing_pct = round((missing_count / total_rows) * 100, 4) if total_rows > 0 else 0.0
        column_info.append({
            'column': col,
            'dtype': str(df[col].dtype),
            'non_null': non_null_count,
            'missing': missing_count,
            'missing_pct': missing_pct
        })
    col_df = pd.DataFrame(column_info)
    
    # 2. Numerical summary statistics
    numeric_cols = ['step', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']
    num_stats = df[numeric_cols].describe().T[['count', 'mean', 'std', 'min', '50%', 'max']].rename(columns={'50%': 'median'})
    
    # 3. Categorical breakdown (transaction type)
    type_counts = df['type'].value_counts()
    cat_summary = {
        'type': {
            'unique_count': int(df['type'].nunique()),
            'top_categories': type_counts.to_dict(),
            'frequencies_pct': (type_counts / total_rows * 100).round(4).to_dict() if total_rows > 0 else {}
        },
        'nameOrig': {
            'unique_count': int(df['nameOrig'].nunique()),
            'sample_values': df['nameOrig'].head(3).tolist()
        },
        'nameDest': {
            'unique_count': int(df['nameDest'].nunique()),
            'sample_values': df['nameDest'].head(3).tolist()
        }
    }
    
    # 4. Target variable analysis (isFraud & isFlaggedFraud)
    fraud_counts = df['isFraud'].value_counts().to_dict()
    legit_count = int(fraud_counts.get(0, 0))
    fraud_count = int(fraud_counts.get(1, 0))
    fraud_rate_pct = round((fraud_count / total_rows * 100), 4) if total_rows > 0 else 0.0
    legit_rate_pct = round((legit_count / total_rows * 100), 4) if total_rows > 0 else 0.0
    
    flagged_counts = df['isFlaggedFraud'].value_counts().to_dict() if 'isFlaggedFraud' in df.columns else {}
    
    target_summary = {
        'total_transactions': total_rows,
        'fraud_transactions': fraud_count,
        'legitimate_transactions': legit_count,
        'fraud_percentage': fraud_rate_pct,
        'legitimate_percentage': legit_rate_pct,
        'flagged_fraud_count': int(flagged_counts.get(1, 0)),
        'unflagged_count': int(flagged_counts.get(0, 0))
    }
    
    # 5. Data integrity & logical validation
    duplicate_records = int(df.duplicated(subset=['step', 'type', 'amount', 'nameOrig', 'nameDest']).sum())
    negative_amounts = int((df['amount'] < 0).sum())
    zero_amounts = int((df['amount'] == 0).sum())
    negative_balances = int((
        (df['oldbalanceOrg'] < 0) | (df['newbalanceOrig'] < 0) |
        (df['oldbalanceDest'] < 0) | (df['newbalanceDest'] < 0)
    ).sum())
    valid_fraud_labels = bool(set(df['isFraud'].unique()).issubset({0, 1}))
    
    validation_status = 'PASS'
    issues = []
    if duplicate_records > 0:
        issues.append(f'{duplicate_records} potential duplicate records found on key tuple.')
    if negative_amounts > 0:
        validation_status = 'FAIL'
        issues.append(f'{negative_amounts} negative transaction amounts.')
    if not valid_fraud_labels:
        validation_status = 'FAIL'
        issues.append('Invalid target values detected in isFraud.')
    if zero_amounts > 0:
        issues.append(f'{zero_amounts} transactions with amount == .00 (documented cancellation edge cases).')
        
    results = {
        'dimensions': {'rows': total_rows, 'columns': total_cols},
        'columns': col_df,
        'numerical_statistics': num_stats,
        'categorical_summary': cat_summary,
        'target_summary': target_summary,
        'validation': {
            'status': validation_status,
            'duplicate_records': duplicate_records,
            'negative_amounts': negative_amounts,
            'zero_amounts': zero_amounts,
            'negative_balances': negative_balances,
            'valid_fraud_labels': valid_fraud_labels,
            'issues': issues
        }
    }
    return results

def run_inspection():
    sep = '=' * 75
    print(sep)
    print('  FraudLens - Phase 1: Dataset & Project Setup Inspection')
    print(sep)
    
    df = load_dataset()
    results = inspect_dataset(df)
    
    print('')
    print('[1] DATASET DIMENSIONS')
    print(f"  Rows:    {results['dimensions']['rows']:,}")
    print(f"  Columns: {results['dimensions']['columns']}")
    
    print('')
    print('[2] COLUMN DATA TYPES & MISSING VALUES')
    print(results['columns'].to_string(index=False))
    
    print('')
    print('[3] NUMERICAL SUMMARY STATISTICS')
    print(results['numerical_statistics'].to_string())
    
    print('')
    print('[4] TARGET VARIABLE GROUND TRUTH (isFraud)')
    t = results['target_summary']
    print(f"  Total Transactions:      {t['total_transactions']:,}")
    print(f"  Legitimate Transactions: {t['legitimate_transactions']:,} ({t['legitimate_percentage']}%)")
    print(f"  Fraudulent Transactions: {t['fraud_transactions']:,} ({t['fraud_percentage']}%)")
    print(f"  System Flagged Fraud:    {t['flagged_fraud_count']:,}")
    
    print('')
    print('[5] TRANSACTION TYPES DISTRIBUTION')
    type_counts = results['categorical_summary']['type']
    for t_name, count in type_counts['top_categories'].items():
        pct = type_counts['frequencies_pct'][t_name]
        print(f"  - {t_name:<10}: {count:>10,} ({pct:.4f}%)")
        
    print('')
    print('[6] DATA INTEGRITY & VALIDATION')
    v = results['validation']
    print(f"  Validation Status: {v['status']}")
    print(f"  Duplicate Records: {v['duplicate_records']}")
    print(f"  Negative Amounts:  {v['negative_amounts']}")
    print(f"  Zero Amounts:      {v['zero_amounts']}")
    print(f"  Negative Balances: {v['negative_balances']}")
    if v['issues']:
        print('  Identified Issues/Notes:')
        for issue in v['issues']:
            print(f'    * {issue}')
            
    print('')
    print(sep)
    print(f"  PHASE 1 STATUS: {v['status']}")
    print(sep)

if __name__ == '__main__':
    run_inspection()
