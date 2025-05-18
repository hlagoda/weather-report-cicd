import boto3
import os

def upload_to_s3(pdf_path, bucket, key):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )
    s3.upload_file(pdf_path, bucket, key)
    print(f"Uploaded {pdf_path} to s3://{bucket}/{key}")

key = os.path.basename(PDF_FILE)
upload_to_s3(PDF_FILE, os.getenv("S3_BUCKET"), key)