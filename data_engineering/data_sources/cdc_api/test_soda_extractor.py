import pandas as pd
from pathlib import Path
from data_engineering.data_sources.cdc_api.soda_extractor import CDCSodaExtractor

def test_save_to_csv(tmp_path: Path):
    """Test saving a DataFrame to a CSV file."""
    extractor = CDCSodaExtractor()

    # Create a dummy DataFrame
    df = pd.DataFrame({
        "indicator": ["Synthetic opioids, excl. methadone (T40.4)", "Synthetic opioids, excl. methadone (T40.4)"],
        "year": [2021, 2022],
        "deaths": [1000, 1200]
    })

    # Define a test output path inside a non-existent subdirectory
    # to test parent directory creation
    output_path = tmp_path / "test_dir" / "test_output.csv"

    # Save to CSV
    extractor.save_to_csv(df, output_path)

    # Assert the file was created
    assert output_path.exists()
    assert output_path.is_file()

    # Read back the saved CSV and verify its contents
    saved_df = pd.read_csv(output_path)

    # Verify shape and columns
    assert len(saved_df) == 2
    assert list(saved_df.columns) == ["indicator", "year", "deaths"]

    # Verify data types and values
    assert saved_df["year"].tolist() == [2021, 2022]
    assert saved_df["deaths"].tolist() == [1000, 1200]
    assert saved_df["indicator"].tolist() == ["Synthetic opioids, excl. methadone (T40.4)", "Synthetic opioids, excl. methadone (T40.4)"]
