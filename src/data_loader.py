import os
import pandas as pd

_CACHED_DATA = None


def load_data():
    global _CACHED_DATA
    if _CACHED_DATA is not None:
        return _CACHED_DATA

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, "data", "software_defect_prediction_dataset.csv")

    data = pd.read_csv(file_path)

    print("Dataset Loaded Successfully!\n")
    print(data.head())
    print("\nColumn Names:")
    print(data.columns.tolist())

    _CACHED_DATA = data
    return data