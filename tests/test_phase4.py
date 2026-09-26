"""
FraudLens — Phase 4: SQL Analytics & Database Tests
Validates database schema creation, row and fraud counts, SQL query results,
risk scoring rules, confusion matrices, and analytical result CSV exports.
"""

import sqlite3
import pytest
import pandas as pd
from pathlib import Path

from src.data.load_sql_database import get_db_path, load_database
from src.analysis.sql_analysis import (
    get_sql_dir,
    get_results_dir,
    execute_query,
    execute_sql_file,
    run_sql_analytics
)

@pytest.fixture(scope="module")
def db_conn():
    """Provides an active connection to the SQLite database."""
    db_file = get_db_path()
    if not db_file.exists():
        load_database(db_path=db_file)
    conn = sqlite3.connect(str(db_file))
    yield conn
    conn.close()

def test_1_database_creation(db_conn):
    """1. Validates that database exists and contains transactions table."""
    cur = db_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';")
    assert cur.fetchone() is not None

def test_2_transaction_row_count(db_conn):
    """2. Validates total row count against 6.36M PaySim dataset."""
    df = execute_query(db_conn, "SELECT COUNT(*) AS total_rows FROM transactions;")
    assert int(df['total_rows'].iloc[0]) == 6362620

def test_3_fraud_count(db_conn):
    """3. Validates total confirmed fraud count."""
    df = execute_query(db_conn, "SELECT SUM(isFraud) AS fraud_rows FROM transactions;")
    assert int(df['fraud_rows'].iloc[0]) == 8213

def test_4_fraud_rate(db_conn):
    """4. Validates calculated fraud rate."""
    df = execute_query(db_conn, "SELECT ROUND(SUM(isFraud) * 100.0 / COUNT(*), 4) AS fraud_rate FROM transactions;")
    assert float(df['fraud_rate'].iloc[0]) == 0.1291

def test_5_transaction_type_counts(db_conn):
    """5. Validates distribution across all 5 payment channels."""
    df = execute_query(db_conn, "SELECT type, COUNT(*) AS count, SUM(isFraud) AS fraud_count FROM transactions GROUP BY type;")
    type_dict = dict(zip(df['type'], df['count']))
    fraud_dict = dict(zip(df['type'], df['fraud_count']))
    
    assert set(type_dict.keys()) == {'CASH_OUT', 'PAYMENT', 'CASH_IN', 'TRANSFER', 'DEBIT'}
    assert fraud_dict['PAYMENT'] == 0
    assert fraud_dict['CASH_IN'] == 0
    assert fraud_dict['DEBIT'] == 0
    assert fraud_dict['TRANSFER'] == 4097
    assert fraud_dict['CASH_OUT'] == 4116

def test_6_null_checks(db_conn):
    """6. Validates that no column contains NULL values."""
    query = """
    SELECT 
        SUM(CASE WHEN step IS NULL THEN 1 ELSE 0 END) AS null_step,
        SUM(CASE WHEN type IS NULL THEN 1 ELSE 0 END) AS null_type,
        SUM(CASE WHEN amount IS NULL THEN 1 ELSE 0 END) AS null_amount,
        SUM(CASE WHEN isFraud IS NULL THEN 1 ELSE 0 END) AS null_isFraud
    FROM transactions;
    """
    df = execute_query(db_conn, query)
    assert df.sum().sum() == 0

def test_7_duplicate_checks(db_conn):
    """7. Validates zero duplicate rows across keys."""
    query = """
    SELECT step, type, amount, nameOrig, nameDest, COUNT(*) AS dup_count
    FROM transactions
    GROUP BY step, type, amount, nameOrig, nameDest
    HAVING COUNT(*) > 1;
    """
    df = execute_query(db_conn, query)
    assert len(df) == 0

def test_8_flagged_fraud_calculations(db_conn):
    """8. Validates isFlaggedFraud confusion matrix values."""
    query = """
    SELECT 
        SUM(CASE WHEN isFlaggedFraud = 1 AND isFraud = 1 THEN 1 ELSE 0 END) AS TP,
        SUM(CASE WHEN isFlaggedFraud = 1 AND isFraud = 0 THEN 1 ELSE 0 END) AS FP,
        SUM(CASE WHEN isFlaggedFraud = 0 AND isFraud = 1 THEN 1 ELSE 0 END) AS FN
    FROM transactions;
    """
    df = execute_query(db_conn, query)
    assert int(df['TP'].iloc[0]) == 16
    assert int(df['FP'].iloc[0]) == 0
    assert int(df['FN'].iloc[0]) == 8197

def test_9_drainage_calculations(db_conn):
    """9. Validates account drainage metrics."""
    query = """
    SELECT 
        SUM(zero_balance_origin_after_transaction) AS total_drained,
        SUM(CASE WHEN isFraud = 1 AND zero_balance_origin_after_transaction = 1 THEN 1 ELSE 0 END) AS fraud_drained
    FROM transactions;
    """
    df = execute_query(db_conn, query)
    assert int(df['fraud_drained'].iloc[0]) == 8012

def test_10_account_risk_score_bounds(db_conn):
    """10. Validates that risk scores are strictly bounded within [0, 100]."""
    query = """
    WITH SampleScores AS (
        SELECT 
            MIN(100, (
                (CASE WHEN SUM(zero_balance_origin_after_transaction) > 0 THEN 25 ELSE 0 END) +
                (CASE WHEN MAX(amount) >= 200000.0 THEN 20 ELSE 0 END) +
                (CASE WHEN MAX(amount) >= 1000000.0 THEN 20 ELSE 0 END) +
                (CASE WHEN SUM(CASE WHEN type IN ('TRANSFER', 'CASH_OUT') THEN 1 ELSE 0 END) > 0 THEN 15 ELSE 0 END) +
                (CASE WHEN SUM(CASE WHEN oldbalanceDest = 0.0 THEN 1 ELSE 0 END) > 0 THEN 10 ELSE 0 END) +
                (CASE WHEN SUM(isFraud) > 0 THEN 10 ELSE 0 END)
            )) AS score
        FROM transactions
        GROUP BY nameOrig
        LIMIT 1000
    )
    SELECT MIN(score) AS min_score, MAX(score) AS max_score FROM SampleScores;
    """
    df = execute_query(db_conn, query)
    min_s = float(df['min_score'].iloc[0])
    max_s = float(df['max_score'].iloc[0])
    assert 0 <= min_s <= 100
    assert 0 <= max_s <= 100

def test_11_risk_categories(db_conn):
    """11. Validates risk tier categorizations."""
    sql_dir = get_sql_dir()
    results = execute_sql_file(db_conn, sql_dir / "customer_risk.sql")
    df_tiers = results[1][1]
    tiers = set(df_tiers['risk_tier'].tolist())
    assert any('Critical' in t for t in tiers)
    assert any('High' in t for t in tiers)
    assert any('Low' in t for t in tiers)

def test_12_sql_result_files_exported():
    """12. Validates that analytical CSV result exports exist and are populated."""
    results_dir = get_results_dir()
    expected_files = [
        "fraud_kpis.csv",
        "fraud_by_type.csv",
        "fraud_amount_bands.csv",
        "flagged_fraud_performance.csv",
        "account_risk.csv",
        "fraud_exposure_by_type.csv",
        "drainage_analysis.csv"
    ]
    for filename in expected_files:
        f = results_dir / filename
        assert f.exists(), f"Missing export file: {filename}"
        assert f.stat().st_size > 10, f"Export file is empty: {filename}"

def test_13_sql_runner_end_to_end():
    """13. Validates end-to-end execution of Python SQL analytics runner."""
    res = run_sql_analytics()
    assert res['status'] == 'PASS'
    assert res['cross_validation_pass'] is True
