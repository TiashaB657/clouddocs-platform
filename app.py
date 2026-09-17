from datetime import datetime
from flask import redirect
import boto3
from flask import Flask, render_template, request
import os

app = Flask(__name__)

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION
)

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

table = dynamodb.Table("CloudDocsMetadata")


@app.route("/")
def home():
    return render_template("upload.html")


    # table.put_item(
    # Item={
    #     "file_name": file.filename,
    #     "uploaded_by": "Tiasha",
    #     "upload_time": str(datetime.now()),
    #     "status": "Uploaded"
    # }
    # )
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    s3.upload_fileobj(
        file,
        "clouddocs-platform-tiasha",
        file.filename
   )

    return "File uploaded successfully!"

@app.route("/files")

def files():

    response = s3.list_objects_v2(
        Bucket="clouddocs-platform-tiasha"
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
            "Bucket": "clouddocs-platform-tiasha",
            "Key": filename
        },
        ExpiresIn=300
    )

    # print(f"Generated URL: {url}")

    return redirect(url)
@app.route("/metadata/<filename>")
def metadata(filename):

    response = table.get_item(
    Key={
        "file_name": filename
    }
)

    
    return response["Item"]
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)