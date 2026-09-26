import pytest
from src.ml.predict import predict_transaction

def test_ml_predict_inference_contract():
    sample_txn = {
        'step': 10,
        'type': 'TRANSFER',
        'amount': 200000.0,
        'nameOrig': 'C_TEST',
        'oldbalanceOrg': 200000.0,
        'newbalanceOrig': 0.0,
        'nameDest': 'C_TEST_DEST',
        'oldbalanceDest': 0.0,
        'newbalanceDest': 0.0
    }
    pred = predict_transaction(sample_txn)
    
    assert 'fraud_probability' in pred
    assert 'predicted_label' in pred
    assert 'risk_tier' in pred
    assert 'explanation_factors' in pred
    assert 0.0 <= pred['fraud_probability'] <= 1.0
    assert pred['predicted_label'] in [0, 1]
    assert pred['risk_tier'] in ['Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk']
    assert isinstance(pred['explanation_factors'], list)
