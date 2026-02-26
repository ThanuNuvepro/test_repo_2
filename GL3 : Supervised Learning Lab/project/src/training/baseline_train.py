import os
import sys
import json
import yaml
import numpy as np
import joblib
import logging
import time
import hashlib
import shutil
from collections import Counter
from typing import Any, Dict
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# --- Logging Setup: Remove all handlers before setting config to avoid ignoring config in multi-module pipelines ---
def setup_logging():
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )

# --- Secure Path Validation (aligns with previous context) ---
def is_valid_path(path: str) -> bool:
    import re
    if not isinstance(path, str):
        return False
    norm_path = os.path.normpath(path)
    if '..' in norm_path.split(os.sep):
        return False
    # Allow .csv, .npy, .json, .joblib, .pkl, .yaml, .yml inside data/
    if not norm_path.startswith('data' + os.sep):
        return False
    if not re.match(r'^data\%s[a-zA-Z0-9_\-/]+\.(csv|npy|json|joblib|pkl|yaml|yml)$' % re.escape(os.sep), norm_path):
        return False
    return True

# --- Robust NumPy Loading ---
def load_numpy_array(path: str) -> np.ndarray:
    if not os.path.exists(path):
        raise FileNotFoundError(f'{path} not found')
    return np.load(path)

# --- YAML/JSON Config Loading ---
def load_config(config_path: str) -> Dict[str, Any]:
    if not isinstance(config_path, str):
        raise ValueError('Config path must be a string.')
    if not os.path.exists(config_path):
        raise FileNotFoundError(f'Config file not found at {config_path}')
    ext = os.path.splitext(config_path)[1].lower()
    with open(config_path, 'r') as f:
        if ext in ['.yaml', '.yml']:
            conf = yaml.safe_load(f)
        elif ext == '.json':
            conf = json.load(f)
        else:
            raise ValueError('Unsupported config file extension.')
    return conf

# --- Classifier Selection with Defaults ---
def get_classifier(model_type: str = 'random_forest', params: Dict[str, Any] = None):
    if model_type == 'random_forest':
        return RandomForestClassifier(**(params or {}))
    elif model_type == 'logistic_regression':
        return LogisticRegression(**(params or {}))
    else:
        raise ValueError(f'Unknown model_type: {model_type}')

# --- Model Saving with backup if existing ---
def save_model(model, out_path: str):
    dir_path = os.path.dirname(out_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # Backup old model if present
    if os.path.exists(out_path):
        shutil.copy2(out_path, out_path + '.bak')
        logging.warning(f'Previous model at {out_path} backed up as {out_path}.bak')
    joblib.dump(model, out_path)

# --- Save dictionary as JSON with dir creation ---
def save_dict(dct: dict, out_path: str):
    dir_path = os.path.dirname(out_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(out_path, 'w') as f:
        json.dump(dct, f, indent=2)

# --- Compute Model Hash for Versioning (astype to bytes then sha256) ---
def get_model_hash(model, config: dict = None) -> str:
    # Use joblib serialization to generate a hash from model and (optionally) config
    import io
    bytestream = io.BytesIO()
    joblib.dump(model, bytestream)
    hash_input = bytestream.getvalue()
    if config:
        hash_input += json.dumps(config, sort_keys=True).encode('utf-8')
    return hashlib.sha256(hash_input).hexdigest()

# --- Audit Trail Creation ---
def create_audit_trail(metadata: dict, filepath: str):
    dir_path = os.path.dirname(filepath)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(filepath, 'w') as f:
        json.dump(metadata, f, indent=2)
    logging.info(f'Audit trail written to {filepath}')

# --- Detect Class Imbalance (warn if severe) ---
def detect_class_imbalance(y: np.ndarray, threshold: float = 0.8):
    counts = Counter(y.tolist())
    if len(counts) <= 1:
        logging.warning('Only one class present in label array; all samples have the same class.')
        return True, counts
    max_class = max(counts.values())
    total = sum(counts.values())
    imbalance_ratio = max_class / total
    imbalanced = (imbalance_ratio > threshold)
    if imbalanced:
        logging.warning(f'Class imbalance detected: Class distribution {dict(counts)}, max class {imbalance_ratio*100:.1f}% of total.')
    return imbalanced, counts

# --- Modular Metrics Evaluation with Explicit NaN Checking and Average Determination ---
def evaluate_model(clf, X, y, average: str = None) -> Dict[str, float]:
    # Prediction
    try:
        y_pred = clf.predict(X)
    except Exception as e:
        logging.error(f'Prediction failed: {e}')
        raise
    metrics = {}
    # Determine average if not provided
    n_classes = len(np.unique(y))
    if average is None:
        average = 'binary' if n_classes == 2 else 'macro'
    # Metrics calculation
    metrics['accuracy'] = float(accuracy_score(y, y_pred))
    # F1, Precision, Recall
    metrics['precision'] = float(precision_score(y, y_pred, average=average, zero_division=0))
    metrics['recall'] = float(recall_score(y, y_pred, average=average, zero_division=0))
    metrics['f1'] = float(f1_score(y, y_pred, average=average, zero_division=0))
    # ROC AUC for binary or multi-class with predict_proba
    if hasattr(clf, 'predict_proba') and (average == 'binary' or n_classes > 2):
        try:
            if n_classes == 2:
                y_proba = clf.predict_proba(X)[:, 1]
                metrics['roc_auc'] = float(roc_auc_score(y, y_proba))
            else:
                y_prob = clf.predict_proba(X)
                metrics['roc_auc'] = float(roc_auc_score(y, y_prob, multi_class='ovr', average=average))
        except Exception as e:
            logging.warning(f'ROC AUC calculation failed: {e}')
            metrics['roc_auc'] = float('nan')
    # NaN checking
    for k, v in metrics.items():
        if np.isnan(v):
            logging.warning(f'Metric {k} is NaN. Possibly due to single-class y or metric instability.')
    return metrics

# --- Ensure Output Directory Exists ---
def ensure_output_dir(path: str):
    dir_path = os.path.dirname(path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)

# --- Structured Error Handling for Training ---
def robust_fit(clf, X, y):
    try:
        clf.fit(X, y)
        return clf
    except Exception as e:
        logging.exception('Model training failed.')
        raise RuntimeError(f'Model training failed: {e}')

# --- Dependency Recording ---
def dump_env_requirements(filepath: str):
    try:
        import pkg_resources
        reqs = {dist.project_name: dist.version for dist in pkg_resources.working_set}
        dir_path = os.path.dirname(filepath)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(filepath, 'w') as f:
            json.dump(reqs, f, indent=2)
        logging.info(f'Environment dependency versions dumped at {filepath}')
    except Exception as e:
        logging.warning(f'Failed to record environment requirements: {e}')

# --- Resource & Duration Tracking ---
def log_resource_utilization(start_time, comment_prefix=''):
    duration = time.time() - start_time
    try:
        import psutil
        mem_mb = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
        logging.info(f'{comment_prefix}Train duration: {duration:.2f}s, Memory used: {mem_mb:.1f} MB')
    except ImportError:
        logging.info(f'{comment_prefix}Train duration: {duration:.2f}s')

# --- Main Entrypoint ---
def main():
    import argparse
    setup_logging()
    parser = argparse.ArgumentParser(description='Baseline model training (scikit-learn) with audit, versioning, and reproducibility')
    parser.add_argument('--X_train', type=str, default='data/X_train.npy', help='Path to training features .npy')
    parser.add_argument('--y_train', type=str, default='data/y_train.npy', help='Path to training target .npy')
    parser.add_argument('--X_test', type=str, default='data/X_test.npy', help='Path to test features .npy')
    parser.add_argument('--y_test', type=str, default='data/y_test.npy', help='Path to test target .npy')
    parser.add_argument('--config', type=str, default='src/config/baseline_model_config.yaml', help='Path to config file (YAML/JSON)')
    parser.add_argument('--output_model', type=str, default='data/baseline_model.joblib', help='Path to save trained model')
    parser.add_argument('--metrics_out', type=str, default='data/baseline_metrics.json', help='Where to record evaluation metrics')
    parser.add_argument('--audit_trail', type=str, default='data/baseline_train_audit.json', help='Where to record audit trail')
    parser.add_argument('--env_dump', type=str, default='data/requirements.env.json', help='Where to record dependency environment')
    args = parser.parse_args()

    # Securely check CLI-supplied data and output paths
    input_paths = [args.X_train, args.y_train, args.X_test, args.y_test, args.config]
    output_paths = [args.output_model, args.metrics_out, args.audit_trail, args.env_dump]
    for p in input_paths + output_paths:
        if not is_valid_path(p):
            logging.error(f'Unsafe or invalid path: {p}')
            sys.exit(1)
    # Ensure output/output_model/metrics_out dirs exist
    for p in output_paths:
        ensure_output_dir(p)
    # Load train/test arrays and config
    X_train = load_numpy_array(args.X_train)
    y_train = load_numpy_array(args.y_train)
    X_test = load_numpy_array(args.X_test)
    y_test = load_numpy_array(args.y_test)
    config = load_config(args.config)
    model_type = config.get('model_type', 'random_forest')
    model_params = config.get('model_params', {})

    # Set seeds for numpy, sklearn, and Python for reproducibility
    seed = model_params.get('random_state', 42)
    np.random.seed(seed)
    import random
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)

    # Detect and warn about severe class imbalance on y_train
    imbalance, class_counts = detect_class_imbalance(y_train)
    # Allow user config to opt-in to class_weight='balanced' for imbalanced targets
    if imbalance and 'class_weight' not in model_params:
        logging.info('Severe class imbalance detected. Adding class_weight="balanced" to model parameters.')
        model_params['class_weight'] = 'balanced'

    clf = get_classifier(model_type, model_params)
    logging.info(f'Training baseline {model_type} with params: {model_params}')
    start_train_time = time.time()
    # Robust training
    clf = robust_fit(clf, X_train, y_train)
    log_resource_utilization(start_train_time, comment_prefix='Training - ')

    # Save model with backup/version safety
    save_model(clf, args.output_model)
    logging.info(f'Trained model saved: {args.output_model}')

    # Version/hash and audit-trail
    model_hash = get_model_hash(clf, {'type': model_type, 'params': model_params})

    # Train & test metrics with explicit average strategy
    n_classes = len(np.unique(y_train))
    average_strategy = 'binary' if n_classes == 2 else 'macro'
    train_metrics = evaluate_model(clf, X_train, y_train, average=average_strategy)
    test_metrics = evaluate_model(clf, X_test, y_test, average=average_strategy)
    # If any metric is nan present, emit warning
    if any(np.isnan(v) for v in list(train_metrics.values()) + list(test_metrics.values())):
        logging.warning('Some evaluation metrics are NaN. Check for single-class splits or metric definition compatibility.')

    # Audit trail with hash over config, code, input sets
    audit_info = {
        'model_type': model_type,
        'model_params': model_params,
        'trained_model_hash': model_hash,
        'X_train': args.X_train,
        'y_train': args.y_train,
        'X_test': args.X_test,
        'y_test': args.y_test,
        'config_path': args.config,
        'output_model': args.output_model,
        'metrics_out': args.metrics_out,
        'class_counts': dict(class_counts),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
        'git_commit': get_git_commit_hash(),
        'env_requirements_file': args.env_dump
    }
    create_audit_trail(audit_info, args.audit_trail)

    metrics = {
        'train': train_metrics,
        'test': test_metrics,
        'model_type': model_type,
        'model_params': model_params,
        'hash': model_hash,
        'audit_trail': args.audit_trail,
        'X_train_shape': list(X_train.shape),
        'X_test_shape': list(X_test.shape),
        'class_counts': dict(class_counts)
    }
    save_dict(metrics, args.metrics_out)
    logging.info(f'Model evaluation metrics written to: {args.metrics_out}')
    # Dump environment
    dump_env_requirements(args.env_dump)

    print(f'Baseline training complete. Model: {args.output_model}. Metrics: {args.metrics_out}.')
    print(json.dumps(metrics, indent=2))
    print(f'Audit trail: {args.audit_trail}, dependencies: {args.env_dump}')

    # Simple post-training drift/monitoring hook stub
    try:
        drift_report = check_post_training_drift(X_train, X_test)
        if drift_report:
            logging.info(f'Monitoring: Feature drift report: {drift_report}')
    except Exception as e:
        logging.warning(f'Post-training drift check skipped/failing: {e}')

# --- Git Commit Hash for Audit ---
def get_git_commit_hash():
    try:
        import subprocess
        output = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=os.getcwd())
        return output.decode('utf-8').strip()
    except Exception:
        return None

# --- Post-training Drift Monitoring Stub ---
def check_post_training_drift(X_train: np.ndarray, X_test: np.ndarray) -> dict:
    from scipy.stats import wasserstein_distance
    drift_report = {}
    # Compare marginal distributions for each feature
    n_features = X_train.shape[1]
    for i in range(n_features):
        distance = wasserstein_distance(X_train[:, i], X_test[:, i])
        drift_report[f'feature_{i}'] = distance
    # High drift values can be flagged
    max_drift = max(drift_report.values())
    if max_drift > 1.0:
        logging.warning(f'Major drift detected in at least one feature: Wasserstein distance = {max_drift:.3f}')
    return drift_report

if __name__ == '__main__':
    main()
