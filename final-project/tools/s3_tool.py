from .schemas import S3UploadInputSchema, S3UploadOutputSchema
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
import os
from dotenv import load_dotenv
import logging
from io import BytesIO

logger = logging.getLogger(__name__)
load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

if not AWS_REGION or not S3_BUCKET_NAME:
    logger.warning("AWS_REGION or S3_BUCKET_NAME not configured. S3 tool may not fully function.")

s3_client = None
if AWS_REGION and S3_BUCKET_NAME: # Only initialize if configured
    try:
        s3_client = boto3.client(
            's3',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        # Test credentials by listing buckets (optional, requires ListBuckets permission)
        # s3_client.list_buckets() # Uncomment to test connection early
    except (NoCredentialsError, PartialCredentialsError):
        logger.error("AWS credentials not found or incomplete. S3 tool will not work.")
        s3_client = None
    except Exception as e:
        logger.error(f"Error initializing S3 client: {e}")
        s3_client = None

def upload_to_s3(file_content: bytes, s3_key: str, content_type: str | None = None) -> S3UploadOutputSchema:
    """Uploads byte content to the configured S3 bucket."""
    if not s3_client:
        logger.error("S3 client not initialized. Cannot upload.")
        return S3UploadOutputSchema(s3_path="error/s3_not_configured")
    if not S3_BUCKET_NAME:
         logger.error("S3_BUCKET_NAME not configured. Cannot upload.")
         return S3UploadOutputSchema(s3_path="error/s3_bucket_not_set")

    logger.info(f"Attempting to upload to S3 bucket '{S3_BUCKET_NAME}' with key '{s3_key}'")
    file_obj = BytesIO(file_content)
    extra_args = {}
    if content_type:
        extra_args['ContentType'] = content_type
        # Example: Make publically readable if needed
        # extra_args['ACL'] = 'public-read'

    try:
        s3_client.upload_fileobj(
            Fileobj=file_obj,
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            ExtraArgs=extra_args
        )
        s3_path = f"s3://{S3_BUCKET_NAME}/{s3_key}"

        # Construct URL (basic example, assumes region and standard endpoint)
        # For more robust URL generation, consider bucket settings (website hosting, etc.)
        # Note: This URL might not be publically accessible depending on bucket policy/ACLs
        url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

        logger.info(f"Successfully uploaded to {s3_path}")
        return S3UploadOutputSchema(s3_path=s3_path, url=url)

    except ClientError as e:
        logger.error(f"S3 ClientError during upload: {e}", exc_info=True)
        return S3UploadOutputSchema(s3_path=f"error/s3_client_error")
    except Exception as e:
        logger.error(f"Unexpected error during S3 upload: {e}", exc_info=True)
        return S3UploadOutputSchema(s3_path=f"error/unknown_upload_error")

# This function is intended to be called by other tools (TTS, TTI)
# If direct upload via this module is needed, create a wrapper function
# def run_s3_upload(input_data: S3UploadInputSchema) -> S3UploadOutputSchema:
#     return upload_to_s3(
#         file_content=input_data.file_content,
#         s3_key=input_data.s3_key,
#         content_type=input_data.content_type
#     )

# Example usage (for testing - requires AWS creds/bucket)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if s3_client and S3_BUCKET_NAME:
        test_content = b"This is a test file content."
        test_key = "test_files/test_upload.txt"
        output = upload_to_s3(file_content=test_content, s3_key=test_key, content_type="text/plain")
        print(output.model_dump_json(indent=2))

        # Example of uploading an image (replace with actual image bytes)
        # try:
        #     with open("path/to/your/image.png", "rb") as f:
        #         image_bytes = f.read()
        #     img_output = upload_to_s3(image_bytes, "test_images/my_test_image.png", "image/png")
        #     print(f"Image upload: {img_output.model_dump_json(indent=2)}")
        # except FileNotFoundError:
        #     print("Test image not found, skipping image upload test.")

    else:
        print("S3 client not configured. Skipping S3 upload test.")
