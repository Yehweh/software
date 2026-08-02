import pandas as pd

def load_data():

    file_path = "data/software_defect_prediction_dataset.csv"

    data = pd.read_csv(file_path)

    print("Dataset Loaded Successfully!\n")

    print(data.head())

    print("\nColumn Names:")
    print(data.columns.tolist())

    return data