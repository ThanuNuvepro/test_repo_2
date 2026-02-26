import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from typing import List, Optional
from src.data.preprocessing import load_sensor_data, is_valid_path  # import secure path checker from context
from src.data.feature_engineering import identify_features_and_target

# --- Logging Setup ---
def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )

# --- Safe directory creation ---
def safe_mkdir(path: str):
    """
    Create directory if it doesn't exist.
    """
    if not os.path.exists(path):
        os.makedirs(path)

# --- Feature Selection Utility ---
def select_key_features(
    df: pd.DataFrame,
    n: int = 3,
    explicit_features: Optional[List[str]] = None
) -> List[str]:
    """
    Select the key features for univariate EDA.
    If explicit_features is supplied, those are returned (if valid).
    Otherwise, selects top n most variable numeric columns.
    """
    if explicit_features is not None:
        # Use features only if they are in dataframe columns
        filtered = [f for f in explicit_features if f in df.columns]
        if filtered:
            return filtered
        else:
            logging.warning(f'Explicit feature list does not match any columns. Falling back to auto-selection.')
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Choose most variable features if possible
    if len(numeric_cols) == 0:
        return []
    variances = df[numeric_cols].var().sort_values(ascending=False)
    selected = variances.head(n).index.tolist()
    if not selected:
        # Fallback: just pick first n numeric columns
        selected = numeric_cols[:n]
    return selected

# --- Missing Value Imputation for EDA Safety ---
def impute_for_eda(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute missing numerical values with column mean before EDA.
    Object columns are forward-filled for minimal EDA stability.
    """
    df_new = df.copy()
    num_cols = df_new.select_dtypes(include=[np.number]).columns
    for col in num_cols:
        if df_new[col].isnull().sum() > 0:
            fill_val = df_new[col].mean()
            df_new[col].fillna(fill_val, inplace=True)
            logging.info(f'Imputed missing values in {col} with mean before EDA: {fill_val:.3f}')
    obj_cols = df_new.select_dtypes(include=[object]).columns
    for col in obj_cols:
        if df_new[col].isnull().sum() > 0:
            df_new[col].fillna(method='ffill', inplace=True)
            logging.info(f'Forward-filled missing values in {col}')
    return df_new

# --- Safe plot saving with error handling & logging ---
def try_savefig(plot_file: str):
    """
    Save a Matplotlib figure with error logging.
    """
    try:
        plt.tight_layout()
        plt.savefig(plot_file)
        logging.info(f'Saved plot: {plot_file}')
    except Exception as e:
        logging.error(f'Failed to save plot {plot_file}: {e}')

# --- Univariate Plotting Function ---
def plot_univariate_distributions(
    df: pd.DataFrame,
    features: List[str],
    target: str,
    out_dir: str = 'data/eda_univariate_plots',
    color_palette: str = 'Set2'
):
    """
    Plot univariate feature distributions and optionally overlay by target labels.
    Plots are saved as PNG. Class balance is plotted if target is classification.
    Returns list of plot file paths.
    """
    safe_mkdir(out_dir)  # Ensure output directory exists
    plot_paths = []
    for f in features:
        if f not in df.columns:
            logging.warning(f'Feature {f} not in dataframe; skipping.')
            continue
        plt.figure(figsize=(8,5))
        try:
            if target in df.columns:
                # If classification with reasonable class count
                if pd.api.types.is_numeric_dtype(df[target]) and len(df[target].unique()) <= 10:
                    palette = sns.color_palette(color_palette, len(df[target].unique()))
                    sns.histplot(data=df, x=f, hue=target, kde=True, element='step', palette=palette, stat='probability', alpha=0.8)
                else:
                    sns.histplot(df[f], kde=True, color='steelblue', stat='probability')
            else:
                sns.histplot(df[f], kde=True, color='steelblue', stat='probability')
            plt.title(f'Distribution of {f}')
            plt.xlabel(f)
            plt.ylabel('Probability')
            plot_file = os.path.join(out_dir, f'{f}_distribution.png')
            try_savefig(plot_file)
            plot_paths.append(plot_file)
        except Exception as e:
            logging.error(f'Error plotting {f}: {e}')
        plt.close()
    # Target/class balance plot
    if target in df.columns:
        plt.figure(figsize=(6,4))
        try:
            if pd.api.types.is_numeric_dtype(df[target]) and len(df[target].unique()) <= 10:
                sns.countplot(x=target, data=df, palette=color_palette)
                plt.title(f'Class Balance for Target: {target}')
                plt.xlabel(target)
                plt.ylabel('Count')
                for i, val in enumerate(df[target].value_counts().values):
                    plt.text(i, val, str(val), ha='center', va='bottom', fontsize=10)
                class_balance_path = os.path.join(out_dir, f'{target}_class_balance.png')
                try_savefig(class_balance_path)
                plot_paths.append(class_balance_path)
        except Exception as e:
            logging.error(f'Error plotting class balance for {target}: {e}')
        plt.close()
    return plot_paths

# --- Text Summary Extraction ---
def summarize_univariate_patterns(
    df: pd.DataFrame,
    features: List[str],
    target: str,
    out_path: str = 'data/univariate_summary.txt'
):
    """
    Summarize descriptive statistics for each feature and by target (if classification).
    Output is written to a text file at out_path.
    """
    summaries = []
    for f in features:
        if f not in df.columns:
            logging.warning(f'Feature {f} not in dataframe; skipping summary.')
            continue
        desc = df[f].describe()
        msg = f'Feature: {f}
Mean: {desc.get("mean", float("nan")):.3f}
Std: {desc.get("std", float("nan")):.3f}
Min: {desc.get("min", float("nan")):.3f}
Max: {desc.get("max", float("nan")):.3f}
'
        if target in df.columns and f != target:
            if pd.api.types.is_numeric_dtype(df[target]) and len(df[target].unique()) <= 10:
                means = df.groupby(target)[f].mean()
                msg += 'Means by Target:
'
                for tval, tmean in means.items():
                    msg += f'- {target}={tval}: mean={tmean:.3f}
'
        summaries.append(msg)
    # Add target class distribution summary
    if target in df.columns:
        counts = df[target].value_counts().to_dict()
        target_summary = f'Target {target} class distribution: ' + ', '.join([
            f'{k}: {v}' for k, v in counts.items()])
        summaries.append(target_summary)
    summary_report = '
'.join(summaries)
    try:
        # Use is_valid_path from context for compliance with security
        dirpath = os.path.dirname(out_path)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath)
        # Allow only .txt files under data/
        if not (is_valid_path(out_path.replace('.txt', '.csv')) or out_path.endswith('.txt')):
            logging.warning(f'Refusing to write summary to unsafe path: {out_path}')
            return None
        with open(out_path, 'w') as f:
            f.write(summary_report)
        logging.info(f'Wrote univariate summary to {out_path}')
    except Exception as e:
        logging.error(f'Failed to write summary to {out_path}: {e}')
        return None
    return out_path

# --- EDA High-Level Flow ---
def run_univariate_eda(
    csv_path: str = 'data/cleaned_sensor_data.csv',
    out_dir: str = 'data/eda_univariate_plots',
    summary_txt: str = 'data/univariate_summary.txt',
    explicit_features: Optional[List[str]] = None
):
    """
    Main EDA pipeline: loads data, imputes missing values for EDA safety, selects features, plots, summarizes.
    """
    setup_logging()
    # Secure input path
    if not is_valid_path(csv_path):
        raise ValueError(f'Unsafe input file path: {csv_path}')
    # Load data
    df = load_sensor_data(csv_path)
    # Impute missing values for EDA stability
    df = impute_for_eda(df)
    # Identify features & target
    feature_cols, target_col = identify_features_and_target(df)
    key_features = select_key_features(df, explicit_features=explicit_features)
    if not key_features:
        raise ValueError('No features selected for EDA.')
    logging.info(f'Selected features for EDA: {key_features}. Target: {target_col}')
    # Plots
    plot_files = plot_univariate_distributions(df, key_features, target_col, out_dir)
    logging.info(f'Saved univariate plots: {plot_files}')
    # Summary
    summary_path = summarize_univariate_patterns(df, key_features, target_col, summary_txt)
    if summary_path:
        logging.info(f'Saved summary: {summary_path}')
        print(f'Key distributions saved as images in {out_dir}. Summary written to {summary_txt}.')
    else:
        print('Summary report not written due to path/security error.')
    return plot_files, summary_path

# --- CLI Entrypoint ---
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Univariate EDA with visualization')
    parser.add_argument('--input', type=str, default='data/cleaned_sensor_data.csv', help='Cleaned sensor data path')
    parser.add_argument('--out_dir', type=str, default='data/eda_univariate_plots', help='Directory to save plots')
    parser.add_argument('--summary', type=str, default='data/univariate_summary.txt', help='Text file to save summary')
    parser.add_argument('--features', type=str, nargs='+', default=None, help='Explicit features to plot (optional)')
    args = parser.parse_args()
    run_univariate_eda(csv_path=args.input, out_dir=args.out_dir, summary_txt=args.summary, explicit_features=args.features)
