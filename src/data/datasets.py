import functions_framework # type: ignore
import logging
import os
import traceback
import re

from google.cloud import bigquery
from google.cloud import storage

import yaml # type: ignore

# Load schema configuration from a YAML file
with open("./schemas.yaml") as schema_file:
    config = yaml.safe_load(schema_file)

# Constants
PROJECT_ID = os.getenv('strkfarm')  # Environment variable for project ID
BQ_DATASET = 'staging'
CLOUD_STORAGE_CLIENT = storage.Client()
BIGQUERY_CLIENT = bigquery.Client()
JOB_CONFIG = bigquery.LoadJobConfig()

def streaming(data):
    """
    Process a file uploaded to a Cloud Storage bucket and stream its data to BigQuery.

    Args:
        data (dict): Event data containing bucket name, file name, and time created.
    """
    bucket_name = data['bucket'] 
    print("Bucket name:", bucket_name)
    file_name = data['name']   
    print("File name:", file_name)  
    time_created = data['timeCreated']
    print("Time Created:", time_created) 

    try:
        for table in config:
            table_name = table.get('name')
            if re.search(table_name.replace('_', '-'), file_name) or re.search(table_name, file_name):
                table_schema = table.get('schema')
                _check_if_table_exists(table_name, table_schema)
                table_format = table.get('format')

                if table_format == 'NEWLINE_DELIMITED_JSON':
                    _load_table_from_uri(bucket_name, file_name, table_schema, table_name)
    except Exception:
        print('Error streaming file. Cause: %s' % (traceback.format_exc()))

def _check_if_table_exists(table_name, table_schema):
    """
    Check if a BigQuery table exists; if not, create it.

    Args:
        table_name (str): Name of the table to check or create.
        table_schema (list): Schema of the table defined in YAML.
    """
    table_id = BIGQUERY_CLIENT.dataset(BQ_DATASET).table(table_name)

    try:
        BIGQUERY_CLIENT.get_table(table_id)
    except Exception:
        logging.warning('Creating table: %s' % table_name)
        schema = create_schema_from_yaml(table_schema)
        table = bigquery.Table(table_id, schema=schema)
        table = BIGQUERY_CLIENT.create_table(table)
        print("Created table {}.{}.{}".format(table.project, table.dataset_id, table.table_id))

def _load_table_from_uri(bucket_name, file_name, table_schema, table_name):
    """
    Load data from a Cloud Storage file into a BigQuery table.

    Args:
        bucket_name (str): Name of the Cloud Storage bucket.
        file_name (str): Name of the file in the bucket.
        table_schema (list): Schema of the BigQuery table.
        table_name (str): Name of the BigQuery table.
    """
    uri = f'gs://{bucket_name}/{file_name}'
    table_id = BIGQUERY_CLIENT.dataset(BQ_DATASET).table(table_name)

    schema = create_schema_from_yaml(table_schema) 
    JOB_CONFIG.schema = schema
    JOB_CONFIG.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
    JOB_CONFIG.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

    load_job = BIGQUERY_CLIENT.load_table_from_uri(uri, table_id, job_config=JOB_CONFIG) 
    load_job.result()
    print("Job finished.")

def create_schema_from_yaml(table_schema):
    """
    Create a BigQuery schema from YAML configuration.

    Args:
        table_schema (list): Schema configuration in YAML format.

    Returns:
        list: List of BigQuery SchemaField objects.
    """
    schema = []
    for column in table_schema:
        schema_field = bigquery.SchemaField(column['name'], column['type'], column['mode'])
        schema.append(schema_field)

        if column['type'] == 'RECORD':
            schema_field._fields = create_schema_from_yaml(column['fields'])
    return schema

@functions_framework.cloud_event
def hello_gcs(cloud_event):
    """
    Triggered by a change in a Cloud Storage bucket.

    Args:
        cloud_event (CloudEvent): Event data for the trigger.
    """
    data = cloud_event.data

    print(f"Event ID: {cloud_event['id']}")
    print(f"Event type: {cloud_event['type']}")
    print(f"Bucket: {data['bucket']}")
    print(f"File: {data['name']}")
    print(f"Metageneration: {data['metageneration']}")
    print(f"Created: {data['timeCreated']}")
    print(f"Updated: {data['updated']}")

    streaming(data)