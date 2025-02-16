import boto3
import requests
import os

def handler(event, context):
    BUCKET_NAME = os.environ.get("BUCKET_NAME")
    api_url = "https://www.eirgrid.ie/api/graph-data"

    response = requests.get(api_url, params={"area": "demandactual", "region": "ALL"})
    if response.status_code == 200:
        data = response.json()
        filename = "raw_data.json"
        
        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"raw/{filename}",
            Body=str(data),
            ContentType="application/json"
        )
        return {"statusCode": 200, "body": f"Data saved to S3: {filename}"}
    else:
        return {"statusCode": response.status_code, "body": "Failed to fetch data"}
