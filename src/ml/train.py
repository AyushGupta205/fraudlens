import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import json
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from src.utils.config import MODELS_DIR, REPORTS_DIR, RANDOM_STATE, PROCESSED_DATA_DIR
from src.utils.logger import get_logger
from src.data.load_data import load_raw_data, create_analytical_sample
from src.data.clean_data import clean_data
from src.data.feature_engineering import engineer_features
from src.ml.evaluate import evaluate_model_performance

logger = get_logger(__name__)

FEATURE_COLUMNS = [
    'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest',
    'hour_of_day', 'day_of_week', 'is_weekend', 'is_night_hours',
    'orig_balance_error', 'dest_balance_error', 'orig_drain_ratio',
    'is_orig_fully_emptied', 'is_orig_zero_initial', 'is_dest_zero_initial',
    'is_dest_merchant', 'is_orig_merchant', 'log_amount',
    'is_transfer', 'is_cashout'
]

def prepare_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, np.ndarray]:
    df_clean, _ = clean_data(df)
    df_feat = engineer_features(df_clean)
    
    for col in FEATURE_COLUMNS:
        if col not in df_feat.columns:
            df_feat[col] = 0.0
            
    X = df_feat[FEATURE_COLUMNS].copy()
    y = df_feat['isFraud'].copy()
    amounts = df_feat['amount'].values
    return X, y, amounts

def train_and_compare_models(df: pd.DataFrame = None) -> Dict[str, Any]:
    if df is None:
        clean_parquet = PROCESSED_DATA_DIR / 'transactions_clean.parquet'
        if clean_parquet.exists():
            logger.info(f'Loading existing clean parquet dataset from {clean_parquet}...')
            df = pd.read_parquet(clean_parquet)
        else:
            df = create_analytical_sample(sample_size=300000)
        
    X, y, amounts = prepare_dataset(df)
    
    logger.info(f'Training on dataset with shape {X.shape}, fraud cases: {y.sum():,} ({y.mean():.4%})')
    
    X_train, X_test, y_train, y_test, amt_train, amt_test = train_test_split(
        X, y, amounts, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    pos_weight = float((len(y_train) - sum(y_train)) / max(sum(y_train), 1))
    
    models = {
        'LogisticRegression': (
            LogisticRegression(max_iter=1000, class_weight='balanced', random_state=RANDOM_STATE),
            X_train_scaled, X_test_scaled
        ),
        'RandomForest': (
            RandomForestClassifier(n_estimators=100, max_depth=12, class_weight='balanced', random_state=RANDOM_STATE, n_jobs=-1),
            X_train, X_test
        ),
        'XGBoost': (
            XGBClassifier(
                n_estimators=120,
                max_depth=6,
                learning_rate=0.1,
                scale_pos_weight=pos_weight,
                random_state=RANDOM_STATE,
                n_jobs=-1,
                eval_metric='logloss'
            ),
            X_train, X_test
        )
    }
    
    results = {}
    best_pr_auc = -1.0
    best_model_name = 'XGBoost'
    best_model_obj = None
    
    for name, (clf, xtr, xte) in models.items():
        logger.info(f'Fitting {name}...')
        clf.fit(xtr, y_train)
        
        y_pred = clf.predict(xte)
        y_prob = clf.predict_proba(xte)[:, 1]
        
        perf = evaluate_model_performance(y_test.values, y_pred, y_prob, amounts=amt_test)
        results[name] = perf
        logger.info(f'{name} Results -> Precision: {perf["precision"]:.4f}, Recall: {perf["recall"]:.4f}, F1: {perf["f1_score"]:.4f}, PR-AUC: {perf["pr_auc"]:.4f}, ROC-AUC: {perf["roc_auc"]:.4f}')
        
        if perf['pr_auc'] > best_pr_auc:
            best_pr_auc = perf['pr_auc']
            best_model_name = name
            best_model_obj = clf
            
    if hasattr(best_model_obj, 'feature_importances_'):
        importances = {
            col: round(float(imp), 4)
            for col, imp in zip(FEATURE_COLUMNS, best_model_obj.feature_importances_)
        }
        sorted_imp = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
    else:
        sorted_imp = {}
        
    model_artifact = {
        'model_name': best_model_name,
        'model': best_model_obj,
        'scaler': scaler,
        'feature_columns': FEATURE_COLUMNS,
        'best_metrics': results[best_model_name],
        'all_model_results': results,
        'feature_importance': sorted_imp
    }
    
    model_save_path = MODELS_DIR / 'fraud_model.joblib'
    joblib.dump(model_artifact, model_save_path)
    
    eval_report = {
        'best_model': best_model_name,
        'comparison': results,
        'feature_importance': sorted_imp
    }
    with open(REPORTS_DIR / 'model_evaluation.json', 'w', encoding='utf-8') as f:
        json.dump(eval_report, f, indent=4)
        
    logger.info(f'Best Model ({best_model_name}) saved to {model_save_path}')
    return model_artifact

if __name__ == '__main__':
    train_and_compare_models()
