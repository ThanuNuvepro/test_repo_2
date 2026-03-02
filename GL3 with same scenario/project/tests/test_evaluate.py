import os
import sys
import tempfile
import shutil
import json
import numpy as np
import pandas as pd
import joblib
import pytest
from unittest import mock
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.metrics import confusion_matrix, roc_auc_score, classification_report, precision_score, recall_score, f1_score
import src.training.evaluate as evaluate_module

# --- Fixtures ---
@pytest.fixture(scope="module")
def sample_data():
    X, y = make_classification(
        n_samples=200,
        n_features=6,
        n_classes=2,
        n_informative=3,
        random_state=42
    )
    df = pd.DataFrame(X, columns=[f"sensor_{i}" for i in range(X.shape[1])])
    df['target'] = y
    return df

@pytest.fixture(scope="module")
def temp_artifacts_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

@pytest.fixture(scope="module")
def simple_rf_model(sample_data, temp_artifacts_dir):
    X = sample_data.drop(columns=['target'])
    y = sample_data['target']
    model = RandomForestClassifier(n_estimators=5, random_state=231)
    model.fit(X, y)
    # Store feature order for test
    model.feature_names_in_ = X.columns.tolist()
    model_path = os.path.join(temp_artifacts_dir, 'rf.joblib')
    joblib.dump(model, model_path)
    return model, model_path

# --- Tests ---
def test_load_model(simple_rf_model):
    _, model_path = simple_rf_model
    model = evaluate_module.load_model(model_path)
    assert hasattr(model, 'predict')
    assert callable(model.predict)

def test_load_data(sample_data, temp_artifacts_dir):
    path = os.path.join(temp_artifacts_dir, 'data.csv')
    sample_data.to_csv(path, index=False)
    X, y, df = evaluate_module.load_data(path, 'target')
    assert isinstance(X, pd.DataFrame)
    assert (df['target'] == y).all()
    assert X.shape[1] == sample_data.shape[1]-1

def test_load_split_idx_and_get_split_indices(sample_data, temp_artifacts_dir):
    path = os.path.join(temp_artifacts_dir, 'data.csv')
    sample_data.to_csv(path, index=False)
    test_idx = sample_data.index[:10].tolist()
    split_meta = {'test_idx': test_idx}
    meta_path = os.path.join(temp_artifacts_dir, 'split.json')
    with open(meta_path, 'w') as f:
        json.dump(split_meta, f)
    loaded = evaluate_module.load_split_idx(meta_path)
    assert 'test_idx' in loaded
    df = pd.read_csv(path)
    split_df, idxs = evaluate_module.get_split_indices(df, loaded, 'test')
    assert len(split_df) == len(test_idx)
    assert all([i in idxs for i in test_idx])

def test_compute_confusion(sample_data, temp_artifacts_dir):
    y_true = sample_data['target']
    y_pred = sample_data['target'].copy()
    out_path = os.path.join(temp_artifacts_dir, 'conf.png')
    labels = sorted(np.unique(y_true))
    cm = evaluate_module.compute_confusion(y_true, y_pred, labels, out_path)
    assert os.path.exists(out_path)
    assert (cm == confusion_matrix(y_true, y_pred, labels=labels)).all()

@pytest.mark.parametrize('n_classes', [2, 3])
def test_compute_roc_multiclass(sample_data, temp_artifacts_dir, n_classes):
    X = sample_data.drop(columns=['target'])
    y = sample_data['target'] if n_classes == 2 else np.random.randint(n_classes, size=len(sample_data))
    y_proba = np.zeros((len(y), n_classes))
    for i in range(n_classes):
        y_proba[y == i, i] = 1.0
    out_path = os.path.join(temp_artifacts_dir, f'roc_{n_classes}.png')
    labels = sorted(np.unique(y))
    result = evaluate_module.compute_roc(y, y_proba, n_classes=n_classes, out_path=out_path, class_labels=labels)
    assert os.path.exists(out_path)
    for k in range(n_classes):
        assert 0 <= result[k] <= 1

@pytest.mark.parametrize('n_classes', [2, 3])
def test_compute_pr_curve(sample_data, temp_artifacts_dir, n_classes):
    X = sample_data.drop(columns=['target'])
    y = sample_data['target'] if n_classes == 2 else np.random.randint(n_classes, size=len(sample_data))
    y_proba = np.zeros((len(y), n_classes))
    for i in range(n_classes):
        y_proba[y == i, i] = 1.0
    out_path = os.path.join(temp_artifacts_dir, f'pr_{n_classes}.png')
    labels = sorted(np.unique(y))
    evaluate_module.compute_pr_curve(y, y_proba, n_classes=n_classes, out_path=out_path, class_labels=labels)
    assert os.path.exists(out_path)

def test_feature_importance_plot(simple_rf_model, sample_data, temp_artifacts_dir):
    model, _ = simple_rf_model
    X = sample_data.drop(columns=['target'])
    out_path = os.path.join(temp_artifacts_dir, 'featimp.png')
    fi = evaluate_module.feature_importance_plot(model, X, out_path, 'rf')
    assert os.path.exists(out_path)
    assert len(fi) == X.shape[1]


def test_save_metrics_report(temp_artifacts_dir):
    d = {'metric1': 1.23, 'metric2': 2.345}
    out_path = os.path.join(temp_artifacts_dir, 'report.json')
    evaluate_module.save_metrics_report(d, out_path)
    assert os.path.exists(out_path)
    loaded = json.load(open(out_path))
    assert loaded == d


def test_save_classification_report(sample_data, temp_artifacts_dir):
    y_pred = sample_data['target'].copy()[::-1].reset_index(drop=True)
    y_true = sample_data['target']
    out_path = os.path.join(temp_artifacts_dir, 'cls_report.json')
    names = [str(x) for x in sorted(sample_data['target'].unique())]
    result = evaluate_module.save_classification_report(y_true, y_pred, names, out_path)
    assert os.path.exists(out_path)
    loaded = json.load(open(out_path))
    # Should contain per-class metrics in string keys
    assert all(k in loaded for k in names)


def test_get_business_metrics():
    metrics = {
        'test_f1': 0.73,
        'test_precision': 0.78,
        'test_recall': 0.55,
        'test_roc_auc': 0.95
    }
    result = evaluate_module.get_business_metrics(metrics, 'rf')
    assert result['test_f1'] == metrics['test_f1']
    assert result['test_roc_auc'] == metrics['test_roc_auc']


def test_log_results_summary(temp_artifacts_dir):
    # Prepare dummy args
    report_path = os.path.join(temp_artifacts_dir, 'report.json')
    model_results = {
        'random_forest': {
            'test_f1': 0.91,
            'test_precision': 0.9,
            'test_recall': 0.92,
            'test_roc_auc': 0.97
        }
    }
    key_findings_path = os.path.join(temp_artifacts_dir, 'key_findings.json')
    preferred_model = 'random_forest'
    top_features = ['a', 'b', 'c']
    feature_importances = {'random_forest': pd.Series([.4, .3, .3], index=['a', 'b', 'c'])}
    business_metric_note = "Business relevant summary."
    evaluate_module.log_results_summary(report_path, model_results, key_findings_path, preferred_model, feature_importances, top_features, business_metric_note)
    assert os.path.exists(key_findings_path)
    loaded = json.load(open(key_findings_path))
    assert loaded['preferred_model'] == preferred_model
    assert loaded['top_features'] == top_features

# --- Edge Cases ---
def test_get_split_indices_fallback(sample_data):
    df = sample_data.copy()
    split_info = None
    split_df, idxs = evaluate_module.get_split_indices(df, split_info, 'test')
    assert isinstance(split_df, pd.DataFrame)
    assert len(split_df) == len(df)

# --- Permissions Edge Case (Platform-Neutral Test) ---
def test_secure_file_permissions_warn(monkeypatch, tmp_path):
    # Simulate OS error
    dummy_path = tmp_path / "file.txt"
    dummy_path.write_text("test")
    with mock.patch("os.chmod", side_effect=OSError("not allowed")):
        evaluate_module.secure_file_permissions(str(dummy_path))
#
# Note: run with pytest -v tests/test_evaluate.py
