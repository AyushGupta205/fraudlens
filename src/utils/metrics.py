import pandas as pd
import numpy as np
from typing import Dict, Any

def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    total_txns = len(df)
    total_val = float(df['amount'].sum()) if total_txns > 0 else 0.0
    
    fraud_mask = df['isFraud'] == 1
    fraud_txns = int(fraud_mask.sum())
    fraud_loss = float(df.loc[fraud_mask, 'amount'].sum()) if fraud_txns > 0 else 0.0
    
    legit_mask = df['isFraud'] == 0
    legit_txns = int(legit_mask.sum())
    legit_val = float(df.loc[legit_mask, 'amount'].sum()) if legit_txns > 0 else 0.0
    
    fraud_rate_pct = (fraud_txns / total_txns * 100) if total_txns > 0 else 0.0
    fraud_loss_rate_pct = (fraud_loss / total_val * 100) if total_val > 0 else 0.0
    
    avg_fraud_txn = float(df.loc[fraud_mask, 'amount'].mean()) if fraud_txns > 0 else 0.0
    avg_legit_txn = float(df.loc[legit_mask, 'amount'].mean()) if legit_txns > 0 else 0.0
    median_fraud_txn = float(df.loc[fraud_mask, 'amount'].median()) if fraud_txns > 0 else 0.0
    median_legit_txn = float(df.loc[legit_mask, 'amount'].median()) if legit_txns > 0 else 0.0
    
    flagged_txns = int(df['isFlaggedFraud'].sum()) if 'isFlaggedFraud' in df.columns else 0
    
    return {
        'total_transactions': total_txns,
        'total_transaction_value': round(total_val, 2),
        'fraud_transactions': fraud_txns,
        'fraud_loss': round(fraud_loss, 2),
        'legitimate_transactions': legit_txns,
        'legitimate_value': round(legit_val, 2),
        'fraud_rate_pct': round(fraud_rate_pct, 4),
        'fraud_loss_rate_pct': round(fraud_loss_rate_pct, 4),
        'avg_fraud_transaction': round(avg_fraud_txn, 2),
        'avg_legitimate_transaction': round(avg_legit_txn, 2),
        'median_fraud_transaction': round(median_fraud_txn, 2),
        'median_legitimate_transaction': round(median_legit_txn, 2),
        'system_flagged_transactions': flagged_txns
    }
