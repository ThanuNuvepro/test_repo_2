import os
import json
import joblib
import numpy as np
import matplotlib.pyplot as plt
import logging
from typing import Dict, Tuple, List, Optional
import re
import time

# --- Setup module-specific logger ---
logger = logging.getLogger(__name__)

# Improved logging setup (module-level, does not reset other configs)
def setup_logging():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(handler)

# File and output path security - restricts traversal & enforces data dir scope
def is_valid_path(path: str) -> bool:
    if not isinstance(path, str):
        return False
    norm_path = os.path.normpath(path)
    if '..' in norm_path.split(os.sep):
        return False
    if not norm_path.startswith('data' + os.sep):
        return False
    # Only allow supported file types for models/data/images/reports
    allowed_exts = ['joblib', 'pkl', 'npy', 'json', 'png', 'txt']
    ext = os.path.splitext(norm_path)[1].replace('.', '')
    if ext not in allowed_exts:
        return False
    # Directory for output (does not check extension here but prevents escapes)
    return True

def is_valid_out_dir(directory: str) -> bool:
    """Ensure output directory doesn't escape 'data/' root, not just for files."""
    if not isinstance(directory, str):
        return False
    norm = os.path.normpath(directory)
    if '..' in norm.split(os.sep):
        return False
    if not norm.startswith('data'+os.sep):
        return False
    return True

# --- Helper: Load Feature Manifest ---
def get_feature_names(manifest_path: str) -> List[str]:
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f'Feature manifest not found: {manifest_path}')
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    names = manifest.get('features', [])
    if not names:
        raise RuntimeError(f"No features found in manifest {manifest_path}")
    return names

# --- Helper: Load Model ---
def load_model(model_path: str):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f'Model not found: {model_path}')
    return joblib.load(model_path)

# Baseline (scikit-learn) feature importance
# Improvements:
#   - If model has no feature_importances_/coef_, info in logger AND RuntimeError
#   - If length mismatch, log error with importances/feature_names values
#   - If ensemble model, flag generic error

def extract_sklearn_importance(clf, feature_names: List[str]) -> Tuple[str, List[str], np.ndarray]:
    if hasattr(clf, 'estimators_'):
        logger.info('Model is ensemble/voting/stacking; feature_importance extraction not currently supported.')
        raise RuntimeError('Ensemble models (Voting/Stacking) are not supported for global feature importance extraction.')
    # Try known keys
    if hasattr(clf, 'feature_importances_'):
        importances = clf.feature_importances_
        model_type = 'Random Forest'
    elif hasattr(clf, 'coef_'):
        coef = clf.coef_
        if coef.ndim == 1:
            importances = np.abs(coef)
        else:
            importances = np.mean(np.abs(coef), axis=0)
        model_type = 'Logistic Regression'
    else:
        logger.error(f'Model {type(clf)} does not expose feature_importances_ or coef_. Cannot extract feature importance.')
        raise RuntimeError('Model does not expose feature_importances_ or coef_. Cannot extract feature importance.')
    if len(importances) != len(feature_names):
        logger.error(f'IMPORTANCE-LENGTH MISMATCH: importances={importances} ({len(importances)}), feature_names={feature_names} ({len(feature_names)})')
        raise ValueError(f'Importances length {len(importances)} does not match feature names {len(feature_names)}')
    return model_type, feature_names, importances

# --- XGBoost feature importance extraction ---
def extract_xgboost_importance(xgb_clf, feature_names: List[str]) -> Tuple[str, List[str], np.ndarray]:
    try:
        # Try XGBoost's native get_booster
        booster = xgb_clf.get_booster() if hasattr(xgb_clf, 'get_booster') else None
        if booster is not None:
            internal_names = booster.feature_names or feature_names
            # Feature keys may be 'f0', 'f1', ... or custom-named
            importances_dict = booster.get_score(importance_type='weight')
            # Try mapping by internal_names vs manifest
            mapped = []
            try:
                # Detect if keys are integers or custom names -> remap accordingly
                if all(k.startswith('f') and k[1:].isdigit() for k in importances_dict):
                    # Typical XGBoost f0..fN: rely on manifest order
                    mapped = [importances_dict.get(f'f{i}', 0.0) for i in range(len(feature_names))]
                else:
                    # Feature names are custom/named: map from feature_names (manifest)
                    mapped = [importances_dict.get(fname, 0.0) for fname in feature_names]
            except Exception:
                # Fallback
                mapped = [importances_dict.get(f'f{i}', 0.0) for i in range(len(feature_names))]
            importance_arr = np.array(mapped)
            # If all-zero, try 'gain' as fallback
            if (importance_arr == 0).all():
                importances_dict = booster.get_score(importance_type='gain')
                try:
                    if all(k.startswith('f') and k[1:].isdigit() for k in importances_dict):
                        mapped = [importances_dict.get(f'f{i}', 0.0) for i in range(len(feature_names))]
                    else:
                        mapped = [importances_dict.get(fname, 0.0) for fname in feature_names]
                except Exception:
                    mapped = [importances_dict.get(f'f{i}', 0.0) for i in range(len(feature_names))]
                importance_arr = np.array(mapped)
            model_type = 'XGBoost'
        elif hasattr(xgb_clf, 'feature_importances_'):
            importance_arr = xgb_clf.feature_importances_
            model_type = 'XGBoost'
        else:
            logger.error('Model does not expose native XGBoost booster or feature_importances_.')
            raise RuntimeError('XGBoost model missing importance attributes.')
        names_used = feature_names
    except Exception as ex:
        logger.error(f'Exception extracting importance from XGBoost: {ex}')
        if hasattr(xgb_clf, 'feature_importances_'):
            importance_arr = xgb_clf.feature_importances_
            model_type = 'XGBoost'
            names_used = feature_names
        else:
            raise RuntimeError('Cannot extract importances from XGBoost model.')
    if len(importance_arr) != len(feature_names):
        logger.error(f'XGBOOST IMPORTANCE-LENGTH MISMATCH: importances={importance_arr} ({len(importance_arr)}), feature_names={feature_names} ({len(feature_names)})')
        raise ValueError(f'Feature importance length {len(importance_arr)} != feature name count {len(feature_names)})')
    return model_type, feature_names, importance_arr

# --- Plotting ---
def plot_importance(feature_names: List[str], importances: np.ndarray, title: str, out_path: str, top_n: int = 10) -> str:
    idx_sorted = np.argsort(importances)[::-1]
    top_idx = idx_sorted[:top_n]
    top_features = [feature_names[i] for i in top_idx]
    top_importances = importances[top_idx]
    plt.figure(figsize=(1.4*max(5, len(top_features)), 6))
    plt.bar(top_features, top_importances, color='royalblue')
    plt.ylabel('Importance Score')
    plt.title(title)
    plt.xticks(rotation=35, ha='right')
    plt.tight_layout()
    try:
        plt.savefig(out_path)
        logger.info(f'Saved feature importance chart: {out_path}')
    except Exception as ex:
        logger.error(f'Failed to save chart {out_path}: {ex}')
        raise
    finally:
        plt.close()
    return out_path

# --- Feature importance summary ---
def summarize_feature_importance(feature_names, importances, model_type, top_n=5, provenance: Optional[dict]=None) -> str:
    idx_sorted = np.argsort(importances)[::-1]
    msg = []
    msg.append(f'Feature Importance Summary ({model_type})')
    if provenance:
        msg.append(f"- Model hash: {provenance.get('model_hash','N/A')}")
        msg.append(f"- Feature manifest: {provenance.get('manifest','N/A')}")
        msg.append(f"- Metrics file: {provenance.get('metrics','N/A')}")
    for i in range(min(len(idx_sorted), top_n)):
        idx = idx_sorted[i]
        msg.append(f'- {i+1}. {feature_names[idx]}: {importances[idx]:.4f}')
    msg.append('Interpretation:')
    main_feats = [feature_names[idx_sorted[i]] for i in range(min(len(idx_sorted), top_n))]
    msg.append(
        f'The most influential features for this model are: {", ".join(main_feats)}.'
    )
    msg.append('Practically, these sensor readings should be prioritized for monitoring, maintenance, and domain review, as anomalies in these heavily affect predictive outcomes.')
    return '
'.join(msg)

# --- Audit Info Embedding ---
def load_model_hash_and_metrics(model_path: str, metrics_path: Optional[str]) -> dict:
    hash_val = None
    metrics = None
    try:
        # Model hash can be derived as in training pipeline
        if os.path.exists(model_path):
            import hashlib
            import io
            bytestream = io.BytesIO()
            joblib.dump(joblib.load(model_path), bytestream)
            hash_val = hashlib.sha256(bytestream.getvalue()).hexdigest()
    except Exception as ex:
        logger.warning(f'Unable to compute model hash for {model_path}: {ex}')
        hash_val = None
    if metrics_path and os.path.exists(metrics_path):
        try:
            with open(metrics_path) as f:
                metrics = json.load(f)
        except Exception:
            metrics = None
    return {'model_hash': hash_val, 'metrics': metrics_path}

# --- Write summary to text file ---
def write_interpretation_to_file(report: str, report_path: str) -> str:
    dir_path = os.path.dirname(report_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(report_path, 'w') as f:
        f.write(report)
    logger.info(f'Interpretation written to: {report_path}')
    return report_path

# --- Pipeline: Compute, log, output summaries and charts, with compliance and audit integration ---
def feature_importance_pipeline(
    sklearn_model_path: str = 'data/baseline_model.joblib',
    xgb_model_path: str = 'data/xgb_model.joblib',
    manifest_path: str = 'data/feature_manifest.json',
    out_dir: str = 'data/feature_importance',
    baseline_metrics: Optional[str] = 'data/baseline_metrics.json',
    xgb_metrics: Optional[str] = 'data/xgb_metrics.json',
    top_n: int = 10
) -> Dict[str, str]:
    setup_logging()
    logger.info('Starting feature importance pipeline...')
    # --- Path and output dir checks ---
    for p in [sklearn_model_path, xgb_model_path, manifest_path]:
        if not is_valid_path(p):
            logger.error(f'Unsafe or invalid file path supplied: {p}')
            raise ValueError(f'Unsafe or invalid path: {p}')
    if not is_valid_out_dir(out_dir):
        logger.error(f"Unsafe/invalid output dir: {out_dir}")
        raise ValueError(f'Unsafe or invalid directory: {out_dir}')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    # --- Feature names from latest manifest ---
    feature_names = get_feature_names(manifest_path)
    # --- Baseline ---
    clf = load_model(sklearn_model_path)
    try:
        model_type_sklearn, features, importances = extract_sklearn_importance(clf, feature_names)
    except Exception as ex:
        logger.error(f'Error extracting baseline feature importance: {ex}')
        raise
    out_chart1 = os.path.join(out_dir, 'baseline_sklearn_feature_importance.png')
    plot_importance(features, importances, title=f'{model_type_sklearn} - Feature Importance', out_path=out_chart1, top_n=top_n)
    provenance = {
        'model_hash': load_model_hash_and_metrics(sklearn_model_path, baseline_metrics).get('model_hash'),
        'manifest': manifest_path,
        'metrics': baseline_metrics
    }
    interp_txt1 = summarize_feature_importance(features, importances, model_type_sklearn, top_n=top_n, provenance=provenance)
    interp_file1 = os.path.join(out_dir, 'baseline_sklearn_importance_interpretation.txt')
    write_interpretation_to_file(interp_txt1, interp_file1)
    # --- XGBoost ---
    xgb = load_model(xgb_model_path)
    try:
        model_type_xgb, features_xgb, importances_xgb = extract_xgboost_importance(xgb, feature_names)
    except Exception as ex:
        logger.error(f'Error extracting XGBoost feature importance: {ex}')
        raise
    out_chart2 = os.path.join(out_dir, 'xgboost_feature_importance.png')
    plot_importance(features_xgb, importances_xgb, title=f'{model_type_xgb} - Feature Importance', out_path=out_chart2, top_n=top_n)
    provenance2 = {
        'model_hash': load_model_hash_and_metrics(xgb_model_path, xgb_metrics).get('model_hash'),
        'manifest': manifest_path,
        'metrics': xgb_metrics
    }
    interp_txt2 = summarize_feature_importance(features_xgb, importances_xgb, model_type_xgb, top_n=top_n, provenance=provenance2)
    interp_file2 = os.path.join(out_dir, 'xgboost_importance_interpretation.txt')
    write_interpretation_to_file(interp_txt2, interp_file2)
    # --- Process metadata logging ---
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    meta_path = os.path.join(out_dir, 'feature_importance_process_metadata.json')
    try:
        with open(meta_path, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'out_dir': out_dir,
                'baseline_chart': out_chart1,
                'xgboost_chart': out_chart2,
                'baseline_interpretation': interp_file1,
                'xgboost_interpretation': interp_file2,
                'manifest': manifest_path
            }, f, indent=2)
        logger.info(f'Process metadata written to {meta_path}')
    except Exception as ex:
        logger.warning(f'Could not write metadata file: {ex}')
    print(f'Feature importance bar charts saved: {out_chart1}, {out_chart2}')
    print(f'Written interpretation/summary: {interp_file1}, {interp_file2}')
    return {
        'baseline_chart': out_chart1,
        'xgboost_chart': out_chart2,
        'baseline_interpretation': interp_file1,
        'xgboost_interpretation': interp_file2,
        'process_metadata': meta_path
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extract and visualize feature importance for both models, with audit trail and error handling.')
    parser.add_argument('--sklearn_model', type=str, default='data/baseline_model.joblib', help='Baseline model path (.joblib/.pkl)')
    parser.add_argument('--xgb_model', type=str, default='data/xgb_model.joblib', help='XGBoost model path (.joblib/.pkl)')
    parser.add_argument('--feature_manifest', type=str, default='data/feature_manifest.json', help='Feature manifest JSON')
    parser.add_argument('--out_dir', type=str, default='data/feature_importance', help='Directory to store bar charts and summaries')
    parser.add_argument('--top_n', type=int, default=10, help='Top N features to plot')
    parser.add_argument('--baseline_metrics', type=str, default='data/baseline_metrics.json', help='(Optional) Path to baseline model metrics for audit')
    parser.add_argument('--xgb_metrics', type=str, default='data/xgb_metrics.json', help='(Optional) Path to xgboost model metrics for audit')
    args = parser.parse_args()
    feature_importance_pipeline(
        sklearn_model_path=args.sklearn_model,
        xgb_model_path=args.xgb_model,
        manifest_path=args.feature_manifest,
        out_dir=args.out_dir,
        baseline_metrics=args.baseline_metrics,
        xgb_metrics=args.xgb_metrics,
        top_n=args.top_n
    )
