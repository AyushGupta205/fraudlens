"""
FraudLens — Phase 7: ML Data Preparation and Leakage Audit Module
Handles feature selection, leakage audit, stratified splitting, and validation partitioning.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.utils.config import PROCESSED_DATA_DIR, RANDOM_STATE
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Explicit feature definition
FEATURE_COLUMNS = [
    'step',
    'amount',
    'oldbalanceOrg',
    'newbalanceOrig',
    'oldbalanceDest',
    'newbalanceDest',
    'orig_balance_error',
    'dest_balance_error',
    'transaction_hour',
    'transaction_day',
    'origin_balance_change',
    'destination_balance_change',
    'amount_to_origin_balance_ratio',
    'amount_to_destination_balance_ratio',
    'zero_balance_origin_after_transaction',
    'zero_balance_destination_after_transaction',
    'is_transfer',
    'is_cashout',
    'is_payment',
    'is_dest_merchant'
]

EXCLUDED_COLUMNS = {
    'isFraud': 'Target variable',
    'isFlaggedFraud': 'Heuristic rule flag (excluded to prevent circular leakage)',
    'nameOrig': 'High-cardinality raw account identifier',
    'nameDest': 'High-cardinality raw recipient identifier',
    'type': 'Transformed into one-hot binary indicator columns (is_transfer, is_cashout, is_payment)',
    'orig_balance_consistency': 'Redundant categorical text label derived from orig_balance_error'
}


def audit_features(df: pd.DataFrame) -> Dict[str, Any]:
    """Performs a formal data leakage and feature classification audit."""
    cols = df.columns.tolist()
    
    leakage_risks = []
    if 'isFraud' in FEATURE_COLUMNS:
        leakage_risks.append('CRITICAL: isFraud is in FEATURE_COLUMNS')
    if 'isFlaggedFraud' in FEATURE_COLUMNS:
        leakage_risks.append('CRITICAL: isFlaggedFraud is in FEATURE_COLUMNS')
    if 'nameOrig' in FEATURE_COLUMNS or 'nameDest' in FEATURE_COLUMNS:
        leakage_risks.append('WARNING: Raw identifiers in FEATURE_COLUMNS')
        
    return {
        'total_dataset_columns': len(cols),
        'selected_features_count': len(FEATURE_COLUMNS),
        'selected_features': FEATURE_COLUMNS,
        'excluded_features': EXCLUDED_COLUMNS,
        'target_column': 'isFraud',
        'leakage_status': 'PASS (Zero Leakage)' if not leakage_risks else 'FAIL',
        'leakage_risks': leakage_risks
    }


def load_and_prepare_features(
    data_path: Path = None
) -> Tuple[pd.DataFrame, pd.Series, np.ndarray]:
    """
    Loads cleaned parquet data, generates one-hot indicators, and extracts feature matrix X and target y.
    """
    if data_path is None:
        data_path = PROCESSED_DATA_DIR / 'paysim_clean.parquet'
        
    logger.info(f'Loading cleaned data from {data_path}...')
    df = pd.read_parquet(data_path)
    
    # Feature extraction & binary indicator mapping
    X = pd.DataFrame(index=df.index)
    
    # Base numeric and engineered features
    base_numeric = [
        'step', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest',
        'orig_balance_error', 'dest_balance_error', 'transaction_hour', 'transaction_day',
        'origin_balance_change', 'destination_balance_change',
        'amount_to_origin_balance_ratio', 'amount_to_destination_balance_ratio',
        'zero_balance_origin_after_transaction', 'zero_balance_destination_after_transaction'
    ]
    for col in base_numeric:
        if col in df.columns:
            X[col] = df[col].astype(np.float32 if 'balance' in col or 'amount' in col or 'change' in col or 'error' in col or 'ratio' in col else np.int32)
            
    # Binary indicators from categoricals/strings
    X['is_transfer'] = (df['type'] == 'TRANSFER').astype(np.int8)
    X['is_cashout'] = (df['type'] == 'CASH_OUT').astype(np.int8)
    X['is_payment'] = (df['type'] == 'PAYMENT').astype(np.int8)
    X['is_dest_merchant'] = df['nameDest'].str.startswith('M').astype(np.int8)
    
    # Ensure column order matches FEATURE_COLUMNS
    X = X[FEATURE_COLUMNS].copy()
    y = df['isFraud'].astype(np.int8)
    amounts = df['amount'].to_numpy(dtype=np.float64)
    
    logger.info(f'Prepared feature matrix X: {X.shape}, target y: {y.shape} (Fraud cases: {y.sum():,})')
    return X, y, amounts


def create_train_test_splits(
    X: pd.DataFrame,
    y: pd.Series,
    amounts: np.ndarray = None,
    test_size: float = 0.2,
    random_state: int = RANDOM_STATE
) -> Dict[str, Any]:
    """
    Creates a stratified train/test split.
    """
    logger.info(f'Creating stratified split (test_size={test_size}, random_state={random_state})...')
    
    indices = np.arange(len(y))
    idx_train, idx_test = train_test_split(
        indices,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )
    
    X_train, X_test = X.iloc[idx_train].copy(), X.iloc[idx_test].copy()
    y_train, y_test = y.iloc[idx_train].copy(), y.iloc[idx_test].copy()
    amt_train = amounts[idx_train] if amounts is not None else None
    amt_test = amounts[idx_test] if amounts is not None else None
    
    logger.info(
        f'Train split: {len(y_train):,} rows ({y_train.sum():,} fraud, {y_train.mean():.4%}) | '
        f'Test split: {len(y_test):,} rows ({y_test.sum():,} fraud, {y_test.mean():.4%})'
    )
    
    return {
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'amt_train': amt_train,
        'amt_test': amt_test,
        'idx_train': idx_train,
        'idx_test': idx_test
    }


def create_validation_split(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    amt_train: np.ndarray = None,
    val_size: float = 0.2,
    random_state: int = RANDOM_STATE
) -> Dict[str, Any]:
    """
    Creates an internal validation split strictly from training data for threshold tuning.
    """
    logger.info(f'Creating internal validation split from X_train (val_size={val_size})...')
    indices = np.arange(len(y_train))
    idx_tr, idx_val = train_test_split(
        indices,
        test_size=val_size,
        random_state=random_state,
        stratify=y_train
    )
    
    return {
        'X_train_sub': X_train.iloc[idx_tr].copy(),
        'X_val': X_train.iloc[idx_val].copy(),
        'y_train_sub': y_train.iloc[idx_tr].copy(),
        'y_val': y_train.iloc[idx_val].copy(),
        'amt_val': amt_train[idx_val] if amt_train is not None else None
    }
