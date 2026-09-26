"""
FraudLens ? Phase 2 Unit Tests
Tests the data cleaning pipeline, balance consistency calculations, feature engineering,
categorical validation, and ground-truth preservation.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data.load_data import load_dataset
from src.data.clean_data import (
    clean_dataset,
    standardize_columns,
    handle_missing_values,
    handle_duplicates,
    validate_numeric_columns,
    validate_categorical_columns,
    calculate_balance_errors,
    engineer_analytical_features,
    validate_transaction_logic,
    VALID_TRANSACTION_TYPES
)

@pytest.fixture
def sample_raw_df():
    return pd.DataFrame({
        'step': [1, 2, 3],
        'type': ['TRANSFER', 'CASH_OUT', 'PAYMENT'],
        'amount': [100000.0, 50000.0, 150.0],
        'nameOrig': ['C1001', 'C1002', 'C1003'],
        'oldbalanceOrg': [100000.0, 50000.0, 1000.0],
        'newbalanceOrig': [0.0, 0.0, 850.0],
        'nameDest': ['C2001', 'C2002', 'M3001'],
        'oldbalanceDest': [0.0, 20000.0, 0.0],
        'newbalanceDest': [100000.0, 70000.0, 0.0],
        'isFraud': [1, 1, 0],
        'isFlaggedFraud': [0, 0, 0]
    })

def test_standardize_columns(sample_raw_df):
    cleaned = standardize_columns(sample_raw_df)
    assert cleaned['step'].dtype == np.int32
    assert cleaned['amount'].dtype == np.float64
    assert cleaned['isFraud'].dtype == np.int8
    assert len(cleaned) == len(sample_raw_df)

def test_handle_missing_values(sample_raw_df):
    _, audit = handle_missing_values(sample_raw_df)
    assert audit['total_missing'] == 0
    assert isinstance(audit['missing_per_column'], dict)

def test_handle_duplicates_no_duplicates(sample_raw_df):
    _, dup_count = handle_duplicates(sample_raw_df)
    assert dup_count == 0

def test_validate_numeric_columns_valid(sample_raw_df):
    audit = validate_numeric_columns(sample_raw_df)
    assert audit['is_valid'] is True
    assert sum(audit['negative_counts'].values()) == 0

def test_validate_categorical_columns_valid(sample_raw_df):
    audit = validate_categorical_columns(sample_raw_df)
    assert audit['is_valid'] is True
    assert len(audit['unexpected_types']) == 0

def test_calculate_balance_errors(sample_raw_df):
    df_err = calculate_balance_errors(sample_raw_df)
    
    assert 'orig_balance_error' in df_err.columns
    assert 'dest_balance_error' in df_err.columns
    assert 'orig_balance_consistency' in df_err.columns
    
    # Check exact balance math:
    # Row 0: oldbalanceOrg (100k) - amount (100k) == 0.0 == newbalanceOrig => error = 0.0
    assert df_err.loc[0, 'orig_balance_error'] == pytest.approx(0.0, 0.001)
    assert df_err.loc[0, 'orig_balance_consistency'] == 'Consistent'

def test_engineer_analytical_features(sample_raw_df):
    df_feat = engineer_analytical_features(sample_raw_df)
    
    expected_new_cols = [
        'transaction_hour',
        'transaction_day',
        'origin_balance_change',
        'destination_balance_change',
        'amount_to_origin_balance_ratio',
        'amount_to_destination_balance_ratio',
        'zero_balance_origin_after_transaction',
        'zero_balance_destination_after_transaction'
    ]
    for col in expected_new_cols:
        assert col in df_feat.columns
        
    assert df_feat.loc[0, 'zero_balance_origin_after_transaction'] == 1
    assert df_feat.loc[2, 'zero_balance_origin_after_transaction'] == 0

def test_validate_transaction_logic(sample_raw_df):
    audit = validate_transaction_logic(sample_raw_df)
    assert audit['target_valid'] is True
    assert audit['fraud_count'] == 2
    assert audit['legit_count'] == 1

def test_clean_dataset_end_to_end():
    sample_df = load_dataset(nrows=500)
    df_clean, audit = clean_dataset(sample_df)
    
    assert len(df_clean) == 500
    assert audit['status'] == 'PASS'
    assert df_clean.shape[1] > sample_df.shape[1]
    assert df_clean['isFraud'].nunique() <= 2
