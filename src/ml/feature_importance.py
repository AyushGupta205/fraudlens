"""
FraudLens — Phase 7: Feature Importance Module
Extracts tree-based feature importances and standardized Logistic Regression coefficients.
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from src.utils.logger import get_logger

logger = get_logger(__name__)


def extract_feature_importance(
    model: Any,
    feature_names: List[str],
    model_name: str = 'Model'
) -> pd.DataFrame:
    """
    Extracts structured feature attributions from fitted model.
    """
    if hasattr(model, 'feature_importances_'):
        # Tree-based models (RandomForest, XGBoost)
        importances = model.feature_importances_
        df_imp = pd.DataFrame({
            'feature': feature_names,
            'importance_score': importances,
            'relative_importance_pct': (importances / importances.sum()) * 100.0
        }).sort_values(by='importance_score', ascending=False).reset_index(drop=True)
        df_imp['rank'] = np.arange(1, len(df_imp) + 1)
        df_imp['model_type'] = model_name
        return df_imp
        
    elif isinstance(model, LogisticRegression) or hasattr(model, 'coef_'):
        # Linear models (standardized coefficients)
        coefs = model.coef_[0]
        abs_coefs = np.abs(coefs)
        df_imp = pd.DataFrame({
            'feature': feature_names,
            'coefficient': coefs,
            'odds_ratio': np.exp(coefs),
            'importance_score': abs_coefs,
            'relative_importance_pct': (abs_coefs / abs_coefs.sum()) * 100.0
        }).sort_values(by='importance_score', ascending=False).reset_index(drop=True)
        df_imp['rank'] = np.arange(1, len(df_imp) + 1)
        df_imp['model_type'] = model_name
        return df_imp
        
    else:
        logger.warning(f"Model {type(model)} does not support direct feature importances.")
        return pd.DataFrame({'feature': feature_names, 'importance_score': 0.0, 'rank': 1})
