# %%

import datetime
import json
import os
import boto3
import requests

DATE_PARAM = "2023-10-21"
date = datetime.datetime.strptime(DATE_PARAM, "%Y-%m-%d")
# %%
url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{date.strftime('%Y/%m/%d')}"
print(f"Requesting REST API URL: {url}")

# Getting response from Wikimedia API
wiki_server_response = requests.get(url, headers={"User-Agent": "curl/7.68.0"})
wiki_response_status = wiki_server_response.status_code
wiki_response_body = wiki_server_response.text

print(f"Wikipedia REST API Response body: {wiki_response_body}")
print(f"Wikipedia REST API Response Code: {wiki_response_status}")

# Check if response status is not OK
if wiki_response_status != 200:
    print(
        f"Received non-OK status code from Wiki Server: {wiki_response_status}. Response body: {wiki_response_body}"
    )

# %%
from pathlib import Path

## Get the directory of the current file
current_directory = Path(__file__).parent

# Path for the new directory
RAW_LOCATION_BASE = current_directory /"raw-views"

# Create the new directory, ignore if it already exists
RAW_LOCATION_BASE.mkdir(exist_ok=True, parents=True)
print(f"Created directory {RAW_LOCATION_BASE}")
# %%

# Saving the contents of `wiki_response_body` to a file
raw_edits_file = RAW_LOCATION_BASE / f"raw-views-{date.strftime('%Y-%m-%d')}.txt"
with raw_edits_file.open("w") as file:
    file.write(wiki_response_body)
    print(f"Saved raw edits to {raw_edits_file}")
# %%
S3_WIKI_BUCKET = ""
# Create a new bucket for your wikipedia pipeline
s3 = boto3.client("s3")
S3_WIKI_BUCKET = "homework-balint-thaler"

bucket_names = [bucket["Name"] for bucket in s3.list_buckets()["Buckets"]]
# Only create the bucket if it doesn't exist
if S3_WIKI_BUCKET not in bucket_names:
    s3.create_bucket(
        Bucket=S3_WIKI_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
    )
# Check your solution
assert S3_WIKI_BUCKET != "", "Please set the S3_WIKI_BUCKET variable"
assert s3.list_objects(
    Bucket=S3_WIKI_BUCKET
), "The bucket {S3_WIKI_BUCKET} does not exist"
# %%
res = s3.upload_file(
    raw_edits_file,
    S3_WIKI_BUCKET,
    f"datalake/raw/raw-views-{date.strftime('%Y-%m-%d')}.txt",
    )
print(
    f"Uploaded raw edits to s3://{S3_WIKI_BUCKET}/datalake/raw/raw-views-{date.strftime('%Y-%m-%d')}.txt")

# %%
wiki_response_parsed = wiki_server_response.json()
top_views = wiki_response_parsed["items"][0]["articles"]

# Convert server's response to JSON lines
current_time = datetime.datetime.utcnow()  
json_lines = ""
for page in top_views:
    record = {
        "article": page["article"],
        "views": page["views"],
        "rank" : page["rank"],
        "date": date.strftime("%Y-%m-%d"),
        "retrieved_at": current_time.isoformat(),
    }
    json_lines += json.dumps(record) + "\n"

# Save the Top views JSON lines
JSON_LOCATION_DIR = current_directory / "data" / "views"
JSON_LOCATION_DIR.mkdir(exist_ok=True, parents=True)
print(f"Created directory {JSON_LOCATION_DIR}")
print(f"JSON lines:\n{json_lines}")

json_lines_filename = f"views-{date.strftime('%Y-%m-%d')}.json"
json_lines_file = JSON_LOCATION_DIR / json_lines_filename

with json_lines_file.open("w") as file:
    file.write(json_lines)
# %%
json_lines_filename2 = f"views-{date.strftime('%Y-%m-%d')}.txt"
json_lines_file2 = JSON_LOCATION_DIR / json_lines_filename
s3.upload_file(
    json_lines_file2, S3_WIKI_BUCKET, f"datalake/views/{json_lines_filename2}"
)
print(
    f"Uploaded JSON lines to s3://{S3_WIKI_BUCKET}/datalake/views/{json_lines_filename2}"
)
# %%
