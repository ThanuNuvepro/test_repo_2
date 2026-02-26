import numpy as np
import pandas as pd
import os
import logging
import json
import joblib  # Added for scaler persistence
from typing import Tuple, List, Optional
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import re

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )

def is_valid_path(path: str) -> bool:
    """
    Securely validate that a file path is inside the 'data/' directory and conforms to expected filename patterns.
    Prevents path traversal and ensures only allowed paths are processed.
    """
    if not isinstance(path, str):
        return False
    normalized_path = os.path.normpath(path)
    if '..' in normalized_path.split(os.sep):  # Prohibit directory traversal explicitly
        return False
    if not normalized_path.startswith('data' + os.sep):
        return False
    # Allow .csv, .npy, .json for this activity (can be enhanced as needed)
    if not re.match(r'^data\%s[a-zA-Z0-9_\-/]+\.(csv|npy|json)$' % re.escape(os.sep), normalized_path):
        return False
    return True

def load_features_and_target(features_path: str, target_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load features and target arrays from .npy files, with error handling.
    """
    if not (os.path.exists(features_path) and os.path.exists(target_path)):
        raise FileNotFoundError(f"One or both feature/target .npy files not found: {features_path}, {target_path}")
    X = np.load(features_path)
    y = np.load(target_path)
    if len(X.shape) == 1:
        X = X.reshape(-1, 1)
    return X, y

def get_feature_column_names(feature_manifest_path: str) -> List[str]:
    """
    Retrieve feature (column) names from manifest JSON if available.
    """
    if not os.path.exists(feature_manifest_path):
        raise FileNotFoundError(f"Feature manifest not found at {feature_manifest_path}")
    with open(feature_manifest_path, 'r') as f:
        manifest = json.load(f)
    numeric_features = manifest.get('features', [])
    return numeric_features

def split_data(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    random_state: int = 42,
    stratify: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split arrays into training and test sets. Optional stratification for classification tasks.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify)
    return X_train, X_test, y_train, y_test

def is_classification(y: np.ndarray) -> bool:
    """
    Basic heuristic to determine if y is for classification (discrete labels).
    """
    # Cast to int, compare number of unique discrete values vs number of samples
    return np.issubdtype(y.dtype, np.integer) and len(np.unique(y)) < 0.5 * len(y)

def scale_features(
    X_train: np.ndarray,
    X_test: np.ndarray,
    scaler_type: str = 'standard'  # or 'minmax'
) -> Tuple[np.ndarray, np.ndarray, List[str], str, object]:
    """
    Scale features using the selected scaler. Returns scaled arrays, column names, scaler type, and scaler object.
    """
    if scaler_type.lower() == 'minmax':
        scaler = MinMaxScaler()
    else:
        scaler = StandardScaler()
    scaler.fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    # Only StandardScaler (sklearn >= 1.0) has get_feature_names_out
    if hasattr(scaler, 'get_feature_names_out'):
        columns = scaler.get_feature_names_out().tolist()
    else:
        columns = []
    return X_train_scaled, X_test_scaled, columns, scaler.__class__.__name__, scaler

def save_numpy_array(arr: np.ndarray, path: str):
    """
    Save NumPy array to disk with .npy extension.
    """
    np.save(path, arr)

def save_scaling_metadata(columns: List[str], scaler_type: str, meta_path: str):
    """
    Write scaling metadata (column names, scaler) to JSON.
    """
    meta = {
        "scaled_columns": columns,
        "scaler": scaler_type
    }
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)
    logging.info(f"Scaling metadata saved: {meta_path}")

def save_scaler_object(scaler, scaler_path: str):
    """
    Persist the scaler object (for future inference-time transformation).
    """
    joblib.dump(scaler, scaler_path)
    logging.info(f"Scaler object saved: {scaler_path}")

def check_feature_alignment(feature_names: List[str], X: np.ndarray) -> List[str]:
    """
    Ensures the feature names align with the number of features. Falls back to indexed names if mismatch.
    """
    if feature_names and len(feature_names) == X.shape[1]:
        return feature_names
    else:
        logging.warning("Feature names do not match X shape. Using fallback column names.")
        return [f"col_{i}" for i in range(X.shape[1])]

def main():
    import argparse
    setup_logging()
    parser = argparse.ArgumentParser(description='Split data and scale features for ML model readiness (manufacturing sensor project)')
    parser.add_argument('--features', type=str, default='data/features.npy', help='Feature .npy file (must be in data/)')
    parser.add_argument('--target', type=str, default='data/target.npy', help='Target .npy file (must be in data/)')
    parser.add_argument('--feature_manifest', type=str, default='data/feature_manifest.json', help='Feature manifest (for audit/documentation)')
    parser.add_argument('--train_features', type=str, default='data/X_train.npy', help='Where to save train features')
    parser.add_argument('--test_features', type=str, default='data/X_test.npy', help='Where to save test features')
    parser.add_argument('--train_target', type=str, default='data/y_train.npy', help='Where to save train labels')
    parser.add_argument('--test_target', type=str, default='data/y_test.npy', help='Where to save test labels')
    parser.add_argument('--scaler_type', type=str, default='standard', choices=['standard', 'minmax'], help='Feature scaling type')
    parser.add_argument('--scaling_meta', type=str, default='data/scaling_metadata.json', help='Path to save scaling metadata JSON')
    parser.add_argument('--scaler_object', type=str, default='data/scaler.joblib', help='Path to save the fitted scaler object')
    parser.add_argument('--test_ratio', type=float, default=0.2, help='Ratio (0,1) for held-out test set')
    parser.add_argument('--stratified', action='store_true', help='Use stratified split if classification labels detected')
    args = parser.parse_args()

    # Validate all CLI-supplied paths
    paths_to_validate = [
        args.features, args.target, args.feature_manifest,
        args.train_features, args.test_features, args.train_target, args.test_target,
        args.scaling_meta, args.scaler_object
    ]
    for p in paths_to_validate:
        if not is_valid_path(p):
            logging.error(f"Unsafe or invalid path detected: {p}")
            raise ValueError(f"Unsafe or invalid file path: {p}")

    # Load arrays
    X, y = load_features_and_target(args.features, args.target)
    feature_names = get_feature_column_names(args.feature_manifest)
    logging.info(f"Loaded features shape: {X.shape}, target shape: {y.shape}")

    # Check for stratification if requested
    stratify = None
    if args.stratified:
        if is_classification(y):
            stratify = y
            logging.info("Stratified split enabled (classification detected).")
        else:
            logging.warning("Stratified split requested, but target does not look like classification. Disabling stratify.")
            stratify = None

    # Split
    X_train, X_test, y_train, y_test = split_data(
        X, y, test_size=args.test_ratio, stratify=stratify  # Defensive stratify logic
    )
    logging.info(f"Split done: X_train {X_train.shape}, X_test {X_test.shape}")

    # Scale
    X_train_scaled, X_test_scaled, scaled_cols, scaler_type_name, scaler = scale_features(
        X_train, X_test, scaler_type=args.scaler_type
    )

    # Include robust alignment for feature names
    colnames = check_feature_alignment(feature_names, X_train)

    # Save scaling metadata
    save_scaling_metadata(colnames, scaler_type_name, args.scaling_meta)

    # Persist the scaler object for future inference use
    save_scaler_object(scaler, args.scaler_object)

    # Save split arrays
    save_numpy_array(X_train_scaled, args.train_features)
    save_numpy_array(X_test_scaled, args.test_features)
    save_numpy_array(y_train, args.train_target)
    save_numpy_array(y_test, args.test_target)
    logging.info(f"Train/test split and scaling complete.
Train features: {args.train_features}
Test features: {args.test_features}")
    logging.info(f"Scaling applied to columns: {colnames} using {scaler_type_name}")
    print(f"Split and scaling complete. Scaled columns: {colnames}.
Train shape: {X_train_scaled.shape}, Test shape: {X_test_scaled.shape}")

if __name__ == '__main__':
    main()

# ---------------- Unit Test Section -----------------
# Automated regression tests are essential for pipelines. Cover input handling, split, scaling, and error clauses.
import pytest
import tempfile

def create_dummy_arrays(shape_X=(10, 4), shape_y=(10,)):
    np.random.seed(42)
    X = np.random.rand(*shape_X)
    y = np.random.randint(0, 2, size=shape_y)  # Classification labels
    return X, y

def test_is_valid_path():
    assert is_valid_path('data/features.npy')
    assert not is_valid_path('../data/features.npy')
    assert not is_valid_path('data/../features.npy')
    assert not is_valid_path('invalid/features.npy')
    assert not is_valid_path('data/badpath/../../features.npy')
    assert is_valid_path('data/mysubdir/feats.npy')
    assert is_valid_path('data/mysubdir/feats.json')
    assert not is_valid_path('data/mysubdir/feats.exe')


def test_split_and_scale(tmp_path):
    # Prepare and save dummy arrays and manifest
    X, y = create_dummy_arrays()
    feat_path = tmp_path / 'data' / 'features.npy'
    targ_path = tmp_path / 'data' / 'target.npy'
    feat_dir = feat_path.parent
    feat_dir.mkdir(parents=True, exist_ok=True)
    np.save(str(feat_path), X)
    np.save(str(targ_path), y)
    feature_manifest_path = tmp_path / 'data' / 'feature_manifest.json'
    feature_names = [f'f{i}' for i in range(X.shape[1])]
    with open(feature_manifest_path, 'w') as f:
        json.dump({'features': feature_names}, f)
    # Perform split/scale
    X2, y2 = load_features_and_target(str(feat_path), str(targ_path))
    assert X2.shape == X.shape
    assert y2.shape == y.shape
    X_train, X_test, y_train, y_test = split_data(X2, y2, test_size=0.3, random_state=0, stratify=y2)
    assert X_train.shape[0] + X_test.shape[0] == X.shape[0]
    X_train_scaled, X_test_scaled, cols, scaler_nm, scaler_obj = scale_features(X_train, X_test, 'standard')
    assert X_train_scaled.shape == X_train.shape
    assert X_test_scaled.shape == X_test.shape
    assert scaler_nm in ('StandardScaler', 'MinMaxScaler')
    # Test saving scaler object and metadata
    scaler_path = tmp_path / 'data' / 'scaler.joblib'
    save_scaler_object(scaler_obj, str(scaler_path))
    assert os.path.exists(scaler_path)
    meta_path = tmp_path / 'data' / 'scaling_meta.json'
    save_scaling_metadata(feature_names, scaler_nm, str(meta_path))
    with open(meta_path, 'r') as mf:
        meta = json.load(mf)
    assert meta['scaler'] == scaler_nm
    assert meta['scaled_columns'] == feature_names

def test_feature_alignment_fallback():
    feat_names = ['a', 'b', 'c']
    X = np.zeros((2, 2))
    colnames = check_feature_alignment(feat_names, X)
    assert colnames == ['col_0', 'col_1']
    # When lengths match
    X2 = np.zeros((2, 3))
    colnames2 = check_feature_alignment(['a', 'b', 'c'], X2)
    assert colnames2 == ['a', 'b', 'c']

def test_is_classification():
    y_class = np.array([0, 1, 1, 0, 1, 0, 1, 0, 0, 1])
    assert is_classification(y_class)
    y_regress = np.array([0.1, 2.3, 4.5, 6.7, 8.9, 1.2, 3.4, 5.6, 7.8, 9.0])
    assert not is_classification(y_regress)
