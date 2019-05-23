import logging
import boto3
from botocore.exceptions import ClientError
from django.conf import settings

def upload_file(file_path, file_key):
    s3 = boto3.resource('s3')
    data = open(file_path, 'rb')
    try:
        s3.Bucket('openroad-flow').put_object(Key=file_key, Body=data, ACL='public-read')
        return settings.S3_BUCKET_URL + file_key
    except ClientError as e:
        logging.error(e)