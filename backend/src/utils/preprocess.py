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
    """

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    # Load the dataset
    if sample > 0:
        df = (
            pd.read_csv(data_path)
            .sample(sample, random_state=42)
            .reset_index(drop=True)
        )
    else:
        df = pd.read_csv(data_path)

    # Clean the dataset
    df.fillna(
        {
            "budget": 0,
            "genres": "Unknown",
            "homepage": "Unknown",
            "keywords": "Unknown",
            "original_language": "Unknown",
            "original_title": "Unknown",
            "overview": "Unknown",
            "popularity": 0.0,
            "production_companies": "[]",
            "production_countries": "[]",
            "release_date": "01/01/1970",
            "revenue": 0,
            "runtime": 0,
            "spoken_languages": "[]",
            "status": "Unknown",
            "tagline": "Unknown",
            "title": "Unknown",
            "vote_average": 0.0,
            "vote_count": 0,
            "cast": "Unknown",
            "crew": "[]",
            "director": "Unknown",
        },
        inplace=True,
    )

    # Save the cleaned dataset
    df.to_csv(save_path, index=False)
