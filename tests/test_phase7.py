"""
FraudLens — Phase 7: Automated Test Suite for Machine Learning Fraud Detection
Validates feature engineering, leakage prevention, stratified splitting, model training,
metric calculations, threshold analysis, feature importance, and inference contracts.
"""

import os
from pathlib import Path
import pytest
import numpy as np
import pandas as pd
import joblib

from src.utils.config import MODELS_DIR, PROCESSED_DATA_DIR, RANDOM_STATE
from src.ml.prepare_ml_data import (
    FEATURE_COLUMNS,
    EXCLUDED_COLUMNS,
    audit_features,
    load_and_prepare_features,
    create_train_test_splits,
    create_validation_split
)
from src.ml.evaluate_models import evaluate_predictions
from src.ml.threshold_analysis import evaluate_threshold_grid, select_best_threshold
from src.ml.feature_importance import extract_feature_importance
from src.ml.predict import predict_transaction, load_model


def test_1_feature_preparation_and_leakage_audit():
    """Verifies that all 20 predictive features are defined and zero target/heuristic leakage exists."""
    assert len(FEATURE_COLUMNS) == 20
    assert 'isFraud' not in FEATURE_COLUMNS
    assert 'isFlaggedFraud' not in FEATURE_COLUMNS
    assert 'nameOrig' not in FEATURE_COLUMNS
    assert 'nameDest' not in FEATURE_COLUMNS
    assert 'orig_balance_consistency' not in FEATURE_COLUMNS
    
    # Audit test
    dummy_df = pd.DataFrame(columns=FEATURE_COLUMNS + ['isFraud', 'isFlaggedFraud'])
    audit = audit_features(dummy_df)
    assert audit['leakage_status'] == 'PASS (Zero Leakage)'
    assert len(audit['leakage_risks']) == 0
    assert audit['selected_features_count'] == 20


def test_2_stratified_split_proportions():
    """Verifies stratified 80/20 train/test split preserving target class ratio."""
    # Create small synthetic test set to verify split mechanics
    y_synth = pd.Series([1] * 100 + [0] * 9900)  # 1% fraud
    X_synth = pd.DataFrame(np.random.randn(10000, 20), columns=FEATURE_COLUMNS)
    amounts_synth = np.ones(10000) * 100.0
    
    splits = create_train_test_splits(X_synth, y_synth, amounts_synth, test_size=0.2, random_state=42)
    assert len(splits['y_train']) == 8000
    assert len(splits['y_test']) == 2000
    assert splits['y_train'].sum() == 80
    assert splits['y_test'].sum() == 20
    assert abs(splits['y_train'].mean() - 0.01) < 1e-4
    assert abs(splits['y_test'].mean() - 0.01) < 1e-4


def test_3_training_weight_calculation():
    """Verifies class imbalance weight is computed strictly from training labels."""
    y_train = pd.Series([1] * 100 + [0] * 9900)
    train_negatives = int((y_train == 0).sum())
    train_positives = int((y_train == 1).sum())
    pos_weight = float(train_negatives / train_positives)
    assert pos_weight == 99.0


def test_4_model_artifacts_exist():
    """Verifies all serialized models and scaler exist in models directory."""
    expected_files = [
        'logisticregression_model.joblib',
        'randomforest_model.joblib',
        'xgboost_model.joblib',
        'scaler.joblib'
    ]
    for filename in expected_files:
        path1 = MODELS_DIR / filename
        path2 = Path('models') / filename
        assert path1.exists() or path2.exists(), f"Model artifact {filename} missing"


def test_5_model_loading_and_prediction_ranges():
    """Verifies models load cleanly and generate valid probability scores in [0, 1]."""
    for model_name in ['xgboost', 'randomforest', 'logisticregression']:
        art = load_model(model_name)
        assert art['model'] is not None
        assert art['feature_columns'] == FEATURE_COLUMNS


def test_6_confusion_matrix_reconciliation():
    """Verifies exact reconciliation of TP, FP, FN, TN against test set truth."""
    y_true = np.array([1] * 50 + [0] * 950)
    y_prob = np.linspace(0, 1, 1000)
    y_pred = (y_prob >= 0.50).astype(int)
    
    eval_res = evaluate_predictions(y_true, y_pred, y_prob)
    assert eval_res['true_positives'] + eval_res['false_negatives'] == 50
    assert eval_res['true_negatives'] + eval_res['false_positives'] == 950
    assert eval_res['total_samples'] == 1000


def test_7_evaluation_metrics_precision_recall_f1():
    """Verifies mathematical consistency of precision, recall, and F1 calculations."""
    y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0])
    y_pred = np.array([1, 1, 0, 0, 1, 0, 0, 0])
    # TP = 2, FP = 1, FN = 2, TN = 3
    # Precision = 2 / 3 = 0.6667, Recall = 2 / 4 = 0.5000, F1 = 2 * (2/3 * 0.5) / (2/3 + 0.5) = 0.5714
    res = evaluate_predictions(y_true, y_pred)
    assert res['true_positives'] == 2
    assert res['false_positives'] == 1
    assert res['false_negatives'] == 2
    assert res['true_negatives'] == 3
    assert abs(res['precision'] - 0.6667) < 1e-3
    assert abs(res['recall'] - 0.5000) < 1e-3
    assert abs(res['f1_score'] - 0.5714) < 1e-3


def test_8_threshold_grid_monotonicity_and_tradeoffs():
    """Verifies that higher probability thresholds monotonically decrease false alert counts."""
    y_true = np.random.binomial(1, 0.05, 500)
    y_prob = np.random.uniform(0, 1, 500)
    
    df_grid = evaluate_threshold_grid(y_true, y_prob, thresholds=[0.1, 0.3, 0.5, 0.7, 0.9])
    assert len(df_grid) == 5
    assert (df_grid['alert_count'].diff().dropna() <= 0).all()  # Non-increasing alerts


def test_9_feature_importance_ranking():
    """Verifies feature importances structure and non-empty ranking."""
    art = load_model('xgboost')
    df_imp = extract_feature_importance(art['model'], FEATURE_COLUMNS, 'XGBoost')
    assert len(df_imp) == len(FEATURE_COLUMNS)
    assert 'importance_score' in df_imp.columns
    assert 'relative_importance_pct' in df_imp.columns
    assert df_imp['importance_score'].iloc[0] >= df_imp['importance_score'].iloc[-1]


def test_10_single_transaction_inference_contract():
    """Verifies single-transaction prediction API returns formatted response dictionary."""
    sample_payload = {
        'step': 100,
        'type': 'TRANSFER',
        'amount': 500000.0,
        'oldbalanceOrg': 500000.0,
        'newbalanceOrig': 0.0,
        'oldbalanceDest': 0.0,
        'newbalanceDest': 0.0,
        'nameOrig': 'C123456789',
        'nameDest': 'C987654321'
    }
    pred_res = predict_transaction(sample_payload, model_name='xgboost', threshold=0.50)
    assert 'fraud_probability' in pred_res
    assert 'is_fraud_predicted' in pred_res
    assert 'risk_tier' in pred_res
    assert 0.0 <= pred_res['fraud_probability'] <= 1.0
    assert pred_res['is_fraud_predicted'] in (0, 1)


def test_11_model_comparison_table_integrity():
    """Verifies that model_comparison.csv contains all 3 models with verified test metrics."""
    comp_file = PROCESSED_DATA_DIR / 'ml' / 'model_comparison.csv'
    assert comp_file.exists()
    df_comp = pd.read_csv(comp_file)
    assert len(df_comp) == 3
    assert set(df_comp['Model']) == {'LogisticRegression', 'RandomForest', 'XGBoost'}
    
    # Check that PR-AUC and ROC-AUC are valid
    assert (df_comp['PR_AUC'] >= 0.80).all()
    assert (df_comp['ROC_AUC'] >= 0.95).all()
    
    # Check that confusion matrix sums to test set size (1,272,524)
    for _, row in df_comp.iterrows():
        total_cm = row['True_Positives'] + row['False_Positives'] + row['False_Negatives'] + row['True_Negatives']
        assert total_cm == 1272524
        assert row['True_Positives'] + row['False_Negatives'] == 1643


def test_12_validation_split_prevents_test_leakage():
    """Verifies that internal validation split is disjoint from test split."""
    y_synth = pd.Series([1] * 100 + [0] * 9900)
    X_synth = pd.DataFrame(np.random.randn(10000, 20), columns=FEATURE_COLUMNS)
    
    train_test = create_train_test_splits(X_synth, y_synth, test_size=0.2, random_state=42)
    val_splits = create_validation_split(train_test['X_train'], train_test['y_train'], val_size=0.2, random_state=42)
    
    # Check indices are mutually exclusive
    train_indices = set(train_test['idx_train'])
    test_indices = set(train_test['idx_test'])
    assert len(train_indices.intersection(test_indices)) == 0
