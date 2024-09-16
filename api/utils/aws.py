import boto3
from botocore.client import BaseClient

import api.utils.env as env


def get_s3_client() -> BaseClient:
    region = env.S3_REGION
    access_key = env.S3_ACCESS_KEY
    secret_key = env.S3_SECRET_KEY

    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )
    return s3_client
