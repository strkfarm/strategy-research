import logging  # For logging error messages and warnings
import os  # For environment variables and file path manipulation
import traceback  # For capturing detailed stack traces in case of an error
import re  # For regular expressions to match table names in filenames

from google.cloud import bigquery  # Google Cloud BigQuery API
from google.cloud import storage  # Google Cloud Storage API

import yaml  # For parsing YAML configuration files

# Open the 'schemas.yaml' file and load its contents into the 'config' variable
with open("./schemas.yaml") as schema_file:
     config = yaml.safe_load(schema_file, Loader=yaml.Loader)

# Environment variables
PROJECT_ID = os.getenv('strkfarm')  # Retrieve the Google Cloud project ID from the environment
BQ_DATASET = 'staging'  # The BigQuery dataset name where tables will be loaded
CS = storage.Client()  # Google Cloud Storage client for interacting with GCS
BQ = bigquery.Client()  # Google Cloud BigQuery client for querying and managing BigQuery tables
job_config = bigquery.LoadJobConfig()  # Configuration for loading data into BigQuery


def streaming(data):
     """
     Function that processes a file event and loads the data into BigQuery.
     Triggered when a file is uploaded to a Google Cloud Storage bucket.
     """
     bucketname = data['bucket']  # Get the name of the GCS bucket
     print("Bucket name", bucketname)
     filename = data['name']  # Get the name of the file uploaded
     print("File name", filename)
     timeCreated = data['timeCreated']  # Timestamp of when the file was created
     print("Time Created", timeCreated)

     try:
          # Loop through each table configuration in the YAML file
          for table in config:
               tableName = table.get('name')  # Get the table name from the config
               
               # Check if the file name matches the table name (with a regex check)
               if re.search(tableName.replace('_', '-'), filename) or re.search(tableName, filename):
                    tableSchema = table.get('schema')  # Get the table schema from the config
                    _check_if_table_exists(tableName, tableSchema)  # Check if the table exists in BigQuery
                    tableFormat = table.get('format')  # Get the table format from the config
                    if tableFormat == 'NEWLINE_DELIMITED_JSON':  # If the file format is JSON
                         _load_table_from_uri(data['bucket'], data['name'], tableSchema, tableName)  # Load data into BigQuery
     except Exception:
          # Log any errors that occur during streaming processing
          print('Error streaming file. Cause: %s' % (traceback.format_exc()))

def _check_if_table_exists(tableName, tableSchema):
     """
     Checks if the table exists in BigQuery. If not, creates a new table using the schema.
     """
     table_id = BQ.dataset(BQ_DATASET).table(tableName)  # Get the table ID for the dataset

     try:
          # Try to get the table from BigQuery
          BQ.get_table(table_id)
     except Exception:
          # If the table does not exist, create a new one
          logging.warn('Creating table: %s' % (tableName))
          schema = create_schema_from_yaml(tableSchema)  # Convert schema from YAML to BigQuery schema
          table = bigquery.Table(table_id, schema=schema)  # Create a new BigQuery table object
          table = BQ.create_table(table)  # Create the table in BigQuery
          print("Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))  # Log the table creation

def _load_table_from_uri(bucket_name, file_name, tableSchema, tableName):
     """
     Loads data from a file in a GCS bucket into a BigQuery table.
     """
     uri = 'gs://%s/%s' % (bucket_name, file_name)  # GCS URI for the file
     table_id = BQ.dataset(BQ_DATASET).table(tableName)  # Get the BigQuery table ID

     schema = create_schema_from_yaml(tableSchema)  # Convert schema from YAML to BigQuery schema
     print(schema)
     job_config.schema = schema  # Set the schema in the job configuration

     # Specify the source format for the file and the write disposition (append data)
     job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
     job_config.write_disposition = 'WRITE_APPEND'

     # Load the file from GCS into BigQuery
     load_job = BQ.load_table_from_uri(
     uri,
     table_id,
     job_config=job_config,
     ) 

     load_job.result()  # Wait for the job to complete
     print("Job finished.")  # Log completion of the load job

def create_schema_from_yaml(table_schema):
     """
     Converts the schema defined in YAML format to a BigQuery schema.
     """
     schema = []  # Initialize an empty list to store schema fields
     for column in table_schema:
          # Create a SchemaField object for each column in the schema
          schemaField = bigquery.SchemaField(column['name'], column['type'], column['mode'])
          schema.append(schemaField)  # Add the field to the schema list

          # If the column type is 'RECORD', recursively create fields for the nested schema
          if column['type'] == 'RECORD':
               schemaField._fields = create_schema_from_yaml(column['fields'])
     return schema  # Return the generated schema list

# Call the 'streaming' function with the 'data' argument (this seems to be missing in your code)
# You need to define the 'data' dictionary elsewhere in the code to call this function correctly.
