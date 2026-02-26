import pandas as pd
import os
import logging
import re

# Set up logging to record information and errors
def setup_logging():
    """Set up the logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[logging.StreamHandler()]
    )

# Helper function to validate file paths securely
def is_valid_path(path):
    """
    Validate the given file path to prevent path traversal and unauthorized access.
    Only allows paths inside the 'data/' directory with CSV extension.
    """
    if not isinstance(path, str):
        return False
    # Only allow files inside the data directory and with .csv extension
    normalized_path = os.path.normpath(path)
    if not normalized_path.startswith('data' + os.sep):
        return False
    if not re.match(r'^data\%s[a-zA-Z0-9_\-]+\.csv$' % re.escape(os.sep), normalized_path):
        return False
    return True

def load_sensor_data(csv_path):
    """
    Load manufacturing sensor data from a CSV file, with robust error handling.

    Args:
        csv_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded sensor data as a pandas DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If file permissions are insufficient.
        pd.errors.ParserError: If CSV parsing fails.
        ValueError: If input file path is invalid.
    """
    setup_logging()
    # Validate input path securely
    if not is_valid_path(csv_path):
        logging.error(f"Invalid or potentially unsafe file path: {csv_path}")
        raise ValueError(f"Invalid or potentially unsafe file path: {csv_path}")
    if not os.path.exists(csv_path):
        logging.error(f"Dataset not found at given path: {csv_path}")
        raise FileNotFoundError(f"Dataset not found at given path: {csv_path}")
    try:
        # Attempt to read CSV file
        data = pd.read_csv(csv_path)
        logging.info(f"Successfully loaded data from {csv_path}, shape: {data.shape}")
        return data
    except pd.errors.ParserError as pe:
        logging.error(f"Parsing error reading file {csv_path}: {pe}")
        raise
    except PermissionError as perm_err:
        logging.error(f"Permission denied for file {csv_path}: {perm_err}")
        raise
    except Exception as ex:
        logging.error(f"An unexpected error occurred while loading the file {csv_path}: {ex}")
        raise

def inspect_sensor_data(data):
    """
    Inspect the structure of manufacturing sensor data.

    Args:
        data (pd.DataFrame): The sensor data.

    Returns:
        tuple: (shape of the data, first 5 rows of the data as DataFrame)
    """
    if not isinstance(data, pd.DataFrame):
        logging.error("Input data must be a pandas DataFrame.")
        raise TypeError("Input data must be a pandas DataFrame.")
    shape = data.shape  # Tuple (rows, columns)
    head = data.head(5) # First 5 rows for preview
    logging.info(f"Data shape: {shape}")
    return shape, head

if __name__ == '__main__':
    import os
    from dotenv import load_dotenv

    setup_logging()

    # Load environment variables from .env file if exists
    load_dotenv()
    # Fetch path from environment variables (default to 'data/manufacturing_sensor_data.csv')
    csv_path = os.getenv('SENSOR_CSV_PATH', 'data/manufacturing_sensor_data.csv')
    
    try:
        # Load and inspect the data
        data = load_sensor_data(csv_path)
        shape, head = inspect_sensor_data(data)
        print(f'Dataset shape: {shape}')
        print('First five rows:')
        print(head)
    except Exception as e:
        print(f'Error: {str(e)}')
