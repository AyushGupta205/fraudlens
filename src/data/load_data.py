"""
FraudLens ? Data Loading Module
Provides robust, configurable loading functions for the PaySim transaction dataset.
"""

import os
from pathlib import Path
from typing import Optional, List, Union
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Expected schema fields
EXPECTED_COLUMNS: List[str] = [
    'step',
    'type',
    'amount',
    'nameOrig',
    'oldbalanceOrg',
    'newbalanceOrig',
    'nameDest',
    'oldbalanceDest',
    'newbalanceDest',
    'isFraud',
    'isFlaggedFraud'
]

def get_dataset_path(custom_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Resolves the dataset file path using priority order:
    1. Explicit function argument
    2. Environment variable FRAUDLENS_DATA_PATH or DATA_RAW_PATH
    3. Standard repository relative paths under data/raw/
    4. Default KaggleHub cache directory on local environment
    """
    if custom_path:
        p = Path(custom_path)
        if p.exists():
            return p
        raise FileNotFoundError(f'Specified dataset path does not exist: {custom_path}')
        
    env_path = os.getenv('FRAUDLENS_DATA_PATH') or os.getenv('DATA_RAW_PATH')
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p

    # Check relative paths
    base_dir = Path(__file__).resolve().parent.parent.parent
    potential_paths = [
        base_dir / 'data' / 'raw' / 'PS_20174392719_1491204439457_log.csv',
        base_dir / 'data' / 'raw' / 'paysim.csv',
        base_dir / 'data' / 'raw' / 'transactions.csv',
        Path.home() / '.cache' / 'kagglehub' / 'datasets' / 'ealaxi' / 'paysim1' / 'versions' / '2' / 'PS_20174392719_1491204439457_log.csv'
    ]
    
    for candidate in potential_paths:
        if candidate.exists():
            return candidate
            
    raise FileNotFoundError(
        'PaySim dataset file could not be located. '
        'Please place the CSV in data/raw/ or set FRAUDLENS_DATA_PATH in .env. '
        'See DATASET_SETUP.md for instructions.'
    )

def validate_dataset_file(file_path: Path) -> bool:
    """
    Performs fast header inspection to ensure schema integrity before loading.
    """
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f'Dataset file does not exist: {file_path}')
        
    # Read only the header
    header_df = pd.read_csv(file_path, nrows=1)
    missing_cols = set(EXPECTED_COLUMNS) - set(header_df.columns)
    if missing_cols:
        raise ValueError(f'Dataset is missing required columns: {missing_cols}')
        
    return True

def load_dataset(
    file_path: Optional[Union[str, Path]] = None,
    nrows: Optional[int] = None,
    usecols: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Loads the PaySim transaction dataset into a Pandas DataFrame.
    
    Parameters:
        file_path: Optional custom path to dataset CSV.
        nrows: Optional limit on number of rows to load (useful for testing).
        usecols: Optional subset of columns to load.
        
    Returns:
        pd.DataFrame containing the transactions data.
    """
    path = get_dataset_path(file_path)
    validate_dataset_file(path)
    
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f'[FraudLens] Loading dataset from: {path} ({size_mb:.2f} MB)...')
    
    df = pd.read_csv(path, nrows=nrows, usecols=usecols)
    print(f'[FraudLens] Successfully loaded {len(df):,} records with {df.shape[1]} columns.')
    return df
