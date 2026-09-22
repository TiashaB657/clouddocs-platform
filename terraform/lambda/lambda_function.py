import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])
S3_BUCKET = os.environ["S3_BUCKET"]


def lambda_handler(event, context):
    response = table.scan()

    documents = []

    for item in response.get("Items", []):
        file_name = item.get("file_name")

        download_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": S3_BUCKET,
                "Key": file_name
            },
            ExpiresIn=300
        )

        documents.append({
            "file_name": file_name,
            "uploaded_by": item.get("uploaded_by"),
            "upload_time": item.get("upload_time"),
            "status": item.get("status"),
            "download_url": download_url
        })

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "documents": documents
        })
    }