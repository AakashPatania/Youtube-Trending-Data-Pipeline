import json
import os
import pandas as pd
import logging
from datetime import datetime, timezone
from urllib.parse import unquote_plus
import boto3
import awswrangler as wr

# Logging 

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Config 

SILVER_BUCKET = os.environ["S3_BUCKET_SILVER"]
GLUE_DB = os.environ.get("GLUE_DB_SILVER", "yt_pipeline_silver_dev")
GLUE_TABLE = os.environ.get("GLUE_TABLE_REFERENCE", "clean_reference_data")
SNS_TOPIC = os.environ.get("SNS_ALERT_TOPIC_ARN", "")
SILVER_PATH = f"s3://{SILVER_BUCKET}/youtube/reference_data/"

s3_client = boto3.client("s3")
sns_client = boto3.client("sns")


def read_json_from_s3(bucket: str, key: str) -> dict:
    """
    This function takes a bucket name and a file path(key) and returns the file contents as
    a Python dictionary. Here we are not using awswrangler instead of boto3 because it 
    fails on the kaggle/youtube category Json
    """
    response = s3_client.get_object(Bucket=bucket, Key=key)        # download the file from s3
    content = response["Body"].read().decode("utf-8")               # reads the raw bytes and converts to a string
    return json.loads(content)                                      # converts the JSON string to a python dictionary


def validate_category_data(df):
    """
    Takes a dataframe, checks it, cleans it and returns it.
    """ 
    if df.empty:
        raise ValueError("Empty Dataframe - no category items found")
    
    required_cols = {"id", "snippet.title"}                        # Priority Columns to define 
    actual_cols = set(df.columns)
    missing = required_cols - actual_cols

    if missing:
        logger.warning(f"Missing expected columns {missing}. Available: {actual_cols}")

    # Dropping duplicate categories (same id)
    before = len(df)
    if "id" in df.columns:
        df = df.drop_duplicates(subset=["id"], keep="last")
    after = len(df)
    if before != after:   
        logger.info(f"Removed {before - after} duplicate categories")

    return df    


def send_alert(subject: str, message: str):
    """
    If something goes wrong, this sends an alert notification to an SNS topic 
    (which could be an email or slack webhook). It only runs if SNS_TOPIC is 
    configured. subject[:100] trims the subject to 100 characters because SNS 
    has a limit.
    """     
    if SNS_TOPIC: 
        sns_client.publish(TopicArn=SNS_TOPIC, Subject=subject[:100], Message=message)


def lambda_handler(event, context):
    """
    This is the entry point - AWS calls this function when the Lambda is triggered.
    Process S3 event for new JSON reference files.
    """
    
    # Handle both direct S3 events and EventBridge-wrapped events
    records = event.get("Records", [])
    if not records:
        # Could be invoked directly by Step Functions
        records = [event] if "s3" in event else []

    processed = []
    errors = []

    for record in records:
        key = "unknown"                                             # ✅ defined before try so except can always access it
        try:
            s3_info = record["s3"]
            bucket = s3_info["bucket"]["name"]
            key = unquote_plus(s3_info["object"]["key"])

            logger.info(f"Processing: s3://{bucket}/{key}")
            
            raw_data = read_json_from_s3(bucket, key)

            if "items" in raw_data and isinstance(raw_data["items"], list):
                df = pd.json_normalize(raw_data["items"])
            else:
                # Fallback: try to normalize the entire object
                df = pd.json_normalize(raw_data)

            logger.info(f"  Raw shape: {df.shape}")  

            df = validate_category_data(df) 

            # Adding metadata columns
            df["_ingestion_timestamp"] = datetime.now(timezone.utc).isoformat()
            df["_source_file"] = key

            # Extracting region and making it a column
            region = "unknown"
            for part in key.split("/"):
                if part.startswith("region="):
                    region = part.split("=")[1]
                    break
            df["region"] = region

            logger.info(f"  Clean shape: {df.shape}, region: {region}")

            # Writing to Silver Layer as Parquet
            wr_response = wr.s3.to_parquet(
                df=df,
                path=SILVER_PATH,
                dataset=True,
                database=GLUE_DB,
                table=GLUE_TABLE,
                partition_cols=["region"],
                mode="overwrite_partitions",
                schema_evolution=True,
            )
        
            logger.info(f"  Written to Silver: {SILVER_PATH}")          # ✅ inside try
            processed.append({"key": key, "region": region, "rows": len(df)})  # ✅ inside try

        except Exception as e:                                          # ✅ aligned with try
            logger.error(f"Error processing record: {e}", exc_info=True)
            errors.append({"key": key, "error": str(e)})

    # Summary                                                           # ✅ outside the for loop
    if errors:
        send_alert(
            subject="[YT Pipeline] Silver reference transform failed",
            message=json.dumps(errors, indent=2),
        )    

    return {                                                             # ✅ inside lambda_handler, outside for loop
        "statusCode": 200,
        "processed": processed,
        "errors": errors
    }