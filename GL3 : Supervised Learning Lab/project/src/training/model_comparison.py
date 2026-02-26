import os
import json
import numpy as np
import logging
from typing import Dict, Any
import re

def setup_logging():
    """Set up basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )

def is_valid_path(path: str) -> bool:
    """Check that the path is a valid, safe data path."""
    if not isinstance(path, str):
        return False
    norm_path = os.path.normpath(path)
    if '..' in norm_path.split(os.sep):
        return False
    if not norm_path.startswith('data' + os.sep):
        return False
    if not re.match(r'^data\%s[a-zA-Z0-9_\-/]+\.(json|npy)$' % re.escape(os.sep), norm_path):
        return False
    return True

def load_metrics(metrics_path: str) -> Dict[str, Any]:
    """Load metrics from JSON file, logging and raising error if file does not exist or is malformed."""
    if not os.path.exists(metrics_path):
        logging.error(f'Metrics file not found: {metrics_path}')
        raise FileNotFoundError(f'Metrics file not found: {metrics_path}')
    try:
        with open(metrics_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f'Error loading metrics file {metrics_path}: {e}')
        raise

def safe_float(val):
    """Convert values to float safely, return None if not possible or not finite."""
    try:
        if val is None:
            return None
        if isinstance(val, (float, int, np.floating, np.integer)):
            if isinstance(val, float) or isinstance(val, np.floating):
                if np.isnan(val) or np.isinf(val):
                    return None
            return float(val)
        if isinstance(val, str):
            # Sometimes value may be 'NA', 'nan', etc
            if val.strip().lower() in ['na', 'nan', 'none']:
                return None
            fval = float(val)
            if np.isnan(fval) or np.isinf(fval):
                return None
            return fval
        return None  # Unexpected type
    except Exception:
        return None

def format_metrics_row(name: str, metrics: Dict[str, Any]) -> str:
    """Format metrics values, displaying 'NA' if values are None or not numbers."""
    fields = ['accuracy', 'precision', 'recall', 'f1']
    vals = []
    for f in fields:
        val = safe_float(metrics.get(f, None))
        if val is not None:
            vals.append(f"{val:.4f}")
        else:
            vals.append('NA')
    return f"{name:<20} | {vals[0]:<9} | {vals[1]:<9} | {vals[2]:<9} | {vals[3]:<9}"

def get_main_metrics_dict(metrics_all: Dict[str, Any]) -> Dict[str, Any]:
    """Robustly retrieve main test/eval metrics with fallback if 'test' is missing or malformed."""
    for key in ['test', 'eval', 'validation', 'val']:
        d = metrics_all.get(key, None)
        if isinstance(d, dict):
            return d
    # Fallback: check for flat metrics dict (legacy output?)
    if isinstance(metrics_all, dict) and any(k in metrics_all for k in ['accuracy','precision','recall','f1']):
        return metrics_all
    return {}

def interpret_results(mt1: Dict[str, Any], mt2: Dict[str, Any], model1_name: str, model2_name: str) -> str:
    """Interpret comparison between two sets of metrics, with robust checking for all numeric types, None, and NaN."""
    def all_number(*args):
        for v in args:
            f = safe_float(v)
            if f is None:
                return False
        return True
    f1_1 = safe_float(mt1.get('f1', None))
    f1_2 = safe_float(mt2.get('f1', None))
    acc_1 = safe_float(mt1.get('accuracy', None))
    acc_2 = safe_float(mt2.get('accuracy', None))
    prec_1 = safe_float(mt1.get('precision', None))
    prec_2 = safe_float(mt2.get('precision', None))
    recall_1 = safe_float(mt1.get('recall', None))
    recall_2 = safe_float(mt2.get('recall', None))
    if not all_number(f1_1, f1_2, acc_1, acc_2, prec_1, prec_2, recall_1, recall_2):
        return "Cannot interpret due to unavailable or malformed metric(s)."
    if f1_1 > f1_2:
        winner = model1_name
        reason = "F1 score is higher"
        metric_diff = f1_1 - f1_2
    elif f1_2 > f1_1:
        winner = model2_name
        reason = "F1 score is higher"
        metric_diff = f1_2 - f1_1
    else:
        if acc_1 > acc_2:
            winner = model1_name
            reason = "accuracy is higher (F1 tied)"
            metric_diff = acc_1 - acc_2
        elif acc_2 > acc_1:
            winner = model2_name
            reason = "accuracy is higher (F1 tied)"
            metric_diff = acc_2 - acc_1
        else:
            winner = "Neither"
            reason = "Same F1 and accuracy - models perform equivalently"
            metric_diff = 0.0
    details = [
        f"{model1_name} metrics:",
        f"  Accuracy: {acc_1:.4f}",
        f"  Precision: {prec_1:.4f}",
        f"  Recall: {recall_1:.4f}",
        f"  F1: {f1_1:.4f}",
        f"{model2_name} metrics:",
        f"  Accuracy: {acc_2:.4f}",
        f"  Precision: {prec_2:.4f}",
        f"  Recall: {recall_2:.4f}",
        f"  F1: {f1_2:.4f}",
    ]
    explanation = f"Model comparison complete. {winner} performs better ({reason}) by {abs(metric_diff):.4f} on F1."
    return '
'.join(details + [explanation])

def print_comparison_table(model1_name: str, mt1: Dict[str, Any], model2_name: str, mt2: Dict[str, Any]) -> None:
    """Print model comparison results in clear tabular format."""
    columns = ["Model", "Accuracy", "Precision", "Recall", "F1"]
    print("
MODEL COMPARISON RESULTS
------------------------")
    print(f"{' | '.join(columns)}")
    print("-" * 60)
    print(format_metrics_row(model1_name, mt1))
    print(format_metrics_row(model2_name, mt2))
    print("-" * 60)
    print()
    print(interpret_results(mt1, mt2, model1_name, model2_name))

def save_comparison_report(report: str, out_path: str):
    """Save the comparison report to a file, safely creating parent directories."""
    dir_path = os.path.dirname(out_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(out_path, 'w') as f:
        f.write(report)

def main():
    import argparse
    setup_logging()
    parser = argparse.ArgumentParser(description='Compare scikit-learn baseline and XGBoost models on accuracy, precision, recall, and F1-score.')
    parser.add_argument('--baseline_metrics', type=str, default='data/baseline_metrics.json', help='Metrics file for baseline model')
    parser.add_argument('--xgboost_metrics', type=str, default='data/xgb_metrics.json', help='Metrics file for XGBoost model')
    parser.add_argument('--report_out', type=str, default='data/model_comparison_report.txt', help='Where to save the comparison/interpretation report')
    args = parser.parse_args()

    # Input path validation
    for p in [args.baseline_metrics, args.xgboost_metrics]:
        if not is_valid_path(p):
            logging.error(f'Invalid/unsafe metrics file path: {p}')
            raise ValueError(f'Unsafe file path: {p}')
    # Load metrics, handling missing/malformed files robustly
    try:
        baseline_all = load_metrics(args.baseline_metrics)
        xgb_all = load_metrics(args.xgboost_metrics)
    except Exception as e:
        logging.error(f'Failed to load metrics: {e}')
        raise
    # Robustly extract metrics dicts
    mt1 = get_main_metrics_dict(baseline_all)
    mt2 = get_main_metrics_dict(xgb_all)
    model1_name = baseline_all.get('model_type', 'Baseline')
    model2_name = xgb_all.get('model_type', 'XGBoost')
    # Output table and interpretation
    report_lines = []
    columns = ["Model", "Accuracy", "Precision", "Recall", "F1"]
    report_lines.append("MODEL COMPARISON RESULTS
------------------------")
    report_lines.append(f"{' | '.join(columns)}")
    report_lines.append("-" * 60)
    report_lines.append(format_metrics_row(model1_name, mt1))
    report_lines.append(format_metrics_row(model2_name, mt2))
    report_lines.append("-" * 60)
    report_lines.append("")
    report_lines.append(interpret_results(mt1, mt2, model1_name, model2_name))
    report = '
'.join(report_lines)
    # Print to stdout
    print(report)
    # Write to file if output path is valid
    if is_valid_path(args.report_out):
        try:
            save_comparison_report(report, args.report_out)
            print(f"Comparison report saved at {args.report_out}")
        except Exception as e:
            logging.error(f'Failed to save comparison report: {e}')
            print('Comparison report NOT saved -- error occurred.')
    else:
        logging.warning(f'Output path for comparison report not safe: {args.report_out}')
        print('Comparison report NOT saved -- output path rejected as unsafe.')

if __name__ == '__main__':
    main()
