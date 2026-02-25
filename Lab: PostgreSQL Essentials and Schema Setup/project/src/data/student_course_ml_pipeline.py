# End-to-End ML Data Pipeline integrating relational schema for Student Course Management
# This script contains:
# 1. Data connectors to the schema tables
# 2. Data preprocessing and feature engineering
# 3. Model training and evaluation
# 4. Model versioning and data integrity features
# 5. Model deployment as a REST API (Flask) with improved security and error handling

import os
import sys
import hashlib
import json
import logging
from functools import wraps

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
import joblib
from flask import Flask, request, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env if present
load_dotenv()

###############################################
# Logging Configuration and Audit Log         #
###############################################

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler("ml_pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
auditor = logging.getLogger('audit')

def log_audit(event_type, details):
    auditor.info(json.dumps({
        'event_type': event_type,
        'timestamp': datetime.utcnow().isoformat(),
        'details': details
    }))

###############################################
# 1. Data Ingestion: Connect to relational DB #
###############################################

# Use env variables for credentials
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'student_course_db')

# Error if required credentials missing
if not DB_USER or not DB_PASS:
    logging.error("Database credentials must not be empty. Set DB_USER and DB_PASS as environment variables.")
    raise ValueError("Database credentials missing from environment variables.")

DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    logging.error(f"Failed to create database engine: {e}")
    raise

# Data loading functions

def load_tables(engine):
    """Load tables from the database with error handling."""
    try:
        # Use text() for safer SQL
        students = pd.read_sql(text("SELECT * FROM students"), engine)
        courses = pd.read_sql(text("SELECT * FROM courses"), engine)
        enrollments = pd.read_sql(text("SELECT * FROM enrollments"), engine)
        # Data integrity hash logging
        for table_name, df in [('students', students), ('courses', courses), ('enrollments', enrollments)]:
            data_hash = hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest()
            log_audit('data_loaded', {'table': table_name, 'row_count': len(df), 'hash': data_hash})
        return students, courses, enrollments
    except Exception as e:
        logging.exception("Data loading failed.")
        raise

#############################################
# 2. Data Preprocessing and Feature Engineering #
#############################################

def preprocess_and_join(students, courses, enrollments):
    """
    Merge and preprocess data to generate model-ready features.
    Predictive Task: Predict whether a student will complete a course based on student/course features.
    """
    try:
        df = enrollments.merge(students, on='student_id', suffixes=('', '_student'))                        .merge(courses, on='course_id', suffixes=('', '_course'))
        # Target encoding
        df['target_completed'] = (df['enrollment_status'].str.lower() == 'completed').astype(int)
        # Feature engineering
        df['student_age'] = ((pd.Timestamp("now") - pd.to_datetime(df['date_of_birth'])) / pd.Timedelta(days=365)).astype(int)
        le_dept = LabelEncoder()
        df['department_encoded'] = le_dept.fit_transform(df['department'].fillna('UNKNOWN'))
        df['course_is_active'] = df['is_active'].astype(int)
        df['student_is_active'] = df['active'].astype(int)
        feature_cols = [
            'student_age',
            'department_encoded',
            'credits',
            'course_is_active',
            'student_is_active'
        ]
        X = df[feature_cols]
        y = df['target_completed']
        return X, y, df
    except Exception as e:
        logging.exception("Preprocessing or feature engineering failed.")
        raise

############################################
# 3. Feature Scaling and Train/Test Split #
############################################

def scale_and_split(X, y, test_size=0.2, random_state=42):
    try:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=random_state, stratify=y
        )
        return X_train, X_test, y_train, y_test, scaler
    except Exception as e:
        logging.exception("Scaling or train/test split failed.")
        raise

#########################
# 4. Model Training    #
#########################

def train_random_forest(X_train, y_train, n_estimators=100, random_state=42):
    try:
        model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
        model.fit(X_train, y_train)
        return model
    except Exception as e:
        logging.exception("Model training failed.")
        raise

#################################
# 5. Model Evaluation           #
#################################

def evaluate_model(model, X_test, y_test):
    try:
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)
        clf_report = classification_report(y_test, y_pred)
        logging.info(f"Accuracy: {acc:.3f}, F1: {f1:.3f}")
        logging.info("Confusion Matrix:
%s", cm)
        logging.info("Classification Report:
%s", clf_report)
        log_audit('model_evaluated', {
            'accuracy': acc,
            'f1_score': f1,
            'confusion_matrix': cm.tolist()
        })
        return {
            'accuracy': acc,
            'f1_score': f1,
            'confusion_matrix': cm.tolist(),
            'classification_report': clf_report
        }
    except Exception as e:
        logging.exception("Model evaluation failed.")
        raise

########################################
# 6. Model/Scaler Serialization (Joblib)
########################################

def save_model_and_scaler(model, scaler, model_path='model.pkl', scaler_path='scaler.pkl'):
    try:
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        log_audit('model_saved', {'model_path': model_path, 'scaler_path': scaler_path})
    except Exception as e:
        logging.exception("Saving model/scaler failed.")
        raise

def load_model_and_scaler(model_path='model.pkl', scaler_path='scaler.pkl'):
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        return model, scaler
    except Exception as e:
        logging.exception("Loading model/scaler failed.")
        raise

def verify_model_file(model_path):
    """Simple SHA256 hash check for audit purposes."""
    try:
        with open(model_path, 'rb') as f:
            content = f.read()
            hashval = hashlib.sha256(content).hexdigest()
        log_audit('model_file_verified', {'model_path': model_path, 'sha256': hashval})
        return hashval
    except Exception as e:
        logging.exception(f"Model file integrity check failed for {model_path}")
        return None

###########################################
# 7. Model Versioning and Data Integrity  #
###########################################

def get_schema_hash(engine):
    # Create a hash of the DB schema for tracking
    try:
        insp = engine.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in insp]
        schema_concat = ''
        for tbl in sorted(tables):
            res = engine.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{tbl}' ORDER BY column_name"))
            schema_concat += tbl + ':' + ','.join(f"{r[0]}:{r[1]}" for r in res) + ';'
        schema_hash = hashlib.sha256(schema_concat.encode('utf-8')).hexdigest()
        log_audit('schema_hash', {'schema_hash': schema_hash})
        return schema_hash
    except Exception as e:
        logging.exception("Could not compute schema hash.")
        return None

################################
# 8. REST API for Model Serving
################################

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=[os.getenv('API_RATE_LIMIT', '10/minute')])

# Configurable API key for authentication
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    logging.error('API_KEY missing in environment variables! Secure the API before exposure.')
    API_KEY = 'testdevkey'  # Only for dev/demo; must be set for production!

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            log_audit('auth_fail', {'remote_addr': request.remote_addr})
            return jsonify({'error': 'Invalid or missing API key.'}), 401
        return f(*args, **kwargs)
    return decorated

MODEL_PATH = 'model.pkl'
SCALER_PATH = 'scaler.pkl'

# Checks for presence of model/scaler files

def check_model_files():
    return os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH)

@app.route('/predict', methods=['POST'])
@require_api_key
@limiter.limit(os.getenv('API_PREDICT_RATE', '5/minute'))
def predict_completion():
    if not check_model_files():
        log_audit('prediction_error', {'reason': 'model or scaler missing'})
        return jsonify({"error": "Model or scaler not found. Train and save first."}), 400
    try:
        model, scaler = load_model_and_scaler(MODEL_PATH, SCALER_PATH)
    except Exception:
        return jsonify({"error": "Failed to load model or scaler."}), 500
    input_json = request.get_json(force=True, silent=True)
    required_fields = [
        'student_age', 'department_encoded', 'credits', 'course_is_active', 'student_is_active'
    ]
    if not input_json:
        return jsonify({"error": "Empty or malformed JSON payload."}), 400
    if not all(f in input_json for f in required_fields):
        return jsonify({"error": f"Payload missing one or more required fields: {required_fields}"}), 400
    # Type and range check
    for field in required_fields:
        val = input_json[field]
        if not isinstance(val, (int, float)):
            return jsonify({"error": f"Field '{field}' must be numeric."}), 400
        if field == 'credits' and (val <= 0 or val > 100):
            return jsonify({"error": "Credits must be in (0, 100]."}), 400
        if field in ('course_is_active', 'student_is_active') and val not in (0, 1):
            return jsonify({"error": f"Field '{field}' must be 0 or 1."}), 400
        if field == 'student_age' and (val < 10 or val > 100):
            return jsonify({"error": f"Unrealistic student_age ({val})"}), 400
    try:
        input_data = np.array([[input_json[f] for f in required_fields]])
        input_scaled = scaler.transform(input_data)
        pred = model.predict(input_scaled)[0]
        prob = float(model.predict_proba(input_scaled)[0][1])
        response = {"completed": int(pred), "probability_completed": prob}
        log_audit('prediction', {
            'input': input_json,
            'result': response,
            'client_ip': request.remote_addr
        })
        return jsonify(response)
    except Exception as e:
        log_audit('prediction_error', {'exception': str(e)})
        return jsonify({"error": "Prediction failed: input/data error."}), 500

@app.route('/health', methods=['GET'])
def health():
    # Sha256 hashes of files and schema hash
    model_hash = verify_model_file(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
    scaler_hash = verify_model_file(SCALER_PATH) if os.path.exists(SCALER_PATH) else None
    schema_hash = get_schema_hash(engine)
    status = {
        'status': 'ok',
        'model_file': MODEL_PATH,
        'model_hash': model_hash,
        'scaler_file': SCALER_PATH,
        'scaler_hash': scaler_hash,
        'schema_hash': schema_hash
    }
    return jsonify(status)

#########################
# 9. Main execution     #
#########################

def main():
    try:
        logging.info("Loading tables from database...")
        students, courses, enrollments = load_tables(engine)
        logging.info("Preprocessing and feature engineering...")
        X, y, _ = preprocess_and_join(students, courses, enrollments)
        logging.info("Scaling features and splitting train/test set...")
        X_train, X_test, y_train, y_test, scaler = scale_and_split(X, y)
        logging.info("Training Random Forest classifier...")
        model = train_random_forest(X_train, y_train)
        logging.info("Evaluating model...")
        metrics = evaluate_model(model, X_test, y_test)
        logging.info("Saving model and scaler...")
        save_model_and_scaler(model, scaler, MODEL_PATH, SCALER_PATH)
        logging.info("Done. Model and scaler are saved.")
        print("Evaluation metrics:", metrics)
    except Exception as e:
        logging.exception("Pipeline execution failed.")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Student Course ML Pipeline')
    parser.add_argument('--train', action='store_true', help='Run training pipeline')
    parser.add_argument('--serve', action='store_true', help='Run API server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (for --serve)')
    parser.add_argument('--port', default=5000, type=int, help='Server port (for --serve)')
    args = parser.parse_args()

    if args.train:
        main()
    if args.serve:
        log_audit('api_started', {'host': args.host, 'port': args.port})
        app.run(host=args.host, port=args.port, debug=True)
