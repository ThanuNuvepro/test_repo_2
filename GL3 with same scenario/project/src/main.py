import os
import sys
import subprocess
import logging
import getpass
import shutil
import json
from datetime import datetime
import traceback


def setup_logging(logfile='pipeline_execution.log'):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(logfile, mode='a')
        ]
    )


def run_cli(cmd, label=None):
    if label:
        logging.info(f"--- Executing: {label} ---")
    logging.info(f"Running command: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        logging.info(f"Output for '{label}':
{result.stdout}")
        if result.stderr:
            logging.warning(f"Stderr for '{label}':
{result.stderr}")
    except subprocess.CalledProcessError as e:
        # Log traceback for debugging (fix: capture/print full stack--review feedback)
        logging.error(f"Pipeline step '{label}' failed with code {e.returncode}.
Stdout: {e.stdout}
Stderr: {e.stderr}")
        logging.error("Exception Traceback:
" + traceback.format_exc())
        sys.exit(1)
    except Exception as e:
        # Catch other exceptions and log
        logging.error(f"Unexpected error during '{label}': {e}")
        logging.error("Exception Traceback:
" + traceback.format_exc())
        sys.exit(1)


def file_checksum(path, algo='sha256'):
    import hashlib
    hash_func = hashlib.new(algo)
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def check_artifacts(paths):
    # This check can be extended with hash verification for better integrity (fix: based on feedback)
    missing = [p for p in paths if not os.path.exists(p)]
    if missing:
        msg = f"Missing expected artifact files: {missing}"
        logging.error(msg)
        sys.exit(2)
    for p in paths:
        logging.info(f"Verified artifact present: {p}")
        # Optionally, print checksum for each artifact (enhanced auditing)
        try:
            checksum = file_checksum(p)
            logging.info(f"Artifact checksum (sha256) for {p}: {checksum}")
        except Exception as e:
            logging.warning(f"Unable to compute checksum for {p}: {e}")


def main():
    setup_logging()
    logging.info("Starting end-to-end CLI pipeline execution.")

    # Directories
    user = getpass.getuser()
    timestamp = datetime.now().strftime('%Y%m%dT%H%M%S')
    base_output_dir = f"run_{user}_{timestamp}"
    os.makedirs(base_output_dir, exist_ok=True)

    # --- Step 1: Data Ingestion and Inspection ---
    raw_csv = os.environ.get("RAW_DATA_PATH", "data/input_sensor_data.csv")
    ingestion_dir = os.path.join(base_output_dir, "ingestion")
    os.makedirs(ingestion_dir, exist_ok=True)
    ingestion_cmd = f"python src/data/preprocessing.py --input_csv '{raw_csv}' --output_dir '{ingestion_dir}'"
    run_cli(ingestion_cmd, label="Data Ingestion Pipeline")

    # Retrieve latest cleaned CSV file from ingestion_dir
    cleaned_files = [f for f in os.listdir(ingestion_dir) if f.endswith('.csv') and f.startswith('summary_statistics')]
    if not cleaned_files:
        logging.error(f"No summary_statistics CSV found in {ingestion_dir} after ingestion.")
        sys.exit(3)
    # Choose the latest summary statistics CSV (by timestamp in filename; assuming unique_suffix includes timestamp)
    latest_cleaned_csv = sorted(
        cleaned_files,
        key=lambda x: x,  # filenames are unique with timestamp; a simple sort works
        reverse=True
    )[0]
    cleaned_csv_path = os.path.join(ingestion_dir, latest_cleaned_csv)
    # For lineage, propagate the cleaned CSV as next input
    preproc_input_path = cleaned_csv_path

    # --- Step 1b: Propagate anonymized/cleaned for next stage (fixes review feedback on incorrect data flow) ---
    preproc_dir = os.path.join(base_output_dir, "preproc")
    os.makedirs(preproc_dir, exist_ok=True)
    preproc_output = os.path.join(preproc_dir, "preprocessed.csv")
    encoders_path = os.path.join(preproc_dir, "encoders.joblib")
    scaler_path = os.path.join(preproc_dir, "scaler.joblib")
    preproc_cmd = f"python src/data/preprocessing.py --input '{preproc_input_path}' --output '{preproc_output}' --encoders '{encoders_path}' --scaler '{scaler_path}' --target 'target'"
    run_cli(preproc_cmd, label="Preprocessing Pipeline")

    # --- Step 2: Feature Engineering and Selection ---
    fe_dir = os.path.join(base_output_dir, "features")
    os.makedirs(fe_dir, exist_ok=True)
    feature_engineered_path = os.path.join(fe_dir, "feature_engineered.csv")
    feature_metadata_path = os.path.join(fe_dir, "feature_metadata.json")
    selection_matrix_path = os.path.join(fe_dir, "selected_features.csv")
    feature_importance_report = os.path.join(fe_dir, "feature_importance.csv")
    selection_log = os.path.join(fe_dir, "selection_rationale.json")
    thresholds = '{}'  # If real thresholds needed, set as JSON str
    exclude_cols = ''  # If any columns to exclude, pass as comma string
    # Note: add sensitive_cols as needed
    fe_cmd = (
        f"python src/data/feature_engineering.py --input '{preproc_output}' --output '{feature_engineered_path}' "
        f"--selection_output '{selection_matrix_path}' --feature_importance_report '{feature_importance_report}' "
        f"--selection_log '{selection_log}' --feature_metadata '{feature_metadata_path}' --target_col 'target' --problem_type 'classification' "
        f"--num_features 20 --condition_thresholds '{thresholds}' --exclude_cols '{exclude_cols}'"
    )
    run_cli(fe_cmd, label="Feature Engineering Pipeline")

    # --- Step 3: Model Training ---
    train_dir = os.path.join(base_output_dir, "train")
    os.makedirs(train_dir, exist_ok=True)
    train_cmd = (
        f"python src/training/train.py --feature_matrix '{selection_matrix_path}' --target_col 'target' "
        f"--artifacts_dir '{train_dir}'"
    )
    run_cli(train_cmd, label="Model Training Pipeline")

    # --- Step 4: Results Verification ---
    expected_artifacts = [
        preproc_output,
        encoders_path,
        scaler_path,
        feature_engineered_path,
        selection_matrix_path,
        feature_importance_report,
        selection_log,
        feature_metadata_path,
        os.path.join(train_dir, 'random_forest_best.joblib'),
        os.path.join(train_dir, 'xgboost_best.joblib'),
        os.path.join(train_dir, 'model_training_log.json')
    ]
    check_artifacts(expected_artifacts)
    logging.info("All designated output artifacts present. Pipeline execution completed successfully.")

    # Optionally, print report summaries for user verification
    train_log_path = os.path.join(train_dir, 'model_training_log.json')
    try:
        with open(train_log_path) as f:
            training_report = json.load(f)
        logging.info(f"Key Model Training Results: 
"
                     f"Random Forest: {json.dumps(training_report.get('rf_metrics', {}), indent=2)}
"
                     f"XGBoost: {json.dumps(training_report.get('xgb_metrics', {}), indent=2)}")
    except Exception as e:
        logging.warning(f"Could not read model_training_log.json: {e}")

    logging.info(f"Pipeline finished: All workflow stages executed and validated.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Fatal pipeline error: {e}")
        logging.error("Exception Traceback:
" + traceback.format_exc())
        sys.exit(99)
