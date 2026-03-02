import os
import sys
import getpass
import logging
import hashlib
import json
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler, MinMaxScaler
from pandas.api.types import is_numeric_dtype, is_object_dtype, is_categorical_dtype

# Try to import mlflow and dvc for versioning (optional and robust to environment)
try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

# DVC is generally a CLI tool, but will emit relevant versioning commands/logs if available
DVC_USED = False

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('preprocessing.log', mode='a')
    ]
)

# --- Utility Functions for Reproducibility & Security ---
def validate_file(filepath: str) -> bool:
    """Checks if file exists and is a CSV."""
    if not os.path.isfile(filepath):
        logging.error(f"File '{filepath}' does not exist.")
        return False
    if not filepath.lower().endswith('.csv'):
        logging.error(f"File '{filepath}' is not a CSV file.")
        return False
    return True

def get_file_checksum(filepath: str, algo: str = 'sha256') -> str:
    """Computes hash/checksum (SHA256 by default) of the file for provenance."""
    hash_func = hashlib.new(algo)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def secure_file_permissions(filepath: str):
    """Set output file to owner read/write only (POSIX) and log exception otherwise."""
    try:
        os.chmod(filepath, 0o600)
        logging.info(f"Restricted permissions for {filepath} to owner only.")
    except Exception as e:
        logging.warning(f"Could not set secure permissions for {filepath}: {e}")

# --- Versioning/Audit Trail Functions ---
def get_git_commit() -> str:
    """Attempts to obtain git commit SHA for provenance."""
    try:
        import subprocess
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL)
        return commit.decode('ascii').strip()
    except Exception:
        return "N/A"

def save_run_metadata(
    output_path: str,
    input_path: str,
    input_checksum: str,
    encoders_path: str,
    scaler_path: str,
    pipeline_config: dict,
    user: str,
    run_id: str
):
    """
    Saves a JSON metadata containing audit trail and pipeline info.
    """
    metadata = {
        "input_path": input_path,
        "input_checksum_sha256": input_checksum,
        "preprocessed_data_path": output_path,
        "encoders_path": encoders_path,
        "scaler_path": scaler_path,
        "preprocessing_config": pipeline_config,
        "user": user,
        "preprocessing_timestamp": datetime.now().isoformat(),
        "git_commit": get_git_commit(),
        "run_id": run_id,
        "script": os.path.basename(__file__)
    }
    meta_path = os.path.splitext(output_path)[0] + f"_metadata_{run_id}.json"
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    secure_file_permissions(meta_path)
    logging.info(f"Run metadata saved to {meta_path}")

# Function to check for target column leakage
def detect_target_leakage(df: pd.DataFrame, target: str = 'target'):
    """
    Warn or error if the target column is present in features, for label leakage.
    """
    if target in df.columns:
        logging.warning(f"Target column '{target}' detected in input data. Pipeline should remove target prior to feature engineering to prevent leakage.")

# --- Main Preprocessing Pipeline Functions ---
def load_data(input_path: str) -> pd.DataFrame:
    """Loads CSV and logs size/info with error handling."""
    if not validate_file(input_path):
        raise FileNotFoundError(f"{input_path} does not exist or is not a CSV.")
    try:
        df = pd.read_csv(input_path)
        logging.info(f"Loaded data from {input_path} with shape {df.shape}")
    except Exception as e:
        logging.error(f"Failed to load input data: {e}")
        raise
    return df

def save_data(df: pd.DataFrame, output_path: str):
    """Saves cleaned DataFrame to CSV & sets file permissions."""
    df.to_csv(output_path, index=False)
    secure_file_permissions(output_path)
    logging.info(f"Cleaned data saved to {output_path}")

def impute_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Impute numeric as mean and categorical as most_frequent with explicit metadata."""
    num_cols = [c for c in df.columns if is_numeric_dtype(df[c])]
    cat_cols = [c for c in df.columns if is_object_dtype(df[c]) or is_categorical_dtype(df[c])]
    if num_cols:
        num_imputer = SimpleImputer(strategy='mean')
        df[num_cols] = num_imputer.fit_transform(df[num_cols])
        logging.info(f"Imputed missing values for numeric columns: {num_cols}")
    if cat_cols:
        cat_imputer = SimpleImputer(strategy='most_frequent')
        df[cat_cols] = cat_imputer.fit_transform(df[cat_cols])
        logging.info(f"Imputed missing values for categorical columns: {cat_cols}")
    return df

def encode_categorical(df: pd.DataFrame):
    """
    Encode object dtypes as one-hot or label encoded. Returns: transformed df, encoder objects as dict.
    Persists encoder objects for reproducibility.
    """
    object_cols = [c for c in df.columns if is_object_dtype(df[c])]
    encoders = {}
    for col in object_cols:
        n_unique = df[col].nunique()
        if n_unique > 2:
            ohe = OneHotEncoder(sparse=False, handle_unknown='ignore')
            vals = ohe.fit_transform(df[[col]])
            feature_labels = [f"{col}__{cat}" for cat in ohe.categories_[0]]
            df_ohe = pd.DataFrame(vals, columns=feature_labels, index=df.index)
            df = df.drop(col, axis=1)
            df = pd.concat([df, df_ohe], axis=1)
            encoders[col] = ('ohe', ohe)
            logging.info(f"Applied OneHotEncoding to column {col}")
        else:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            encoders[col] = ('le', le)
            logging.info(f"Applied LabelEncoding to column {col}")
    return df, encoders

def save_encoders(encoders: dict, path: str):
    """
    Persist encoders/scalers using joblib for reuse in validation/prediction.
    """
    import joblib
    joblib.dump(encoders, path)
    secure_file_permissions(path)
    logging.info(f"Encoder/scaler objects saved to {path}")

def scale_features(df: pd.DataFrame):
    """
    Scale numeric features. Returns transformed df and scaler instance.
    """
    numeric_cols = [c for c in df.columns if is_numeric_dtype(df[c])]
    if not numeric_cols:
        return df, None
    values = df[numeric_cols].values
    skewness = np.abs(pd.DataFrame(values, columns=numeric_cols).skew())
    if (skewness > 1).any():
        scaler = MinMaxScaler()
        logging.info(f"Used MinMaxScaler for columns: {numeric_cols}")
    else:
        scaler = StandardScaler()
        logging.info(f"Used StandardScaler for columns: {numeric_cols}")
    scaled_values = scaler.fit_transform(df[numeric_cols])
    df[numeric_cols] = scaled_values
    return df, scaler

def run_pipeline(
    input_path: str,
    output_path: str,
    encoders_path: str,
    scaler_path: str,
    target: str = 'target'
):
    """
    Complete preprocessing pipeline with reproducibility, provenance, audit, leakage check, and error handling.
    """
    run_id = datetime.now().strftime('%Y%m%dT%H%M%S')
    user = getpass.getuser() if hasattr(getpass, 'getuser') else 'unknown'
    input_checksum = get_file_checksum(input_path)
    try:
        df = load_data(input_path)
        detect_target_leakage(df, target=target)
        pipeline_config = {}
        # --- Impute missing ---
        df = impute_missing_values(df)
        pipeline_config['imputation'] = 'numeric=mean; categorical=most_frequent'
        # --- Encode categorical ---
        df, encoders = encode_categorical(df)
        save_encoders(encoders, encoders_path)
        pipeline_config['categorical_encoding'] = 'Label/OneHot per unique count'
        # --- Scale numeric ---
        df, scaler = scale_features(df)
        if scaler is not None:
            save_encoders(scaler, scaler_path)
        pipeline_config['scaling'] = scaler.__class__.__name__ if scaler else None
        # --- Save output ---
        save_data(df, output_path)
        # --- Run metadata ---
        save_run_metadata(
            output_path=output_path,
            input_path=input_path,
            input_checksum=input_checksum,
            encoders_path=encoders_path,
            scaler_path=scaler_path,
            pipeline_config=pipeline_config,
            user=user,
            run_id=run_id
        )
        if MLFLOW_AVAILABLE:
            mlflow.log_artifact(output_path)
            mlflow.log_artifact(encoders_path)
            if scaler_path: mlflow.log_artifact(scaler_path)
            logging.info("Logged artifacts to MLflow.")
        logging.info("Preprocessing pipeline completed successfully.")
    except Exception as e:
        logging.error(f"Critical failure during preprocessing: {e}")
        sys.exit(2)

def main():
    """
    CLI entrypoint: cleans and prepares a dataset, with versioning and provenance.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Data Preprocessing Pipeline with Audit Trail and Versioning")
    parser.add_argument('--input', required=True, help='Path to raw CSV data file')
    parser.add_argument('--output', required=True, help='Path to save cleaned CSV data file')
    parser.add_argument('--encoders', required=False, default='encoders.joblib', help='Path to save encoder objects (joblib)')
    parser.add_argument('--scaler', required=False, default='scaler.joblib', help='Path to save scaler object (joblib)')
    parser.add_argument('--target', required=False, default='target', help='Name of target column to check for leakage')
    args = parser.parse_args()
    run_pipeline(args.input, args.output, args.encoders, args.scaler, args.target)

if __name__ == "__main__":
    main()
