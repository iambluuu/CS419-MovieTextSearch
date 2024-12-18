import pandas as pd
import os
import logging

from pymongo import MongoClient
from src.utils.config import config
from src.utils import logconfig


log = logging.getLogger(name="MovieApp")
logconfig.setup_logging()



def load_data_into_db(data_path: str) -> None:
    """Load the dataset into MongoDB.

    Args:
        data_path (str): The path to the dataset.

    Returns:
        None

    Raises:
        FileNotFoundError: If the dataset is not found at the specified path.
    """

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}")

     
    # Read the dataset
    log.info("Loading dataset...")
    try:
        data_frame = pd.read_excel(data_path)
        log.info(f"Dataset loaded successfully with {data_frame.shape[0]} rows and {data_frame.shape[1]} columns.")
    except Exception as e:
        log.error(f"Failed to load dataset at data path {data_path}: {str(e)}")
        raise e


    # Connect to MongoDB
    print("Connecting to MongoDB...")
    try:
        mongodb_uri = config["MONGODB_URI"]
        client = MongoClient(mongodb_uri)
        db = client["CS419-MovieTextSearch"]  
        collection = db["movies"] 
        log.info("MongoDB connection established.")
    except Exception as e:
        log.error(f"Failed to connect to MongoDB: {str(e)}")
        raise e
    

    # If the collection already exists, don't insert the data
    if collection.estimated_document_count() > 0:
        log.info("Data already exists in MongoDB collection 'your_collection_name'. Skipping insertion.")
        client.close()
        return


    # Insert data into MongoDB
    log.info("Inserting data into MongoDB...")
    try:
        # Convert DataFrame rows to dictionaries for MongoDB insertion
        records = data_frame.to_dict(orient="records")
        collection.insert_many(records)
        log.info(f"Inserted {len(records)} records into MongoDB collection 'your_collection_name'.")
    except Exception as e:
        log.error(f"Failed to insert data into MongoDB: {str(e)}")
        raise e
    finally:
        client.close()
        log.info("MongoDB connection closed.")



if __name__ == "__main__":
    # Path to the dataset (update this path as needed)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset_path = os.path.join(base_dir, "data", "merged_movies_dataset.xlsx")
    try:
        load_data_into_db(dataset_path)
    except Exception as e:
        log.error(f"Error occurred: {str(e)}")
        raise e