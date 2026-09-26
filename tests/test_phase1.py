import pytest
import pandas as pd
from pathlib import Path
from src.data.load_data import get_dataset_path, validate_dataset_file, load_dataset, EXPECTED_COLUMNS
from src.data.inspect_data import inspect_dataset

def test_dataset_path_resolution():
    path = get_dataset_path()
    assert path.exists()
    assert path.is_file()
    assert path.suffix == '.csv'

def test_validate_dataset_file_header():
    path = get_dataset_path()
    assert validate_dataset_file(path) is True

def test_load_dataset_sample():
    df_sample = load_dataset(nrows=100)
    assert isinstance(df_sample, pd.DataFrame)
    assert len(df_sample) == 100
    assert list(df_sample.columns) == EXPECTED_COLUMNS

def test_expected_columns_present():
    df_sample = load_dataset(nrows=10)
    for col in EXPECTED_COLUMNS:
        assert col in df_sample.columns

def test_fraud_target_column_integrity():
    df_sample = load_dataset(nrows=1000)
    assert 'isFraud' in df_sample.columns
    unique_values = set(df_sample['isFraud'].unique())
    assert unique_values.issubset({0, 1})

def test_inspect_dataset_structure():
    df_sample = load_dataset(nrows=1000)
    results = inspect_dataset(df_sample)
    
    assert 'dimensions' in results
    assert 'columns' in results
    assert 'numerical_statistics' in results
    assert 'categorical_summary' in results
    assert 'target_summary' in results
    assert 'validation' in results
    assert results['validation']['status'] == 'PASS'
