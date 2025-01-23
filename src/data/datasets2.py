"""
Google Cloud Storage Dataset Manager Module

This module provides a class for managing datasets in Google Cloud Storage (GCS).
It supports various data formats and common operations like upload, read, update, and delete.

Constants:
    DEFAULT_PROJECT_ID: The default Google Cloud project ID
    DEFAULT_BUCKET_NAME: The default GCS bucket name

Dependencies:
    - google-cloud-storage
    - pandas
    - json
    - csv
    - pickle
    - io

Typical usage example:
    datasets = Datasets()  # Uses default constants
    datasets.upload_dataset(my_dataframe, "dataset.csv", data_format="csv")
    data = datasets.read_dataset("dataset.csv", data_format="csv")
"""

import json
import csv
import pickle
import os
from typing import Union, List, Dict, Any, Optional
from google.cloud import storage
import io
import pandas as pd

# Module-level constants
DEFAULT_PROJECT_ID: str = "strkfarm"
DEFAULT_BUCKET_NAME: str = "strkfarm"  


# Environment variable overrides for constants
PROJECT_ID = os.getenv('GCS_PROJECT_ID', DEFAULT_PROJECT_ID)
BUCKET_NAME = os.getenv('GCS_BUCKET_NAME', DEFAULT_BUCKET_NAME)

# Supported data formats
SUPPORTED_FORMATS = ["json", "csv", "pickle"]


class Datasets:
    """
    A class to manage dataset operations in Google Cloud Storage.

    This class provides methods for uploading, reading, updating, and deleting
    datasets in various formats (JSON, CSV, Pickle) to/from Google Cloud Storage.

    Attributes:
        project_id (str): The Google Cloud project ID.
        bucket_name (str): The name of the GCS bucket.
        storage_client: The Google Cloud Storage client instance.
        bucket: The GCS bucket instance.
    """

    def __init__(self, project_id: str = PROJECT_ID, bucket_name: str = BUCKET_NAME) -> None:
        """
        Initializes the Datasets class with GCS credentials and bucket information.

        Args:
            project_id: The Google Cloud project ID. Defaults to PROJECT_ID constant.
            bucket_name: The name of the GCS bucket. Defaults to BUCKET_NAME constant.

        Raises:
            Exception: If authentication fails or bucket access is denied.
        """
        self.project_id = project_id
        self.bucket_name = bucket_name

        # Initialize GCS client and bucket
        try:
            self.storage_client = storage.Client(project=self.project_id)
            self.bucket = self.storage_client.bucket(self.bucket_name)
            self.bucket.reload()  # Verify bucket exists and is accessible
            print("Successfully authenticated to Google Cloud Storage.")
        except Exception as e:
            print(f"Error authenticating or accessing bucket: {e}")
            print("Ensure GOOGLE_APPLICATION_CREDENTIALS is set correctly and the service account has permissions.")
            raise

    def upload_dataset(self, 
                      data: Union[pd.DataFrame, Dict, List, Any], 
                      filename: str, 
                      data_format: str = "json") -> None:
        """
        Uploads data to Google Cloud Storage in the specified format.

        Args:
            data: The data to upload. Can be a pandas DataFrame, dict, list, or other serializable object.
            filename: The target filename in GCS.
            data_format: The format to store the data ("json", "csv", or "pickle"). Defaults to "json".

        Raises:
            ValueError: If the data_format is not supported.
            Exception: If upload fails.
        """
        if data_format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported data format: {data_format}. Must be one of {SUPPORTED_FORMATS}")

        try:
            # Handle different input data types and formats
            if isinstance(data, pd.DataFrame):
                blob_data = data.to_csv(index=False).encode('utf-8')
                content_type = 'text/csv'
            elif data_format == "json":
                blob_data = json.dumps(data).encode('utf-8')
                content_type = 'application/json'
            elif data_format == "csv":
                blob_data = self._write_csv(data)
                content_type = 'text/csv'
            elif data_format == "pickle":
                blob_data = pickle.dumps(data)
                content_type = 'application/octet-stream'

            # Upload to GCS
            blob = self.bucket.blob(filename)
            blob.upload_from_string(blob_data, content_type=content_type)
            print(f"Dataset '{filename}' uploaded successfully.")

        except Exception as e:
            print(f"Error uploading dataset: {e}")
            raise

    def _write_csv(self, data: List[List[Any]]) -> bytes:
        """
        Helper function to convert data to CSV format.

        Args:
            data: List of rows to write to CSV.

        Returns:
            bytes: Encoded CSV data as bytes.

        Raises:
            Exception: If CSV conversion fails.
        """
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(data)
            return output.getvalue().encode('utf-8')
        except Exception as e:
            print(f"Error converting to CSV: {e}")
            raise

    def read_dataset(self, 
                    filename: str, 
                    data_format: str = "json",
                    as_dataframe: bool = False) -> Optional[Union[pd.DataFrame, Dict, List, Any]]:
        """
        Reads data from Google Cloud Storage in the specified format.

        Args:
            filename: The name of the file to read from GCS.
            data_format: The format of the stored data ("json", "csv", or "pickle"). Defaults to "json".
            as_dataframe: If True and format is "csv", returns a pandas DataFrame. Defaults to False.

        Returns:
            The loaded data in its appropriate Python format, or None if reading fails.

        Raises:
            ValueError: If the data_format is not supported.
            Exception: If read operation fails.
        """
        if data_format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported data format: {data_format}. Must be one of {SUPPORTED_FORMATS}")

        try:
            blob = self.bucket.blob(filename)
            blob_data = blob.download_as_bytes()

            if data_format == "json":
                return json.loads(blob_data.decode('utf-8'))
            elif data_format == "csv":
                csv_data = self._read_csv(blob_data)
                if as_dataframe:
                    return pd.DataFrame(csv_data[1:], columns=csv_data[0])
                return csv_data
            elif data_format == "pickle":
                return pickle.loads(blob_data)

        except Exception as e:
            print(f"Error reading {data_format} data: {e}")
            return None

    def _read_csv(self, data: bytes) -> List[List[str]]:
        """
        Helper function to read CSV data.

        Args:
            data: The CSV data as bytes.

        Returns:
            List[List[str]]: List of rows from the CSV data.

        Raises:
            Exception: If CSV parsing fails.
        """
        try:
            reader = csv.reader(io.StringIO(data.decode('utf-8')))
            return list(reader)
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            raise

    def update_dataset(self, 
                      data: Union[pd.DataFrame, Dict, List, Any], 
                      filename: str, 
                      data_format: str = "json") -> None:
        """
        Updates (overwrites) an existing dataset in Google Cloud Storage.

        This is a wrapper around upload_dataset that makes the update operation explicit.

        Args:
            data: The new data to upload.
            filename: The name of the file to update.
            data_format: The format to store the data ("json", "csv", or "pickle"). Defaults to "json".

        Raises:
            ValueError: If the data_format is not supported.
            Exception: If update fails.
        """
        self.upload_dataset(data, filename, data_format)

    def delete_dataset(self, filename: str) -> bool:
        """
        Deletes a dataset from Google Cloud Storage.

        Args:
            filename: The name of the file to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.

        Raises:
            Exception: If deletion fails.
        """
        blob = self.bucket.blob(filename)
        try:
            blob.delete()
            print(f"Dataset '{filename}' deleted successfully.")
            return True
        except Exception as e:
            print(f"Error deleting dataset: {e}")
            return False

    def list_datasets(self, prefix: str = None) -> List[str]:
        """
        Lists all datasets in the bucket, optionally filtered by prefix.

        Args:
            prefix: Optional prefix to filter the files. Defaults to None.

        Returns:
            List[str]: List of dataset filenames.
        """
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"Error listing datasets: {e}")
            return []


def main():
    """
    Main entry point for demonstration purposes.
    Shows example usage of the Datasets class.
    """
    try:
        # Initialize with default settings
        datasets = Datasets()

        # Specify the file path and target filename
        file_path = "/Users/mac/Documents/React projects/strkfarm/strategy-research/data_downloaded/events_response_positions_updated.pkl"  # Replace with the actual file path
        target_filename = "events_response_positions_updated.pkl"  # Desired name in GCS

        # Open the pickle file in binary mode and load it
        with open(file_path, "rb") as f:
            file_content = f.read()

        # Upload the file content (as a pickle object)
        datasets.upload_dataset(file_content, target_filename, data_format="pickle")

        print(f"File '{file_path}' uploaded successfully as '{target_filename}'.")

        # List all datasets
        print("\nAvailable datasets:")
        for dataset in datasets.list_datasets():
            print(f"- {dataset}")

    except Exception as e:
        print(f"An error occurred in main: {e}")
    """
    Main entry point for demonstration purposes.
    Shows example usage of the Datasets class.
    """
    try:
        # Initialize with default settings
        datasets = Datasets()
        
        # Local pickle file path (in the same directory as the script)
        local_pickle_path = "/Users/mac/Documents/React projects/strkfarm/strategy-research/data_downloaded/events_response_positions_updated.pkl"   # Replace with your pickle file name
        
        # Read the local pickle file
        with open(local_pickle_path, 'rb') as file:
            pickle_data = pickle.load(file)
            
        # Upload to GCS with the same filename (or change as needed)
        gcs_filename = os.path.basename(local_pickle_path)  # Uses same filename
        
        datasets.upload_dataset(pickle_data, gcs_filename, data_format="pickle")
        
        print(f"Successfully uploaded {local_pickle_path} to GCS")
        
        # Optional: Verify the upload by listing files
        print("\nAvailable datasets in bucket:")
        for dataset in datasets.list_datasets():
            print(f"- {dataset}")

    except FileNotFoundError as e:
        print(f"Error: Pickle file not found - {e}")
    except pickle.UnpicklingError as e:
        print(f"Error: Invalid pickle file - {e}")
    except Exception as e:
        print(f"An error occurred in main: {e}")


if __name__ == "__main__":
    main()