import pandas as pd
import numpy as np
from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)

def generate_customer_profiles(df: pd.DataFrame) -> pd.DataFrame:
    logger.info('Generating customer-level risk profiles and behavioral metrics...')
    df_temp = df.copy()
    df_temp['is_transfer'] = (df_temp['type'] == 'TRANSFER').astype(int)
    df_temp['is_cashout'] = (df_temp['type'] == 'CASH_OUT').astype(int)
    df_temp['fraud_amt'] = np.where(df_temp['isFraud'] == 1, df_temp['amount'], 0.0)
    
    orig_profiles = df_temp.groupby('nameOrig').agg(
        total_transactions=('isFraud', 'count'),
        total_volume=('amount', 'sum'),
        avg_transaction_val=('amount', 'mean'),
        max_transaction_val=('amount', 'max'),
        fraud_transactions=('isFraud', 'sum'),
        fraud_volume=('fraud_amt', 'sum'),
        transfer_count=('is_transfer', 'sum'),
        cashout_count=('is_cashout', 'sum'),
        min_step=('step', 'min'),
        max_step=('step', 'max')
    ).reset_index()
    
    orig_profiles['fraud_rate_pct'] = (
        orig_profiles['fraud_transactions'] / orig_profiles['total_transactions'] * 100
    ).round(4)
    
    avg_txn_norm = np.clip(orig_profiles['avg_transaction_val'] / 200000.0, 0, 1.0)
    high_risk_type_ratio = (orig_profiles['transfer_count'] + orig_profiles['cashout_count']) / orig_profiles['total_transactions']
    fraud_score_component = np.where(orig_profiles['fraud_transactions'] > 0, 1.0, 0.0)
    
    raw_risk_score = (
        fraud_score_component * 45.0 +
        high_risk_type_ratio * 25.0 +
        avg_txn_norm * 20.0 +
        np.clip(orig_profiles['total_transactions'] / 5.0, 0, 1.0) * 10.0
    )
    
    orig_profiles['risk_score'] = np.clip(raw_risk_score, 0, 100.0).round(1)
    
    conditions = [
        (orig_profiles['risk_score'] >= 75.0),
        (orig_profiles['risk_score'] >= 45.0) & (orig_profiles['risk_score'] < 75.0),
        (orig_profiles['risk_score'] >= 20.0) & (orig_profiles['risk_score'] < 45.0),
        (orig_profiles['risk_score'] < 20.0)
    ]
    choices = ['Critical Risk', 'High Risk', 'Medium Risk', 'Low Risk']
    orig_profiles['risk_category'] = np.select(conditions, choices, default='Low Risk')
    
    logger.info(f'Generated {len(orig_profiles):,} customer profiles.')
    return orig_profiles

def summarize_customer_risk(profiles_df: pd.DataFrame) -> pd.DataFrame:
    summary = profiles_df.groupby('risk_category').agg(
        customer_count=('nameOrig', 'count'),
        total_volume=('total_volume', 'sum'),
        avg_risk_score=('risk_score', 'mean'),
        customers_with_fraud=('fraud_transactions', lambda x: (x > 0).sum()),
        total_fraud_txns=('fraud_transactions', 'sum'),
        total_fraud_volume=('fraud_volume', 'sum')
    ).reset_index()
    
    total_cust = len(profiles_df)
    summary['customer_share_pct'] = (summary['customer_count'] / total_cust * 100).round(2)
    summary['avg_risk_score'] = summary['avg_risk_score'].round(2)
    summary['total_volume'] = summary['total_volume'].round(2)
    summary['total_fraud_volume'] = summary['total_fraud_volume'].round(2)
    
    cat_order = {'Critical Risk': 0, 'High Risk': 1, 'Medium Risk': 2, 'Low Risk': 3}
    summary['sort_order'] = summary['risk_category'].map(cat_order)
    return summary.sort_values(by='sort_order').drop(columns=['sort_order'])
