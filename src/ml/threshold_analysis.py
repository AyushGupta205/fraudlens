"""
FraudLens — Phase 7: Threshold Analysis Module
Evaluates multiple decision thresholds on validation data to analyze precision, recall, and investigation workload trade-offs.
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd

from src.ml.evaluate_models import evaluate_predictions
from src.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_THRESHOLDS = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]


def evaluate_threshold_grid(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    amounts: np.ndarray = None,
    thresholds: List[float] = None
) -> pd.DataFrame:
    """
    Evaluates predictions across multiple probability thresholds.
    """
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS
        
    y_true_arr = np.asarray(y_true, dtype=int)
    y_prob_arr = np.asarray(y_prob, dtype=float)
    
    rows = []
    for th in thresholds:
        y_pred = (y_prob_arr >= th).astype(int)
        res = evaluate_predictions(
            y_true=y_true_arr,
            y_pred=y_pred,
            y_prob=y_prob_arr,
            amounts=amounts,
            threshold=th
        )
        
        row = {
            'threshold': th,
            'precision': res['precision'],
            'recall': res['recall'],
            'f1_score': res['f1_score'],
            'true_positives': res['true_positives'],
            'false_positives': res['false_positives'],
            'false_negatives': res['false_negatives'],
            'true_negatives': res['true_negatives'],
            'alert_count': res['true_positives'] + res['false_positives']
        }
        if res['financial_impact']:
            row['fraud_exposure_recall_pct'] = res['financial_impact'].get('fraud_exposure_recall_pct', 0.0)
            row['flagged_fraud_exposure_usd'] = res['financial_impact'].get('flagged_fraud_exposure_usd', 0.0)
            row['false_alert_volume_usd'] = res['financial_impact'].get('false_alert_volume_usd', 0.0)
            
        rows.append(row)
        
    df_grid = pd.DataFrame(rows)
    return df_grid


def select_best_threshold(
    df_grid: pd.DataFrame,
    criterion: str = 'f1_score',
    min_precision: float = 0.80
) -> Dict[str, Any]:
    """
    Selects an operating threshold based on specified validation criteria (e.g. max F1 with minimum precision).
    """
    if criterion == 'f1_score':
        best_row = df_grid.sort_values(by=['f1_score', 'precision'], ascending=[False, False]).iloc[0]
    elif criterion == 'balanced_triage':
        # Select highest recall subject to min_precision constraint
        valid_candidates = df_grid[df_grid['precision'] >= min_precision]
        if not valid_candidates.empty:
            best_row = valid_candidates.sort_values(by=['recall', 'f1_score'], ascending=[False, False]).iloc[0]
        else:
            best_row = df_grid.sort_values(by='f1_score', ascending=False).iloc[0]
    else:
        best_row = df_grid.sort_values(by=criterion, ascending=False).iloc[0]
        
    return {
        'selected_threshold': float(best_row['threshold']),
        'criterion': criterion,
        'precision': float(best_row['precision']),
        'recall': float(best_row['recall']),
        'f1_score': float(best_row['f1_score']),
        'alert_count': int(best_row['alert_count']),
        'true_positives': int(best_row['true_positives']),
        'false_positives': int(best_row['false_positives'])
    }
