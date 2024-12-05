import os
import pandas as pd


def preprocess_data(data_path: str) -> None:
    """Preprocess the dataset.

    Prepares the dataset for indexing by filling missing values and saving the cleaned dataset.
    May include additional preprocessing steps in the future.

    Args:
        data_path (str): The path to the dataset.

    Returns:
        None

    Raises:
        FileNotFoundError: If the dataset is not found at the specified path.
    """

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}")

    # Load the dataset
    df = pd.read_csv(data_path)

    # Clean the dataset
    df.fillna(
        {
            "budget": 0,
            "genres": "Unknowns",
            "homepage": "Unknown",
            "keywords": "",
            "original_language": "Unknown",
            "original_title": "",
            "overview": "",
            "popularity": 0.0,
            "production_companies": "",
            "production_countries": "",
            "release_date": "",
            "revenue": 0,
            "runtime": 0,
            "spoken_languages": "",
            "status": "Unknown",
            "tagline": "Unknown",
            "title": "",
            "vote_average": 0.0,
            "vote_count": 0,
            "cast": "",
            "crew": "",
            "director": "",
        },
        inplace=True,
    )

    # Save the cleaned dataset
    df.to_csv("src/data/cleaned.csv", index=False)
