import os
import pandas as pd


def preprocess_data(data_path: str, save_path: str, sample: int = 500) -> None:
    """Preprocess the dataset.

    Prepares the dataset for indexing by filling missing values and saving the cleaned dataset.
    May include additional preprocessing steps in the future.

    Args:
        data_path (str): The path to the dataset.
        save_path (str): The path to save the cleaned dataset.
        sample (int): The number of rows to sample from the dataset. Defaults to 500.

    Returns:
        None

    Raises:
        FileNotFoundError: If the dataset is not found at the specified path.
        ValueError: If the file format is not supported.
    """

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    # Load the dataset
    if data_path.endswith(".csv"):
        df = pd.read_csv(data_path, encoding="utf-8")

        if sample >= 0:
            df = df.sample(sample, random_state=42).reset_index(drop=True)
    elif data_path.endswith(".xlsx"):
        df = pd.read_excel(data_path)

        if sample >= 0:
            df = df.sample(sample, random_state=42).reset_index(drop=True)
    else:
        raise ValueError("File format not supported.")

    # Clean the dataset
    ## Fill missing values
    df.fillna(
        {
            "id": -1,
            "title": "Unknown",
            "vote_average": 0.0,
            "vote_count": 0,
            "status": "Unknown",
            "release_date": "Unknown",
            "revenue": 0,
            "runtime": 0,
            "budget": 0,
            "original_language": "Unknown",
            "poster_path": "Unknown",
            "genres": "Unknown",
            "production_companies": "Unknown",
            "production_countries": "Unknown",
            "spoken_languages": "Unknown",
            "cast": "Unknown",
            "director": "Unknown",
            "imdb_rating": 0.0,
            "imdb_votes": 0,
            "plot_synopsis": "Unknown",
        },
        inplace=True,
    )

    # Save the cleaned dataset
    if save_path.endswith(".csv"):
        df.to_csv(save_path, index=False)
    elif save_path.endswith(".xlsx"):
        df.to_excel(save_path, index=False)
    else:
        raise ValueError("File format not supported.")
