import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from datetime import datetime
from typing import List, Optional
from src.data.preprocessing import load_sensor_data, is_valid_path
from src.data.feature_engineering import identify_features_and_target

# --- Improved Logging Setup ---
def setup_logging():
    """
    Set up logging configuration, and reset handlers to avoid duplicate logs when called in multi-module pipelines.
    """
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )

# --- Safe directory creation with error handling ---
def safe_mkdir(path: str):
    """
    Safely create directory and log any errors.
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        logging.error(f'Error creating directory {path}: {e}')
        raise

def infer_time_column(df: pd.DataFrame) -> Optional[str]:
    candidates = [c for c in df.columns if 'time' in c.lower() or 'date' in c.lower() or 'timestamp' in c.lower()]
    if not candidates:
        return None
    for c in candidates:
        try:
            pd.to_datetime(df[c])
            return c
        except Exception:
            continue
    return None

def select_bivariate_pairs(df: pd.DataFrame, target_col: str, n_pairs: int = 2) -> List[tuple]:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    pairs = []
    for i in range(len(numeric_cols)):
        for j in range(i+1, len(numeric_cols)):
            pairs.append((numeric_cols[i], numeric_cols[j]))
    if len(numeric_cols) >= 2 and target_col in df.columns:
        for col in numeric_cols:
            if col != target_col:
                pairs.insert(0, (col, target_col))
    pairs = [p for p in pairs if p[0] != p[1]]
    seen = set()
    unique_pairs = []
    for pair in pairs:
        sorted_pair = tuple(sorted(pair))
        if sorted_pair not in seen:
            seen.add(sorted_pair)
            unique_pairs.append(pair)
    return unique_pairs[:n_pairs]

def plot_bivariate_relationships(df: pd.DataFrame, pairs: List[tuple], out_dir: str = 'data/eda_bivariate_plots', hue: Optional[str]=None):
    safe_mkdir(out_dir)
    plot_paths = []
    plot_count = 0
    for x, y in pairs:
        plt.figure(figsize=(8,6))
        title = f'Scatter: {x} vs {y}'
        fname = f'bivariate_{x}_vs_{y}.png'
        fpath = os.path.join(out_dir, fname)
        try:
            plot_args = dict(data=df, x=x, y=y, alpha=0.7)
            if hue and hue in df.columns and hue != x and hue != y and pd.api.types.is_numeric_dtype(df[hue]) and len(df[hue].unique()) <= 10:
                plot_args['hue'] = hue
                plot_args['palette'] = 'Set1'
            sns.scatterplot(**plot_args)
            corr = df[[x, y]].corr().iloc[0, 1]
            plt.title(f'{title}
Pearson Correlation: {corr:.3f}')
            plt.xlabel(x)
            plt.ylabel(y)
            plt.tight_layout()
            plt.savefig(fpath)
            logging.info(f'Saved bivariate plot: {fpath}')
            plot_paths.append(fpath)
            plot_count += 1
        except Exception as e:
            logging.error(f'Error plotting {x} vs {y}: {e}')
        plt.close()
    logging.info(f'Total bivariate plots saved: {plot_count}')
    return plot_paths

def plot_time_trends(df: pd.DataFrame, time_col: str, features: List[str], target_col: Optional[str], out_dir: str = 'data/eda_time_trends'):
    safe_mkdir(out_dir)
    plot_paths = []
    plot_count = 0
    try:
        df_time = df.copy()
        df_time[time_col] = pd.to_datetime(df_time[time_col], errors='coerce')
        df_time = df_time.sort_values(by=time_col).reset_index(drop=True)
        features = features[:2]
        for feat in features:
            plt.figure(figsize=(10,5))
            plt.plot(df_time[time_col], df_time[feat], label=f'{feat}', color='blue', linewidth=1.2)
            if target_col and target_col in df.columns and pd.api.types.is_numeric_dtype(df[target_col]) and len(df[target_col].unique()) <= 3:
                ts = df_time[target_col]*(df_time[feat].max()-df_time[feat].min())/2 + df_time[feat].min() + (df_time[feat].max()-df_time[feat].min())*0.07
                plt.scatter(df_time[time_col], ts, c=df_time[target_col], cmap='Set1', marker='o', s=12, alpha=0.5, label='Target (positioned)')
            plt.title(f'Time Trend: {feat} over {time_col}')
            plt.xlabel(time_col)
            plt.ylabel(feat)
            plt.legend()
            fname = f'time_trend_{feat}_over_{time_col}.png'
            fpath = os.path.join(out_dir, fname)
            plt.tight_layout()
            plt.savefig(fpath)
            logging.info(f'Saved time trend plot: {fpath}')
            plot_paths.append(fpath)
            plot_count += 1
            plt.close()
    except Exception as e:
        logging.error(f'Error in time trend plotting: {e}')
    logging.info(f'Total time trend plots saved: {plot_count}')
    return plot_paths

def plot_correlation_heatmap(df: pd.DataFrame, out_path: str = 'data/eda_bivariate_plots/correlation_heatmap.png'):
    safe_mkdir(os.path.dirname(out_path))
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Heuristic for very high-dimensional data (>20 features): sample features for readability
    MAX_HEATMAP_FEATURES = 20
    if len(num_cols) > MAX_HEATMAP_FEATURES:
        logging.warning(f'Too many numeric features ({len(num_cols)}); truncating heatmap to first {MAX_HEATMAP_FEATURES} columns.')
        num_cols = num_cols[:MAX_HEATMAP_FEATURES]
    plt.figure(figsize=(1+1.2*len(num_cols), 1+0.8*len(num_cols)))
    corr = df[num_cols].corr()
    sns.heatmap(corr, annot=True, cmap='RdBu_r', fmt='.2f', square=True, cbar=True)
    plt.title('Feature Correlation Heatmap')
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    logging.info(f'Saved correlation heatmap: {out_path}')
    return out_path

def detect_bivariate_insights(df: pd.DataFrame, pairs: List[tuple], correlation_threshold: float = 0.7) -> List[str]:
    insights = []
    for x, y in pairs:
        if x in df.columns and y in df.columns:
            corr = df[[x, y]].corr().iloc[0, 1]
            # Only Pearson; surface a warning if columns are non-numeric or likely non-linear
            if not (pd.api.types.is_numeric_dtype(df[x]) and pd.api.types.is_numeric_dtype(df[y])):
                logging.warning(f'Bivariate insight: Skipping non-numeric pair {x}, {y}.')
                continue
            if abs(corr) > correlation_threshold:
                s = f'High correlation between {x} and {y} (Pearson r={corr:.2f}).'
            elif abs(corr) > 0.5:
                s = f'Moderate correlation between {x} and {y} (r={corr:.2f}).'
            else:
                s = f'Weak or no significant linear relationship between {x} and {y} (r={corr:.2f}).'
            insights.append(f'Bivariate: {s}')
    return insights

def time_trend_insights(df: pd.DataFrame, time_col: str, features: List[str], target_col: Optional[str]) -> List[str]:
    insights = []
    df_time = df.copy()
    df_time[time_col] = pd.to_datetime(df_time[time_col], errors='coerce')
    df_time = df_time.sort_values(by=time_col)
    for feat in features:
        if feat in df_time.columns:
            v = df_time[feat]
            rolling_mean = v.rolling(window=max(len(v)//20, 5), min_periods=1).mean()
            trend = rolling_mean.iloc[-1] - rolling_mean.iloc[0]
            if abs(trend) > v.std():
                if trend > 0:
                    tmsg = f'Increasing trend in {feat} over time.'
                else:
                    tmsg = f'Decreasing trend in {feat} over time.'
                insights.append(f'Time: {tmsg}')
    if target_col and target_col in df_time.columns and pd.api.types.is_numeric_dtype(df_time[target_col]):
        uniques = df_time[target_col].unique()
        if len(uniques) <= 3:
            counts_by_time = df_time.groupby([pd.Grouper(key=time_col, freq='M')])[target_col].sum()
            if any(counts_by_time != 0):
                insights.append(f'Target events (e.g., failures or alarms) observed over time. Possible seasonal or periodic pattern to investigate.')
    return insights

def summarize_and_save_insights(bivariate_insights: List[str], time_insights: List[str], summary_path: str = 'data/eda_bivariate_time_summary.txt', plot_dirs: Optional[List[str]] = None, plot_counts: Optional[dict] = None):
    safe_mkdir(os.path.dirname(summary_path))
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report = f"EDA Summary generated at {timestamp}
"
    if plot_counts:
        for kind, count in plot_counts.items():
            report += f'Plots saved ({kind}): {count}
'
    if plot_dirs:
        report += f'Plot directories: {', '.join(plot_dirs)}
'
    report += '
'.join(bivariate_insights + time_insights)
    # Emit simple metrics: number of plots, files, row count
    try:
        with open(summary_path, 'w') as f:
            f.write(report)
        logging.info(f'Saved bivariate/time EDA insight summary: {summary_path}')
    except Exception as e:
        logging.error(f'Failed to save insight summary {summary_path}: {e}')
        raise
    return summary_path

def security_check_output_dir(directory: str):
    """
    Basic output dir safety check (not bulletproof, but prevents ../ path escapes).
    """
    if not isinstance(directory, str):
        raise ValueError(f'Output directory not a string: {directory}')
    norm = os.path.normpath(directory)
    if not norm.startswith('data'+os.sep):
        raise ValueError(f'Unsafe output directory: {directory}')
    if '..' in norm.split(os.sep):
        raise ValueError(f'Output directory contains parent traversal: {directory}')
    return True

def warn_if_will_overwrite(files: List[str]):
    """
    Emit a warning if any output files already exist and will be overwritten.
    """
    for f in files:
        if os.path.exists(f):
            logging.warning(f'File will be overwritten: {f}')

# --- Main Pipeline Function ---
def run_bivariate_time_eda(
    csv_path: str = 'data/cleaned_sensor_data.csv',
    out_dir_bivar: str = 'data/eda_bivariate_plots',
    out_dir_time: str = 'data/eda_time_trends',
    summary_txt: str = 'data/eda_bivariate_time_summary.txt'
):
    setup_logging()
    if not is_valid_path(csv_path):
        raise ValueError(f'Unsafe input file path: {csv_path}')
    security_check_output_dir(out_dir_bivar)
    security_check_output_dir(out_dir_time)
    # Output file overwrite warning
    warn_if_will_overwrite([
        os.path.join(out_dir_bivar, 'correlation_heatmap.png'),
        summary_txt
    ])
    df = load_sensor_data(csv_path)
    df = df.copy()
    feature_cols, target_col = identify_features_and_target(df)
    time_col = infer_time_column(df)
    bivar_pairs = select_bivariate_pairs(df, target_col, n_pairs=3)
    bivar_paths = plot_bivariate_relationships(df, bivar_pairs, out_dir_bivar, hue=target_col)
    heatmap_path = plot_correlation_heatmap(df, out_path=os.path.join(out_dir_bivar, 'correlation_heatmap.png'))
    bivar_insights = detect_bivariate_insights(df, bivar_pairs)
    time_paths = []
    time_insights = []
    if time_col:
        time_paths = plot_time_trends(df, time_col, feature_cols, target_col, out_dir=out_dir_time)
        time_insights = time_trend_insights(df, time_col, feature_cols, target_col)
    else:
        time_insights = ['No time column found in data. Skipping time series plots.']
    plot_counts = {'bivariate': len(bivar_paths), 'time_trends': len(time_paths), 'heatmap': 1}
    summary_path = summarize_and_save_insights(bivar_insights, time_insights, summary_txt, plot_dirs=[out_dir_bivar, out_dir_time], plot_counts=plot_counts)
    # Emit process metadata and monitoring information
    row_counts = {'row_count': len(df)}
    logging.info(f'Bivariate plots: {bivar_paths}, time plots: {time_paths}, heatmap: {heatmap_path}, summary: {summary_path}, processed rows: {row_counts["row_count"]}')
    print(f'Bivariate relationship visualizations saved in {out_dir_bivar}. Time trends in {out_dir_time}. Summary & insights in {summary_path}.')
    print(f'Processed {row_counts["row_count"]} rows. Plots saved: bivariate={len(bivar_paths)}, time_trends={len(time_paths)}, heatmap=1.')
    return {
        'bivariate_plots': bivar_paths,
        'time_trend_plots': time_paths,
        'correlation_heatmap': heatmap_path,
        'insights_summary': summary_path,
        'row_count': row_counts['row_count'],
        'plot_counts': plot_counts
    }

# --- CLI Entrypoint ---
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Bivariate and Time-Based EDA with Visualization')
    parser.add_argument('--input', type=str, default='data/cleaned_sensor_data.csv', help='Cleaned sensor data path')
    parser.add_argument('--bivar_dir', type=str, default='data/eda_bivariate_plots', help='Directory for bivariate plots')
    parser.add_argument('--time_dir', type=str, default='data/eda_time_trends', help='Directory for time trend plots')
    parser.add_argument('--summary', type=str, default='data/eda_bivariate_time_summary.txt', help='Text file for insights summary')
    args = parser.parse_args()
    run_bivariate_time_eda(csv_path=args.input, out_dir_bivar=args.bivar_dir, out_dir_time=args.time_dir, summary_txt=args.summary)
