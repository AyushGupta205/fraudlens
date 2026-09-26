import pytest
import pandas as pd
import numpy as np
from src.data.clean_data import clean_data, perform_data_quality_audit
from src.data.feature_engineering import engineer_features

def test_clean_data_validates_and_handles_types():
    raw_dict = {
        'step': ['1', '2'],
        'type': [' payment ', 'transfer'],
        'amount': ['100.50', '250000.0'],
        'nameOrig': ['C123 ', ' C456'],
        'oldbalanceOrg': ['500.0', '250000.0'],
        'newbalanceOrig': ['399.50', '0.0'],
        'nameDest': ['M789 ', ' C999'],
        'oldbalanceDest': ['0.0', '0.0'],
        'newbalanceDest': ['0.0', '250000.0'],
        'isFraud': ['0', '1']
    }
    df = pd.DataFrame(raw_dict)
    clean_df, audit = clean_data(df)
    
    assert len(clean_df) == 2
    assert clean_df['type'].tolist() == ['PAYMENT', 'TRANSFER']
    assert clean_df['nameOrig'].tolist() == ['C123', 'C456']
    assert np.issubdtype(clean_df['isFraud'].dtype, np.integer)
    assert audit['status'] == 'PASS'

def test_feature_engineering_creates_expected_columns():
    df = pd.DataFrame({
        'step': [1, 25],
        'type': ['TRANSFER', 'CASH_OUT'],
        'amount': [1000.0, 5000.0],
        'nameOrig': ['C1', 'C2'],
        'oldbalanceOrg': [1000.0, 5000.0],
        'newbalanceOrig': [0.0, 0.0],
        'nameDest': ['C3', 'M4'],
        'oldbalanceDest': [0.0, 0.0],
        'newbalanceDest': [1000.0, 0.0],
        'isFraud': [1, 0]
    })
    feat_df = engineer_features(df)
    
    assert 'hour_of_day' in feat_df.columns
    assert 'orig_balance_error' in feat_df.columns
    assert 'is_orig_fully_emptied' in feat_df.columns
    assert feat_df.loc[0, 'hour_of_day'] == 0
    assert feat_df.loc[1, 'hour_of_day'] == 0  # (25-1) % 24 = 0
    assert feat_df.loc[0, 'is_orig_fully_emptied'] == 1
