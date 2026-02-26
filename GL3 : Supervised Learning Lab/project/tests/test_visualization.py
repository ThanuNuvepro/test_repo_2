import os
import numpy as np
import pytest
import shutil
import tempfile
import joblib
import types
from src.training import visualization

# Generate dummy classifier with .predict and .predict_proba
class DummyBinaryClassifier:
    def predict(self, X):
        return np.array([1 if np.mean(x) > 0.5 else 0 for x in X])
    def predict_proba(self, X):
        p = np.clip(np.mean(X, axis=1), 0, 1)
        return np.vstack([1-p, p]).T

class DummyMultiClassifier:
    def predict(self, X):
        # Classes: 0,1,2
        return np.array([int(np.mean(x) * 3) % 3 for x in X])
    def predict_proba(self, X):
        px = np.clip(np.mean(X, axis=1), 0, 1)
        p0, p1 = px/3, px/2
        p2 = 1 - (p0 + p1)
        arr = np.vstack([p0, p1, p2]).T
        arr[arr<0]=0
        # Normalize to sum 1
        arr = arr / arr.sum(axis=1, keepdims=True)
        return arr


def create_temp_files(tmp_path, mode='binary'):
    X_test = np.random.rand(20, 5)
    if mode == 'binary':
        y_test = np.random.randint(0, 2, size=20)
        clf = DummyBinaryClassifier()
    else:
        y_test = np.random.randint(0, 3, size=20)
        clf = DummyMultiClassifier()
    x_path = tmp_path / "data" / "X_test.npy"
    y_path = tmp_path / "data" / "y_test.npy"
    model_path = tmp_path / "data" / ("clf.joblib" if mode == 'binary' else "multi_clf.joblib")
    out_dir = tmp_path / "data" / "plots"
    x_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(str(x_path), X_test)
    np.save(str(y_path), y_test)
    joblib.dump(clf, str(model_path))
    out_dir.mkdir(parents=True, exist_ok=True)
    return str(x_path), str(y_path), str(model_path), str(out_dir), y_test, X_test


def test_is_valid_path_accepts_and_rejects():
    # Should accept safe path, reject unsafe
    assert visualization.is_valid_path('data/X_test.npy')
    assert not visualization.is_valid_path('../data/X_test.npy')
    assert not visualization.is_valid_path('data/../secret.txt')
    assert not visualization.is_valid_path('secret.txt')
    assert visualization.is_valid_path('data/plots/vis.png')
    assert not visualization.is_valid_path('data/plots/vis.exe')


def test_safe_make_dir(tmp_path):
    p = tmp_path / "data" / "a" / "b" / "file.txt"
    d = visualization.safe_make_dir(str(p))
    assert os.path.exists(d)
    d2 = visualization.safe_make_dir(str(tmp_path / "data" / "c"/ "d"))  # Test as directory
    assert os.path.exists(d2)


def test_plot_and_save_confusion_matrix_and_roc_binary(tmp_path):
    x_path, y_path, model_path, out_dir, y_true, X_test = create_temp_files(tmp_path, 'binary')
    cm_png = str(tmp_path / "data" / "plots" / "cm_test.png")
    y_pred = DummyBinaryClassifier().predict(X_test)
    class_names = ['0', '1']
    visualization.plot_and_save_confusion_matrix(y_true, y_pred, class_names, cm_png, "Test CM")
    assert os.path.exists(cm_png)
    roc_png = str(tmp_path / "data" / "plots" / "roc_test.png")
    y_proba = DummyBinaryClassifier().predict_proba(X_test)[:,1]
    visualization.plot_and_save_roc_curve(y_true, y_proba, roc_png, "Test ROC", n_classes=2)
    assert os.path.exists(roc_png)


def test_plot_and_save_confusion_matrix_and_roc_multiclass(tmp_path):
    x_path, y_path, model_path, out_dir, y_true, X_test = create_temp_files(tmp_path, 'multiclass')
    cm_png = str(tmp_path / "data" / "plots" / "cm_multi.png")
    y_pred = DummyMultiClassifier().predict(X_test)
    class_names = ['0', '1', '2']
    visualization.plot_and_save_confusion_matrix(y_true, y_pred, class_names, cm_png, "Multi CM")
    assert os.path.exists(cm_png)
    roc_png = str(tmp_path / "data" / "plots" / "roc_multi.png")
    y_proba = DummyMultiClassifier().predict_proba(X_test)
    visualization.plot_and_save_roc_curve(y_true, y_proba, roc_png, "Test ROC Multi", n_classes=3)
    assert os.path.exists(roc_png)


def test_explanation_texts(tmp_path):
    y_true = np.array([0,1,0,1,1,0])
    y_pred = np.array([0,1,1,0,1,1])
    class_names = ['0','1']
    cm_exp = visualization.get_explanation_from_confusion_matrix(y_true, y_pred, class_names)
    assert "Confusion Matrix" in cm_exp
    y_score = np.array([0.1,0.9,0.5,0.5,0.8,0.2])
    roc_exp = visualization.get_explanation_from_roc_curve(y_true, y_score)
    assert "ROC curve shows" in roc_exp or "Multiclass ROC curves" in roc_exp


def test_compute_visualizations_and_explain_and_save(tmp_path):
    x_path, y_path, model_path, out_dir, y_true, X_test = create_temp_files(tmp_path, 'binary')
    cm_path, roc_path = visualization.compute_visualizations(x_path, y_path, model_path, out_dir, 'dummy')
    assert os.path.exists(cm_path)
    assert os.path.exists(roc_path)
    clf = joblib.load(model_path)
    y_pred = clf.predict(X_test)
    y_score = clf.predict_proba(X_test)[:,1]
    class_names = ['0','1']
    report_txt = visualization.explain_and_save(cm_path, roc_path, y_true, y_pred, y_score, class_names, out_dir, 'dummy')
    assert os.path.exists(report_txt)
    with open(report_txt) as f:
        txt = f.read()
    assert "Confusion matrix" in txt
    assert ("ROC curve" in txt) or (roc_path is None)


def test_visualize_all_models_cli(tmp_path, monkeypatch):
    # Prepare model & data files for both classifiers
    x_path, y_path, model_path, out_dir, y_true, X_test = create_temp_files(tmp_path, 'binary')
    xgb_model_path = model_path.replace("clf.joblib", "xgb_model.joblib")
    # Just use the same model for xgboost slot for test
    shutil.copy2(model_path, xgb_model_path)
    monkeypatch.chdir(str(tmp_path))
    # Patching sys.argv for CLI
    import sys
    sys_argv = [
        'visualization.py',
        '--sklearn_model', model_path,
        '--xgb_model', xgb_model_path,
        '--x_test', x_path,
        '--y_test', y_path,
        '--out_dir', out_dir
    ]
    old_argv = sys.argv
    sys.argv = sys_argv
    # Will run main if guarded
    try:
        # Actually call the function directly (to avoid warnings printed)
        visualization.visualize_all_models(
            sklearn_model_path=model_path,
            xgb_model_path=xgb_model_path,
            x_test_path=x_path,
            y_test_path=y_path,
            out_dir=out_dir,
        )
        # Check files written
        for fname in [
            "baseline_sklearn_confusion_matrix.png",
            "baseline_sklearn_roc_curve.png",
            "xgboost_confusion_matrix.png",
            "xgboost_roc_curve.png",
            "baseline_sklearn_visualization_report.txt",
            "xgboost_visualization_report.txt"
        ]:
            found = os.path.exists(os.path.join(out_dir, fname))
            assert found, f"Missing expected output file: {fname}"
    finally:
        sys.argv = old_argv
