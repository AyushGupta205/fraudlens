"""
FraudLens — Phase 6: Streamlit Application Automated Test Suite
Tests SQLite data loading, caching functions, KPI reconciliation, filter queries,
empty result handling, Plotly chart builders, and Streamlit module integrity.
"""

import os
import pytest
import pandas as pd
import numpy as np

from dashboard.config import DB_PATH
from dashboard.data_loader import (
    get_db_connection,
    get_macro_kpis,
    get_channel_metrics,
    get_daily_exposure_trajectory,
    get_diurnal_hourly_pattern,
    get_amount_bands_summary,
    get_risk_tier_portfolio,
    get_top_risk_accounts,
    query_investigation_transactions
)
from dashboard.charts import (
    plot_channel_volume_vs_exposure,
    plot_channel_fraud_rates,
    plot_daily_exposure_trajectory,
    plot_diurnal_hourly_pattern,
    plot_amount_bands_exposure,
    plot_risk_tier_portfolio,
    plot_origin_drainage_donut
)


def test_1_database_connection():
    """Verifies that data_loader establishes a valid SQLite read-only connection."""
    conn = get_db_connection()
    assert conn is not None
    cursor = conn.execute("SELECT COUNT(*) FROM transactions;")
    count = cursor.fetchone()[0]
    assert count == 6362620, f"Expected 6,362,620 rows in database, got {count}"


def test_2_macro_kpis_reconciliation():
    """Verifies that Streamlit macro KPIs reconcile 100% with Phase 4 SQL and Phase 5 Power BI."""
    kpis = get_macro_kpis()
    assert kpis["total_transactions"] == 6362620
    assert kpis["fraud_transactions"] == 8213
    assert abs(kpis["fraud_rate_pct"] - 0.129082) < 0.001
    assert abs(kpis["total_volume"] - 1144392944759.77) < 1.0
    assert abs(kpis["fraud_exposure"] - 12056415427.84) < 1.0
    assert kpis["flagged_tp"] == 16
    assert kpis["flagged_fn"] == 8197
    assert kpis["flagged_fp"] == 0
    assert kpis["flagged_tn"] == 6354407
    assert kpis["flagged_precision"] == 100.0
    assert abs(kpis["flagged_recall"] - 0.1948) < 0.01
    assert kpis["fraud_drainage"] == 8012
    assert abs(kpis["fraud_drainage_pct"] - 97.5526) < 0.01


def test_3_channel_metrics_reconciliation():
    """Verifies channel breakdown transaction counts and fraud counts match exact figures."""
    df = get_channel_metrics().set_index("transaction_type")
    assert df.loc["TRANSFER", "total_transactions"] == 532909
    assert df.loc["TRANSFER", "fraud_transactions"] == 4097
    assert df.loc["CASH_OUT", "total_transactions"] == 2237500
    assert df.loc["CASH_OUT", "fraud_transactions"] == 4116
    assert df.loc["PAYMENT", "fraud_transactions"] == 0
    assert df.loc["CASH_IN", "fraud_transactions"] == 0
    assert df.loc["DEBIT", "fraud_transactions"] == 0


def test_4_daily_exposure_trajectory():
    """Verifies 31-day daily trajectory dataframe is correctly populated with rolling average."""
    df = get_daily_exposure_trajectory()
    assert len(df) == 31, f"Expected 31 simulation days, got {len(df)}"
    assert df["fraud_transactions"].sum() == 8213
    assert abs(df["fraud_exposure"].sum() - 12056415427.84) < 1.0
    assert "rolling_7d_exposure" in df.columns
    assert not df["rolling_7d_exposure"].isna().any()


def test_5_diurnal_hourly_pattern():
    """Verifies 24-hour diurnal pattern covers hours 0 to 23 with exact fraud total."""
    df = get_diurnal_hourly_pattern()
    assert len(df) == 24, f"Expected 24 hours, got {len(df)}"
    assert df["hour_of_day"].min() == 0
    assert df["hour_of_day"].max() == 23
    assert df["fraud_transactions"].sum() == 8213
    assert df["total_transactions"].sum() == 6362620


def test_6_amount_bands_summary():
    """Verifies the 6 monetary value bands match total transactions and exposure."""
    df = get_amount_bands_summary()
    assert len(df) == 6
    assert df["total_transactions"].sum() == 6362620
    assert df["fraud_transactions"].sum() == 8213
    assert abs(df["fraud_exposure"].sum() - 12056415427.84) < 1.0


def test_7_risk_tier_portfolio():
    """Verifies behavioral risk tiers match Phase 4/5 exact portfolio counts."""
    df = get_risk_tier_portfolio().set_index("risk_category")
    assert len(df) == 4
    assert df["total_accounts"].sum() == 6362620
    assert df["fraud_associated_accounts"].sum() == 8213
    assert df.loc["Critical", "total_accounts"] == 67252
    assert df.loc["Critical", "fraud_associated_accounts"] == 4334
    assert df.loc["High", "total_accounts"] == 605922
    assert df.loc["High", "fraud_associated_accounts"] == 2890


def test_8_top_risk_accounts_query():
    """Verifies account risk search and pagination queries work without memory overload."""
    df, total_matched = get_top_risk_accounts(risk_category="Critical", limit=10, offset=0)
    assert total_matched > 0
    assert len(df) <= 10
    assert "account_id" in df.columns
    assert "risk_score" in df.columns
    assert (df["risk_score"] >= 76).all()


def test_9_investigation_query_filtering():
    """Verifies multi-criteria investigation query filtering and summary calculations."""
    df, summary = query_investigation_transactions(
        channel="TRANSFER",
        fraud_status="Confirmed Fraud",
        limit=25,
        offset=0
    )
    assert summary["match_count"] == 4097
    assert summary["match_fraud_count"] == 4097
    assert len(df) == 25
    assert (df["transaction_type"] == "TRANSFER").all()
    assert (df["is_fraud"] == 1).all()


def test_10_empty_result_filter_handling():
    """Verifies that an unmatchable filter returns an empty dataframe gracefully without crashing."""
    df, summary = query_investigation_transactions(
        channel="DEBIT",
        fraud_status="Confirmed Fraud",  # DEBIT has 0 frauds
        limit=25,
        offset=0
    )
    assert summary["match_count"] == 0
    assert summary["match_fraud_count"] == 0
    assert summary["match_volume"] == 0.0
    assert df.empty


def test_11_plotly_chart_builders():
    """Verifies that all Plotly chart generation functions execute and return valid figures."""
    channel_df = get_channel_metrics()
    daily_df = get_daily_exposure_trajectory()
    diurnal_df = get_diurnal_hourly_pattern()
    bands_df = get_amount_bands_summary()
    risk_df = get_risk_tier_portfolio()
    kpis = get_macro_kpis()

    fig1 = plot_channel_volume_vs_exposure(channel_df)
    assert fig1 is not None and len(fig1.data) == 2

    fig2 = plot_channel_fraud_rates(channel_df)
    assert fig2 is not None and len(fig2.data) == 1

    fig3 = plot_daily_exposure_trajectory(daily_df)
    assert fig3 is not None and len(fig3.data) == 2

    fig4 = plot_diurnal_hourly_pattern(diurnal_df)
    assert fig4 is not None and len(fig4.data) == 2

    fig5 = plot_amount_bands_exposure(bands_df)
    assert fig5 is not None and len(fig5.data) == 1

    fig6 = plot_risk_tier_portfolio(risk_df)
    assert fig6 is not None and len(fig6.data) == 1

    fig7 = plot_origin_drainage_donut(kpis)
    assert fig7 is not None and len(fig7.data) == 1


def test_12_streamlit_app_import():
    """Verifies that dashboard modules and entrypoint can be imported without errors."""
    import dashboard.config
    import dashboard.data_loader
    import dashboard.charts
    import dashboard.components
    assert dashboard.config.APP_TITLE == "FraudLens"
