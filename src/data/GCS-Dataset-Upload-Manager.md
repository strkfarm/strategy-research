# Google Cloud Storage Dataset Manager

This Python module provides a class for managing datasets in Google Cloud Storage (GCS). It includes functionalities for uploading, reading, updating, deleting, and listing datasets in various formats like **JSON**, **CSV**, and **Pickle**.

## Features

- **Upload Dataset**: Upload data in various formats (CSV, JSON, Pickle) to Google Cloud Storage.
- **Read Dataset**: Read and download datasets from Google Cloud Storage.
- **Update Dataset**: Update (overwrite) an existing dataset in the cloud.
- **Delete Dataset**: Delete a dataset from the cloud.
- **List Datasets**: List all datasets stored in a bucket with optional filtering by prefix.

## Prerequisites

Before you start using this module, ensure you have the following:

1. **Google Cloud Account**: You must have a Google Cloud project and a GCS bucket to store your datasets.
2. **Google Cloud SDK**: Install and configure the Google Cloud SDK, including setting up authentication via service accounts.
3. **Required Python Packages**:
   - `google-cloud-storage`: Library to interact with Google Cloud Storage.
   - `pandas`: For handling and manipulating datasets (especially for CSV handling).

### Installation

1. **Install Python dependencies**:
   - You can install the necessary libraries using pip. Run the following command:

     ```bash
     pip install google-cloud-storage pandas
     ```

2. **Set up Google Cloud Credentials**:
   - You need to authenticate your Google Cloud access by setting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable. You can do this by running:

     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"
     ```

   - Make sure to replace `/path/to/your/service-account-file.json` with the path to your service account JSON file.

## Module Overview

The **`Datasets`** class includes methods for uploading, reading, updating, deleting, and listing datasets in your Google Cloud Storage bucket.

### Constants

- `DEFAULT_PROJECT_ID`: The Google Cloud project ID (default: `"strkfarm"`).
- `DEFAULT_BUCKET_NAME`: The GCS bucket name (default: `"strkfarm"`).

### Class: `Datasets`

This class allows you to interact with your GCS bucket and perform dataset management tasks.

#### Methods:

1. **`__init__(self, project_id: str, bucket_name: str)`**:
   - Initializes the `Datasets` class with Google Cloud credentials and bucket information.

2. **`upload_dataset(self, data, filename, data_format='json')`**:
   - Uploads a dataset to Google Cloud Storage in the specified format.
   - Supported formats: `json`, `csv`, `pickle`.

3. **`read_dataset(self, filename, data_format='json', as_dataframe=False)`**:
   - Reads a dataset from Google Cloud Storage in the specified format and returns the data.
   - Returns a pandas DataFrame if the data is in CSV format and `as_dataframe=True`.

4. **`update_dataset(self, data, filename, data_format='json')`**:
   - Updates (overwrites) an existing dataset in Google Cloud Storage.

5. **`delete_dataset(self, filename)`**:
   - Deletes a dataset from Google Cloud Storage.

6. **`list_datasets(self, prefix=None)`**:
   - Lists all datasets in the GCS bucket, optionally filtering by prefix.

---

## Example Usage

### Initializing the Datasets Class

```python
from dataset_manager import Datasets

# Initialize with your project ID and bucket name (or use defaults)
datasets = Datasets(project_id="your-project-id", bucket_name="your-bucket-name")
