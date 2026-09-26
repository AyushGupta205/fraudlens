"""
FraudLens — Financial Fraud Analytics & Detection Platform
Production-Quality Interactive Streamlit Analytical Application.
Phase 6: Interactive Analytics, Risk Scoring, and Forensic Investigation Workbench.
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from dashboard.config import (
    APP_TITLE, APP_SUBTITLE, APP_TAGLINE, APP_ICON,
    COLORS, RISK_COLORS, DEFAULT_PAGE_SIZE, INVESTIGATION_PAGE_SIZE
)
from dashboard.data_loader import (
    get_macro_kpis,
    get_channel_metrics,
    get_daily_exposure_trajectory,
    get_diurnal_hourly_pattern,
    get_amount_bands_summary,
    get_risk_tier_portfolio,
    get_top_risk_accounts,
    query_investigation_transactions,
    get_ml_model_comparison,
    get_ml_feature_importance,
    get_ml_threshold_grid
)
from dashboard.charts import (
    plot_channel_volume_vs_exposure,
    plot_channel_fraud_rates,
    plot_daily_exposure_trajectory,
    plot_diurnal_hourly_pattern,
    plot_amount_bands_exposure,
    plot_risk_tier_portfolio,
    plot_origin_drainage_donut,
    plot_feature_importance_bar,
    plot_threshold_tradeoff_curve
)
from dashboard.components import (
    load_custom_css,
    render_header,
    render_kpi_card,
    render_callout,
    render_confusion_matrix_grid
)

# Set page configuration
st.set_page_config(
    page_title=f"{APP_TITLE} — Financial Fraud Analytics",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply styling
load_custom_css()

# Sidebar Brand & Navigation
with st.sidebar:
    st.markdown(f"## {APP_ICON} {APP_TITLE}")
    st.caption(f"**{APP_TAGLINE}**")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "📊 Executive Overview",
            "🔍 Fraud Analytics",
            "⚠️ Account Risk",
            "🕵️ Fraud Investigation",
            "🤖 ML Model Analysis",
            "📖 About / Methodology"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("### 🗄️ Dataset Metadata")
    st.markdown("""
    - **Dataset**: PaySim Mobile Money
    - **Total Records**: 6,362,620
    - **Simulation Window**: 743 Hours (~31 Days)
    - **Confirmed Frauds**: 8,213 (0.1291%)
    - **Fraud Exposure**: $12.06 Billion
    """)
    st.markdown("---")
    st.caption("FraudLens Analytics Engine v1.0.0 (Phase 6)")


# Load Macro KPIs
try:
    kpis = get_macro_kpis()
except Exception as e:
    st.error(f"Error loading database analytics: {e}")
    st.stop()


# ==============================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# ==============================================================================
if page == "📊 Executive Overview":
    render_header(
        "FraudLens — Financial Fraud Analytics & Executive Overview",
        "Data-driven analysis of transaction fraud patterns, exposure, and account risk across 6.36M records."
    )

    # Top KPI Cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        render_kpi_card("Total Transactions", f"{kpis['total_transactions']:,}", "31-Day Simulation")
    with col2:
        render_kpi_card("Total Volume", f"${kpis['total_volume']/1e12:.3f} T", "$1.144 Trillion USD")
    with col3:
        render_kpi_card("Fraud Incidents", f"{kpis['fraud_transactions']:,}", "Confirmed Ground-Truth", highlight_color=COLORS["fraud_crimson"])
    with col4:
        render_kpi_card("Fraud Exposure", f"${kpis['fraud_exposure']/1e9:.2f} B", "Fraud-Labeled Volume", highlight_color=COLORS["fraud_crimson"])
    with col5:
        render_kpi_card("Overall Fraud Rate", f"{kpis['fraud_rate_pct']:.4f}%", "Class Imbalance 775:1", highlight_color=COLORS["fraud_crimson"])
    with col6:
        render_kpi_card("Critical Accounts", "67,252", "Score 76–100 (1.06%)", highlight_color=COLORS["warning_amber"])

    render_callout(
        "💡 <b>Executive Insight:</b> Confirmed fraud is strictly isolated to two transaction channels: <b>TRANSFER</b> (0.7688% fraud rate) and <b>CASH_OUT</b> (0.1840% fraud rate). 100% of the $12.06B fraud exposure is concentrated in these two outgoing liquidity vectors, while PAYMENT, CASH_IN, and DEBIT exhibit zero fraud incidents.",
        "info"
    )

    # Visual Row 1: Channel Volume & Exposure + 30-Day Exposure Trajectory
    c1, c2 = st.columns(2)
    with c1:
        channel_df = get_channel_metrics()
        st.plotly_chart(plot_channel_volume_vs_exposure(channel_df), use_container_width=True)
    with c2:
        daily_df = get_daily_exposure_trajectory()
        st.plotly_chart(plot_daily_exposure_trajectory(daily_df), use_container_width=True)

    # Visual Row 2: Channel Fraud Rates & Legitimate vs Fraud Comparison
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(plot_channel_fraud_rates(channel_df), use_container_width=True)
    with c4:
        st.markdown("### 📊 Macro Summary Comparison")
        st.dataframe(
            channel_df[[
                "transaction_type", "total_transactions", "total_volume", 
                "fraud_transactions", "fraud_exposure", "fraud_rate_pct"
            ]].style.format({
                "total_transactions": "{:,}",
                "total_volume": "${:,.2f}",
                "fraud_transactions": "{:,}",
                "fraud_exposure": "${:,.2f}",
                "fraud_rate_pct": "{:.4f}%"
            }),
            use_container_width=True,
            hide_index=True
        )


# ==============================================================================
# PAGE 2: FRAUD ANALYTICS
# ==============================================================================
elif page == "🔍 Fraud Analytics":
    render_header(
        "Fraud Pattern & Heuristic Evaluation Analytics",
        "Deep-dive exploration of monetary value bands, diurnal timing patterns, and rule-based heuristic efficacy."
    )

    # Value Bands & Diurnal Timing
    col1, col2 = st.columns(2)
    with col1:
        bands_df = get_amount_bands_summary()
        st.plotly_chart(plot_amount_bands_exposure(bands_df), use_container_width=True)
    with col2:
        diurnal_df = get_diurnal_hourly_pattern()
        st.plotly_chart(plot_diurnal_hourly_pattern(diurnal_df), use_container_width=True)

    render_callout(
        "⏱️ <b>Diurnal Pattern Finding:</b> While legitimate transaction volume follows a cyclical diurnal curve peaking during daytime hours, fraudulent incidents are executed <b>uniformly at 10 to 14 incidents per hour across all 24 hours</b>. Fraudulent actors operate continuously without diurnal seasonality.",
        "warning"
    )

    # Average Ticket Sizing & Value Concentration
    st.markdown("### 💰 Transaction Ticket Sizing Comparison")
    s1, s2, s3 = st.columns(3)
    with s1:
        render_kpi_card("Avg Legitimate Amount", f"${kpis['avg_legit_amount']:,.2f}", "Across 6.35M non-fraud txns")
    with s2:
        render_kpi_card("Avg Fraudulent Amount", f"${kpis['avg_fraud_amount']:,.2f}", "8.2x Legitimate Multiplier", highlight_color=COLORS["fraud_crimson"])
    with s3:
        render_kpi_card("Extreme Value (> $5M) Exposure", "$6.11 B", "52.3% of Total Fraud Exposure", highlight_color=COLORS["fraud_crimson"])

    st.markdown("---")

    # Heuristic Flag Performance (Confusion Matrix)
    st.markdown("### ⚙️ Heuristic Rule Performance (`isFlaggedFraud` Rule Evaluation)")
    st.markdown("Evaluation of the existing legacy rule flagging single transfers exceeding **$200,000.00**:")

    cm_col1, cm_col2 = st.columns([1.2, 1])
    with cm_col1:
        render_confusion_matrix_grid(kpis)
    with cm_col2:
        st.markdown(f"""
        - **Precision**: `{kpis['flagged_precision']:.2f}%` (16 / 16 flags confirmed fraud)
        - **Recall**: `{kpis['flagged_recall']:.4f}%` (Detected only 16 of 8,213 frauds)
        - **False Negatives (FN)**: **{kpis['flagged_fn']:,}** undetected fraud incidents
        - **Analytical Takeaway**: The legacy heuristic achieves high precision but catches under 0.20% of fraudulent volume. Advanced machine learning models (Phase 7) are essential to capture sophisticated behavioral patterns.
        """)


# ==============================================================================
# PAGE 3: ACCOUNT RISK
# ==============================================================================
elif page == "⚠️ Account Risk":
    render_header(
        "Account Risk Triage & Behavioral Health",
        "Behavioral risk tiering (0–100 score) and origin account drainage analysis for investigative prioritization."
    )

    risk_portfolio_df = get_risk_tier_portfolio()

    # Portfolio Distribution & Drainage Analysis
    r1, r2 = st.columns(2)
    with r1:
        st.plotly_chart(plot_risk_tier_portfolio(risk_portfolio_df), use_container_width=True)
    with r2:
        st.plotly_chart(plot_origin_drainage_donut(kpis), use_container_width=True)

    render_callout(
        "🚨 <b>Origin Account Drainage Behavior:</b> In <b>8,012 out of 8,213 confirmed fraud incidents (97.55%)</b>, the originating account balance was completely emptied to exactly $0.00. Account liquidation is the primary behavioral signature of fraudulent transactions in PaySim.",
        "danger"
    )

    # Interactive Account Risk Filter & Table
    st.markdown("### 📋 Account Risk Triage Workbench")
    st.caption("Search and filter account risk profiles. *Note: Risk scores serve as investigative prioritization mechanism, not conclusive proof of customer intent.*")

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        selected_risk_cat = st.selectbox("Risk Category", ["All", "Critical", "High", "Medium", "Low"], index=1)
    with f2:
        min_score = st.slider("Minimum Risk Score", 0, 100, 76 if selected_risk_cat == "Critical" else 0)
    with f3:
        min_fraud = st.number_input("Minimum Fraud Incidents", min_value=0, max_value=10, value=0)
    with f4:
        min_vol = st.number_input("Minimum Transacted Value ($)", min_value=0.0, value=0.0, step=10000.0)

    # Paginated Account Query
    accounts_df, total_accounts_matched = get_top_risk_accounts(
        risk_category=selected_risk_cat,
        min_score=min_score,
        min_fraud_count=min_fraud,
        min_volume=min_vol,
        limit=25,
        offset=0
    )

    st.markdown(f"**Matching Accounts:** `{total_accounts_matched:,}` accounts found.")

    if not accounts_df.empty:
        st.dataframe(
            accounts_df.style.format({
                "transaction_count": "{:,}",
                "total_transaction_value": "${:,.2f}",
                "fraud_count": "{:,}",
                "fraud_exposure": "${:,.2f}",
                "fraud_rate_pct": "{:.2f}%",
                "drainage_count": "{:,}",
                "risk_score": "{:.0f}"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No accounts matched the selected filter criteria. Try adjusting the threshold values.")


# ==============================================================================
# PAGE 4: FRAUD INVESTIGATION
# ==============================================================================
elif page == "🕵️ Fraud Investigation":
    render_header(
        "Transaction Forensic Investigation Workbench",
        "Multi-criteria forensic search and ledger discrepancy inspection. Queries directly from SQLite with index optimization."
    )

    # Filter Controls
    with st.expander("🛠️ Advanced Search & Filter Controls", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            channel_filter = st.selectbox("Channel", ["All", "TRANSFER", "CASH_OUT", "PAYMENT", "CASH_IN", "DEBIT"], index=0)
        with c2:
            fraud_filter = st.selectbox("Fraud Status", ["All", "Confirmed Fraud", "Legitimate Only"], index=1)
        with c3:
            drain_filter = st.selectbox("Origin Drainage", ["All", "Drained to $0.00", "Retained Balance"], index=0)
        with c4:
            search_acc = st.text_input("Search Account ID (Origin/Dest)", placeholder="e.g. C123456789")

        c5, c6 = st.columns([2, 2])
        with c5:
            amount_range = st.slider("Monetary Amount Range ($ USD)", 0.0, 10000000.0, (0.0, 10000000.0), step=50000.0)
        with c6:
            step_range = st.slider("Simulation Step (Hour 1 to 743)", 1, 743, (1, 743))

    # Pagination state
    if "investigation_page" not in st.session_state:
        st.session_state.investigation_page = 0

    page_offset = st.session_state.investigation_page * INVESTIGATION_PAGE_SIZE

    # Query Data
    inv_df, inv_summary = query_investigation_transactions(
        channel=channel_filter,
        fraud_status=fraud_filter,
        drainage=drain_filter,
        min_amount=amount_range[0],
        max_amount=amount_range[1],
        step_range=step_range,
        search_account=search_acc,
        limit=INVESTIGATION_PAGE_SIZE,
        offset=page_offset
    )

    # Investigation Metrics Summary Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_kpi_card("Matching Transactions", f"{inv_summary['match_count']:,}", "Filtered Ledger Entries")
    with m2:
        render_kpi_card("Matching Volume", f"${inv_summary['match_volume']:,.2f}", "Total Transacted Value")
    with m3:
        render_kpi_card("Confirmed Frauds in Filter", f"{inv_summary['match_fraud_count']:,}", "Fraud Incidents", highlight_color=COLORS["fraud_crimson"])
    with m4:
        render_kpi_card("Fraud Exposure in Filter", f"${inv_summary['match_fraud_exposure']:,.2f}", "Exposure Subtotal", highlight_color=COLORS["fraud_crimson"])

    # Detailed Table
    if not inv_df.empty:
        st.markdown(f"### 📋 Ledger Transaction Grid (Displaying Rows {page_offset + 1} – {min(page_offset + INVESTIGATION_PAGE_SIZE, inv_summary['match_count'])})")
        
        st.dataframe(
            inv_df[[
                "transaction_id", "step", "transaction_type", "amount",
                "origin_account", "orig_old_balance", "orig_new_balance",
                "dest_account", "dest_old_balance", "dest_new_balance",
                "is_fraud", "is_flagged_fraud", "orig_balance_error",
                "is_drainage", "risk_score", "risk_category"
            ]].style.format({
                "amount": "${:,.2f}",
                "orig_old_balance": "${:,.2f}",
                "orig_new_balance": "${:,.2f}",
                "dest_old_balance": "${:,.2f}",
                "dest_new_balance": "${:,.2f}",
                "orig_balance_error": "${:,.2f}",
                "risk_score": "{:.0f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        # Pagination controls
        p_col1, p_col2, p_col3 = st.columns([1, 2, 1])
        with p_col1:
            if st.button("⬅️ Previous Page", disabled=(st.session_state.investigation_page == 0)):
                st.session_state.investigation_page -= 1
                st.rerun()
        with p_col2:
            total_pages = (inv_summary["match_count"] + INVESTIGATION_PAGE_SIZE - 1) // INVESTIGATION_PAGE_SIZE
            st.markdown(f"<div style='text-align: center; padding-top: 8px;'>Page <b>{st.session_state.investigation_page + 1}</b> of <b>{max(total_pages, 1)}</b></div>", unsafe_allow_html=True)
        with p_col3:
            if st.button("Next Page ➡️", disabled=((st.session_state.investigation_page + 1) >= total_pages)):
                st.session_state.investigation_page += 1
                st.rerun()
    else:
        st.info("No ledger transactions matched the active filter criteria. Try expanding the search bounds.")


# ==============================================================================
# PAGE 5: ABOUT / METHODOLOGY
# ==============================================================================
elif page == "📖 About / Methodology":
    render_header(
        "About FraudLens & Engineering Methodology",
        "Architectural governance, analytical data pipeline, and synthetic data disclosures."
    )

    st.markdown("""
    ### 🎯 Project Overview & Objectives
    **FraudLens** is an end-to-end Financial Fraud Analytics and Risk Intelligence platform built on the **PaySim synthetic mobile-money dataset** (6.36 million transactions). The project demonstrates rigorous data analyst, SQL development, data engineering, business intelligence, and risk analysis workflows.

    ---

    ### 🔄 End-to-End Analytical Pipeline
    ```
    Raw PaySim CSV (6.36M Rows)
         │
         ▼
    [Phase 1 & 2: Data Cleaning & Feature Engineering]
    • Type conversions, duplicate checks, zero nulls verified.
    • Engineered: orig_balance_error, dest_balance_error, transaction_hour/day, is_drainage.
         │
         ▼
    [Phase 3: Exploratory Data Analysis (EDA)]
    • Validated 8,213 frauds ($12.06B exposure, 0.1291% fraud rate).
    • Established channel exclusivity (TRANSFER & CASH_OUT).
         │
         ▼
    [Phase 4: SQLite Relational Database & SQL Analytics]
    • Relational schema with 10 performance B-tree indexes.
    • Multi-factor behavioral risk scoring (0–100 scale).
         │
         ▼
    [Phase 5: Power BI Architecture & Star Schema]
    • Star schema design (fact summaries + investigation extracts).
    • 27 verified DAX measures with 100% SQL reconciliation.
         │
         ▼
    [Phase 6: Streamlit Interactive Analytics Platform]
    • High-performance interactive dashboard with Plotly visual analytics.
    • Forensic investigation workbench with indexed SQL filtering.
         │
         ▼
    [Phase 7: Machine Learning Fraud Detection Layer] (Upcoming)
    • Supervised classification and anomaly scoring models.
    ```

    ---

    ### 🛡️ Risk Governance & Disclaimers
    1. **Synthetic Dataset Disclosure**: PaySim is a synthetic simulation generated from financial logs. It represents realistic mobile-money topologies but is not actual production banking data.
    2. **Risk Score as Prioritization**: The multi-factor 0–100 risk score is an operational triage mechanism for AML/compliance queues. It is **never** used as definitive proof of wrongdoing.
    3. **Exposure vs Loss**: Fraud metrics represent *"fraud-labeled transaction exposure"* rather than confirmed unrecovered financial loss.
    4. **Class Imbalance**: Fraud occurs at an incidence rate of **0.1291% (1 in every 775 transactions)**, requiring precision-recall optimization over standard accuracy metrics.
    """)


# ==============================================================================
# PAGE 6: ML MODEL ANALYSIS (EXPERIMENTAL)
# ==============================================================================
elif page == "🤖 ML Model Analysis":
    render_header(
        "Machine Learning Fraud Classification & Model Evaluation",
        "Supervised classification layer evaluating Logistic Regression, Random Forest, and XGBoost on holdout test data."
    )

    st.warning(
        "⚠️ **Academic & Portfolio Disclaimer**: Machine Learning models are evaluated for comparative fraud analytics "
        "and investigative prioritization. Predictions represent model confidence scores on synthetic simulation data "
        "and are NOT autonomous real-time banking decisions."
    )

    df_comp = get_ml_model_comparison()
    if df_comp.empty:
        st.info("ML evaluation metrics are currently loading or generating. Please run the training pipeline.")
    else:
        st.markdown("### 🏆 Model Performance Comparison (Untouched Holdout Test Set: 1,272,524 Rows)")
        
        # Display comparison table with formatted metrics
        disp_cols = [
            'Model', 'Threshold', 'Precision', 'Recall', 'F1_Score', 'PR_AUC', 'ROC_AUC',
            'True_Positives', 'False_Positives', 'False_Negatives', 'True_Negatives'
        ]
        st.dataframe(
            df_comp[disp_cols].style.format({
                'Threshold': '{:.2f}',
                'Precision': '{:.4f}',
                'Recall': '{:.4f}',
                'F1_Score': '{:.4f}',
                'PR_AUC': '{:.4f}',
                'ROC_AUC': '{:.4f}',
                'True_Positives': '{:,}',
                'False_Positives': '{:,}',
                'False_Negatives': '{:,}',
                'True_Negatives': '{:,}'
            }),
            use_container_width=True
        )

        st.markdown("---")
        
        # Interactive Model Inspection Selector
        selected_model = st.selectbox(
            "Select Model for Detailed Attribution & Threshold Analysis:",
            options=["XGBoost", "RandomForest", "LogisticRegression"],
            index=0
        )

        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown(f"#### 🔍 Feature Attributions ({selected_model})")
            df_imp = get_ml_feature_importance(selected_model)
            if not df_imp.empty:
                fig_imp = plot_feature_importance_bar(df_imp, top_n=10)
                st.plotly_chart(fig_imp, use_container_width=True)
            else:
                st.info("Feature importance data unavailable.")

        with col_right:
            st.markdown(f"#### ⚖️ Decision Threshold Trade-offs ({selected_model})")
            df_grid = get_ml_threshold_grid(selected_model)
            if not df_grid.empty:
                fig_grid = plot_threshold_tradeoff_curve(df_grid)
                st.plotly_chart(fig_grid, use_container_width=True)
            else:
                st.info("Threshold grid data unavailable.")

        st.markdown("---")
        st.markdown("### 💡 Data Analyst Insights on Model Trade-Offs")
        st.markdown("""
        - **Class Imbalance Resilience**: With a 0.1291% base fraud rate, tree-based ensemble models (`XGBoost` and `RandomForest`) achieved near-perfect PR-AUC scores (**0.9987+**) by heavily prioritizing origin balance discrepancies (`orig_balance_error`) and residual balance post-transaction (`newbalanceOrig`).
        - **Investigator Workload vs. Recall**:
          - **Default (0.50 Threshold)**: Catches **99.82%** of test-set fraud cases (1,640 out of 1,643) with only 116 false alerts across 1.27M test transactions.
          - **Conservative (0.90 Threshold)**: Slashes false alerts down to **14** while retaining **99.76%** recall (1,639 out of 1,643 frauds detected).
        - **Linear Baseline Contrast**: `LogisticRegression` provides interpretable standardized log-odds coefficients but yields higher false positives (24,050 alerts at 0.50 threshold) due to non-linear interaction terms between balance changes and channel types.
        """)
