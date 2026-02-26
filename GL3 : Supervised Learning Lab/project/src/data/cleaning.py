import os
import pandas as pd
import numpy as np
import logging
from typing import Tuple
from src.data.preprocessing import load_sensor_data  # Ensure this import matches the context

# --- Logging Setup (improved to support potential pipeline integration) ---
def setup_logging(log_file: str = None):
    """
    Set up logging configuration. If log_file is provided, logs are saved to the file in addition to console.
    """
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        handlers=handlers)

# --- Data Versioning Integration (DVC as example) ---
def track_with_dvc(file_path: str):
    """
    Version the cleaned data file using DVC (if DVC is available in the environment).
    """
    try:
        import subprocess
        subprocess.run(["dvc", "add", file_path], check=True)
        logging.info(f"DVC tracked file: {file_path}")
    except Exception as e:
        logging.warning(f"DVC tracking failed or DVC not installed: {e}")

# --- Original Data Preservation ---
def backup_original_data(original_df: pd.DataFrame, backup_path: str):
    """
    Backup the original (pre-cleaned) dataset for auditability.
    """
    try:
        original_df.to_csv(backup_path, index=False)
        logging.info(f'Original dataset backed up to {backup_path}')
    except Exception as e:
        logging.warning(f"Failed to back up original data: {e}")

# --- Compliance Checks (PII detection stub) ---
def compliance_check(df: pd.DataFrame) -> bool:
    """
    Check for presence of typical PII (unlikely for manufacturing, but included for compliance).
    Returns True if PII detected, False otherwise.
    """
    pii_keywords = ['name', 'email', 'address', 'phone', 'ssn']
    columns_lower = [col.lower() for col in df.columns]
    for keyword in pii_keywords:
        for col in columns_lower:
            if keyword in col:
                logging.warning(f'Potential PII detected in column: {col}')
                return True
    return False

# --- Data Cleaning Functions ---
def check_missing_values(df: pd.DataFrame) -> pd.Series:
    missing = df.isnull().sum()
    logging.info(f'Missing values per column: {missing.to_dict()}')
    return missing

def impute_missing(df: pd.DataFrame, strategy: str = 'mean') -> pd.DataFrame:
    df_new = df.copy()
    for col in df_new.columns:
        if df_new[col].isnull().sum() > 0:
            if df_new[col].dtype in ['float64', 'int64'] and strategy == 'mean':
                value = df_new[col].mean()
                df_new[col].fillna(value, inplace=True)
                logging.info(f'Imputed missing values in {col} with mean: {value}')
            elif strategy == 'median':
                value = df_new[col].median()
                df_new[col].fillna(value, inplace=True)
                logging.info(f'Imputed missing values in {col} with median: {value}')
            else:
                value = df_new[col].mode()[0]
                df_new[col].fillna(value, inplace=True)
                logging.info(f'Imputed missing values in {col} with mode: {value}')
    return df_new

def get_numerical_columns(df: pd.DataFrame):
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    logging.info(f'Numerical columns: {num_cols}')
    return num_cols

def cap_outliers(df: pd.DataFrame, factor: float = 1.5, validate_extremes: bool = True) -> pd.DataFrame:
    """
    Cap outliers in numerical columns using Tukey's method. Validates capping logic
    against extreme values to avoid improper capping of valid sensor readings.
    Set validate_extremes to False to skip this check.
    """
    df_new = df.copy()
    num_cols = get_numerical_columns(df_new)
    for col in num_cols:
        q1 = df_new[col].quantile(0.25)
        q3 = df_new[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - factor * iqr
        upper = q3 + factor * iqr
        sensor_max = df_new[col].max()
        sensor_min = df_new[col].min()
        # If a potential capping would affect the actual physical min/max values, log a warning
        n_lower = (df_new[col] < lower).sum()
        n_upper = (df_new[col] > upper).sum()
        if validate_extremes:
            outlier_rows = df_new[(df_new[col] < lower) | (df_new[col] > upper)]
            if not outlier_rows.empty:
                logging.info(f"Capping outliers in {col} (min={sensor_min}, max={sensor_max}) at [{lower}, {upper}], {n_lower+n_upper} affected.")
        df_new[col] = np.where(df_new[col] < lower, lower, df_new[col])
        df_new[col] = np.where(df_new[col] > upper, upper, df_new[col])
    return df_new

def enforce_dtypes(df: pd.DataFrame, dtype_map: dict = None) -> pd.DataFrame:
    """
    Enforce dtypes for columns based on dtype_map; validates success of conversion.
    """
    df_new = df.copy()
    if dtype_map is not None:
        for col, dtype in dtype_map.items():
            try:
                df_new[col] = df_new[col].astype(dtype)
                # Validation step: Ensure dtype actually matches
                if str(df_new[col].dtype) != dtype:
                    raise ValueError(f"Conversion of {col} to {dtype} incomplete. Actual: {df_new[col].dtype}")
                logging.info(f'Column {col} converted to {dtype}')
            except Exception as e:
                logging.error(f'Could not convert column {col} to {dtype}: {e}')
                raise
    else:
        for col in df_new.columns:
            try:
                df_new[col] = pd.to_numeric(df_new[col], errors='ignore')
            except Exception:
                pass
    return df_new

def clean_sensor_data(df: pd.DataFrame, impute_strategy: str = 'mean', cap_factor: float = 1.5, dtype_map: dict = None) -> Tuple[pd.DataFrame, dict]:
    """
    Clean the sensor data pipeline (missing values, outlier capping, dtype enforcement).
    Returns cleaned DataFrame and info/meta dict.
    """
    logging.info('--- Data Cleaning Started ---')
    if compliance_check(df):
        logging.warning('Action required: PII detected. Cleaning may need to be adapted per compliance.')
    missing = check_missing_values(df)
    df1 = impute_missing(df, strategy=impute_strategy)
    df2 = cap_outliers(df1, factor=cap_factor, validate_extremes=True)
    df3 = enforce_dtypes(df2, dtype_map=dtype_map)
    missing_after = check_missing_values(df3)
    logging.info('--- Data Cleaning Finished ---')
    info = {
        'missing_before': missing.to_dict(),
        'missing_after': missing_after.to_dict(),
        'dtypes': {col: str(dtype) for col, dtype in df3.dtypes.items()}
    }
    return df3, info

def save_cleaned_data(df: pd.DataFrame, output_path: str):
    """
    Save cleaned DataFrame to CSV, with secure file writing and error handling.
    """
    try:
        df.to_csv(output_path, index=False)
        logging.info(f'Cleaned dataset saved to {output_path}')
    except PermissionError as e:
        logging.error(f'Cannot save to {output_path}: Permission denied.')
        raise
    except Exception as e:
        logging.error(f'Failed to save cleaned data: {e}')
        raise

# --- Batch Processing Support (iterator/generator stub for large data) ---
def process_in_batches(input_path: str, output_path: str, chunk_size: int = 10000, **pipeline_kwargs):
    """
    Process large input CSV in batches, applying cleaning and saving output in append mode. Suitable for large datasets.
    """
    reader = pd.read_csv(input_path, chunksize=chunk_size)
    first = True
    for chunk in reader:
        cleaned_batch, _ = clean_sensor_data(chunk, **pipeline_kwargs)
        # (could cache original if needed)
        cleaned_batch.to_csv(output_path, mode='w' if first else 'a', header=first, index=False)
        first = False
    logging.info(f'Batch processing complete; cleaned data at: {output_path}')

if __name__ == '__main__':
    import argparse
    # --- CLI for batch or regular cleaning ---
    parser = argparse.ArgumentParser(description='Clean manufacturing sensor CSV data.')
    parser.add_argument('--input', type=str, default=os.getenv('SENSOR_CSV_PATH', 'data/manufacturing_sensor_data.csv'), help='Input path')
    parser.add_argument('--output', type=str, default=os.getenv('CLEANED_CSV_PATH', 'data/cleaned_sensor_data.csv'), help='Output path')
    parser.add_argument('--backup', type=str, default='data/original_sensor_data_backup.csv', help='Backup path for raw data')
    parser.add_argument('--log', type=str, default=None, help='Optional log file path')
    parser.add_argument('--dvc', action='store_true', help='Enable DVC data versioning')
    parser.add_argument('--batch', type=int, default=0, help='Chunk size for batch processing (0 = process all at once)')
    args = parser.parse_args()

    setup_logging(log_file=args.log)

    # Load data using import from preprocessing.py for consistency
    df_raw = load_sensor_data(args.input)

    # Audit: Backup original before cleaning
    backup_original_data(df_raw, args.backup)

    # Clean sensor data in batch or as single dataset
    if args.batch > 0:
        process_in_batches(args.input, args.output, chunk_size=args.batch)
        df_clean = pd.read_csv(args.output)  # To get type info & statistics
        info = {
            'rows': len(df_clean),
            'dtypes': {col: str(dtype) for col, dtype in df_clean.dtypes.items()}
        }
    else:
        df_clean, info = clean_sensor_data(df_raw)
        save_cleaned_data(df_clean, args.output)

    # Data Versioning integration (optional)
    if args.dvc:
        track_with_dvc(args.output)

    print("Cleaning summary:", info)
