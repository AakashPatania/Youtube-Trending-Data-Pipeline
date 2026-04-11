import json
import os
import boto3
import logging
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

logger = logging.getlogger()
logger.setLevel(logging.INFO)


# Connecting to AWS clients both s3 and sns

s3_client = boto3.client("s3")
sns_client = boto3.client("sns")

## CONFIG

API_KEY = os.environ["YOUTUBE_API_KEY"]
BUCKET = os.environ["S3_BUCKET_BRONZE"]
REGIONS = os.environ.get("YOUTUBE_REGIONS", "US,GB,CA,DE,FR,IN,JP,KR,MX,RU").split(",")
SNS_TOPIC = os.environ.get("SNS_ALERT_TOPIC_ARN", "")
API_BASE = "https://www.googleapis.com/youtube/v3"
MAX_RESULTS = 50


def fetch_trending_videos(region_code: str) -> dict:

    """
    
    Call the youtube data API to get the current trending videos for a give region
    
    """

    params = urlencode({
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region_code,
        "maxResults": MAX_RESULTS,
        "key": API_KEY,
    })

    url = f"{API_KEY}/videos?{params}"

    req = Request(url, headers={"Accept": "application/json"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_video_categories(region_code: str) -> dict:

    """
    fetch the video category mapping for a region.
    this replaces the static json reference files from kaggle.
    
    """

    params = urlencode({
        "part": "snippet",
        "regionCode": region_code,
        "key": API_KEY,
    })
    url = f"{API_BASE}/videoCategories?{params}"

    req = Request(url, headers={"Accept": "application/json"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))
    


def write_to_s3(data: dict, bucket: str, key: str) -> dict:

    """
    write JSON data to s3 with metadata
    """    

    body = json.dumps(data, ensure_ascii=False, indent=2)
    response = s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body.encode("utf-8"),
        ContentType="application/json",
        Metadata={
            "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "youtube_data_api_v3",
        },
    )
    return response


def send_alert(subject: str, message: str):
    """ send failure alert via SNS  """

    if SNS_TOPIC:
        sns_client.publish(
        TopicArn=SNS_TOPIC,
        Subject=subject[:100],
        Message=message,    

        )



def lambda_handler(event, context):
    """
    Main handler, Iterates over regions, fetches trending videos and category mappings, writes
    everything to bronze layer
    """


    now = datetime.now(timezone.utc)
    date_partition = now.strftime("%Y-%m-%d")
    hour_partition = now.strftime("%H")
    ingestion_id = now.strftime("%Y%m%d_%H%M%S")

    results = {"success": [], "failed": []}


    for region in REGIONS:
        region = region.strip().lower()
        logger.info(f"Processing region: {region}")

        ## Fetch trending videos

        try: 
            trending_data = fetch_trending_videos(region)
            video_count = len(trending_data.get("items", []))

            # Add pipeline metadata to the new response
            trending_data["_pipeline_metadata"] = {
                "ingestion_id": ingestion_id,
                "region": region,
                "ingestion_timestamp": now.isoformat(),
                "video_count": video_count,
                "source": "youtube_data_api_v3",
            }

            # S3 key with hive style partitioning
            # s3://bucket/youtube/raw_statistics/region=US/date=2026-03-02/hour=14/data.json
            
            s3_key = (
                f"youtube/raw_statistics/"
                f"region={region}/"
                f"date={date_partition}/"
                f"hour={hour_partition}/"
                f"{ingestion_id}.json"
            )
            write_to_s3(trending_data, BUCKET, s3_key)
            logger.info(f"  Wrote {video_count} videos → s3://{BUCKET}/{s3_key}")

        
        except (HTTPError, URLError) as e:
            logger.error(f"  API error for {region} trending: {e}")
            results["failed"].append({"region": region, "type": "trending", "error": str(e)})
            continue
        except Exception as e:
            logger.error(f"  Unexpected error for {region} trending: {e}")
            results["failed"].append({"region": region, "type": "trending", "error": str(e)})
            continue
    

        try: 
            category_data = fetch_video_categories(region)
            category_data["_pipeline_metadata"] = {
                "ingestion_id": ingestion_id,
                "region": region,
                "ingestion_timestamp": now.isoformat(),
                "source": "youtube_data_api_v3",
            }

            ref_key = (
                f"youtube/raw_statistics_reference_data/"
                f"region={region}/"
                f"date={date_partition}/"
                f"{region}_category_id.json"
            )
            write_to_s3(category_data, BUCKET, ref_key)
            logger.info(f"  Wrote categories → s3://{BUCKET}/{ref_key}")


        except (HTTPError, URLError) as e:
            logger.error(f"  API error for {region} categories: {e}")
            results["failed"].append({"region": region, "type": "categories", "error": str(e)})
            continue

        results["success"].append(region)


        ## Summary & Alerting


        summary = (

            f"Ingestion {ingestion_id} complete. "
            f"Success: {len(results['success'])}/{len(REGIONS)} regions. "
            f"Failed: {len(results['failed'])}."
        )
        logger.info(summary)

        if results["failed"]:
            send_alert(
                subject=f"[YT Pipeline] Ingestion partial failure - {ingestion_id}",
                message=json.dumps(results, indent=2)
            )
     




    return {
        'statusCode': 200,
        'ingestion_id': ingestion_id,
        'results': results        
        
    }
