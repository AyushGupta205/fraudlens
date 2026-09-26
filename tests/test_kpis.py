import pytest
import pandas as pd
from src.utils.metrics import calculate_kpis

def test_kpi_calculations_accurate():
    df = pd.DataFrame({
        'amount': [100.0, 200.0, 300.0, 400.0],
        'isFraud': [0, 0, 1, 0],
        'isFlaggedFraud': [0, 0, 0, 0]
    })
    kpis = calculate_kpis(df)
    
    assert kpis['total_transactions'] == 4
    assert kpis['total_transaction_value'] == 1000.0
    assert kpis['fraud_transactions'] == 1
    assert kpis['fraud_loss'] == 300.0
    assert kpis['fraud_rate_pct'] == 25.0
    assert kpis['avg_fraud_transaction'] == 300.0
    assert kpis['avg_legitimate_transaction'] == pytest.approx(233.33, 0.01)

def test_kpi_handles_empty_dataframe():
    df = pd.DataFrame(columns=['amount', 'isFraud'])
    kpis = calculate_kpis(df)
    
    assert kpis['total_transactions'] == 0
    assert kpis['fraud_rate_pct'] == 0.0
    assert kpis['total_transaction_value'] == 0.0
