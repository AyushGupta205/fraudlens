"""
FraudLens — Phase 7: Model Evaluation Module
Calculates Confusion Matrix, Precision, Recall, F1-Score, ROC-AUC, PR-AUC, and financial exposure impact.
"""

from typing import Dict, Any, Union
import numpy as np
import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    roc_curve,
    precision_recall_curve
)

from src.utils.logger import get_logger

logger = get_logger(__name__)


def evaluate_predictions(
    y_true: Union[pd.Series, np.ndarray],
    y_pred: Union[pd.Series, np.ndarray],
    y_prob: Union[pd.Series, np.ndarray] = None,
    amounts: np.ndarray = None,
    threshold: float = 0.5
) -> Dict[str, Any]:
    """
    Evaluates binary classification predictions and calculates comprehensive metrics.
    Reconciles TP, FP, FN, TN with true labels and returns PR-AUC and ROC-AUC.
    """
    y_t = np.asarray(y_true, dtype=int)
    y_p = np.asarray(y_pred, dtype=int)
    
    # Calculate confusion matrix
    cm = confusion_matrix(y_t, y_p, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    
    total_test = int(len(y_t))
    total_fraud = int(y_t.sum())
    total_legit = total_test - total_fraud
    
    # Validation checks
    assert tp + fn == total_fraud, f"Reconciliation Error: TP({tp}) + FN({fn}) != Total Fraud({total_fraud})"
    assert tn + fp == total_legit, f"Reconciliation Error: TN({tn}) + FP({fp}) != Total Legit({total_legit})"
    assert tp + fp + tn + fn == total_test, f"Reconciliation Error: Total CM != Total test cases ({total_test})"
    
    precision = float(precision_score(y_t, y_p, zero_division=0))
    recall = float(recall_score(y_t, y_p, zero_division=0))
    f1 = float(f1_score(y_t, y_p, zero_division=0))
    
    roc_auc = 0.0
    pr_auc = 0.0
    if y_prob is not None:
        y_prob_arr = np.asarray(y_prob, dtype=float)
        if len(np.unique(y_t)) > 1:
            roc_auc = float(roc_auc_score(y_t, y_prob_arr))
            pr_auc = float(average_precision_score(y_t, y_prob_arr))
            
    # Financial metrics if amounts are provided
    financial_impact = {}
    if amounts is not None:
        amt_arr = np.asarray(amounts, dtype=float)
        tp_mask = (y_t == 1) & (y_p == 1)
        fn_mask = (y_t == 1) & (y_p == 0)
        fp_mask = (y_t == 0) & (y_p == 1)
        
        flagged_fraud_exposure = float(amt_arr[tp_mask].sum())
        unflagged_fraud_exposure = float(amt_arr[fn_mask].sum())
        false_alert_volume = float(amt_arr[fp_mask].sum())
        
        financial_impact = {
            'flagged_fraud_exposure_usd': round(flagged_fraud_exposure, 2),
            'unflagged_fraud_exposure_usd': round(unflagged_fraud_exposure, 2),
            'false_alert_volume_usd': round(false_alert_volume, 2),
            'fraud_exposure_recall_pct': round(flagged_fraud_exposure / max(flagged_fraud_exposure + unflagged_fraud_exposure, 1e-9) * 100, 4)
        }
        
    return {
        'threshold': float(threshold),
        'total_samples': total_test,
        'fraud_samples': total_fraud,
        'legit_samples': total_legit,
        'true_positives': int(tp),
        'false_positives': int(fp),
        'false_negatives': int(fn),
        'true_negatives': int(tn),
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1_score': round(f1, 4),
        'roc_auc': round(roc_auc, 4),
        'pr_auc': round(pr_auc, 4),
        'financial_impact': financial_impact
    }
