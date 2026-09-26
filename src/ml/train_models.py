"""
FraudLens — Phase 7: Machine Learning Model Training & Experimentation Pipeline
Trains Logistic Regression, Random Forest, and XGBoost models with strict leakage prevention and class imbalance handling.
"""

import os
import json
import joblib
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from src.utils.config import MODELS_DIR, PROCESSED_DATA_DIR, RANDOM_STATE
from src.utils.logger import get_logger
from src.ml.prepare_ml_data import (
    load_and_prepare_features,
    create_train_test_splits,
    create_validation_split,
    audit_features,
    FEATURE_COLUMNS
)
from src.ml.evaluate_models import evaluate_predictions
from src.ml.threshold_analysis import evaluate_threshold_grid, select_best_threshold
from src.ml.feature_importance import extract_feature_importance

logger = get_logger(__name__)

ML_RESULTS_DIR = PROCESSED_DATA_DIR / 'ml'


def train_and_evaluate_all_models(
    data_path: Path = None,
    save_artifacts: bool = True
) -> Dict[str, Any]:
    """
    Executes the end-to-end ML pipeline:
    1. Loads features and performs leakage audit.
    2. Creates stratified 80/20 train/test split.
    3. Fits StandardScaler strictly on X_train.
    4. Trains Logistic Regression, Random Forest, and XGBoost.
    5. Tunes decision thresholds using internal validation split.
    6. Evaluates final performance on untouched holdout test set.
    7. Extracts feature importances.
    8. Persists models and summary tables.
    """
    ML_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Feature Extraction & Leakage Audit
    X, y, amounts = load_and_prepare_features(data_path)
    leakage_audit = audit_features(pd.DataFrame(columns=FEATURE_COLUMNS + ['isFraud', 'isFlaggedFraud']))
    logger.info(f"Leakage Audit Result: {leakage_audit['leakage_status']}")
    
    # 2. Stratified Train / Test Split
    splits = create_train_test_splits(X, y, amounts, test_size=0.2, random_state=RANDOM_STATE)
    X_train, X_test = splits['X_train'], splits['X_test']
    y_train, y_test = splits['y_train'], splits['y_test']
    amt_train, amt_test = splits['amt_train'], splits['amt_test']
    
    # 3. Validation Split for Threshold Tuning (derived from train only)
    val_splits = create_validation_split(X_train, y_train, amt_train, val_size=0.2, random_state=RANDOM_STATE)
    X_train_sub, X_val = val_splits['X_train_sub'], val_splits['X_val']
    y_train_sub, y_val = val_splits['y_train_sub'], val_splits['y_val']
    amt_val = val_splits['amt_val']
    
    # 4. Scaler (fitted strictly on X_train)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    X_val_scaled = scaler.transform(X_val)
    
    # Calculate scale_pos_weight strictly from training data
    train_negatives = int((y_train == 0).sum())
    train_positives = int((y_train == 1).sum())
    pos_weight = float(train_negatives / max(train_positives, 1))
    
    logger.info(f"Calculated training class imbalance weight: {pos_weight:.2f}")
    
    # Define models
    model_defs = {
        'LogisticRegression': {
            'model': LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                random_state=RANDOM_STATE,
                solver='lbfgs'
            ),
            'X_tr': X_train_scaled,
            'X_te': X_test_scaled,
            'X_v': X_val_scaled,
            'description': 'L2-regularized Logistic Regression with balanced class weighting'
        },
        'RandomForest': {
            'model': RandomForestClassifier(
                n_estimators=100,
                max_depth=12,
                class_weight='balanced',
                random_state=RANDOM_STATE,
                n_jobs=-1
            ),
            'X_tr': X_train,
            'X_te': X_test,
            'X_v': X_val,
            'description': 'Balanced Random Forest with 100 estimators and max_depth=12'
        },
        'XGBoost': {
            'model': XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                scale_pos_weight=pos_weight,
                tree_method='hist',
                random_state=RANDOM_STATE,
                n_jobs=-1,
                eval_metric='logloss'
            ),
            'X_tr': X_train,
            'X_te': X_test,
            'X_v': X_val,
            'description': 'Hist-based XGBoost with scale_pos_weight derived from y_train'
        }
    }
    
    results = {}
    comparison_rows = []
    feature_importances = {}
    threshold_grids = {}
    
    for name, config in model_defs.items():
        logger.info(f"--- Training {name} ---")
        clf = config['model']
        clf.fit(config['X_tr'], y_train)
        
        # Probabilities on test set
        if hasattr(clf, 'predict_proba'):
            y_prob_test = clf.predict_proba(config['X_te'])[:, 1]
            y_prob_val = clf.predict_proba(config['X_v'])[:, 1]
        elif hasattr(clf, 'decision_function'):
            scores = clf.decision_function(config['X_te'])
            y_prob_test = 1.0 / (1.0 + np.exp(-scores))
            val_scores = clf.decision_function(config['X_v'])
            y_prob_val = 1.0 / (1.0 + np.exp(-val_scores))
        else:
            y_prob_test = clf.predict(config['X_te']).astype(float)
            y_prob_val = clf.predict(config['X_v']).astype(float)
            
        # Default 0.50 threshold evaluation on test set
        y_pred_default = (y_prob_test >= 0.50).astype(int)
        test_eval = evaluate_predictions(
            y_true=y_test,
            y_pred=y_pred_default,
            y_prob=y_prob_test,
            amounts=amt_test,
            threshold=0.50
        )
        
        # Validation threshold grid
        val_grid = evaluate_threshold_grid(y_true=y_val, y_prob=y_prob_val, amounts=amt_val)
        threshold_grids[name] = val_grid
        
        # Optimal threshold selection on validation data
        best_th_info = select_best_threshold(val_grid, criterion='f1_score')
        selected_th = best_th_info['selected_threshold']
        
        # Test evaluation at selected threshold
        y_pred_tuned = (y_prob_test >= selected_th).astype(int)
        tuned_eval = evaluate_predictions(
            y_true=y_test,
            y_pred=y_pred_tuned,
            y_prob=y_prob_test,
            amounts=amt_test,
            threshold=selected_th
        )
        
        # Extract feature importance
        df_imp = extract_feature_importance(clf, FEATURE_COLUMNS, model_name=name)
        feature_importances[name] = df_imp
        
        comparison_rows.append({
            'Model': name,
            'Threshold': 0.50,
            'Precision': test_eval['precision'],
            'Recall': test_eval['recall'],
            'F1_Score': test_eval['f1_score'],
            'ROC_AUC': test_eval['roc_auc'],
            'PR_AUC': test_eval['pr_auc'],
            'True_Positives': test_eval['true_positives'],
            'False_Positives': test_eval['false_positives'],
            'False_Negatives': test_eval['false_negatives'],
            'True_Negatives': test_eval['true_negatives'],
            'Tuned_Threshold': selected_th,
            'Tuned_Precision': tuned_eval['precision'],
            'Tuned_Recall': tuned_eval['recall'],
            'Tuned_F1_Score': tuned_eval['f1_score'],
            'Tuned_TP': tuned_eval['true_positives'],
            'Tuned_FP': tuned_eval['false_positives'],
            'Tuned_FN': tuned_eval['false_negatives'],
            'Tuned_TN': tuned_eval['true_negatives']
        })
        
        results[name] = {
            'model': clf,
            'default_evaluation': test_eval,
            'tuned_threshold_info': best_th_info,
            'tuned_evaluation': tuned_eval,
            'feature_importance': df_imp,
            'threshold_grid': val_grid
        }
        
        if save_artifacts:
            model_file = MODELS_DIR / f"{name.lower()}_model.joblib"
            joblib.dump(clf, model_file)
            logger.info(f"Saved {name} model to {model_file}")
            
    if save_artifacts:
        scaler_file = MODELS_DIR / 'scaler.joblib'
        joblib.dump(scaler, scaler_file)
        logger.info(f"Saved scaler to {scaler_file}")
        
    df_comparison = pd.DataFrame(comparison_rows)
    
    if save_artifacts:
        df_comparison.to_csv(ML_RESULTS_DIR / 'model_comparison.csv', index=False)
        for name, df_imp in feature_importances.items():
            df_imp.to_csv(ML_RESULTS_DIR / f'feature_importance_{name.lower()}.csv', index=False)
        for name, df_grid in threshold_grids.items():
            df_grid.to_csv(ML_RESULTS_DIR / f'threshold_grid_{name.lower()}.csv', index=False)
            
    # Determine best model by PR-AUC (most appropriate for extreme class imbalance)
    best_model_name = df_comparison.sort_values(by='PR_AUC', ascending=False).iloc[0]['Model']
    
    summary = {
        'split_info': {
            'train_samples': len(y_train),
            'test_samples': len(y_test),
            'train_fraud': int(y_train.sum()),
            'test_fraud': int(y_test.sum()),
            'train_fraud_rate_pct': round(float(y_train.mean() * 100), 4),
            'test_fraud_rate_pct': round(float(y_test.mean() * 100), 4)
        },
        'leakage_audit': leakage_audit,
        'model_comparison': df_comparison.to_dict(orient='records'),
        'best_model': best_model_name,
        'best_model_pr_auc': float(df_comparison.loc[df_comparison['Model'] == best_model_name, 'PR_AUC'].values[0]),
        'results': results
    }
    
    return summary


if __name__ == '__main__':
    train_and_evaluate_all_models()
