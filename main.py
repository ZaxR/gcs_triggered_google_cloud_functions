import logging
import os

import pandas as pd
from google.cloud import bigquery


# This env var is set automatically; see https://cloud.google.com/functions/docs/env-var#environment_variables_set_automatically
project_id = os.environ.get('GCP_PROJECT')


def from_gcs_trigger_to_bq(data, context, allowed_exts=("csv",)):
    """Background Cloud Function to be triggered by Cloud Storage.
       This function updates a BQ table with new files added to a GCS bucket.

    Args:
        data (dict): The Cloud Functions event payload.
        context (google.cloud.functions.Context): Metadata of triggering event.

    Returns:
        None; A BQ table as set in the environment variables is updated.

    """
    # Read environment variables and event payload data
    dataset_id = os.environ.get('DATASET_ID', 'Environment variable "DATASET_ID" is not set.')
    table_id = os.environ.get('TABLE_ID', 'Environment variable "TABLE_ID" is not set.')
    bucket_name = data['bucket']
    file_name = data['name']
    uri = f"gs://{bucket_name}/{file_name}"
    full_table_path = f"{project_id}.{dataset_id}.{table_id}"

    # Example check that the file meets requirements
    assert file_name.endswith(allowed_exts), f"Only files with a type of {allowed_exts} allowed."

    # Note: If you need to do transformations in memory, instead read the file and use a different method to post to BQ

    # Example that doesn't require reading the file into memory
    # Determine whether to insert or update depending on if the file was new or updated.
    # The only way to tell if a file is new or updated is with 'metageneration'.
    # See https://firebase.google.com/docs/functions/gcp-storage-events#access_storage_object_attributes
    if data['metageneration'] == 1:  # 1 indicates a new object
        # Inserts rows for new files
        client = bigquery.Client()
        dataset_ref = client.dataset(dataset_id, project=project_id)
        # See python docs: https://googleapis.github.io/google-cloud-python/latest/bigquery/generated/google.cloud.bigquery.job.LoadJobConfig.html
        # configuration options: https://cloud.google.com/bigquery/docs/reference/rest/v2/JobConfiguration#jobconfigurationload
        job_config = bigquery.LoadJobConfig()
        job_config.autodetect = True
        job_config.write_disposition = 'WRITE_APPEND'
        client.load_table_from_uri(uri, full_table_path, job_config=job_config)
    else:
        # Updates existing rows via DML for updated files
        logging.info("This would update.")
