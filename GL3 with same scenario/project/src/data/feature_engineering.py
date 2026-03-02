import os
import sys
import logging
import getpass
import json
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression
from sklearn.model_selection import train_test_split
import warnings

# Import secure_file_permissions and get_git_commit from preprocessing context
# If not available as modules, define basic versions here based on context

def secure_file_permissions(filepath):
    """
    Restricts file permissions to owner read/write only (POSIX). Logs a warning on failure.
    """
    try:
        os.chmod(filepath, 0o600)
        logging.info(f"Restricted permissions for {filepath} to owner read/write only.")
    except Exception as e:
        logging.warning(f"Could not set secure file permissions for {filepath}: {e}")

def get_git_commit():
    """
    Attempts to obtain git commit SHA for provenance.
    """
    try:
        import subprocess
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL)
        return commit.decode('ascii').strip()
    except Exception:
        return "N/A"

# Config logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('feature_engineering.log', mode='a')
    ]
)

def validate_input_data(df, expected_cols=None):
    """
    Checks for required columns, NaNs, and expected types in df before engineering features.
    """
    if expected_cols:
        missing = [c for c in expected_cols if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
    if df.isnull().all(axis=None):
        raise ValueError("All values in dataframe are NaN.")
    # Optionally log warnings for non-numeric columns found
    return True

def deduplicate_columns(df):
    """
    Removes duplicated columns from the DataFrame, retaining the first occurrence.
    """
    before = df.shape[1]
    df = df.loc[:, ~df.columns.duplicated()]
    after = df.shape[1]
    if after < before:
        logging.info(f"Deduplicated columns. {before-after} duplicate columns removed.")
    return df

def create_rolling_features(df, cols, windows, agg_funcs, log_new_features=True, feature_log=None):
    new_features = []
    for col in cols:
        for w in windows:
            roll = df[col].rolling(window=w, min_periods=1)
            for func in agg_funcs:
                feature_name = f'{col}_roll{w}_{func}'
                if feature_name in df.columns:
                    continue  # Avoid duplication
                if func == 'mean':
                    df[feature_name] = roll.mean()
                elif func == 'std':
                    df[feature_name] = roll.std().fillna(0)
                elif func == 'min':
                    df[feature_name] = roll.min()
                elif func == 'max':
                    df[feature_name] = roll.max()
                else:
                    continue
                new_features.append(feature_name)
    if log_new_features and feature_log is not None:
        feature_log.extend(new_features)
        logging.info(f"Rolling features generated: {new_features}")
    return df

def create_stat_aggregations(df, cols, log_new_features=True, feature_log=None):
    new_features = []
    for col in cols:
        for stat, fn in [('mean', 'mean'), ('max', 'max'), ('min', 'min'), ('std', 'std')]:
            name = f'{col}_{stat}'
            if name in df.columns:
                continue  # Avoid duplication
            if stat == 'std':
                df[name] = df[col].expanding().std().fillna(0)
            else:
                df[name] = getattr(df[col].expanding(), fn)()
            new_features.append(name)
    if log_new_features and feature_log is not None:
        feature_log.extend(new_features)
        logging.info(f"Stat aggregations generated: {new_features}")
    return df

def create_condition_encoding(df, sensor_cols, thresh_dict, log_new_features=True, feature_log=None):
    new_features = []
    # Only condition encode columns explicitly listed in thresh_dict
    for col in sensor_cols:
        if col in thresh_dict:
            threshold = thresh_dict[col]
            high_name = f'{col}_high'
            low_name = f'{col}_low'
            if high_name not in df.columns:
                df[high_name] = (df[col] > threshold).astype(int)
                new_features.append(high_name)
            if low_name not in df.columns:
                df[low_name] = (df[col] < threshold).astype(int)
                new_features.append(low_name)
    if log_new_features and feature_log is not None:
        feature_log.extend(new_features)
        logging.info(f"Condition encoding generated: {new_features}")
    return df

def engineer_features(
    input_path,
    output_path,
    rolling_windows=[5, 15, 30],
    agg_funcs=['mean', 'max', 'min', 'std'],
    condition_thresholds=None,
    exclude=None,
    feature_metadata_path=None,
    resource_row_warn=100000,
    resource_col_warn=200
):
    """
    Ingests data, checks schema/quality, sorts before time-dependent ops, generates features with dedup, logs audit/meta.
    """
    feature_log = []
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        logging.error(f"Input file {input_path} not found.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to load input: {e}")
        sys.exit(1)
    orig_cols = [c for c in df.columns if c not in (exclude or [])]
    numeric_cols = [c for c in orig_cols if pd.api.types.is_numeric_dtype(df[c])]
    # Validate presence of at least one numeric column
    if not numeric_cols:
        logging.error("No numeric columns found for feature engineering.")
        sys.exit(1)
    # Data shape warning for memory/resource constraint
    if df.shape[0] > resource_row_warn:
        logging.warning(f"Large row count: {df.shape[0]}. Feature engineering may be slow or memory intensive.")
    if df.shape[1] > resource_col_warn:
        logging.warning(f"Large number of columns: {df.shape[1]}. May exceed memory or runtime best practices.")
    # Data validation for required columns
    validate_input_data(df, expected_cols=orig_cols)
    # Always sort by timestamp before rolling/statistical features
    if 'timestamp' in df.columns:
        df = df.sort_values('timestamp').reset_index(drop=True)
    # Rolling/statistical feature engineering with deduplication
    df = create_rolling_features(df, numeric_cols, rolling_windows, agg_funcs, feature_log=feature_log)
    df = create_stat_aggregations(df, numeric_cols, feature_log=feature_log)
    # Only apply condition encoding to columns given in condition_thresholds
    threshold_dict = condition_thresholds or {}
    df = create_condition_encoding(df, sensor_cols=list(threshold_dict.keys()), thresh_dict=threshold_dict, feature_log=feature_log)
    # Remove any potential duplicate columns
    df = deduplicate_columns(df)
    # Save feature engineered data
    df.to_csv(output_path, index=False)
    secure_file_permissions(output_path)
    logging.info(f'Feature engineered data saved to {output_path}')
    # Write metadata JSON for reproducibility/audit
    if feature_metadata_path:
        user = getpass.getuser() if hasattr(getpass, 'getuser') else 'unknown'
        auditmeta = {
            "input_csv": input_path,
            "output_features_csv": output_path,
            "engineered_features": feature_log,
            "generated_timestamp": datetime.now().isoformat(),
            "git_commit": get_git_commit(),
            "user": user,
            "num_rows": df.shape[0],
            "num_cols": df.shape[1]
        }
        with open(feature_metadata_path, 'w') as f:
            json.dump(auditmeta, f, indent=2)
        secure_file_permissions(feature_metadata_path)
        logging.info(f"Feature engineering metadata written to {feature_metadata_path}")
    return output_path, list(df.columns), feature_log

def split_feature_target(df, target_col):
    feature_cols = [col for col in df.columns if col != target_col]
    X = df[feature_cols]
    y = df[target_col]
    return X, y

def select_top_features(
    df,
    target_col,
    problem_type='classification',
    importance_method='tree',
    num_features=20,
    feature_report_path=None,
    selection_log_path=None,
    rationale_config=None
):
    """
    Selects top features by combined importance (tree+MI), logs artifact & rationale including per-feature detail.
    """
    # Guard: drop non-numeric columns (unless target)
    non_numeric = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c]) and c != target_col]
    if non_numeric:
        logging.warning(f"Non-numeric columns dropped from selection: {non_numeric}")
        df = df.drop(non_numeric, axis=1)
    X, y = split_feature_target(df, target_col)
    if problem_type == 'classification':
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        mi = mutual_info_classif(X, y, discrete_features='auto', random_state=42)
    else:
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        mi = mutual_info_regression(X, y, discrete_features='auto', random_state=42)
    model.fit(X, y)
    importances = model.feature_importances_
    importance_df = pd.DataFrame({
        'feature': X.columns,
        'tree_importance': importances,
        'mutual_info': mi
    })
    # Combine scores (normalize MI to sum=1, weigh with tree importance)
    mi_norm = importance_df['mutual_info'] / np.nansum(importance_df['mutual_info']) if np.nansum(importance_df['mutual_info']) > 0 else importance_df['mutual_info']
    importance_df['combined_score'] = 0.5 * importance_df['tree_importance'] + 0.5 * mi_norm
    importance_df = importance_df.sort_values('combined_score', ascending=False)
    selected = importance_df['feature'].head(num_features).tolist()
    # Save full report
    if feature_report_path:
        importance_df.to_csv(feature_report_path, index=False)
        secure_file_permissions(feature_report_path)
        logging.info(f'Feature importance report saved to {feature_report_path}')
    # Log rationale with per-feature info or config rationale
    if selection_log_path:
        summary = {
            'timestamp': datetime.now().isoformat(),
            'problem_type': problem_type,
            'num_features_selected': num_features,
            'features_selected': selected,
            'feature_scores': importance_df.head(num_features).to_dict('records'),
            'rationale': f"Features selected using combined RandomForest {'classifier' if problem_type=='classification' else 'regressor'} importance and normalized mutual information. Top {num_features} features have both high nonlinear association (tree splits) and information gain with respect to target.",
            'per_feature_domain_notes': rationale_config or {}
        }
        with open(selection_log_path, 'w') as f:
            json.dump(summary, f, indent=2)
        secure_file_permissions(selection_log_path)
        logging.info(f'Feature selection rationale documented to {selection_log_path}')
    return selected, importance_df

def generate_selected_feature_matrix(df, selected_features, output_path):
    # Always include target columns if present
    target_cols = [col for col in df.columns if col.lower().startswith('target')]
    feat_matrix = df[selected_features + [col for col in target_cols if col not in selected_features]]
    feat_matrix.to_csv(output_path, index=False)
    secure_file_permissions(output_path)
    logging.info(f'Selected feature matrix saved to {output_path}')

def redact_sensitive_output_columns(df, sensitive_columns=None, output_path=None):
    """
    Overwrite sensitive columns with 'REDACTED' marker, if required for privacy compliance.
    """
    if sensitive_columns:
        for col in sensitive_columns:
            if col in df.columns:
                df[col] = 'REDACTED'
    if output_path:
        df.to_csv(output_path, index=False)
        secure_file_permissions(output_path)
        logging.info(f'Sensitive columns were redacted in {output_path}')
    return df

def write_artifact_metadata(feat_output, selection_matrix_path, report_path, selection_log_path, feature_meta_path):
    """
    Writes audit trail for end-to-end feature artifact production as JSON metadata.
    """
    meta = {
        'feature_engineering_csv': feat_output,
        'selected_feature_matrix': selection_matrix_path,
        'feature_importance_report': report_path,
        'selection_rationale': selection_log_path,
        'feature_metadata_json': feature_meta_path,
        'git_commit': get_git_commit(),
        'run_timestamp': datetime.now().isoformat(),
        'user': getpass.getuser() if hasattr(getpass, 'getuser') else 'unknown',
        'script': os.path.basename(__file__)
    }
    outjson = os.path.splitext(selection_matrix_path)[0] + '_artifact_metadata.json'
    with open(outjson, 'w') as f:
        json.dump(meta, f, indent=2)
    secure_file_permissions(outjson)
    logging.info(f"Feature engineering artifact metadata written to {outjson}")
    return outjson

# === Main CLI ===
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Engineer features from manufacturing sensor data and perform robust selection/audit.')
    parser.add_argument('--input', required=True, help='Preprocessed CSV input file')
    parser.add_argument('--output', required=True, help='Output CSV path for feature engineered data')
    parser.add_argument('--selection_output', required=True, help='CSV for the selected feature matrix')
    parser.add_argument('--feature_importance_report', required=True, help='CSV for feature importance')
    parser.add_argument('--selection_log', required=True, help='File for rationale log (JSON)')
    parser.add_argument('--feature_metadata', required=True, help='Path to save feature engineering run metadata (JSON)')
    parser.add_argument('--target_col', required=True, help='Target/label column name')
    parser.add_argument('--problem_type', default='classification', choices=['classification','regression'], help='Problem type')
    parser.add_argument('--num_features', default=20, type=int, help='Number of top features to select')
    parser.add_argument('--condition_thresholds', default='', help='JSON: col:threshold dictionary for condition encoding')
    parser.add_argument('--exclude_cols', default='', help='Comma-separated list of columns to exclude from feature engineering')
    parser.add_argument('--sensitive_cols', default='', help='Comma-separated list for privacy redaction downstream')
    parser.add_argument('--rationale_config', default='', help='Optional JSON: domain rationale per feature')
    args = parser.parse_args()

    try:
        condition_thresholds = json.loads(args.condition_thresholds) if args.condition_thresholds else {}
    except Exception:
        logging.error("Invalid JSON in --condition_thresholds. Must be a JSON dict of col: value.")
        sys.exit(1)
    exclude = [x.strip() for x in args.exclude_cols.split(',') if x.strip()] if args.exclude_cols else []
    sensitive_cols = [x.strip() for x in args.sensitive_cols.split(',') if x.strip()] if args.sensitive_cols else []
    try:
        rationale_config = json.loads(args.rationale_config) if args.rationale_config else None
    except Exception:
        rationale_config = None

    # Feature engineering (with metadata and schema validation)
    feat_out, all_feats, generated_feats = engineer_features(
        args.input,
        args.output,
        rolling_windows=[5, 15, 30],
        agg_funcs=['mean', 'max', 'min', 'std'],
        condition_thresholds=condition_thresholds,
        exclude=exclude,
        feature_metadata_path=args.feature_metadata
    )
    df = pd.read_csv(feat_out)
    # Optionally redact sensitive columns in full output
    if sensitive_cols:
        redact_sensitive_output_columns(df, sensitive_columns=sensitive_cols, output_path=args.output)

    # Select features robustly
    selected, _ = select_top_features(
        df,
        target_col=args.target_col,
        problem_type=args.problem_type,
        importance_method='tree',
        num_features=args.num_features,
        feature_report_path=args.feature_importance_report,
        selection_log_path=args.selection_log,
        rationale_config=rationale_config
    )
    # Generate selected feature matrix
    generate_selected_feature_matrix(df, selected, args.selection_output)
    # Optionally redact sensitive columns in feature matrix (downstream privacy)
    if sensitive_cols:
        featmat = pd.read_csv(args.selection_output)
        redact_sensitive_output_columns(featmat, sensitive_columns=sensitive_cols, output_path=args.selection_output)
    # Write artifact metadata for compliance/audit
    write_artifact_metadata(
        feat_output=args.output,
        selection_matrix_path=args.selection_output,
        report_path=args.feature_importance_report,
        selection_log_path=args.selection_log,
        feature_meta_path=args.feature_metadata
    )
