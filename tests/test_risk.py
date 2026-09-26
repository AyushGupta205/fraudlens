import pytest
import pandas as pd
from src.analysis.customer_analysis import generate_customer_profiles

def test_customer_risk_assignment():
    df = pd.DataFrame({
        'step': [1, 2],
        'type': ['TRANSFER', 'PAYMENT'],
        'amount': [500000.0, 20.0],
        'nameOrig': ['C_FRAUDULENT', 'C_NORMAL'],
        'oldbalanceOrg': [500000.0, 100.0],
        'newbalanceOrig': [0.0, 80.0],
        'nameDest': ['C99', 'M88'],
        'oldbalanceDest': [0.0, 0.0],
        'newbalanceDest': [500000.0, 0.0],
        'isFraud': [1, 0]
    })
    profiles = generate_customer_profiles(df)
    
    fraud_cust = profiles[profiles['nameOrig'] == 'C_FRAUDULENT'].iloc[0]
    normal_cust = profiles[profiles['nameOrig'] == 'C_NORMAL'].iloc[0]
    
    assert fraud_cust['risk_score'] > normal_cust['risk_score']
    assert fraud_cust['risk_category'] in ['Critical Risk', 'High Risk']
    assert normal_cust['risk_category'] == 'Low Risk'
