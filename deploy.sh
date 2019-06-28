#!/bin/sh

##############################################################################################################
# Configurable deploment script.
#
# Env Vars Expected:
#     GOOGLE_PROJECT_NAME:                 	Google project name.
#     CLOUD_FUNCTION_NAME:		      		The name of the function to use from main.py; will use the same name on Cloud Functions.
#	  GCS_BUCKET_NAME:    					Name of the Google Cloud Storage bucket.
#	  MEMORY:								Max memory to be allocated. Default 256MB; Limit of 2048MB
# 	  TIMEOUT:								Number of seconds before function call will time out. Default 60 seconds. Limit of 540 seconds.
# Notes:
# - This will also set the gcloud project.
# - Python 3.7 is the only Python choice at the moment.
# - Add --source to specify the source of the deployment
# - Having --retry keeps retrying in case of failure.
##############################################################################################################

GOOGLE_PROJECT_NAME=your_google_project
CLOUD_FUNCTION_NAME=from_gcs_trigger_to_bq
GCS_BUCKET_NAME=your_google_bucket

MEMORY=256MB
TIMEOUT=60s

DATASET_ID=your_dataset
TABLE_ID=your_table

gcloud config set project ${GOOGLE_PROJECT_NAME}

gcloud functions deploy ${CLOUD_FUNCTION_NAME} \
--memory ${MEMORY} \
--retry \
--runtime python37 \
--timeout ${TIMEOUT} \
--trigger-resource ${GCS_BUCKET_NAME} \
--trigger-event google.storage.object.finalize \
--update-env-vars DATASET_ID=${DATASET_ID},TABLE_ID=${TABLE_ID}  # add or update env vars; these are scoped to the function and can be os.environ.get