"""
FraudLens — Phase 3: Exploratory Data Analysis (EDA) Tests
Validates all analytical functions, metric aggregations, statistical computations,
confusion matrices, and data integrity checks for Phase 3.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.analysis.eda_analysis import (
    get_processed_data_path,
    calculate_dataset_overview,
    calculate_class_distribution,
    calculate_transaction_type_metrics,
    calculate_amount_statistics,
    calculate_temporal_patterns,
    calculate_origin_account_metrics,
    calculate_destination_account_metrics,
    calculate_account_drainage_metrics,
    calculate_zero_amount_metrics,
    calculate_flagged_fraud_metrics,
    calculate_fraud_concentration_metrics,
    calculate_statistical_comparisons,
    calculate_correlation_matrix,
    answer_business_questions
)

@pytest.fixture
def sample_eda_df():
    """Generates a synthetic DataFrame replicating the schema and edge cases of paysim_clean."""
    return pd.DataFrame({
        'step': [1, 2, 3, 25, 26, 49, 50, 75],
        'type': ['TRANSFER', 'CASH_OUT', 'PAYMENT', 'TRANSFER', 'CASH_OUT', 'CASH_IN', 'DEBIT', 'TRANSFER'],
        'amount': [500000.0, 500000.0, 150.0, 250000.0, 250000.0, 1000.0, 50.0, 0.0],
        'nameOrig': ['C1001', 'C1002', 'C1003', 'C1004', 'C1005', 'C1006', 'C1007', 'C1008'],
        'oldbalanceOrg': [500000.0, 500000.0, 1000.0, 250000.0, 250000.0, 0.0, 500.0, 0.0],
        'newbalanceOrig': [0.0, 0.0, 850.0, 0.0, 0.0, 1000.0, 450.0, 0.0],
        'nameDest': ['C2001', 'M3001', 'M3002', 'C2002', 'C2003', 'C2004', 'C2005', 'C2006'],
        'oldbalanceDest': [0.0, 0.0, 0.0, 10000.0, 0.0, 5000.0, 2000.0, 0.0],
        'newbalanceDest': [500000.0, 500000.0, 0.0, 260000.0, 250000.0, 4000.0, 2050.0, 0.0],
        'isFraud': [1, 1, 0, 1, 1, 0, 0, 1],
        'isFlaggedFraud': [1, 0, 0, 1, 0, 0, 0, 0],
        'transaction_hour': [0, 1, 2, 0, 1, 0, 1, 2],
        'transaction_day': [1, 1, 1, 2, 2, 3, 3, 4],
        'origin_balance_change': [500000.0, 500000.0, 150.0, 250000.0, 250000.0, -1000.0, 50.0, 0.0],
        'destination_balance_change': [500000.0, 500000.0, 0.0, 250000.0, 250000.0, -1000.0, 50.0, 0.0],
        'orig_balance_error': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'dest_balance_error': [0.0, 0.0, -150.0, 0.0, 0.0, -2000.0, 0.0, 0.0],
        'orig_balance_consistency': ['Consistent'] * 8,
        'amount_to_origin_balance_ratio': [1.0, 1.0, 0.15, 1.0, 1.0, 0.0, 0.1, 0.0],
        'amount_to_destination_balance_ratio': [0.0, 0.0, 0.0, 25.0, 0.0, 0.2, 0.025, 0.0],
        'zero_balance_origin_after_transaction': [1, 1, 0, 1, 1, 0, 0, 0],
        'zero_balance_destination_after_transaction': [0, 0, 1, 0, 0, 0, 0, 1]
    })

def test_processed_dataset_path():
    """1. Validates that the processed parquet file path exists."""
    path = get_processed_data_path()
    assert path.exists()
    assert path.suffix == '.parquet'

def test_dataset_overview_calculation(sample_eda_df):
    """2. Tests dataset overview metrics computation."""
    overview = calculate_dataset_overview(sample_eda_df)
    assert overview['total_rows'] == 8
    assert overview['total_cols'] == 22
    assert overview['fraud_count'] == 5
    assert overview['legit_count'] == 3
    assert overview['fraud_rate_pct'] == 62.5
    assert overview['unique_orig_accounts'] == 8
    assert overview['num_unique_types'] == 5

def test_class_distribution(sample_eda_df):
    """3. Tests class balance and ratio."""
    dist = calculate_class_distribution(sample_eda_df)
    assert dist['fraud_count'] == 5
    assert dist['legit_count'] == 3
    assert dist['fraud_pct'] == 62.5
    assert dist['legit_pct'] == 37.5

def test_transaction_type_aggregation(sample_eda_df):
    """4. Tests aggregation by transaction type."""
    type_metrics = calculate_transaction_type_metrics(sample_eda_df)
    assert len(type_metrics) == 5
    assert 'fraud_count' in type_metrics.columns
    assert 'fraud_rate_pct' in type_metrics.columns
    
    # Check TRANSFER stats
    transfer_stats = type_metrics[type_metrics['type'] == 'TRANSFER'].iloc[0]
    assert transfer_stats['transaction_count'] == 3
    assert transfer_stats['fraud_count'] == 3
    assert transfer_stats['fraud_rate_pct'] == 100.0

def test_amount_statistics(sample_eda_df):
    """5. Tests amount distribution metrics and comparison."""
    amt_stats = calculate_amount_statistics(sample_eda_df)
    assert amt_stats['fraud']['count'] == 5
    assert amt_stats['legit']['count'] == 3
    assert amt_stats['fraud']['mean'] > amt_stats['legit']['mean']
    assert amt_stats['mean_ratio'] > 1.0

def test_temporal_patterns(sample_eda_df):
    """6. Tests temporal hour and day aggregation."""
    temp_stats = calculate_temporal_patterns(sample_eda_df)
    assert 'hourly' in temp_stats
    assert 'daily' in temp_stats
    assert temp_stats['total_days_observed'] == 4
    assert 0 <= temp_stats['peak_fraud_rate_hour'] <= 23

def test_account_drainage_calculation(sample_eda_df):
    """7. Tests account complete drainage behavior."""
    drain = calculate_account_drainage_metrics(sample_eda_df)
    assert drain['total_drainage_tx'] == 4
    assert drain['drainage_fraud_count'] == 4
    assert drain['drainage_legit_count'] == 0
    assert drain['fraud_drainage_rate_pct'] == 80.0  # 4 out of 5 frauds drained

def test_zero_amount_calculation(sample_eda_df):
    """8. Tests zero-amount edge case detection."""
    zero_stats = calculate_zero_amount_metrics(sample_eda_df)
    assert zero_stats['zero_amount_count'] == 1
    assert zero_stats['zero_amount_fraud_count'] == 1
    assert zero_stats['zero_amount_fraud_rate_pct'] == 100.0

def test_flagged_fraud_confusion_matrix(sample_eda_df):
    """9. Tests isFlaggedFraud confusion table and precision/recall."""
    flags = calculate_flagged_fraud_metrics(sample_eda_df)
    assert flags['TP'] == 2
    assert flags['FP'] == 0
    assert flags['FN'] == 3
    assert flags['TN'] == 3
    assert flags['precision_pct'] == 100.0
    assert flags['recall_pct'] == 40.0

def test_correlation_matrix(sample_eda_df):
    """10. Tests numerical correlation computation."""
    corr = calculate_correlation_matrix(sample_eda_df)
    assert 'isFraud' in corr.columns
    assert 'amount' in corr.columns
    assert corr.loc['amount', 'amount'] == 1.0

def test_business_questions_answers(sample_eda_df):
    """11. Tests business questions answering function."""
    answers = answer_business_questions(sample_eda_df)
    assert len(answers) == 10
    assert "TRANSFER" in answers["Q1"]
    assert "CASH_OUT" in answers["Q2"]
