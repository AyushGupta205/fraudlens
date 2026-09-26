import pandas as pd
import numpy as np
from typing import Dict, Any, List
from src.utils.config import HIGH_AMOUNT_THRESHOLD
from src.utils.logger import get_logger

logger = get_logger(__name__)

def analyze_fraud_by_type(df: pd.DataFrame) -> pd.DataFrame:
    df_temp = df.copy()
    df_temp['fraud_amt'] = np.where(df_temp['isFraud'] == 1, df_temp['amount'], 0.0)
    df_temp['legit_amt'] = np.where(df_temp['isFraud'] == 0, df_temp['amount'], 0.0)
    df_temp['legit_count'] = np.where(df_temp['isFraud'] == 0, 1, 0)
    
    summary = df_temp.groupby('type').agg(
        total_transactions=('isFraud', 'count'),
        total_volume=('amount', 'sum'),
        fraud_transactions=('isFraud', 'sum'),
        fraud_loss=('fraud_amt', 'sum'),
        legit_transactions=('legit_count', 'sum'),
        legit_volume=('legit_amt', 'sum')
    ).reset_index()
    
    summary['fraud_rate_pct'] = (summary['fraud_transactions'] / summary['total_transactions'] * 100).round(4)
    total_loss = summary['fraud_loss'].sum()
    summary['loss_share_pct'] = (summary['fraud_loss'] / total_loss * 100).round(2) if total_loss > 0 else 0.0
    
    summary['avg_fraud_amount'] = np.where(
        summary['fraud_transactions'] > 0,
        (summary['fraud_loss'] / summary['fraud_transactions']).round(2),
        0.0
    )
    summary['avg_legit_amount'] = np.where(
        summary['legit_transactions'] > 0,
        (summary['legit_volume'] / summary['legit_transactions']).round(2),
        0.0
    )
    
    summary['total_volume'] = summary['total_volume'].round(2)
    summary['fraud_loss'] = summary['fraud_loss'].round(2)
    
    return summary.sort_values(by='fraud_transactions', ascending=False)

def analyze_fraud_temporal(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    df_temp = df.copy()
    if 'hour_of_day' not in df_temp.columns:
        df_temp['hour_of_day'] = (df_temp['step'] - 1) % 24
    if 'day_of_week' not in df_temp.columns:
        df_temp['day_of_week'] = ((df_temp['step'] - 1) // 24) % 7
    df_temp['fraud_amt'] = np.where(df_temp['isFraud'] == 1, df_temp['amount'], 0.0)
        
    by_hour = df_temp.groupby('hour_of_day').agg(
        total_transactions=('isFraud', 'count'),
        fraud_transactions=('isFraud', 'sum'),
        total_volume=('amount', 'sum'),
        fraud_loss=('fraud_amt', 'sum')
    ).reset_index()
    by_hour['fraud_rate_pct'] = (by_hour['fraud_transactions'] / by_hour['total_transactions'] * 100).round(4)
    
    by_dow = df_temp.groupby('day_of_week').agg(
        total_transactions=('isFraud', 'count'),
        fraud_transactions=('isFraud', 'sum'),
        total_volume=('amount', 'sum'),
        fraud_loss=('fraud_amt', 'sum')
    ).reset_index()
    by_dow['fraud_rate_pct'] = (by_dow['fraud_transactions'] / by_dow['total_transactions'] * 100).round(4)
    
    return {'by_hour': by_hour, 'by_day_of_week': by_dow}

def evaluate_anomaly_rules(df: pd.DataFrame) -> Dict[str, Any]:
    df_eval = df.copy()
    if 'orig_balance_error' not in df_eval.columns:
        df_eval['orig_balance_error'] = df_eval['newbalanceOrig'] + df_eval['amount'] - df_eval['oldbalanceOrg']
    
    r1_mask = df_eval['amount'] >= HIGH_AMOUNT_THRESHOLD
    r2_mask = (df_eval['oldbalanceOrg'] > 0) & (df_eval['newbalanceOrig'] == 0)
    r3_mask = (df_eval['type'] == 'TRANSFER') & (df_eval['oldbalanceDest'] == 0) & (df_eval['newbalanceDest'] == 0)
    r4_mask = df_eval['orig_balance_error'].abs() > 1.0
    r5_mask = df_eval['type'].isin(['TRANSFER', 'CASH_OUT']) & (df_eval['amount'] > 50000) & (df_eval['newbalanceOrig'] == 0)
    
    rules = [
        {
            'rule_id': 'RULE_01',
            'rule_name': 'High Transaction Amount',
            'threshold': f'>= ',
            'flagged_count': int(r1_mask.sum()),
            'flagged_volume': round(float(df_eval.loc[r1_mask, 'amount'].sum()), 2),
            'true_fraud_captured': int(df_eval.loc[r1_mask, 'isFraud'].sum()),
            'precision_pct': round(float(df_eval.loc[r1_mask, 'isFraud'].mean() * 100), 2) if r1_mask.sum() > 0 else 0.0
        },
        {
            'rule_id': 'RULE_02',
            'rule_name': 'Full Account Liquidation',
            'threshold': 'newbalanceOrig == 0 & oldbalanceOrg > 0',
            'flagged_count': int(r2_mask.sum()),
            'flagged_volume': round(float(df_eval.loc[r2_mask, 'amount'].sum()), 2),
            'true_fraud_captured': int(df_eval.loc[r2_mask, 'isFraud'].sum()),
            'precision_pct': round(float(df_eval.loc[r2_mask, 'isFraud'].mean() * 100), 2) if r2_mask.sum() > 0 else 0.0
        },
        {
            'rule_id': 'RULE_03',
            'rule_name': 'Mule Account Transfer Pattern',
            'threshold': 'TRANSFER & oldbalanceDest == 0 & newbalanceDest == 0',
            'flagged_count': int(r3_mask.sum()),
            'flagged_volume': round(float(df_eval.loc[r3_mask, 'amount'].sum()), 2),
            'true_fraud_captured': int(df_eval.loc[r3_mask, 'isFraud'].sum()),
            'precision_pct': round(float(df_eval.loc[r3_mask, 'isFraud'].mean() * 100), 2) if r3_mask.sum() > 0 else 0.0
        },
        {
            'rule_id': 'RULE_04',
            'rule_name': 'Balance Accounting Discrepancy',
            'threshold': '|orig_balance_error| > .00',
            'flagged_count': int(r4_mask.sum()),
            'flagged_volume': round(float(df_eval.loc[r4_mask, 'amount'].sum()), 2),
            'true_fraud_captured': int(df_eval.loc[r4_mask, 'isFraud'].sum()),
            'precision_pct': round(float(df_eval.loc[r4_mask, 'isFraud'].mean() * 100), 2) if r4_mask.sum() > 0 else 0.0
        },
        {
            'rule_id': 'RULE_05',
            'rule_name': 'High-Risk Transfer/Cashout Drain',
            'threshold': 'TRANSFER/CASH_OUT >  & newbalanceOrig == 0',
            'flagged_count': int(r5_mask.sum()),
            'flagged_volume': round(float(df_eval.loc[r5_mask, 'amount'].sum()), 2),
            'true_fraud_captured': int(df_eval.loc[r5_mask, 'isFraud'].sum()),
            'precision_pct': round(float(df_eval.loc[r5_mask, 'isFraud'].mean() * 100), 2) if r5_mask.sum() > 0 else 0.0
        }
    ]
    
    any_rule_mask = r1_mask | r2_mask | r3_mask | r4_mask | r5_mask
    total_fraud_dataset = int(df_eval['isFraud'].sum())
    total_captured = int(df_eval.loc[any_rule_mask, 'isFraud'].sum())
    
    combined = {
        'total_transactions': len(df_eval),
        'total_flagged': int(any_rule_mask.sum()),
        'flagged_volume': round(float(df_eval.loc[any_rule_mask, 'amount'].sum()), 2),
        'total_fraud_captured': total_captured,
        'coverage_recall_pct': round(float(total_captured / total_fraud_dataset * 100), 2) if total_fraud_dataset > 0 else 0.0,
        'rules': rules
    }
    return combined
