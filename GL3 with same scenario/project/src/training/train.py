import os
import sys
import logging
import json
import getpass
import hashlib
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split, StratifiedKFold, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.utils.multiclass import type_of_target
from typing import Any, Dict

# Try to import MLflow if available
try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('model_training.log', mode='a')
    ]
)

def secure_file_permissions(filepath: str):
    """
    Restricts file permissions to owner read/write only (POSIX).
    """
    try:
        os.chmod(filepath, 0o600)
        logging.info(f"Restricted permissions for {filepath} to owner read/write only.")
    except Exception as e:
        logging.warning(f"Could not set secure file permissions for {filepath}: {e}")

def get_git_commit() -> str:
    """
    Attempts to obtain git commit SHA for provenance.
    """
    try:
        import subprocess
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL)
        return commit.decode('ascii').strip()
    except Exception:
        return "N/A"

def log_class_distribution(y, prefix: str, logger=logging):
    cls, counts = np.unique(y, return_counts=True)
    dist = {str(k): int(v) for k, v in zip(cls, counts)}
    perc = {str(k): round(v * 100.0 / len(y), 2) for k, v in zip(cls, counts)}
    logger.info(f"{prefix} class distribution: {dist} | %: {perc}")
    return dist

def check_nan_inf(X, y, logger=logging):
    X_nan = np.isnan(X).any().any() if isinstance(X, pd.DataFrame) else np.isnan(X).any()
    X_inf = np.isinf(X).any().any() if isinstance(X, pd.DataFrame) else np.isinf(X).any()
    y_nan = pd.isnull(y).any() if isinstance(y, (pd.Series, pd.DataFrame)) else np.isnan(y).any()
    y_inf = np.isinf(y).any() if isinstance(y, (np.ndarray, pd.Series)) else False
    if X_nan or X_inf or y_nan or y_inf:
        logger.error(f"Input contains NaN or Inf values. X_nan={X_nan}, X_inf={X_inf}, y_nan={y_nan}, y_inf={y_inf}")
        raise ValueError("Input contains NaN or Inf values.")
    else:
        logger.info("Input feature and target arrays validated: no NaN or Inf found.")

def detect_target_leakage(X: pd.DataFrame, y: pd.Series, original_df: pd.DataFrame, target_col: str, logger=logging):
    if target_col in X.columns:
        logger.warning(f"Target column '{target_col}' is present in features. Possible target leakage.")
    extra_targets = [col for col in original_df.columns if 'target' in col.lower() and col != target_col]
    if extra_targets:
        logger.warning(f"Columns potentially leaking target info present: {extra_targets}")

def check_data_drift(X_train, X_test, logger=logging, threshold=0.05):
    # Checks mean/std drift for numeric columns, logs severe drift
    num_cols = X_train.select_dtypes(include=np.number).columns if isinstance(X_train, pd.DataFrame) else []
    drifted_cols = []
    for col in num_cols:
        m1, m2 = X_train[col].mean(), X_test[col].mean()
        s1, s2 = X_train[col].std(), X_test[col].std()
        if s1 == 0 or s2 == 0: continue
        if abs(m1-m2) > threshold*abs(m1) or abs(s1-s2) > threshold*abs(s1):
            drifted_cols.append(col)
    if drifted_cols:
        logger.warning(f"Potential data drift detected for columns: {drifted_cols}")
    else:
        logger.info("No significant feature drift detected between train and test splits.")

def load_feature_matrix(feature_matrix_path: str, target_col: str):
    if not os.path.isfile(feature_matrix_path):
        logging.error(f"Feature matrix file '{feature_matrix_path}' does not exist.")
        sys.exit(1)
    df = pd.read_csv(feature_matrix_path)
    if target_col not in df.columns:
        logging.error(f"Target column '{target_col}' is not in the feature matrix.")
        sys.exit(2)
    X = df.drop(columns=[target_col])
    y = df[target_col]
    return X, y, df

def split_train_val_test(X, y, test_size=0.2, val_size=0.1, random_state=42):
    X_train, X_tmp, y_train, y_tmp = train_test_split(
        X, y, test_size=test_size + val_size, stratify=y, random_state=random_state
    )
    # rel_val_size: ratio of validation to (test+val) set
    rel_val_size = val_size / (test_size + val_size)
    X_val, X_test, y_val, y_test = train_test_split(
        X_tmp, y_tmp, test_size=1 - rel_val_size, stratify=y_tmp, random_state=random_state
    )
    return X_train, X_val, X_test, y_train, y_val, y_test

def save_preprocessing_metadata(artifacts_dir: str, feature_list, preprocessing_pipeline_path = None):
    metadata = {
        "feature_columns": feature_list,
        "pipeline_pickle": preprocessing_pipeline_path,
        "saved_at": datetime.now().isoformat(),
    }
    meta_path = os.path.join(artifacts_dir, 'preprocessing_metadata.json')
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    secure_file_permissions(meta_path)
    return meta_path

def log_feature_importance(model, X, artifacts_dir: str, model_name: str):
    if hasattr(model, 'feature_importances_'):
        featimp = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        outpath = os.path.join(artifacts_dir, f'{model_name}_feature_importance.csv')
        featimp.to_csv(outpath, index=False)
        secure_file_permissions(outpath)
        logging.info(f"Feature importance for {model_name} saved to {outpath}")
        return outpath
    return None

def evaluate(model, X, y, prefix='val'):
    y_pred = model.predict(X)
    # Dynamically detect problem type for averaging strategy
    try:
        y_type = type_of_target(y)
    except Exception:
        y_type = 'binary'
    if hasattr(model, 'predict_proba'):
        # If not binary, compute ROC-AUC with multi class support
        proba = model.predict_proba(X)
        try:
            if proba.shape[1] == 2:
                y_prob = proba[:,1]
                roc_auc = roc_auc_score(y, y_prob)
            else:
                roc_auc = roc_auc_score(y, proba, multi_class='ovr')
        except Exception:
            roc_auc = None
    else:
        roc_auc = None

    # Choose average type for multiclass/multilabel
    if y_type in ['multiclass', 'multilabel-indicator']:
        avg = 'weighted'
    else:
        avg = 'binary'

    result = {
        f'{prefix}_accuracy': accuracy_score(y, y_pred),
        f'{prefix}_precision': precision_score(y, y_pred, zero_division=0, average=avg),
        f'{prefix}_recall': recall_score(y, y_pred, zero_division=0, average=avg),
        f'{prefix}_f1': f1_score(y, y_pred, zero_division=0, average=avg),
        f'{prefix}_roc_auc': roc_auc,
        f'{prefix}_confusion_matrix': confusion_matrix(y, y_pred).tolist()
    }
    return result

def has_imbalance(y, threshold=0.8):
    values = pd.Series(y)
    counts = values.value_counts(normalize=True)
    if len(counts) > 1 and counts.max() > threshold:
        return True, counts.to_dict()
    return False, counts.to_dict()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Train and tune supervised classification models (RandomForest, XGBoost)")
    parser.add_argument('--feature_matrix', required=True, help='Input CSV file containing features and target column')
    parser.add_argument('--target_col', required=True, help='Name of the target column for classification')
    parser.add_argument('--artifacts_dir', required=True, help='Directory to save trained models and logs')
    parser.add_argument('--test_size', type=float, default=0.2, help='Test set proportion')
    parser.add_argument('--val_size', type=float, default=0.1, help='Validation set proportion (of entire data)')
    parser.add_argument('--rf_param_dist', default='', help='JSON: param grid for RandomForest (or default)')
    parser.add_argument('--xgb_param_dist', default='', help='JSON: param grid for XGBoost (or default)')
    parser.add_argument('--cv_folds', type=int, default=5, help='Cross-validation folds for tuning')
    parser.add_argument('--n_iter', type=int, default=30, help='Number of parameter settings sampled by randomized search')
    parser.add_argument('--random_state', type=int, default=42, help='Random seed')
    args = parser.parse_args()
    os.makedirs(args.artifacts_dir, exist_ok=True)
    X, y, df = load_feature_matrix(args.feature_matrix, args.target_col)

    # --- Security: Check for sensitive attributes ---
    sensitive_column_candidates = [col for col in X.columns if 'ssn' in col.lower() or 'name' in col.lower() or 'email' in col.lower() or 'dob' in col.lower()]
    if sensitive_column_candidates:
        logging.warning(f"Sensitive candidate columns potentially leaking PII: {sensitive_column_candidates}")
    
    # --- Target leakage detection ---
    detect_target_leakage(X, y, df, args.target_col)

    # --- Preprocessing pipeline feature/versioning ---
    feature_list = list(X.columns)
    preprocessing_meta_path = save_preprocessing_metadata(args.artifacts_dir, feature_list, None)  # Pipeline not provided here

    # --- Check for NaN/Inf and log class distribution ---
    check_nan_inf(X, y, logging)
    
    log_class_distribution(y, 'Original', logging)
    
    # --- Data leakage check: make sure test/val not contaminated ---
    X_train, X_val, X_test, y_train, y_val, y_test = split_train_val_test(X, y, args.test_size, args.val_size, args.random_state)
    logging.info(f"Train/val/test split shapes: X_train: {X_train.shape}, X_val: {X_val.shape}, X_test: {X_test.shape}")
    log_class_distribution(y_train, 'Train', logging)
    log_class_distribution(y_val, 'Val', logging)
    log_class_distribution(y_test, 'Test', logging)

    # --- Test for class imbalance and warn if excessive ---
    is_imbal_train, dist_train = has_imbalance(y_train)
    if is_imbal_train:
        logging.warning(f"Detected class imbalance in train set: {dist_train}")

    # --- Check for data drift between splits ---
    check_data_drift(X_train, X_test, logging)

    training_log = {
        'run_timestamp': datetime.now().isoformat(),
        'user': getpass.getuser(),
        'git_commit': get_git_commit(),
        'feature_matrix': os.path.abspath(args.feature_matrix),
        'target_col': args.target_col,
        'split': {
            'X_train_shape': list(X_train.shape),
            'X_val_shape': list(X_val.shape),
            'X_test_shape': list(X_test.shape),
            'train_class_dist': dist_train,
            'val_class_dist': log_class_distribution(y_val, 'val-class', logging),
            'test_class_dist': log_class_distribution(y_test, 'test-class', logging)
        },
        'rf_hyperparameters': {},
        'xgb_hyperparameters': {},
        'rf_best_param': {},
        'xgb_best_param': {},
        'rf_metrics': {},
        'xgb_metrics': {},
        'random_state': args.random_state,
        'artifacts': {},
        'feature_list': feature_list,
        'preprocessing_meta': preprocessing_meta_path
    }

    # --- Random Forest param distribution ---
    if args.rf_param_dist:
        try:
            rf_param_dist = json.loads(args.rf_param_dist)
        except Exception:
            logging.warning("rf_param_dist not valid JSON; using defaults.")
            rf_param_dist = None
    else:
        rf_param_dist = {
            'n_estimators': [100, 300, 500],
            'max_depth': [None, 5, 10, 20],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['auto', 'sqrt', 'log2'],
            'bootstrap': [True, False]
        }

    # --- XGBoost param distribution ---
    if args.xgb_param_dist:
        try:
            xgb_param_dist = json.loads(args.xgb_param_dist)
        except Exception:
            logging.warning("xgb_param_dist not valid JSON; using defaults.")
            xgb_param_dist = None
    else:
        xgb_param_dist = {
            'n_estimators': [100, 300, 500],
            'learning_rate': [0.01, 0.05, 0.1, 0.2],
            'max_depth': [3, 5, 7, 10],
            'subsample': [0.8, 1.0],
            'colsample_bytree': [0.8, 1.0],
            'gamma': [0, 1, 5],
            'reg_alpha': [0, 0.1, 1.0],
            'reg_lambda': [0.1, 1.0, 10.0]
        }

    # --- Random Forest Training (tunable scoring for imbalance/multiclass) ---
    scoring_metric = 'f1_weighted' if len(np.unique(y_train)) > 2 or is_imbal_train else 'f1'
    rf = RandomForestClassifier(random_state=args.random_state, n_jobs=-1)
    rf_search = RandomizedSearchCV(
        estimator=rf,
        param_distributions=rf_param_dist,
        n_iter=args.n_iter,
        scoring=scoring_metric,
        n_jobs=-1,
        cv=StratifiedKFold(n_splits=args.cv_folds, shuffle=True, random_state=args.random_state),
        verbose=1,
        random_state=args.random_state
    )
    logging.info(f"Starting Random Forest hyperparameter search with scoring: {scoring_metric}")
    rf_search.fit(X_train, y_train)
    best_rf = rf_search.best_estimator_
    training_log['rf_hyperparameters'] = rf_param_dist
    training_log['rf_best_param'] = rf_search.best_params_
    # --- Feature importance log for RF ---
    rf_featimp_path = log_feature_importance(best_rf, X_train, args.artifacts_dir, 'random_forest')
    training_log['artifacts']['rf_feature_importance'] = rf_featimp_path
    # --- Evaluate Random Forest ---
    training_log['rf_metrics'].update(evaluate(best_rf, X_train, y_train, prefix='train'))
    training_log['rf_metrics'].update(evaluate(best_rf, X_val, y_val, prefix='val'))
    training_log['rf_metrics'].update(evaluate(best_rf, X_test, y_test, prefix='test'))
    rf_model_path = os.path.join(args.artifacts_dir, 'random_forest_best.joblib')
    joblib.dump(best_rf, rf_model_path)
    secure_file_permissions(rf_model_path)
    training_log['artifacts']['rf_model'] = rf_model_path
    logging.info(f"Saved Random Forest model to {rf_model_path}")

    # --- XGBoost Training (tunable scoring for imbalance/multiclass) ---
    xgb = XGBClassifier(random_state=args.random_state, use_label_encoder=False, eval_metric='logloss', n_jobs=-1)
    xgb_search = RandomizedSearchCV(
        estimator=xgb,
        param_distributions=xgb_param_dist,
        n_iter=args.n_iter,
        scoring=scoring_metric,
        n_jobs=-1,
        cv=StratifiedKFold(n_splits=args.cv_folds, shuffle=True, random_state=args.random_state),
        verbose=1,
        random_state=args.random_state
    )
    logging.info(f"Starting XGBoost hyperparameter search with scoring: {scoring_metric}")
    xgb_search.fit(X_train, y_train)
    best_xgb = xgb_search.best_estimator_
    training_log['xgb_hyperparameters'] = xgb_param_dist
    training_log['xgb_best_param'] = xgb_search.best_params_
    # --- Feature importance log for XGB ---
    xgb_featimp_path = log_feature_importance(best_xgb, X_train, args.artifacts_dir, 'xgboost')
    training_log['artifacts']['xgb_feature_importance'] = xgb_featimp_path
    # --- Evaluate XGBoost ---
    training_log['xgb_metrics'].update(evaluate(best_xgb, X_train, y_train, prefix='train'))
    training_log['xgb_metrics'].update(evaluate(best_xgb, X_val, y_val, prefix='val'))
    training_log['xgb_metrics'].update(evaluate(best_xgb, X_test, y_test, prefix='test'))
    xgb_model_path = os.path.join(args.artifacts_dir, 'xgboost_best.joblib')
    joblib.dump(best_xgb, xgb_model_path)
    secure_file_permissions(xgb_model_path)
    training_log['artifacts']['xgb_model'] = xgb_model_path
    logging.info(f"Saved XGBoost model to {xgb_model_path}")

    # --- Model explainability & feature importance logging, CLI parameter audit ---
    cli_cmd = ' '.join(sys.argv)
    training_log['cli_command'] = cli_cmd
    
    # --- Log reproducibility: parameters, git, user, etc. ---
    train_log_path = os.path.join(args.artifacts_dir, 'model_training_log.json')
    with open(train_log_path, 'w') as f:
        json.dump(training_log, f, indent=2)
    secure_file_permissions(train_log_path)
    logging.info(f"Training log saved to {train_log_path}")
    if MLFLOW_AVAILABLE:
        try:
            mlflow.log_artifact(train_log_path)
            if rf_featimp_path: mlflow.log_artifact(rf_featimp_path)
            mlflow.log_artifact(rf_model_path)
            if xgb_featimp_path: mlflow.log_artifact(xgb_featimp_path)
            mlflow.log_artifact(xgb_model_path)
            logging.info("Logged artifacts to MLflow.")
        except Exception as e:
            logging.warning(f"MLflow log_artifact failed: {e}")

if __name__ == "__main__":
    main()
