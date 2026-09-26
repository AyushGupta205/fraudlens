"""
FraudLens — High-Performance SQLite Data Access Layer
Queries data/processed/fraudlens.db with caching, indexing, and pagination.
Never loads 6.36M rows into memory. Reconciles 100% with Phase 4/5 ground truth.
"""

import sqlite3
import pandas as pd
import streamlit as st
from typing import Dict, Any, Tuple, Optional
from dashboard.config import DB_PATH, POWERBI_DIR


@st.cache_resource
def get_db_connection() -> sqlite3.Connection:
    """Returns a thread-safe connection to the SQLite database with read-only PRAGMAs."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"FraudLens database not found at {DB_PATH}. Please run Phase 4 setup.")
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON;")
    return conn


@st.cache_data(ttl=3600)
def get_macro_kpis() -> Dict[str, Any]:
    """
    Retrieves overall platform KPIs via indexed aggregate SQL query.
    Reconciles with Phase 4/5: 6,362,620 txns, 8,213 frauds, $12.06B exposure.
    """
    conn = get_db_connection()
    query = """
    SELECT 
        COUNT(*) AS total_transactions,
        SUM(amount) AS total_volume,
        SUM(isFraud) AS fraud_transactions,
        SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) AS fraud_exposure,
        AVG(amount) AS avg_transaction_amount,
        AVG(CASE WHEN isFraud = 1 THEN amount ELSE NULL END) AS avg_fraud_amount,
        AVG(CASE WHEN isFraud = 0 THEN amount ELSE NULL END) AS avg_legit_amount,
        SUM(isFlaggedFraud) AS flagged_count,
        SUM(CASE WHEN isFraud = 1 AND isFlaggedFraud = 1 THEN 1 ELSE 0 END) AS flagged_tp,
        SUM(CASE WHEN isFraud = 1 AND isFlaggedFraud = 0 THEN 1 ELSE 0 END) AS flagged_fn,
        SUM(CASE WHEN isFraud = 0 AND isFlaggedFraud = 1 THEN 1 ELSE 0 END) AS flagged_fp,
        SUM(CASE WHEN isFraud = 0 AND isFlaggedFraud = 0 THEN 1 ELSE 0 END) AS flagged_tn,
        SUM(CASE WHEN zero_balance_origin_after_transaction = 1 THEN 1 ELSE 0 END) AS total_drainage,
        SUM(CASE WHEN isFraud = 1 AND zero_balance_origin_after_transaction = 1 THEN 1 ELSE 0 END) AS fraud_drainage
    FROM transactions;
    """
    row = conn.execute(query).fetchone()
    total_tx = row["total_transactions"]
    fraud_tx = row["fraud_transactions"]
    fraud_exp = row["fraud_exposure"]
    total_vol = row["total_volume"]
    fraud_rate = (fraud_tx / total_tx * 100) if total_tx else 0.0

    return {
        "total_transactions": total_tx,
        "total_volume": total_vol,
        "fraud_transactions": fraud_tx,
        "fraud_exposure": fraud_exp,
        "fraud_rate_pct": fraud_rate,
        "legit_transactions": total_tx - fraud_tx,
        "legit_volume": total_vol - fraud_exp,
        "avg_transaction_amount": row["avg_transaction_amount"],
        "avg_fraud_amount": row["avg_fraud_amount"],
        "avg_legit_amount": row["avg_legit_amount"],
        "flagged_count": row["flagged_count"],
        "flagged_tp": row["flagged_tp"],
        "flagged_fn": row["flagged_fn"],
        "flagged_fp": row["flagged_fp"],
        "flagged_tn": row["flagged_tn"],
        "flagged_precision": (row["flagged_tp"] / (row["flagged_tp"] + row["flagged_fp"]) * 100) if (row["flagged_tp"] + row["flagged_fp"]) else 0.0,
        "flagged_recall": (row["flagged_tp"] / (row["flagged_tp"] + row["flagged_fn"]) * 100) if (row["flagged_tp"] + row["flagged_fn"]) else 0.0,
        "total_drainage": row["total_drainage"],
        "fraud_drainage": row["fraud_drainage"],
        "fraud_drainage_pct": (row["fraud_drainage"] / fraud_tx * 100) if fraud_tx else 0.0,
    }


@st.cache_data(ttl=3600)
def get_channel_metrics() -> pd.DataFrame:
    """Retrieves transaction type breakdown for Volume, Fraud Count, Rate, and Exposure."""
    conn = get_db_connection()
    query = """
    SELECT 
        type AS transaction_type,
        COUNT(*) AS total_transactions,
        SUM(amount) AS total_volume,
        SUM(isFraud) AS fraud_transactions,
        SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) AS fraud_exposure,
        ROUND(CAST(SUM(isFraud) AS FLOAT) / COUNT(*) * 100, 4) AS fraud_rate_pct,
        AVG(amount) AS avg_amount,
        AVG(CASE WHEN isFraud = 1 THEN amount ELSE NULL END) AS avg_fraud_amount,
        AVG(CASE WHEN isFraud = 0 THEN amount ELSE NULL END) AS avg_legit_amount
    FROM transactions
    GROUP BY type
    ORDER BY fraud_transactions DESC, total_transactions DESC;
    """
    return pd.read_sql_query(query, conn)


@st.cache_data(ttl=3600)
def get_daily_exposure_trajectory() -> pd.DataFrame:
    """Retrieves 31-day fraud exposure trajectory with 7-day rolling baseline."""
    conn = get_db_connection()
    query = """
    SELECT 
        transaction_day AS simulation_day,
        COUNT(*) AS total_transactions,
        SUM(amount) AS total_volume,
        SUM(isFraud) AS fraud_transactions,
        SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) AS fraud_exposure
    FROM transactions
    GROUP BY transaction_day
    ORDER BY transaction_day;
    """
    df = pd.read_sql_query(query, conn)
    df["rolling_7d_exposure"] = df["fraud_exposure"].rolling(window=7, min_periods=1).mean()
    return df


@st.cache_data(ttl=3600)
def get_diurnal_hourly_pattern() -> pd.DataFrame:
    """Retrieves 24-hour diurnal pattern comparing total volume and fraud incidents."""
    conn = get_db_connection()
    query = """
    SELECT 
        transaction_hour AS hour_of_day,
        COUNT(*) AS total_transactions,
        SUM(amount) AS total_volume,
        SUM(isFraud) AS fraud_transactions,
        SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) AS fraud_exposure,
        ROUND(CAST(SUM(isFraud) AS FLOAT) / COUNT(*) * 100, 4) AS fraud_rate_pct
    FROM transactions
    GROUP BY transaction_hour
    ORDER BY transaction_hour;
    """
    return pd.read_sql_query(query, conn)


@st.cache_data(ttl=3600)
def get_amount_bands_summary() -> pd.DataFrame:
    """Retrieves exposure and incident distribution across monetary sizing bands."""
    conn = get_db_connection()
    query = """
    SELECT 
        CASE 
            WHEN amount < 10000 THEN '< 10k'
            WHEN amount >= 10000 AND amount < 100000 THEN '10k - 100k'
            WHEN amount >= 100000 AND amount < 500000 THEN '100k - 500k'
            WHEN amount >= 500000 AND amount < 1000000 THEN '500k - 1M'
            WHEN amount >= 1000000 AND amount < 5000000 THEN '1M - 5M'
            ELSE '5M+'
        END AS amount_band,
        COUNT(*) AS total_transactions,
        SUM(amount) AS total_volume,
        SUM(isFraud) AS fraud_transactions,
        SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) AS fraud_exposure,
        ROUND(CAST(SUM(isFraud) AS FLOAT) / COUNT(*) * 100, 4) AS fraud_rate_pct
    FROM transactions
    GROUP BY 
        CASE 
            WHEN amount < 10000 THEN '< 10k'
            WHEN amount >= 10000 AND amount < 100000 THEN '10k - 100k'
            WHEN amount >= 100000 AND amount < 500000 THEN '100k - 500k'
            WHEN amount >= 500000 AND amount < 1000000 THEN '500k - 1M'
            WHEN amount >= 1000000 AND amount < 5000000 THEN '1M - 5M'
            ELSE '5M+'
        END
    ORDER BY 
        CASE amount_band
            WHEN '< 10k' THEN 1
            WHEN '10k - 100k' THEN 2
            WHEN '100k - 500k' THEN 3
            WHEN '500k - 1M' THEN 4
            WHEN '1M - 5M' THEN 5
            WHEN '5M+' THEN 6
            ELSE 7
        END;
    """
    return pd.read_sql_query(query, conn)


@st.cache_data(ttl=3600)
def get_risk_tier_portfolio() -> pd.DataFrame:
    """Retrieves portfolio behavioral risk tier distribution."""
    conn = get_db_connection()
    query = """
    WITH scored_txns AS (
        SELECT 
            amount,
            isFraud,
            MIN(100, (
                (CASE WHEN zero_balance_origin_after_transaction = 1 THEN 25 ELSE 0 END) +
                (CASE WHEN amount >= 200000.0 THEN 20 ELSE 0 END) +
                (CASE WHEN amount >= 1000000.0 THEN 20 ELSE 0 END) +
                (CASE WHEN type IN ('TRANSFER', 'CASH_OUT') THEN 15 ELSE 0 END) +
                (CASE WHEN oldbalanceDest = 0.0 THEN 10 ELSE 0 END) +
                (CASE WHEN isFraud = 1 THEN 10 ELSE 0 END)
            )) AS risk_score
        FROM transactions
    )
    SELECT 
        CASE 
            WHEN risk_score >= 76 THEN 'Critical'
            WHEN risk_score >= 51 THEN 'High'
            WHEN risk_score >= 26 THEN 'Medium'
            ELSE 'Low'
        END AS risk_category,
        COUNT(*) AS total_accounts,
        SUM(isFraud) AS fraud_associated_accounts,
        ROUND(CAST(SUM(isFraud) AS FLOAT) / COUNT(*) * 100, 4) AS account_fraud_rate_pct,
        ROUND(SUM(amount), 2) AS total_volume
    FROM scored_txns
    GROUP BY 
        CASE 
            WHEN risk_score >= 76 THEN 'Critical'
            WHEN risk_score >= 51 THEN 'High'
            WHEN risk_score >= 26 THEN 'Medium'
            ELSE 'Low'
        END
    ORDER BY 
        CASE risk_category
            WHEN 'Critical' THEN 1
            WHEN 'High' THEN 2
            WHEN 'Medium' THEN 3
            WHEN 'Low' THEN 4
        END;
    """
    return pd.read_sql_query(query, conn)


@st.cache_data(ttl=600)
def get_top_risk_accounts(
    risk_category: Optional[str] = None,
    min_score: int = 0,
    min_fraud_count: int = 0,
    min_volume: float = 0.0,
    limit: int = 25,
    offset: int = 0
) -> Tuple[pd.DataFrame, int]:
    """
    Queries account-level risk profiles with filtering and pagination.
    Uses indexed queries to avoid full memory loads.
    """
    conn = get_db_connection()
    where_clauses = []
    params = []

    if risk_category and risk_category != "All":
        if risk_category == "Critical":
            where_clauses.append("risk_score >= 76")
        elif risk_category == "High":
            where_clauses.append("risk_score BETWEEN 51 AND 75")
        elif risk_category == "Medium":
            where_clauses.append("risk_score BETWEEN 26 AND 50")
        elif risk_category == "Low":
            where_clauses.append("risk_score <= 25")

    if min_score > 0:
        where_clauses.append("risk_score >= ?")
        params.append(min_score)

    if min_fraud_count > 0:
        where_clauses.append("isFraud >= ?")
        params.append(min_fraud_count)

    if min_volume > 0:
        where_clauses.append("amount >= ?")
        params.append(min_volume)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    count_query = f"""
    WITH scored_txns AS (
        SELECT 
            nameOrig AS account_id,
            amount,
            isFraud,
            zero_balance_origin_after_transaction AS is_drainage,
            MIN(100, (
                (CASE WHEN zero_balance_origin_after_transaction = 1 THEN 25 ELSE 0 END) +
                (CASE WHEN amount >= 200000.0 THEN 20 ELSE 0 END) +
                (CASE WHEN amount >= 1000000.0 THEN 20 ELSE 0 END) +
                (CASE WHEN type IN ('TRANSFER', 'CASH_OUT') THEN 15 ELSE 0 END) +
                (CASE WHEN oldbalanceDest = 0.0 THEN 10 ELSE 0 END) +
                (CASE WHEN isFraud = 1 THEN 10 ELSE 0 END)
            )) AS risk_score
        FROM transactions
    )
    SELECT COUNT(DISTINCT account_id) FROM scored_txns {where_sql};
    """
    total_matches = conn.execute(count_query, params).fetchone()[0]

    data_query = f"""
    WITH scored_txns AS (
        SELECT 
            transaction_id,
            nameOrig AS account_id,
            amount,
            type,
            isFraud,
            zero_balance_origin_after_transaction AS is_drainage,
            MIN(100, (
                (CASE WHEN zero_balance_origin_after_transaction = 1 THEN 25 ELSE 0 END) +
                (CASE WHEN amount >= 200000.0 THEN 20 ELSE 0 END) +
                (CASE WHEN amount >= 1000000.0 THEN 20 ELSE 0 END) +
                (CASE WHEN type IN ('TRANSFER', 'CASH_OUT') THEN 15 ELSE 0 END) +
                (CASE WHEN oldbalanceDest = 0.0 THEN 10 ELSE 0 END) +
                (CASE WHEN isFraud = 1 THEN 10 ELSE 0 END)
            )) AS risk_score
        FROM transactions
    )
    SELECT 
        account_id,
        COUNT(*) AS transaction_count,
        SUM(amount) AS total_transaction_value,
        SUM(isFraud) AS fraud_count,
        SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0 END) AS fraud_exposure,
        ROUND(CAST(SUM(isFraud) AS FLOAT) / COUNT(*) * 100, 2) AS fraud_rate_pct,
        SUM(is_drainage) AS drainage_count,
        MAX(risk_score) AS risk_score,
        CASE 
            WHEN MAX(risk_score) >= 76 THEN 'Critical'
            WHEN MAX(risk_score) >= 51 THEN 'High'
            WHEN MAX(risk_score) >= 26 THEN 'Medium'
            ELSE 'Low'
        END AS risk_category
    FROM scored_txns
    {where_sql}
    GROUP BY account_id
    ORDER BY fraud_exposure DESC, risk_score DESC, total_transaction_value DESC
    LIMIT ? OFFSET ?;
    """
    df = pd.read_sql_query(data_query, conn, params=params + [limit, offset])
    return df, total_matches


@st.cache_data(ttl=600)
def query_investigation_transactions(
    channel: Optional[str] = None,
    fraud_status: Optional[str] = None,
    risk_category: Optional[str] = None,
    drainage: Optional[str] = None,
    min_amount: float = 0.0,
    max_amount: Optional[float] = None,
    step_range: Optional[Tuple[int, int]] = None,
    search_account: Optional[str] = None,
    limit: int = 25,
    offset: int = 0
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes paginated, multi-criteria forensic investigation queries.
    Returns matching DataFrame and summary aggregates without client RAM overload.
    """
    conn = get_db_connection()
    where_clauses = []
    params = []

    if channel and channel != "All":
        where_clauses.append("type = ?")
        params.append(channel)

    if fraud_status == "Confirmed Fraud":
        where_clauses.append("isFraud = 1")
    elif fraud_status == "Legitimate Only":
        where_clauses.append("isFraud = 0")

    if drainage == "Drained to $0.00":
        where_clauses.append("zero_balance_origin_after_transaction = 1")
    elif drainage == "Retained Balance":
        where_clauses.append("zero_balance_origin_after_transaction = 0")

    if min_amount > 0:
        where_clauses.append("amount >= ?")
        params.append(min_amount)

    if max_amount is not None:
        where_clauses.append("amount <= ?")
        params.append(max_amount)

    if step_range is not None:
        where_clauses.append("step BETWEEN ? AND ?")
        params.extend([step_range[0], step_range[1]])

    if search_account and search_account.strip():
        term = f"%{search_account.strip()}%"
        where_clauses.append("(nameOrig LIKE ? OR nameDest LIKE ?)")
        params.extend([term, term])

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    summary_query = f"""
    WITH scored_records AS (
        SELECT 
            amount,
            isFraud,
            MIN(100, (
                (CASE WHEN zero_balance_origin_after_transaction = 1 THEN 25 ELSE 0 END) +
                (CASE WHEN amount >= 200000.0 THEN 20 ELSE 0 END) +
                (CASE WHEN amount >= 1000000.0 THEN 20 ELSE 0 END) +
                (CASE WHEN type IN ('TRANSFER', 'CASH_OUT') THEN 15 ELSE 0 END) +
                (CASE WHEN oldbalanceDest = 0.0 THEN 10 ELSE 0 END) +
                (CASE WHEN isFraud = 1 THEN 10 ELSE 0 END)
            )) AS risk_score
        FROM transactions
        {where_sql}
    )
    SELECT 
        COUNT(*) AS match_count,
        COALESCE(SUM(amount), 0.0) AS match_volume,
        COALESCE(SUM(isFraud), 0) AS match_fraud_count,
        COALESCE(SUM(CASE WHEN isFraud = 1 THEN amount ELSE 0.0 END), 0.0) AS match_fraud_exposure
    FROM scored_records;
    """
    sum_row = conn.execute(summary_query, params).fetchone()
    summary = {
        "match_count": sum_row["match_count"],
        "match_volume": sum_row["match_volume"],
        "match_fraud_count": sum_row["match_fraud_count"],
        "match_fraud_exposure": sum_row["match_fraud_exposure"],
    }

    if summary["match_count"] == 0:
        return pd.DataFrame(), summary

    data_query = f"""
    WITH scored_records AS (
        SELECT 
            transaction_id,
            step,
            type AS transaction_type,
            amount,
            nameOrig AS origin_account,
            oldbalanceOrg AS orig_old_balance,
            newbalanceOrig AS orig_new_balance,
            nameDest AS dest_account,
            oldbalanceDest AS dest_old_balance,
            newbalanceDest AS dest_new_balance,
            isFraud AS is_fraud,
            isFlaggedFraud AS is_flagged_fraud,
            transaction_hour,
            transaction_day,
            orig_balance_error,
            dest_balance_error,
            zero_balance_origin_after_transaction AS is_drainage,
            MIN(100, (
                (CASE WHEN zero_balance_origin_after_transaction = 1 THEN 25 ELSE 0 END) +
                (CASE WHEN amount >= 200000.0 THEN 20 ELSE 0 END) +
                (CASE WHEN amount >= 1000000.0 THEN 20 ELSE 0 END) +
                (CASE WHEN type IN ('TRANSFER', 'CASH_OUT') THEN 15 ELSE 0 END) +
                (CASE WHEN oldbalanceDest = 0.0 THEN 10 ELSE 0 END) +
                (CASE WHEN isFraud = 1 THEN 10 ELSE 0 END)
            )) AS risk_score
        FROM transactions
        {where_sql}
    )
    SELECT 
        transaction_id,
        step,
        transaction_type,
        amount,
        origin_account,
        orig_old_balance,
        orig_new_balance,
        dest_account,
        dest_old_balance,
        dest_new_balance,
        is_fraud,
        is_flagged_fraud,
        orig_balance_error,
        dest_balance_error,
        is_drainage,
        risk_score,
        CASE 
            WHEN risk_score >= 76 THEN 'Critical'
            WHEN risk_score >= 51 THEN 'High'
            WHEN risk_score >= 26 THEN 'Medium'
            ELSE 'Low'
        END AS risk_category
    FROM scored_records
    ORDER BY is_fraud DESC, risk_score DESC, amount DESC
    LIMIT ? OFFSET ?;
    """
    df = pd.read_sql_query(data_query, conn, params=params + [limit, offset])
    return df, summary


@st.cache_data(ttl=3600)
def get_ml_model_comparison() -> pd.DataFrame:
    """Loads precomputed ML model comparison metrics from data/processed/ml/model_comparison.csv."""
    comp_file = Path("data/processed/ml/model_comparison.csv")
    if comp_file.exists():
        return pd.read_csv(comp_file)
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_ml_feature_importance(model_name: str = "xgboost") -> pd.DataFrame:
    """Loads precomputed feature importance rankings for the specified model."""
    imp_file = Path(f"data/processed/ml/feature_importance_{model_name.lower()}.csv")
    if imp_file.exists():
        return pd.read_csv(imp_file)
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def get_ml_threshold_grid(model_name: str = "xgboost") -> pd.DataFrame:
    """Loads precomputed validation threshold tuning grid."""
    grid_file = Path(f"data/processed/ml/threshold_grid_{model_name.lower()}.csv")
    if grid_file.exists():
        return pd.read_csv(grid_file)
    return pd.DataFrame()

