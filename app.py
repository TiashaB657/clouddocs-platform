from datetime import datetime
from flask import Flask, render_template, request, redirect
import boto3
import os

app = Flask(__name__)

# AWS configuration
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET = os.getenv("S3_BUCKET", "clouddocs-platform-tiasha-mumbai")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE", "CloudDocsMetadata")

# AWS clients
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

table = dynamodb.Table(DYNAMODB_TABLE)


@app.route("/")
def home():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    if not file or file.filename == "":
        return "No file selected", 400

    # Upload file to S3
    s3.upload_fileobj(
        file,
        S3_BUCKET,
        file.filename
    )

    # Store metadata in DynamoDB
    table.put_item(
        Item={
            "file_name": file.filename,
            "uploaded_by": "Tiasha",
            "upload_time": str(datetime.now()),
            "status": "Uploaded"
        }
    )

    return "File uploaded successfully!"


@app.route("/files")
def files():

    response = s3.list_objects_v2(
        Bucket=S3_BUCKET
    )

    uploaded_files = []

    if "Contents" in response:

        for obj in response["Contents"]:
            uploaded_files.append(
                obj["Key"]
            )

    return render_template(
        "files.html",
        files=uploaded_files
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):

    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": filename
        },
        ExpiresIn=300
    )

    return redirect(url)


@app.route("/metadata/<filename>")
def metadata(filename):

    response = table.get_item(
        Key={
            "file_name": filename
        }
    )

    if "Item" not in response:
        return {"error": "Metadata not found"}, 404

    return response["Item"]


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )