"""
This script is for downloading zip files from an S3 bucket and unzipping them.
"""

from mypy_boto3_s3 import S3Client
import boto3
from botocore.exceptions import ClientError
import logging
import os
from zipfile import ZipFile
from s3_backup_service.zip_directory import (
    BUCKET_NAME,
    OBJECT_NAME,
)
from s3_backup_service.zip_directory import (
    create_zipfile_from_directory,
    upload_file_to_s3,
)

def create_backup_directory_and_file():
    os.mkdir(path='./backup')
    fp = open('./backup/downloaded_zipfile.zip', 'w')
    fp.close()

def download_file_from_s3(client: S3Client, file_path: str, bucket_name: str, object_name: str):
    try:
        client.download_file(Bucket=bucket_name, Key=object_name, Filename=file_path)
    except ClientError as error:
        logging.error(error)
        return False
    return True

def unzip_file(path_to_zip_file: str, directory_to_extract_to: str):
    with ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(path=directory_to_extract_to)

if __name__=="__main__":
    s3_client: S3Client = boto3.client("s3")
    zipfile = create_zipfile_from_directory("./tests")
    zipfile_path = zipfile.filename
    upload_file_to_s3(s3_client, zipfile_path, BUCKET_NAME, OBJECT_NAME)
    
    create_backup_directory_and_file()
    download_file_from_s3(s3_client, './backup/downloaded_zipfile.zip', BUCKET_NAME, OBJECT_NAME)
    unzip_file('./backup/downloaded_zipfile.zip', './backup')