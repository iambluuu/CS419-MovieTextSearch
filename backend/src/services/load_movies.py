import ast
import os
from typing import Callable
import pandas as pd
import hashlib

from elasticsearch import helpers
from ..services.elastic import es
from ..utils.config import config

from sentence_transformers import SentenceTransformer
import torch


HASH_FILE = "./src/data/hash.txt"
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")
model = SentenceTransformer("all-mpnet-base-v2")

def format_data(df: pd.DataFrame) -> pd.DataFrame:
    """This is for formatting the data before loading it to Elasticsearch.

    Used for "movies.csv" file.
    """
    df["genres"] = df["genres"].apply(lambda x: x.split(" "))
    df["keywords"] = df["keywords"].apply(lambda x: x.split(" "))
    df["production_companies"] = df["production_companies"].apply(ast.literal_eval)
    df["production_countries"] = df["production_countries"].apply(ast.literal_eval)
    df["spoken_languages"] = df["spoken_languages"].apply(ast.literal_eval)
    df["cast"] = df["cast"].apply(lambda x: x.split(" "))
    df["crew"] = df["crew"].apply(ast.literal_eval)

    return df

def encode_data(text, index = None):
    if index is not None:
        print(f"Encoding text at index {index}")
    try:
        if isinstance(text, str):
            return model.encode(text)
        return None
    except Exception as e:
        print(f"Failed to encode text: {e}")
        return None
    

def format_data2(df: pd.DataFrame) -> pd.DataFrame:
    df["genres"] = df["genres"].apply(lambda x: x.split(", "))
    df["production_companies"] = df["production_companies"].apply(
        lambda x: x.split(", ")
    )
    df["production_countries"] = df["production_countries"].apply(
        lambda x: x.split(", ")
    )
    df["spoken_languages"] = df["spoken_languages"].apply(lambda x: x.split(", "))
    df["cast"] = df["cast"].apply(lambda x: x.split(", "))
    df["director"] = df["director"].apply(lambda x: x.split(", "))

    def calculate_popularity_score(
        df: pd.DataFrame, m: float, C: float
    ) -> pd.DataFrame:
        """Calculate the popularity score based on the IMDB formula.

        Args:
            df (pd.DataFrame): DataFrame containing the movies data.
            m (float): Minimum votes required to be listed in the chart.
            C (float): Mean vote across the whole report.

        Returns:
            pd.DataFrame: DataFrame with the popularity score.
        """
        df["popularity"] = (
            (df["vote_count"] * df["vote_average"])
            + (df["imdb_votes"] * df["imdb_rating"])
            + (m * C)
        ) / (df["vote_count"] + df["imdb_votes"] + m)
        return df

    # Calculate the popularity score
    m = float(df["vote_count"].quantile(0.90))
    C = float(df["vote_average"].mean())
    df = calculate_popularity_score(df, m, C)

    # # Embed the synopsis
    # if df.get("plot_synopsis") is not None and not df.get("synopsis_embedding", None):
    #     df["synopsis_embedding"] = df.apply(lambda row: encode_data(row['plot_synopsis'], index=row.name), axis=1)
    
    print(df.head())

    return df


def compute_hash(file_path: str) -> str:
    """Compute the hash of the file.

    This function computes the hash of the file based on the file size and the last modified time.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Hash of the file.
    """
    file_stat = os.stat(file_path)
    metadata = (file_stat.st_size, file_stat.st_mtime)

    return hashlib.md5(str(metadata).encode()).hexdigest()


def load_movies_to_es(
    panda_path: str,
    index_name: str,
    format_column: Callable | None = format_data2,
    mapping: dict | None = None,
) -> None:
    """Load movies data to Elasticsearch.

    Args:
        panda_path (str): Path to the Pandas readable file.
        index_name (str): Name of the Elasticsearch index.
        format_column (Callable, optional): Function to format columns. Defaults to None.
        mapping (dict, optional): Mapping for the Elasticsearch index. Defaults to None.

    Returns:
        None

    Raises:
        FileNotFoundError: If the CSV file is not found.
    """

    if not os.path.exists(panda_path):
        raise FileNotFoundError(f"File not found: {panda_path}")

    # Check the extension of the file
    if not (panda_path.endswith(".csv") or panda_path.endswith(".xlsx")):
        raise ValueError("File format not supported.")

    new_hash = compute_hash(panda_path)
    old_hash = ""

    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            old_hash = f.read()

    if new_hash == old_hash:
        print("No changes in the dataset. Skipping the loading to Elasticsearch.")
        return

    try:
        # Ensures Elasticsearch index is created
        if es.indices.exists(index=index_name):
            es.indices.delete(index=index_name)
        es.indices.create(index=index_name, body=mapping)

        # Bulk upload data
        actions: list = []

        # Read the data
        if panda_path.endswith(".csv"):
            df = pd.read_csv(panda_path)
        elif panda_path.endswith(".xlsx"):
            df = pd.read_excel(panda_path, engine="openpyxl")
        else:
            raise ValueError("File format not supported.")

        # Format the columns if required
        if format_column:
            df = format_column(df)

        # write the data locally for debugging
        # df.to_excel("movies_embedded.xlsx")

        for i, row in df.iterrows():
            source_dict = row.to_dict()
            source_dict["suggest"] = {
                "input": source_dict["title"].split(" "),
                "weight": float(source_dict["popularity"]),
            }

            action = {
                "_index": index_name,
                "_id": i,
                "_source": source_dict,
            }
            actions.append(action)

        # success, errors = helpers.bulk(es, actions, index=index_name, raise_on_error=False)
        # print(f'Success: {success} errors: {errors}')

        # Preview the mapping
        template = es.indices.get_mapping(index=index_name)
        print(template)
    except Exception as e:
        raise e

    # Save the hash of the file
    with open(HASH_FILE, "w") as f:
        f.write(new_hash)


if __name__ == "__main__":
    load_movies_to_es(config["EMBEDDED_DATA_PATH"], "movies", format_data)
