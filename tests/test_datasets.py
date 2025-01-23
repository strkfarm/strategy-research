import pytest
import pickle
from unittest.mock import MagicMock, patch
from src.data.datasets2 import Datasets
 

@patch("datasets2.storage.Client")
def test_init(mock_storage_client):
    """
    Test initialization of Datasets class.
    Verifies correct project ID, bucket name, and bucket reload.
    """
    # Create mock storage client instances
    mock_client_instance = MagicMock()
    mock_bucket = MagicMock()

    # Configure mock storage client to return predefined instances
    mock_storage_client.return_value = mock_client_instance
    mock_client_instance.bucket.return_value = mock_bucket

    # Create Datasets instance
    datasets = Datasets()

    # Assertions to validate initialization
    assert datasets.project_id == "strkfarm"
    assert datasets.bucket_name == "strkfarm"
    mock_client_instance.bucket.assert_called_once_with("strkfarm")
    mock_bucket.reload.assert_called_once()


@patch("datasets2.storage.Client")
def test_upload_dataset_json(mock_storage_client):
    """
    Test uploading JSON dataset to Google Cloud Storage.
    Verifies correct JSON serialization and upload.
    """
    # Create mock storage client instances
    mock_client_instance = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # Configure mock storage client to return predefined instances
    mock_storage_client.return_value = mock_client_instance
    mock_client_instance.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # Create Datasets instance
    datasets = Datasets()

    # Upload sample JSON dataset
    datasets.upload_dataset({"key": "value"}, "test.json", data_format="json")

    # Verify upload was called with correct parameters
    mock_blob.upload_from_string.assert_called_once_with(
        b'{"key": "value"}', content_type="application/json"
    )


@patch("datasets2.storage.Client")
def test_upload_dataset_csv(mock_storage_client):
    """
    Test uploading CSV dataset to Google Cloud Storage.
    Verifies correct CSV formatting and upload.
    """
    # Create mock storage client instances
    mock_client_instance = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # Configure mock storage client to return predefined instances
    mock_storage_client.return_value = mock_client_instance
    mock_client_instance.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # Create Datasets instance
    datasets = Datasets()

    # Upload sample CSV dataset
    datasets.upload_dataset(
        [["col1", "col2"], ["val1", "val2"]],
        "test.csv",
        data_format="csv",
    )

    # Verify upload was called with correct parameters
    mock_blob.upload_from_string.assert_called_once_with(
        b"col1,col2\r\nval1,val2\r\n", content_type="text/csv"
    )


@patch("datasets2.storage.Client")
def test_read_dataset_json(mock_storage_client):
    """
    Test reading JSON dataset from Google Cloud Storage.
    Verifies correct JSON deserialization.
    """
    # Create mock storage client instances
    mock_client_instance = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # Configure mock storage client and download behavior
    mock_storage_client.return_value = mock_client_instance
    mock_client_instance.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.download_as_bytes.return_value = b'{"key": "value"}'

    # Create Datasets instance
    datasets = Datasets()

    # Read dataset and verify content
    data = datasets.read_dataset("test.json", data_format="json")

    assert data == {"key": "value"}
    mock_blob.download_as_bytes.assert_called_once()


@patch("datasets2.storage.Client")
def test_upload_dataset_pickle(mock_storage_client):
    """
    Test uploading Pickle dataset to Google Cloud Storage.
    Verifies correct pickle serialization and upload.
    """
    # Create mock storage client instances
    mock_client_instance = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # Configure mock storage client to return predefined instances
    mock_storage_client.return_value = mock_client_instance
    mock_client_instance.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # Create Datasets instance
    datasets = Datasets()

    # Prepare sample data for pickle upload
    sample_data = {"key": "value"}
    datasets.upload_dataset(sample_data, "test.pkl", data_format="pickle")

    # Verify pickle upload
    mock_blob.upload_from_string.assert_called_once()
    uploaded_data = mock_blob.upload_from_string.call_args[0][0]
    assert pickle.loads(uploaded_data) == sample_data
    assert mock_blob.upload_from_string.call_args[1]["content_type"] == "application/octet-stream"


@patch("datasets2.storage.Client")
def test_read_dataset_pickle(mock_storage_client):
    """
    Test reading Pickle dataset from Google Cloud Storage.
    Verifies correct pickle deserialization.
    """
    # Create mock storage client instances
    mock_client_instance = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # Configure mock storage client to return predefined instances
    mock_storage_client.return_value = mock_client_instance
    mock_client_instance.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # Prepare sample data for pickle download
    sample_data = {"key": "value"}
    mock_blob.download_as_bytes.return_value = pickle.dumps(sample_data)

    # Create Datasets instance
    datasets = Datasets()

    # Read pickle dataset and verify content
    data = datasets.read_dataset("test.pkl", data_format="pickle")

    # Assertions
    assert data == sample_data  # Check if data is correctly deserialized
    mock_blob.download_as_bytes.assert_called_once()  # Ensure download was called once



@patch("datasets2.storage.Client")
def test_list_datasets(mock_storage_client):
    """
    Test listing datasets from Google Cloud Storage.
    Verifies retrieval of files with different extensions.
    """
    # Create mock storage client instances
    mock_client_instance = MagicMock()
    mock_bucket = MagicMock()
    
    # Create mock blobs with different file extensions
    mock_blob1 = MagicMock()
    mock_blob2 = MagicMock()
    mock_blob3 = MagicMock()

    # Set names for different file types
    mock_blob1.name = "file1.json"
    mock_blob2.name = "file2.csv"
    mock_blob3.name = "file3.pkl"  # Added pickle file

    # Configure mock storage client to return the blobs
    mock_storage_client.return_value = mock_client_instance
    mock_client_instance.bucket.return_value = mock_bucket
    mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2, mock_blob3]

    # Create Datasets instance
    datasets = Datasets()

    # Call list_datasets method
    files = datasets.list_datasets()

    # Assert that all files are returned, including the new pickle file
    assert files == ["file1.json", "file2.csv", "file3.pkl"]
    
    # Verify that list_blobs was called once
    mock_bucket.list_blobs.assert_called_once()


@patch("datasets2.storage.Client")
def test_delete_dataset(mock_storage_client):
    """
    Test deleting a dataset from Google Cloud Storage.
    Verifies successful deletion and return value.
    """
    # Create mock storage client instances
    mock_client_instance = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    # Configure mock storage client to return predefined instances
    mock_storage_client.return_value = mock_client_instance
    mock_client_instance.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    # Create Datasets instance
    datasets = Datasets()

    # Attempt to delete a dataset
    result = datasets.delete_dataset("test.json")

    # Verify deletion was successful
    assert result is True
    mock_blob.delete.assert_called_once()