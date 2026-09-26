"""
FraudLens — Phase 4: High-Performance Database Loading Module
Loads the cleaned PaySim analytical dataset (paysim_clean.parquet) into a local
high-performance SQLite database (data/processed/fraudlens.db) using direct C-level bulk insertion.
"""

import os
import sqlite3
import time
from pathlib import Path
from typing import Optional, Union, Dict, Any

import pandas as pd

def get_db_path(custom_path: Optional[Union[str, Path]] = None) -> Path:
    """Resolves target SQLite database path."""
    if custom_path:
        return Path(custom_path)
    base_dir = Path(__file__).resolve().parent.parent.parent
    return base_dir / "data" / "processed" / "fraudlens.db"

def get_parquet_path(custom_path: Optional[Union[str, Path]] = None) -> Path:
    """Resolves source cleaned parquet path."""
    if custom_path:
        p = Path(custom_path)
        if p.exists():
            return p
        raise FileNotFoundError(f"Source parquet not found: {custom_path}")
    base_dir = Path(__file__).resolve().parent.parent.parent
    p = base_dir / "data" / "processed" / "paysim_clean.parquet"
    if p.exists():
        return p
    raise FileNotFoundError(f"Cleaned dataset not found at: {p}. Run Phase 2 first.")

def load_database(
    db_path: Optional[Union[str, Path]] = None,
    parquet_path: Optional[Union[str, Path]] = None,
    chunksize: int = 250000
) -> Dict[str, Any]:
    """
    Creates and populates the SQLite transactions database from the cleaned parquet dataset.
    Rerunnable, memory-efficient, and optimized for sub-minute insertion.
    """
    target_db = get_db_path(db_path)
    source_parquet = get_parquet_path(parquet_path)
    target_db.parent.mkdir(parents=True, exist_ok=True)
    
    start_time = time.time()
    print(f"[FraudLens DB] Loading dataset from: {source_parquet}")
    print(f"[FraudLens DB] Target SQLite database: {target_db}")
    
    df = pd.read_parquet(source_parquet)
    total_records = len(df)
    
    # Close any existing connections by connecting fresh
    conn = sqlite3.connect(str(target_db))
    cur = conn.cursor()
    
    # Configure SQLite PRAGMAs for high-speed batch operations
    cur.execute("PRAGMA synchronous = OFF;")
    cur.execute("PRAGMA journal_mode = MEMORY;")
    cur.execute("PRAGMA cache_size = 100000;")
    cur.execute("PRAGMA temp_store = MEMORY;")
    cur.execute("PRAGMA locking_mode = EXCLUSIVE;")
    
    # Drop existing table if present
    cur.execute("DROP TABLE IF EXISTS transactions;")
    
    # Create base table
    cur.execute("""
    CREATE TABLE transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        step INTEGER NOT NULL,
        type VARCHAR(20) NOT NULL,
        amount REAL NOT NULL,
        nameOrig VARCHAR(50) NOT NULL,
        oldbalanceOrg REAL NOT NULL,
        newbalanceOrig REAL NOT NULL,
        nameDest VARCHAR(50) NOT NULL,
        oldbalanceDest REAL NOT NULL,
        newbalanceDest REAL NOT NULL,
        isFraud INTEGER NOT NULL DEFAULT 0,
        isFlaggedFraud INTEGER NOT NULL DEFAULT 0,
        transaction_hour INTEGER NOT NULL,
        transaction_day INTEGER NOT NULL,
        origin_balance_change REAL NOT NULL,
        destination_balance_change REAL NOT NULL,
        orig_balance_error REAL NOT NULL,
        dest_balance_error REAL NOT NULL,
        orig_balance_consistency VARCHAR(50) NOT NULL,
        amount_to_origin_balance_ratio REAL NOT NULL,
        amount_to_destination_balance_ratio REAL NOT NULL,
        zero_balance_origin_after_transaction INTEGER NOT NULL,
        zero_balance_destination_after_transaction INTEGER NOT NULL
    );
    """)
    conn.commit()
    
    cols = [
        'step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 'newbalanceOrig',
        'nameDest', 'oldbalanceDest', 'newbalanceDest', 'isFraud', 'isFlaggedFraud',
        'transaction_hour', 'transaction_day', 'origin_balance_change',
        'destination_balance_change', 'orig_balance_error', 'dest_balance_error',
        'orig_balance_consistency', 'amount_to_origin_balance_ratio',
        'amount_to_destination_balance_ratio', 'zero_balance_origin_after_transaction',
        'zero_balance_destination_after_transaction'
    ]
    
    insert_sql = f"INSERT INTO transactions ({', '.join(cols)}) VALUES ({', '.join(['?'] * len(cols))});"
    
    print(f"[FraudLens DB] Ingesting {total_records:,} records in fast batches...")
    
    # Process in slices to keep memory footprint lean
    for start_idx in range(0, total_records, chunksize):
        end_idx = min(start_idx + chunksize, total_records)
        chunk_tuples = list(df.iloc[start_idx:end_idx][cols].itertuples(index=False, name=None))
        cur.executemany(insert_sql, chunk_tuples)
        conn.commit()
        print(f"  -> Ingested rows {end_idx:,} / {total_records:,} ({(end_idx/total_records*100):.1f}%)")
        
    print("[FraudLens DB] Building analytical indexes...")
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_tx_step ON transactions(step);",
        "CREATE INDEX IF NOT EXISTS idx_tx_type ON transactions(type);",
        "CREATE INDEX IF NOT EXISTS idx_tx_nameOrig ON transactions(nameOrig);",
        "CREATE INDEX IF NOT EXISTS idx_tx_nameDest ON transactions(nameDest);",
        "CREATE INDEX IF NOT EXISTS idx_tx_isFraud ON transactions(isFraud);",
        "CREATE INDEX IF NOT EXISTS idx_tx_isFlaggedFraud ON transactions(isFlaggedFraud);",
        "CREATE INDEX IF NOT EXISTS idx_tx_type_isFraud ON transactions(type, isFraud);",
        "CREATE INDEX IF NOT EXISTS idx_tx_drainage ON transactions(zero_balance_origin_after_transaction);",
        "CREATE INDEX IF NOT EXISTS idx_tx_hour ON transactions(transaction_hour);",
        "CREATE INDEX IF NOT EXISTS idx_tx_amount ON transactions(amount);"
    ]
    for idx_sql in indexes:
        cur.execute(idx_sql)
    conn.commit()
    
    # Verification query
    cur.execute("SELECT COUNT(*), SUM(isFraud), SUM(isFlaggedFraud) FROM transactions;")
    row_count, fraud_count, flagged_count = cur.fetchone()
    
    # Reset locking and journal mode
    cur.execute("PRAGMA locking_mode = NORMAL;")
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")
    conn.commit()
    conn.close()
    
    elapsed = time.time() - start_time
    print(f"[FraudLens DB] Ingestion complete in {elapsed:.2f}s!")
    print(f"[FraudLens DB] Verified: {row_count:,} rows, {fraud_count:,} fraud incidents, {flagged_count:,} flagged.")
    
    return {
        "db_path": str(target_db),
        "total_rows": row_count,
        "fraud_count": fraud_count,
        "flagged_count": flagged_count,
        "elapsed_seconds": round(elapsed, 2),
        "status": "PASS" if row_count == total_records and fraud_count == 8213 else "FAIL"
    }

if __name__ == "__main__":
    load_database()
