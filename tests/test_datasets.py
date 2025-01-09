import unittest
from unittest.mock import Mock, patch

class TestETL(unittest.TestCase):

    @patch('google.cloud.bigquery.Client')
    def test_check_if_table_exists(self, mock_bigquery_client):
        mock_bigquery = mock_bigquery_client.return_value
        mock_bigquery.get_table.side_effect = Exception("Table not found")
        
        # Mock schema
        table_schema = [{"name": "column1", "type": "STRING", "mode": "NULLABLE"}]
        _check_if_table_exists("test_table", table_schema)
        
        mock_bigquery.create_table.assert_called_once()

    @patch('google.cloud.storage.Client')
    def test_load_table_from_uri(self, mock_storage_client):
        mock_storage = mock_storage_client.return_value
        # Mock inputs
        bucket_name = "test_bucket"
        file_name = "test_file.json"
        table_schema = [{"name": "column1", "type": "STRING", "mode": "NULLABLE"}]
        table_name = "test_table"

        _load_table_from_uri(bucket_name, file_name, table_schema, table_name)
        # Assert no exceptions raised (would require more detailed mocks for deeper validation)

if __name__ == '__main__':
    unittest.main()