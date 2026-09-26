"""
FraudLens — Plotly Fintech Chart Builders
Generates interactive, accessible, and beautifully styled charts for Streamlit.
Adheres strictly to objective risk terminology and exact mathematical scaling.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dashboard.config import COLORS, RISK_COLORS


def apply_fintech_theme(fig: go.Figure) -> go.Figure:
    """Applies clean enterprise styling to Plotly figures."""
    fig.update_layout(
        template="plotly_white",
        font=dict(family="Segoe UI, -apple-system, sans-serif", size=12, color="#1E293B"),
        title_font=dict(family="Segoe UI, -apple-system, sans-serif", size=15, color="#0F172A"),
        margin=dict(l=40, r=30, t=50, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.8)"
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            font_size=12,
            font_color="#F8FAFC",
            font_family="Segoe UI"
        ),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
    )
    return fig


def plot_channel_volume_vs_exposure(df: pd.DataFrame) -> go.Figure:
    """Bar & line chart comparing total volume vs fraud-labeled exposure by channel."""
    fig = go.Figure()

    # Total Volume Bars
    fig.add_trace(go.Bar(
        x=df["transaction_type"],
        y=df["total_volume"],
        name="Total Transacted Volume ($)",
        marker_color="#93C5FD",
        hovertemplate="<b>%{x}</b><br>Total Volume: $%{y:,.2f}<extra></extra>"
    ))

    # Fraud Exposure Bars
    fig.add_trace(go.Bar(
        x=df["transaction_type"],
        y=df["fraud_exposure"],
        name="Fraud-Labeled Exposure ($)",
        marker_color=COLORS["fraud_crimson"],
        hovertemplate="<b>%{x}</b><br>Fraud Exposure: $%{y:,.2f}<extra></extra>"
    ))

    fig.update_layout(
        title="<b>Total Volume vs Fraud-Labeled Exposure by Channel</b>",
        barmode="group",
        yaxis_title="Monetary Value ($ USD)",
        xaxis_title="Transaction Channel",
    )
    return apply_fintech_theme(fig)


def plot_channel_fraud_rates(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart showing fraud rate % by transaction type."""
    sorted_df = df.sort_values("fraud_rate_pct", ascending=True)
    colors = [COLORS["fraud_crimson"] if r > 0 else "#94A3B8" for r in sorted_df["fraud_rate_pct"]]

    fig = go.Figure(go.Bar(
        x=sorted_df["fraud_rate_pct"],
        y=sorted_df["transaction_type"],
        orientation="h",
        marker_color=colors,
        text=[f"{r:.4f}%" for r in sorted_df["fraud_rate_pct"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Fraud Rate: %{x:.4f}%<extra></extra>"
    ))

    fig.update_layout(
        title="<b>Fraud Rate (%) by Transaction Channel</b>",
        xaxis_title="Fraud Rate (%)",
        yaxis_title="Transaction Channel",
    )
    return apply_fintech_theme(fig)


def plot_daily_exposure_trajectory(df: pd.DataFrame) -> go.Figure:
    """Area and line chart showing 31-day daily fraud exposure trajectory and 7-day rolling average."""
    fig = go.Figure()

    # Daily Exposure Area
    fig.add_trace(go.Scatter(
        x=df["simulation_day"],
        y=df["fraud_exposure"],
        mode="lines",
        name="Daily Fraud Exposure ($)",
        line=dict(color="#FDA4AF", width=1.5),
        fill="tozeroy",
        fillcolor="rgba(244, 63, 94, 0.12)",
        hovertemplate="Day %{x}<br>Daily Exposure: $%{y:,.2f}<extra></extra>"
    ))

    # 7-Day Rolling Baseline Line
    fig.add_trace(go.Scatter(
        x=df["simulation_day"],
        y=df["rolling_7d_exposure"],
        mode="lines",
        name="7-Day Rolling Moving Average",
        line=dict(color=COLORS["fraud_crimson"], width=3),
        hovertemplate="Day %{x}<br>7D Moving Avg: $%{y:,.2f}<extra></extra>"
    ))

    fig.update_layout(
        title="<b>30-Day Fraud Exposure Trajectory (Simulation Cycle)</b>",
        xaxis_title="Simulation Day (1 to 31)",
        yaxis_title="Fraud-Labeled Exposure ($ USD)",
    )
    return apply_fintech_theme(fig)


def plot_diurnal_hourly_pattern(df: pd.DataFrame) -> go.Figure:
    """Dual-axis chart illustrating uniform 24-hour fraud distribution vs legitimate traffic."""
    fig = go.Figure()

    # Total Volume Bars on Left Axis
    fig.add_trace(go.Bar(
        x=df["hour_of_day"],
        y=df["total_transactions"],
        name="Total Transactions (All Channels)",
        marker_color="#E2E8F0",
        yaxis="y1",
        hovertemplate="Hour %{x}:00<br>Total Txns: %{y:,}<extra></extra>"
    ))

    # Fraud Transactions on Right Axis
    fig.add_trace(go.Scatter(
        x=df["hour_of_day"],
        y=df["fraud_transactions"],
        name="Confirmed Fraud Incidents",
        mode="lines+markers",
        line=dict(color=COLORS["fraud_crimson"], width=2.5),
        marker=dict(size=6, color=COLORS["fraud_crimson"]),
        yaxis="y2",
        hovertemplate="Hour %{x}:00<br>Fraud Count: %{y}<extra></extra>"
    ))

    fig.update_layout(
        title="<b>Diurnal 24-Hour Pattern: Total Volume vs Uniform Fraud Execution</b>",
        xaxis=dict(title="Hour of Day (0 to 23)", dtick=1),
        yaxis=dict(title="Total Transactions Count", side="left"),
        yaxis2=dict(
            title="Confirmed Fraud Incidents",
            side="right",
            overlaying="y",
            showgrid=False
        ),
    )
    return apply_fintech_theme(fig)


def plot_amount_bands_exposure(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart showing fraud exposure concentration across amount bands."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["fraud_exposure"],
        y=df["amount_band"],
        orientation="h",
        marker_color=COLORS["secondary_blue"],
        text=[f"${v/1e9:.2f}B" if v >= 1e9 else f"${v/1e6:.1f}M" if v >= 1e6 else f"${v/1e3:.0f}K" for v in df["fraud_exposure"]],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Fraud Exposure: $%{x:,.2f}<br>Frauds: %{customdata[0]:,}<extra></extra>",
        customdata=df[["fraud_transactions"]].values
    ))

    fig.update_layout(
        title="<b>Fraud-Labeled Exposure by Value Band (5M+ = 52.3% of Total)</b>",
        xaxis_title="Fraud-Labeled Exposure ($ USD)",
        yaxis_title="Monetary Value Band",
    )
    return apply_fintech_theme(fig)


def plot_risk_tier_portfolio(df: pd.DataFrame) -> go.Figure:
    """Donut chart illustrating portfolio behavioral risk tier distribution."""
    colors = [RISK_COLORS.get(cat, "#94A3B8") for cat in df["risk_category"]]

    fig = go.Figure(go.Pie(
        labels=df["risk_category"],
        values=df["total_accounts"],
        hole=0.55,
        marker=dict(colors=colors),
        textinfo="label+percent",
        hovertemplate="<b>%{label} Tier</b><br>Accounts: %{value:,}<br>Share: %{percent}<br>Fraud Rate: %{customdata[0]:.4f}%<extra></extra>",
        customdata=df[["account_fraud_rate_pct"]].values
    ))

    fig.update_layout(
        title="<b>Portfolio Behavioral Risk Tier Distribution</b>",
        annotations=[dict(text="Risk<br>Tiers", x=0.5, y=0.5, font_size=14, showarrow=False)]
    )
    return apply_fintech_theme(fig)


def plot_origin_drainage_donut(kpis: dict) -> go.Figure:
    """Donut chart showing origin account drainage concentration in fraud."""
    labels = ["Drained to $0.00 (8,012)", "Retained Positive Balance (201)"]
    values = [kpis["fraud_drainage"], kpis["fraud_transactions"] - kpis["fraud_drainage"]]
    colors = [COLORS["fraud_crimson"], "#CBD5E1"]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors),
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Incidents: %{value:,}<br>Share: %{percent}<extra></extra>"
    ))

    fig.update_layout(
        title="<b>Fraud Origin Account Drainage (97.55% Drained to $0.00)</b>",
        annotations=[dict(text="97.55%<br>Drained", x=0.5, y=0.5, font_size=14, font_color=COLORS["fraud_crimson"], showarrow=False)]
    )
    return apply_fintech_theme(fig)


def plot_feature_importance_bar(df_imp: pd.DataFrame, top_n: int = 12) -> go.Figure:
    """Horizontal bar chart showing relative feature attributions."""
    df_plot = df_imp.head(top_n).sort_values(by="importance_score", ascending=True)
    
    fig = go.Figure(go.Bar(
        x=df_plot["relative_importance_pct"],
        y=df_plot["feature"],
        orientation="h",
        marker_color=COLORS["accent_blue"],
        hovertemplate="<b>%{y}</b><br>Relative Attribution: %{x:.2f}%<br>Score: %{customdata[0]:.4f}<extra></extra>",
        customdata=df_plot[["importance_score"]].values
    ))
    
    fig.update_layout(
        title=f"<b>Top {top_n} Predictive Features ({df_imp['model_type'].iloc[0] if not df_imp.empty else ''})</b>",
        xaxis_title="Relative Attribution (%)",
        yaxis_title="",
        height=420
    )
    return apply_fintech_theme(fig)


def plot_threshold_tradeoff_curve(df_grid: pd.DataFrame) -> go.Figure:
    """Dual-line chart illustrating Precision vs. Recall vs. Alert Count across decision thresholds."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_grid["threshold"],
        y=df_grid["precision"] * 100,
        mode="lines+markers",
        name="Precision (%)",
        line=dict(color=COLORS["primary_navy"], width=3),
        hovertemplate="Threshold %{x:.2f}<br>Precision: %{y:.2f}%<extra></extra>"
    ))
    
    fig.add_trace(go.Scatter(
        x=df_grid["threshold"],
        y=df_grid["recall"] * 100,
        mode="lines+markers",
        name="Recall (%)",
        line=dict(color=COLORS["fraud_crimson"], width=3, dash="dash"),
        hovertemplate="Threshold %{x:.2f}<br>Recall: %{y:.2f}%<extra></extra>"
    ))
    
    fig.add_trace(go.Scatter(
        x=df_grid["threshold"],
        y=df_grid["f1_score"] * 100,
        mode="lines+markers",
        name="F1 Score (%)",
        line=dict(color="#10B981", width=2, dash="dot"),
        hovertemplate="Threshold %{x:.2f}<br>F1 Score: %{y:.2f}%<extra></extra>"
    ))
    
    fig.update_layout(
        title="<b>Precision / Recall / F1 Trade-off Across Decision Thresholds</b>",
        xaxis_title="Probability Decision Threshold",
        yaxis_title="Metric Percentage (%)",
        yaxis=dict(range=[0, 105]),
        height=380
    )
    return apply_fintech_theme(fig)

