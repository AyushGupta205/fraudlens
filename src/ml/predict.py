"""
FraudLens — Phase 7: Model Inference Module
Loads serialized ML models and provides single-transaction and batch fraud prediction scores.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Union

from src.utils.config import MODELS_DIR
from src.ml.prepare_ml_data import FEATURE_COLUMNS
from src.utils.logger import get_logger

logger = get_logger(__name__)

_MODEL_CACHE: Dict[str, Any] = {}


def load_model(model_name: str = 'xgboost'):
    """Loads and caches serialized model and preprocessing scaler."""
    global _MODEL_CACHE
    key = model_name.lower()
    if key not in _MODEL_CACHE:
        # Check both MODELS_DIR and root models/
        candidates = [
            MODELS_DIR / f"{key}_model.joblib",
            Path("models") / f"{key}_model.joblib",
            MODELS_DIR / "xgboost_model.joblib",
            MODELS_DIR / "randomforest_model.joblib",
            MODELS_DIR / "logisticregression_model.joblib"
        ]
        model_path = None
        for p in candidates:
            if p.exists():
                model_path = p
                break
                
        if model_path is None or not model_path.exists():
            raise FileNotFoundError(f"Trained model artifact not found for {model_name} in {MODELS_DIR}")
            
        model = joblib.load(model_path)
        
        scaler_candidates = [
            MODELS_DIR / "scaler.joblib",
            Path("models") / "scaler.joblib"
        ]
        scaler = None
        for sp in scaler_candidates:
            if sp.exists():
                scaler = joblib.load(sp)
                break
                
        _MODEL_CACHE[key] = {
            'model': model,
            'scaler': scaler,
            'feature_columns': FEATURE_COLUMNS,
            'model_name': key
        }
    return _MODEL_CACHE[key]


def predict_transaction(
    txn_data: Union[Dict[str, Any], pd.DataFrame],
    model_name: str = 'xgboost',
    threshold: float = 0.50
) -> Dict[str, Any]:
    """
    Predicts fraud probability and binary decision for a single transaction or batch.
    """
    artifact = load_model(model_name)
    model = artifact['model']
    scaler = artifact['scaler']
    feature_cols = artifact['feature_columns']
    
    if isinstance(txn_data, dict):
        df_in = pd.DataFrame([txn_data])
    else:
        df_in = txn_data.copy()
        
    # Feature engineering for incoming record if not already calculated
    X = pd.DataFrame(index=df_in.index)
    
    # Extract base features
    for col in feature_cols:
        if col in df_in.columns:
            X[col] = df_in[col]
        else:
            # Derive on the fly if needed
            if col == 'is_transfer':
                X[col] = (df_in.get('type', '') == 'TRANSFER').astype(int)
            elif col == 'is_cashout':
                X[col] = (df_in.get('type', '') == 'CASH_OUT').astype(int)
            elif col == 'is_payment':
                X[col] = (df_in.get('type', '') == 'PAYMENT').astype(int)
            elif col == 'is_dest_merchant':
                X[col] = df_in.get('nameDest', pd.Series([''])).astype(str).str.startswith('M').astype(int)
            elif col == 'orig_balance_error':
                old_org = df_in.get('oldbalanceOrg', 0.0)
                new_org = df_in.get('newbalanceOrig', 0.0)
                amt = df_in.get('amount', 0.0)
                X[col] = (old_org - amt) - new_org
            elif col == 'dest_balance_error':
                old_dst = df_in.get('oldbalanceDest', 0.0)
                new_dst = df_in.get('newbalanceDest', 0.0)
                amt = df_in.get('amount', 0.0)
                X[col] = (old_dst + amt) - new_dst
            elif col == 'origin_balance_change':
                X[col] = df_in.get('newbalanceOrig', 0.0) - df_in.get('oldbalanceOrg', 0.0)
            elif col == 'destination_balance_change':
                X[col] = df_in.get('newbalanceDest', 0.0) - df_in.get('oldbalanceDest', 0.0)
            elif col == 'amount_to_origin_balance_ratio':
                X[col] = df_in.get('amount', 0.0) / (df_in.get('oldbalanceOrg', 0.0) + 1.0)
            elif col == 'amount_to_destination_balance_ratio':
                X[col] = df_in.get('amount', 0.0) / (df_in.get('oldbalanceDest', 0.0) + 1.0)
            elif col == 'zero_balance_origin_after_transaction':
                X[col] = (df_in.get('newbalanceOrig', 1.0) == 0.0).astype(int)
            elif col == 'zero_balance_destination_after_transaction':
                X[col] = (df_in.get('newbalanceDest', 1.0) == 0.0).astype(int)
            elif col == 'transaction_hour':
                X[col] = (df_in.get('step', 1) % 24).astype(int)
            elif col == 'transaction_day':
                X[col] = ((df_in.get('step', 1) - 1) // 24 + 1).astype(int)
            else:
                X[col] = 0.0
                
    X = X[feature_cols].copy()
    
    if model_name.lower() == 'logisticregression' and scaler is not None:
        X_eval = scaler.transform(X)
    else:
        X_eval = X
        
    if hasattr(model, 'predict_proba'):
        probs = model.predict_proba(X_eval)[:, 1]
    else:
        probs = model.predict(X_eval).astype(float)
        
    preds = (probs >= threshold).astype(int)
    
    prob_val = float(probs[0])
    pred_val = int(preds[0])
    
    # Risk tier mapping based on model probability
    explanation_factors = []
    if float(X['orig_balance_error'].iloc[0]) != 0.0:
        explanation_factors.append('Origin account balance deduction discrepancy')
    if float(X['zero_balance_origin_after_transaction'].iloc[0]) == 1.0:
        explanation_factors.append('Origin account completely emptied')
    if float(X['amount'].iloc[0]) >= 200000.0:
        explanation_factors.append('High transacted monetary value (>= $200k)')
    if int(X['is_transfer'].iloc[0]) == 1 or int(X['is_cashout'].iloc[0]) == 1:
        explanation_factors.append('High-risk transaction channel (TRANSFER / CASH_OUT)')
    if not explanation_factors:
        explanation_factors.append('Standard behavioral pattern')

    if prob_val >= 0.75:
        tier = "Critical Risk"
    elif prob_val >= 0.50:
        tier = "High Risk"
    elif prob_val >= 0.25:
        tier = "Medium Risk"
    else:
        tier = "Low Risk"
        
    return {
        'model_name': model_name,
        'fraud_probability': round(prob_val, 6),
        'predicted_label': pred_val,
        'is_fraud_predicted': pred_val,
        'decision_threshold': float(threshold),
        'risk_tier': tier,
        'explanation_factors': explanation_factors,
        'feature_count': len(feature_cols)
    }

