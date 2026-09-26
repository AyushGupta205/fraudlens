"""
FraudLens — Reusable Streamlit UI Components & Custom CSS
Implements clean fintech styling, responsive cards, alert callouts, and risk badges.
"""

import streamlit as st
from dashboard.config import COLORS, RISK_COLORS


def load_custom_css():
    """Injects custom fintech CSS for modern cards, typography, and badges."""
    st.markdown("""
    <style>
        /* Main background and layout tweaks */
        .main {
            background-color: #F8FAFC;
        }
        
        /* Header typography */
        .fl-main-title {
            font-size: 1.95rem;
            font-weight: 700;
            color: #0F172A;
            letter-spacing: -0.02em;
            margin-bottom: 2px;
        }
        .fl-subtitle {
            font-size: 1.05rem;
            color: #475569;
            margin-bottom: 1.25rem;
        }

        /* KPI Metric Cards */
        .fl-kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 16px 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 14px;
        }
        .fl-kpi-label {
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            color: #64748B;
            margin-bottom: 6px;
        }
        .fl-kpi-value {
            font-size: 1.7rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.2;
        }
        .fl-kpi-sub {
            font-size: 0.8rem;
            color: #94A3B8;
            margin-top: 4px;
        }

        /* Callout Banners */
        .fl-callout {
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 1.25rem;
            font-size: 0.92rem;
            line-height: 1.5;
        }
        .fl-callout-info {
            background-color: #F0F9FF;
            border-left: 4px solid #0284C7;
            color: #0369A1;
        }
        .fl-callout-warning {
            background-color: #FFFBEB;
            border-left: 4px solid #F59E0B;
            color: #B45309;
        }
        .fl-callout-danger {
            background-color: #FFF1F2;
            border-left: 4px solid #F43F5E;
            color: #BE123C;
        }

        /* Confusion Matrix Grid */
        .cm-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
            margin-top: 10px;
        }
        .cm-table th, .cm-table td {
            border: 1px solid #E2E8F0;
            padding: 10px 14px;
            text-align: center;
        }
        .cm-table th {
            background-color: #F1F5F9;
            color: #334155;
            font-weight: 600;
        }
        .cm-tp {
            background-color: #ECFDF5;
            color: #065F46;
            font-weight: 700;
        }
        .cm-fn {
            background-color: #FEF2F2;
            color: #991B1B;
            font-weight: 700;
        }
    </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str):
    """Renders page title and descriptive subtitle."""
    st.markdown(f'<div class="fl-main-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="fl-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_kpi_card(label: str, value: str, sub: str = "", highlight_color: str = "#0F172A"):
    """Renders a single KPI card inside a Streamlit column."""
    st.markdown(f"""
    <div class="fl-kpi-card">
        <div class="fl-kpi-label">{label}</div>
        <div class="fl-kpi-value" style="color: {highlight_color};">{value}</div>
        <div class="fl-kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def render_callout(text: str, callout_type: str = "info"):
    """Renders an analytical insight callout banner."""
    type_class = f"fl-callout-{callout_type}"
    st.markdown(f'<div class="fl-callout {type_class}">{text}</div>', unsafe_allow_html=True)


def render_confusion_matrix_grid(kpis: dict):
    """Renders the isFlaggedFraud confusion matrix and precision/recall evaluation table."""
    st.markdown(f"""
    <table class="cm-table">
        <tr>
            <th colspan="2" rowspan="2">Heuristic Rule Performance<br>(Threshold > $200k)</th>
            <th colspan="2">Actual Ground Truth (isFraud)</th>
        </tr>
        <tr>
            <th>Positive (1)</th>
            <th>Negative (0)</th>
        </tr>
        <tr>
            <th rowspan="2">Predicted Flag<br>(isFlaggedFraud)</th>
            <th>Flagged (1)</th>
            <td class="cm-tp">True Positives (TP)<br><b>{kpis['flagged_tp']:,}</b></td>
            <td>False Positives (FP)<br><b>{kpis['flagged_fp']:,}</b></td>
        </tr>
        <tr>
            <th>Unflagged (0)</th>
            <td class="cm-fn">False Negatives (FN)<br><b>{kpis['flagged_fn']:,}</b></td>
            <td>True Negatives (TN)<br><b>{kpis['flagged_tn']:,}</b></td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
