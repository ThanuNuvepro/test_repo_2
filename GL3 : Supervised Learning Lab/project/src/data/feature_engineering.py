# Feature Engineering Module for Manufacturing Sensor Data
# ---------------------------------------------------------
# This module performs feature engineering and persists the results.
# It logs major steps, checks numeric-only columns for .npy files, performs secure path validation,
# handles missing values, and writes a feature manifest for auditability and reproducibility.
# Requires: pandas, numpy, logging, os, re, json

import pandas as pd
import numpy as np
import os
import re
import logging
import json
from typing import Tuple, List, Optional

# --- Logging Setup ---
def setup_logging():
    """Set up standard logging configuration for feature engineering."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )

# --- Secure Path Validation ---
def is_valid_path(path: str) -> bool:
    """
    Validate that a file path is inside the 'data/' directory and does not permit traversal.
    Only allows CSV and NPY files in 'data/' subdirs.
    """
    if not isinstance(path, str):
        return False
    normalized_path = os.path.normpath(path)
    if not normalized_path.startswith('data' + os.sep):
        return False
    # Allow .csv, .npy
    if not re.match(r'^data\%s[a-zA-Z0-9_\-]+\.(csv|npy)$' % re.escape(os.sep), normalized_path):
        return False
    return True

# --- Identify Features and Target ---
def identify_features_and_target(df: pd.DataFrame) -> Tuple[List[str], str]:
    """
    Identify feature columns and the target column for prediction.
    The function searches for a likely target by typical outcome column names.
    Returns a tuple (feature_cols, target_col).
    """
    candidates = [c.lower() for c in df.columns]
    target_names = ['failure', 'target', 'maintenance_needed', 'maintenance_due']
    for t in target_names:
        if t in candidates:
            idx = candidates.index(t)
            target_col = df.columns[idx]
            break
    else:
        raise ValueError(f"Could not automatically identify target column from possible names {target_names}. Columns found: {df.columns.tolist()}")
    feature_cols = [c for c in df.columns if c != target_col]
    return feature_cols, target_col

# --- Feature Engineering ---
def add_engineered_features(df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    """
    Add at least one engineered feature using array operations.
    Adds rolling mean and ratio features for major sensor columns.
    """
    df_new = df.copy()
    numeric_cols = df_new[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        col0 = numeric_cols[0]
        feat_name_mean = f'{col0}_rolling_mean3'
        df_new[feat_name_mean] = df_new[col0].rolling(window=3, min_periods=1).mean()
        logging.info(f'Engineered feature added: {feat_name_mean}')
        if len(numeric_cols) > 1:
            col1 = numeric_cols[1]
            feat_name_ratio = f'{col0}_over_{col1}'
            df_new[feat_name_ratio] = np.where(df_new[col1] != 0, df_new[col0] / df_new[col1], 0.0)
            logging.info(f'Engineered feature added: {feat_name_ratio}')
    return df_new

# --- Final Feature Selection ---
def select_final_features(df: pd.DataFrame, feature_cols: List[str], target_col: str, ignore_cols: Optional[List[str]] = None) -> List[str]:
    """
    Select all original and new engineered numeric feature columns, excluding identifiers & target.
    Filtering is case-insensitive on known identifier columns.
    """
    default_ignores = ['id', 'timestamp', 'time', 'batch', 'serial']
    ignore_cols = ignore_cols or default_ignores
    ignore_cols_lower = [ic.lower() for ic in ignore_cols]
    all_cols = df.columns.tolist()
    selected = []
    for c in all_cols:
        if c.lower() in ignore_cols_lower or c == target_col:
            continue
        selected.append(c)
    return selected

# --- Features/Target Extraction (with error checking) ---
def split_features_and_target(df: pd.DataFrame, feature_cols: List[str], target_col: str) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Separate feature columns and target column from DataFrame, checking for existence.
    Raises informative error if any feature is missing.
    """
    missing_cols = [c for c in feature_cols if c not in df.columns]
    if missing_cols:
        raise KeyError(f'Missing feature columns in DataFrame: {missing_cols}')
    if target_col not in df.columns:
        raise KeyError(f'Missing target column in DataFrame: {target_col}')
    X = df[feature_cols].copy()
    y = df[target_col].copy()
    return X, y

# --- Missing Value Checking and (optional) Imputation ---
def has_missing_values(df: pd.DataFrame) -> bool:
    if df.isnull().values.any():
        logging.warning('Detected missing values after feature engineering. Rows with NaN will be dropped.')
        return True
    return False

def drop_or_impute_nans(df: pd.DataFrame) -> pd.DataFrame:
    # Option: Drop all rows with NaN for model ingestion (warning issued)
    df_new = df.copy()
    nan_rows = df_new.isnull().any(axis=1)
    n_dropped = nan_rows.sum()
    if n_dropped:
        df_new = df_new[~nan_rows].reset_index(drop=True)
        logging.info(f"Dropped {n_dropped} rows with missing values.")
    return df_new

# --- Data Versioning/Manifest for Auditability ---
def save_feature_manifest(feature_list: List[str], target_col: str, meta: dict, manifest_path: str):
    """
    Write a feature manifest JSON for versioning and reproducibility.
    """
    manifest = {
        'features': feature_list,
        'target': target_col,
        'meta': meta
    }
    try:
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        logging.info(f'Feature manifest saved: {manifest_path}')
    except Exception as e:
        logging.warning(f'Unable to save feature manifest: {e}')

# --- Versioning Integration Example (DVC or meta hash stub) ---
def register_with_dvc(file_path: str):
    """
    Attempt to version .npy files with DVC if DVC is available.
    """
    try:
        import subprocess
        subprocess.run(["dvc", "add", file_path], check=True)
        logging.info(f'DVC tracked file: {file_path}')
    except Exception as e:
        logging.warning(f'DVC add failed or DVC not present: {e}')

# --- Pipeline Function ---
def engineer_features_pipeline(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str], str]:
    """
    Complete feature engineering pipeline: identify, engineer, select, and extract.
    Returns features DataFrame X, target y, feature list, and target column name.
    """
    logging.info('Feature engineering pipeline started.')
    feature_cols, target_col = identify_features_and_target(df)
    df_extended = add_engineered_features(df, feature_cols)
    selected_features = select_final_features(df_extended, feature_cols, target_col)
    # Remove non-numeric columns for .npy saving, but capture full list for manifest
    X_full = df_extended[selected_features]
    if has_missing_values(X_full):
        X_full = drop_or_impute_nans(X_full)
    # Keep only numeric features for .npy saving
    numeric_features = X_full.select_dtypes(include=[np.number]).columns.tolist()
    # If any non-numeric columns present, warn user
    non_numeric = [c for c in selected_features if c not in numeric_features]
    if non_numeric:
        logging.warning(f"Non-numeric features excluded for .npy: {non_numeric}")
    X = X_full[numeric_features]
    y = df_extended.loc[X_full.index, target_col]
    if has_missing_values(y.to_frame()):
        y = y.dropna().reset_index(drop=True)
        X = X.loc[y.index]
        logging.info('Dropped target NaNs; re-aligned X and y.')
    logging.info('Feature engineering completed.')
    return X, y, selected_features, target_col

# --- CLI Entrypoint ---
if __name__ == '__main__':
    setup_logging()

    import argparse
    parser = argparse.ArgumentParser(description='Feature engineering for manufacturing sensor data.')
    parser.add_argument('--input', type=str, default='data/cleaned_sensor_data.csv', help='Input CSV path (must be in data/)')
    parser.add_argument('--output_features', type=str, default='data/features.npy', help='Output features .npy (must be in data/)')
    parser.add_argument('--output_target', type=str, default='data/target.npy', help='Output target .npy (must be in data/)')
    parser.add_argument('--manifest', type=str, default='data/feature_manifest.json', help='Path to feature manifest JSON')
    parser.add_argument('--save_csv', action='store_true', help='Also save engineered features as a CSV in data/')
    parser.add_argument('--dvc', action='store_true', help='Register features and target with DVC if present')
    args = parser.parse_args()

    # Path validation
    for p in [args.input, args.output_features, args.output_target]:
        if not is_valid_path(p):
            logging.error(f'Invalid or unsafe file path: {p}')
            exit(1)

    if not os.path.exists(args.input):
        logging.error(f'Input data file {args.input} not found. Please run the cleaning pipeline first.')
        exit(1)

    # Load data
    df_in = pd.read_csv(args.input)

    # Run feature engineering pipeline
    X, y, feature_list, target_col = engineer_features_pipeline(df_in)

    # Save .npy files
    try:
        np.save(args.output_features, X.to_numpy())
        np.save(args.output_target, y.to_numpy())
        logging.info(f'Features and target saved as .npy: {args.output_features}, {args.output_target}')
    except Exception as e:
        logging.error(f'Error saving .npy files: {e}')
        exit(1)

    # Optional: Save as CSV for inspection
    if args.save_csv:
        engineered_csv = args.input.replace('.csv', '_with_engineered_features.csv')
        # Secure path check
        if not is_valid_path(engineered_csv.replace('_with_engineered_features', '')):
            logging.warning(f'Unsafe path for engineered CSV: {engineered_csv}')
        else:
            Xy = X.copy()
            Xy[target_col] = y.values
            Xy.to_csv(engineered_csv, index=False)
            logging.info(f'Engineered CSV saved: {engineered_csv}')

    # Save feature manifest for versioning/audit trails
    save_feature_manifest(feature_list, target_col, {
        'engineered_feature_shape': X.shape,
        'numeric_feature_count': len(X.columns),
        'csv_input': args.input
    }, args.manifest)

    # Optionally version .npy files with DVC
    if args.dvc:
        for f in [args.output_features, args.output_target]:
            register_with_dvc(f)

    print(f'Success: Features shape {X.shape}, target shape {y.shape}. Numeric columns for ML: {X.columns.tolist()}')
    print(f'Full (engineered + raw) features: {feature_list}')
