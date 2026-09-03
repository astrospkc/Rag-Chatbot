# aws 
# - file upload 
# - presigned url generation 
# - 

import logging
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from dotenv import load_dotenv
import os

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET = os.getenv("AWS_BUCKET")


def create_presigned_post(
    object_name,
    fields=None,
    conditions=None,
    expiration=3600,
):
    """Generate a presigned URL S3 POST request to upload a file
    :param object_name: string
    :param fields: Dictionary of prefilled form fields
    :param conditions: List of conditions to include in the policy
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Dictionary with the following keys:
        url: URL to post to
        fields: Dictionary of form fields and values to submit with the POST
    :return: None if error.
    """

    # Generate a presigned S3 POST URL
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'virtual'},
        ),
    )
    try:
        response = s3_client.generate_presigned_post(
            AWS_BUCKET,
            object_name,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL and required fields
    return response


def download_file_from_s3(object_name: str, target_path: str) -> bool:
    """Download a file from S3 bucket to a local target path."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'virtual'},
        ),
    )
    try:
        s3_client.download_file(AWS_BUCKET, object_name, target_path)
        return True
    except ClientError as e:
        logging.error(f"Error downloading file from S3: {e}")
        return False

# def create_presigned_download_url(object_key,expiration=3600):
#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=AWS_ACCESS_KEY,
#         aws_secret_access_key=AWS_SECRET_KEY,
#         region_name=AWS_REGION,
#         config=Config(
#             signature_version='s3v4',
#             s3={'addressing_style': 'path'},
#         ),
#     )
#     try:
#         response = s3_client.generate_presigned_url(
#             'get_object',
#             Params={'Bucket': AWS_BUCKET, 'Key': object_key},
#             ExpiresIn=expiration,
#         )
#     except ClientError as e:
#         logging.error(e)
#         return None
#     return response