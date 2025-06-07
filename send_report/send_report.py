import boto3
import os
import glob

def upload_to_s3(pdf_path, bucket, key):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )
    s3.upload_file(pdf_path, bucket, key)
    print(f"Uploaded {pdf_path} to s3://{bucket}/{key}")

OUTPUT_DIR = '/app/output'
list_of_files = glob.glob(f"{OUTPUT_DIR}/*.pdf")
if not list_of_files:
    print("No PDF files found in the output directory.")
    exit(1)

latest_pdf = max(list_of_files, key=os.path.getctime)
key = os.path.basename(latest_pdf)
print(f"Found latest PDF file: {latest_pdf}")
upload_to_s3(latest_pdf, os.getenv("S3_BUCKET"), key)