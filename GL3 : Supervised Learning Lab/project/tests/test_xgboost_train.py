import os
import sys
import json
import tempfile
import shutil
import numpy as np
import pytest
import joblib

# Import the training script's main module as a callable, patching sys.argv as needed
import subprocess

# Paths must correspond to those expected by the training CLI in src/training/xgboost_train.py
XGBOOST_TRAIN_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'training', 'xgboost_train.py'))


def create_dummy_data(tmpdir, regression=False, n_classes=2):
    """
    Generate and save feature/target .npy arrays compatible with CLI arguments.
    """
    data_dir = tmpdir.mkdir('data')
    n_train, n_test, n_feat = 50, 20, 6
    X_tr = np.random.randn(n_train, n_feat)
    X_te = np.random.randn(n_test, n_feat)
    if regression:
        y_tr = np.random.randn(n_train)
        y_te = np.random.randn(n_test)
    elif n_classes > 2:
        y_tr = np.random.randint(0, n_classes, size=(n_train,))
        y_te = np.random.randint(0, n_classes, size=(n_test,))
    else:
        # Ensure imbalanced for imbalance test
        y_tr = np.array([1]*10 + [0]*40)
        np.random.shuffle(y_tr)
        y_te = np.random.randint(0, 2, size=(n_test,))
    X_train_path = str(data_dir.join('X_train.npy'))
    y_train_path = str(data_dir.join('y_train.npy'))
    X_test_path = str(data_dir.join('X_test.npy'))
    y_test_path = str(data_dir.join('y_test.npy'))
    np.save(X_train_path, X_tr)
    np.save(y_train_path, y_tr)
    np.save(X_test_path, X_te)
    np.save(y_test_path, y_te)
    return X_train_path, y_train_path, X_test_path, y_test_path, data_dir


def create_xgb_config(tmpdir, params=None):
    cfg = params or { 'model_params': { 'max_depth': 2, 'n_estimators': 5, 'random_state': 42 }}
    cfg_path = str(tmpdir.join('xgboost_config.yaml'))
    import yaml
    with open(cfg_path, 'w') as f:
        yaml.safe_dump(cfg, f)
    return cfg_path


def run_cli(args, env=None):
    """
    Helper to invoke the XGBoost training script as CLI.
    """
    cmd = [sys.executable, XGBOOST_TRAIN_PATH] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return result


def test_classification_cli_runs_and_saves(tmp_path):
    # Prepare data & config
    X_train, y_train, X_test, y_test, data_dir = create_dummy_data(tmp_path)
    cfg_path = create_xgb_config(tmp_path)
    out_model = str(data_dir.join('xgb_model.joblib'))
    out_metrics = str(data_dir.join('xgb_metrics.json'))
    out_audit = str(data_dir.join('xgb_audit.json'))
    out_env = str(data_dir.join('xgb_env.json'))
    args = [
        '--X_train', X_train,
        '--y_train', y_train,
        '--X_test', X_test,
        '--y_test', y_test,
        '--config', cfg_path,
        '--output_model', out_model,
        '--metrics_out', out_metrics,
        '--audit_trail', out_audit,
        '--env_dump', out_env
    ]
    result = run_cli(args)
    assert result.returncode == 0, f'Failed: {result.stderr}'
    # Check outputs
    assert os.path.exists(out_model)
    assert os.path.exists(out_metrics)
    assert os.path.exists(out_audit)
    assert os.path.exists(out_env)
    # Validate metrics file
    with open(out_metrics) as f:
        metrics = json.load(f)
        assert 'test' in metrics
        assert 'accuracy' in metrics['test']
        assert 0.0 <= metrics['test']['accuracy'] <= 1.0
    # Validate audit has hash/trail
    with open(out_audit) as f:
        audit = json.load(f)
        assert 'trained_model_hash' in audit
    # Validate env json has at least numpy or xgboost
    with open(out_env) as f:
        env = json.load(f)
        assert 'numpy' in env
        assert 'xgboost' in env


def test_cli_argument_errors(tmp_path):
    # Give an invalid config file path
    X_train, y_train, X_test, y_test, data_dir = create_dummy_data(tmp_path)
    bad_path = str(data_dir.join('not_found.yaml'))
    args = [
        '--X_train', X_train,
        '--y_train', y_train,
        '--X_test', X_test,
        '--y_test', y_test,
        '--config', bad_path
    ]
    result = run_cli(args)
    assert result.returncode != 0
    assert 'not found' in result.stderr.lower() or 'error' in result.stderr.lower()


def test_config_parsing_error(tmp_path):
    X_train, y_train, X_test, y_test, data_dir = create_dummy_data(tmp_path)
    # Create malformed config
    bad_cfg_path = str(data_dir.join('bad_config.yaml'))
    with open(bad_cfg_path, 'w') as f:
        f.write('model_params: [ this is not valid yaml')
    args = [
        '--X_train', X_train,
        '--y_train', y_train,
        '--X_test', X_test,
        '--y_test', y_test,
        '--config', bad_cfg_path
    ]
    result = run_cli(args)
    assert result.returncode != 0
    assert 'error' in result.stderr.lower()


def test_training_regression_mode(tmp_path):
    # For regression, target is float with multiple unique values
    X_train, y_train, X_test, y_test, data_dir = create_dummy_data(tmp_path, regression=True)
    cfg_path = create_xgb_config(tmp_path, { 'model_params': {'n_estimators': 5, 'random_state': 7}})
    out_model = str(data_dir.join('xgb_regr_model.joblib'))
    out_metrics = str(data_dir.join('xgb_reg_metrics.json'))
    args = [
        '--X_train', X_train,
        '--y_train', y_train,
        '--X_test', X_test,
        '--y_test', y_test,
        '--config', cfg_path,
        '--output_model', out_model,
        '--metrics_out', out_metrics
    ]
    result = run_cli(args)
    assert result.returncode == 0, f'Failed regression mode: {result.stderr}'
    # Check regression metrics (should be present as floats)
    with open(out_metrics) as f:
        metrics = json.load(f)
        # Should contain train and test, model_type is xgboost
        assert 'test' in metrics
        assert 'model_type' in metrics


def test_imbalance_heuristics(tmp_path):
    # This test checks the scale_pos_weight heuristic
    X_train, y_train, X_test, y_test, data_dir = create_dummy_data(tmp_path)
    cfg_path = create_xgb_config(tmp_path)
    out_metrics = str(data_dir.join('xgb_metrics_imb.json'))
    # Remove scale_pos_weight to force heuristic
    args = [
        '--X_train', X_train,
        '--y_train', y_train,
        '--X_test', X_test,
        '--y_test', y_test,
        '--config', cfg_path,
        '--metrics_out', out_metrics
    ]
    result = run_cli(args)
    assert result.returncode == 0, f'Imbalance test failed: {result.stderr}'
    with open(out_metrics) as f:
        metrics = json.load(f)
        # Make sure model_params has scale_pos_weight (should be set by script)
        assert 'model_params' in metrics
        mp = metrics['model_params']
        assert 'scale_pos_weight' in mp and mp['scale_pos_weight'] != 1.0


def test_multiclass_mode(tmp_path):
    # n_classes>2 triggers multi-class mode
    X_train, y_train, X_test, y_test, data_dir = create_dummy_data(tmp_path, n_classes=4)
    cfg_path = create_xgb_config(tmp_path)
    out_metrics = str(data_dir.join('xgb_metrics_multi.json'))
    args = [
        '--X_train', X_train,
        '--y_train', y_train,
        '--X_test', X_test,
        '--y_test', y_test,
        '--config', cfg_path,
        '--metrics_out', out_metrics
    ]
    result = run_cli(args)
    assert result.returncode == 0, f'Multiclass failed: {result.stderr}'
    with open(out_metrics) as f:
        metrics = json.load(f)
        assert 'model_params' in metrics and 'num_class' in metrics['model_params']


def test_output_overwrite_warning(tmp_path):
    # Ensures script will warn or prevent file overwrite unless properly specified
    X_train, y_train, X_test, y_test, data_dir = create_dummy_data(tmp_path)
    cfg_path = create_xgb_config(tmp_path)
    out_model = str(data_dir.join('xgb_overwrite_model.joblib'))
    np.save(out_model, np.zeros(4))  # Create preexisting mock file
    args = [
        '--X_train', X_train,
        '--y_train', y_train,
        '--X_test', X_test,
        '--y_test', y_test,
        '--config', cfg_path,
        '--output_model', out_model
    ]
    result = run_cli(args)
    assert result.returncode == 0, f'Failed overwrite test: {result.stderr}'
    # Should have backed up .joblib.bak
    assert os.path.exists(out_model + '.bak')


def test_metrics_nan_safe(tmp_path):
    # Simulate a metric NaN case: single-class target in test
    X_train, y_train, X_test, y_test, data_dir = create_dummy_data(tmp_path)
    cfg_path = create_xgb_config(tmp_path)
    # Make test target all zeros (single class)
    y_test_all_zero = np.zeros_like(np.load(y_test))
    np.save(y_test, y_test_all_zero)
    out_metrics = str(data_dir.join('xgb_metrics_nan.json'))
    args = [
        '--X_train', X_train,
        '--y_train', y_train,
        '--X_test', X_test,
        '--y_test', y_test,
        '--config', cfg_path,
        '--metrics_out', out_metrics
    ]
    result = run_cli(args)
    assert result.returncode == 0
    with open(out_metrics) as f:
        metrics = json.load(f)
        # At least one test metric should be nan
        vals = list(metrics['test'].values())
        assert any((v is not None and (isinstance(v, float) and np.isnan(v))) for v in vals)

# End of tests
