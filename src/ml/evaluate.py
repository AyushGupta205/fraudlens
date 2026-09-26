import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)

def evaluate_model_performance(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    cost_fp: float = 25.0,
    cost_fn_rate: float = 1.0,
    amounts: np.ndarray = None
) -> Dict[str, Any]:
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else 0.0
    pr_auc = float(average_precision_score(y_true, y_prob)) if len(np.unique(y_true)) > 1 else 0.0
    
    # Financial Cost-Benefit evaluation
    # FP cost = manual investigation cost (e.g., /alert)
    # FN cost = unprevented fraud loss (total stolen amount or average loss)
    total_fp_cost = float(fp * cost_fp)
    
    if amounts is not None:
        fn_mask = (y_true == 1) & (y_pred == 0)
        total_fn_cost = float(amounts[fn_mask].sum())
        tp_mask = (y_true == 1) & (y_pred == 1)
        prevented_loss = float(amounts[tp_mask].sum())
    else:
        avg_loss_est = 100000.0
        total_fn_cost = float(fn * avg_loss_est)
        prevented_loss = float(tp * avg_loss_est)
        
    net_fraud_benefit = prevented_loss - (total_fp_cost + total_fn_cost)
    
    return {
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1_score': round(f1, 4),
        'roc_auc': round(roc_auc, 4),
        'pr_auc': round(pr_auc, 4),
        'confusion_matrix': {
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp)
        },
        'financial_impact': {
            'investigation_cost_fp': round(total_fp_cost, 2),
            'unmitigated_fraud_loss_fn': round(total_fn_cost, 2),
            'prevented_fraud_value': round(prevented_loss, 2),
            'net_savings': round(prevented_loss - total_fp_cost, 2)
        }
    }
