import pytest
import pandas as pd
import os
import tempfile
from src.data import preprocessing

# Sample CSV data for testing
def dummy_csv_content():
    return """col1,col2
1,2
3,4
5,6
"""

def test_load_sensor_data_success(tmp_path):
    # Create a dummy CSV file in allowed directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    csv_file = data_dir / "sample.csv"
    csv_file.write_text(dummy_csv_content())

    # Load using the function
    df = preprocessing.load_sensor_data(str(csv_file))
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (3, 2)


def test_load_sensor_data_file_not_found(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    csv_path = os.path.join(str(data_dir), "nonexistent.csv")
    with pytest.raises(FileNotFoundError):
        preprocessing.load_sensor_data(csv_path)


def test_load_sensor_data_invalid_path(tmp_path):
    # File is not inside data/ directory
    bogus_file = tmp_path / "malicious.csv"
    bogus_file.write_text(dummy_csv_content())
    with pytest.raises(ValueError):
        preprocessing.load_sensor_data(str(bogus_file))


def test_inspect_sensor_data_shape_and_head(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    csv_file = data_dir / "sample.csv"
    csv_file.write_text(dummy_csv_content())
    df = preprocessing.load_sensor_data(str(csv_file))
    shape, head = preprocessing.inspect_sensor_data(df)
    assert shape == (3, 2)
    assert head.equals(df.head(5))


def test_inspect_sensor_data_typeerror():
    with pytest.raises(TypeError):
        preprocessing.inspect_sensor_data([1, 2, 3])
