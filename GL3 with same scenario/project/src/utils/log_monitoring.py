import os
import re
import json
from glob import glob
from datetime import datetime

# Supported log levels for filtering and interpretation
LOG_LEVELS = ['ERROR', 'WARNING', 'INFO', 'DEBUG', 'CRITICAL']

def find_log_files(log_dir, patterns=None):
    """
    Search log_dir for files matching shell-style glob patterns.
    """
    patterns = patterns or ['*.log']
    files = []
    for pat in patterns:
        files.extend(glob(os.path.join(log_dir, pat)))
    return sorted(files)

def parse_log_file(logfile):
    """
    Parse a log file line by line, extracting timestamp, log level, and message using a regex pattern compatible with standard Python logging.
    """
    log_entries = []
    # Accepts T or space between date/time, optional msec, handles INFO/DEBUG/CRITICAL etc.
    level_regex = r'(\d{4}-\d{2}-\d{2}T? ?\d{2}:\d{2}:\d{2}(?:[,\.]\d+)?)([ T-]*)- (DEBUG|INFO|WARNING|ERROR|CRITICAL) -(.+)'
    with open(logfile, 'r', errors='ignore') as f:
        for line in f:
            line = line.strip()
            m = re.match(level_regex, line)
            if m:
                dt_str, _, level, msg = m.groups()
                log_entries.append({
                    'timestamp': dt_str,
                    'level': level,
                    'message': msg.strip(),
                    'source': os.path.basename(logfile)
                })
            # If regex doesn't match, skip the line (ignores multiline stack traces, see feedback)
    return log_entries

def parse_all_logs(log_dir, patterns=None):
    """
    Parse all log files in log_dir (matching patterns) and return all entries as a sorted list by timestamp.
    """
    files = find_log_files(log_dir, patterns)
    all_entries = []
    for fp in files:
        entries = parse_log_file(fp)
        all_entries.extend(entries)
    # Sort by timestamp string (ISO format is sortable)
    return sorted(all_entries, key=lambda e: e['timestamp'])

def filter_logs(log_entries, levels=None):
    """
    Filter log entries to keep only those with specified log levels (default: ERROR, WARNING).
    """
    levels = levels or ['ERROR', 'WARNING']
    return [e for e in log_entries if e['level'] in levels]

def summarize_errors_and_warnings(log_entries):
    """
    Summarize errors and warnings by log source, and attach per-message actionable plan.
    """
    summary_by_source = {}
    for entry in log_entries:
        key = entry['source']
        if key not in summary_by_source:
            summary_by_source[key] = []
        summary_by_source[key].append(entry)
    actionable = []
    for source, entries in summary_by_source.items():
        for e in entries:
            act = create_action_plan(e)
            actionable.append({
                'source': source,
                'timestamp': e['timestamp'],
                'level': e['level'],
                'message': e['message'],
                'suggested_action': act
            })
    return actionable

def create_action_plan(log_entry):
    """
    Determine an actionable next step based on the content of the log entry message.
    """
    msg = log_entry['message'].lower()
    # Enhance to include row/file context if detectable
    if 'not exist' in msg or 'no such file' in msg or 'missing' in msg:
        return 'Verify input path and existence. Ensure expected data files exist before running pipeline.'
    elif 'not a csv' in msg or 'failed to load' in msg or 'empty file' in msg:
        return 'Review input file integrity or format. Ensure CSV is not empty/corrupted.'
    elif 'nan' in msg or 'inf' in msg:
        # Try to extract column/row context (fix: augment message if found)
        import re
        row_match = re.search(r'row (\d+)', msg)
        col_match = re.search(r'field ['"]([a-zA-Z0-9_]+)['"]', msg)
        if row_match or col_match:
            extra = []
            if row_match:
                extra.append(f"row {row_match.group(1)}")
            if col_match:
                extra.append(f"column {col_match.group(1)}")
            return f"Add/improve missing value or inf handling in the preprocessing pipeline for {' and '.join(extra)}."
        return 'Add/improve missing value or inf handling in the preprocessing pipeline.'
    elif 'class imbalance' in msg:
        return 'Consider addressing class imbalance. Apply SMOTE, down/up-sampling, or adjust class weights.'
    elif 'target column' in msg and 'present' in msg:
        return 'Inspect data schema. Remove target column from feature set before fitting.'
    elif 'data drift' in msg:
        return 'Investigate source data distributions. Apply normalization or fix data split procedure.'
    elif 'permission' in msg and 'set' in msg:
        return 'Check file system permissions and rerun as a user with proper privileges.'
    elif 'could not' in msg or 'critical failure' in msg or 'fatal' in msg:
        # Recommend reviewing traceback if possible (fix)
        return 'Check full traceback for root cause. Address error per stack trace.'
    elif 'invalid json' in msg:
        return 'Rectify command args: pass a proper JSON string for configuration.'
    elif 'unexpected value' in msg and 'row' in msg:
        # User context wants a more row/column specific action
        # Try to extract row/field info
        row_match = re.search(r'row (\d+)', msg)
        col_match = re.search(r'field ['"]([a-zA-Z0-9_]+)['"]', msg)
        extra = []
        if row_match:
            extra.append(f"row {row_match.group(1)}")
        if col_match:
            extra.append(f"column {col_match.group(1)}")
        return f"Review unexpected sensor value for {' and '.join(extra) if extra else 'data'}. Apply a data cleaning rule or filter such outliers in preprocessing."
    else:
        return 'Review pipeline module and logs for details. Apply debug or rerun with verbose logging.'

def dump_log_report(actionable, output_path):
    """
    Write the actionable report (list of dicts) to output_path as JSON.
    """
    with open(output_path, 'w') as f:
        json.dump(actionable, f, indent=2)
    return output_path

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Parse and summarize all errors and warnings in pipeline logs.')
    parser.add_argument('--log_dir', required=True, help='Directory containing pipeline log files')
    parser.add_argument('--output', required=True, help='Output path for the summarized actionable report (JSON)')
    args = parser.parse_args()
    # Parse logs
    log_entries = parse_all_logs(args.log_dir)
    # Only errors/warnings
    errwarn_entries = filter_logs(log_entries, levels=['ERROR', 'WARNING', 'CRITICAL'])
    actionable_summary = summarize_errors_and_warnings(errwarn_entries)
    dump_log_report(actionable_summary, args.output)
    print(f"Actionable log summary written to {args.output}. Found {len(actionable_summary)} error/warning events.")

if __name__ == "__main__":
    main()
