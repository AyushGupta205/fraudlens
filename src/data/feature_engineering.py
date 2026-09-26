import pandas as pd
import numpy as np
from src.utils.logger import get_logger

logger = get_logger(__name__)

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    logger.info('Engineering features for fraud analytics and machine learning...')
    df_feat = df.copy()
    
    # 1. Temporal features (1 step = 1 hour)
    df_feat['hour_of_day'] = (df_feat['step'] - 1) % 24
    df_feat['day_of_month'] = ((df_feat['step'] - 1) // 24) + 1
    df_feat['day_of_week'] = ((df_feat['step'] - 1) // 24) % 7
    df_feat['is_weekend'] = (df_feat['day_of_week'] >= 5).astype(int)
    df_feat['is_night_hours'] = ((df_feat['hour_of_day'] >= 0) & (df_feat['hour_of_day'] <= 6)).astype(int)
    
    # 2. Financial Balance Dynamics & Discrepancies
    df_feat['orig_balance_error'] = df_feat['newbalanceOrig'] + df_feat['amount'] - df_feat['oldbalanceOrg']
    df_feat['dest_balance_error'] = df_feat['oldbalanceDest'] + df_feat['amount'] - df_feat['newbalanceDest']
    
    df_feat['orig_drain_ratio'] = np.where(
        df_feat['oldbalanceOrg'] > 0,
        np.clip(df_feat['amount'] / df_feat['oldbalanceOrg'], 0, 10.0),
        0.0
    )
    
    df_feat['is_orig_fully_emptied'] = (
        (df_feat['oldbalanceOrg'] > 0) & (df_feat['newbalanceOrig'] == 0)
    ).astype(int)
    
    df_feat['is_orig_zero_initial'] = (df_feat['oldbalanceOrg'] == 0).astype(int)
    df_feat['is_dest_zero_initial'] = (df_feat['oldbalanceDest'] == 0).astype(int)
    
    # 3. Entity metadata (Customer vs Merchant)
    df_feat['is_dest_merchant'] = df_feat['nameDest'].astype(str).str.startswith('M').astype(int)
    df_feat['is_orig_merchant'] = df_feat['nameOrig'].astype(str).str.startswith('M').astype(int)
    
    # 4. Log transform of transaction amount
    df_feat['log_amount'] = np.log1p(df_feat['amount'])
    
    # 5. Type flags
    df_feat['is_transfer'] = (df_feat['type'] == 'TRANSFER').astype(int)
    df_feat['is_cashout'] = (df_feat['type'] == 'CASH_OUT').astype(int)
    df_feat['is_transfer_or_cashout'] = df_feat['type'].isin(['TRANSFER', 'CASH_OUT']).astype(int)
    
    logger.info(f'Feature engineering complete. Total columns: {df_feat.shape[1]}')
    return df_feat
