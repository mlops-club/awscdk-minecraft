"""
This script is for zipping folders.

TODO: read https://github.com/rootski-io/rootski/blob/trunk/infrastructure/containers/postgres/automatic-backup/backup_or_restore.py
"""

import logging
import os
from pathlib import Path
from typing import List
from zipfile import ZipFile

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_s3 import S3Client

os.environ["AWS_PROFILE"] = "mlops-club"
os.environ["AWS_REGION"] = "us-west-2"

ZIPFILE_NAME = "zipfile.zip"
BUCKET_NAME = "awscdk-minecraft-bucket43879c71-jgojc4mtvl3t"
OBJECT_NAME = "uploaded_zipfile.zip"


def collect_file_paths(target_dir: str) -> List[Path]:
    """Return a list of all file paths in target directory.

    :param target_dir: The location of content to be zipped.
    """
    # Convert the path str to a Path object
    target_dir = Path(target_dir)
    # Use rglob method to collect strings for all items in target string
    # including subdirectories and their contents
    file_paths: List[Path] = list(target_dir.rglob("*.*"))
    # Output the list of complete file paths
    return file_paths


def create_zipfile_from_directory(target_dir: str) -> ZipFile:
    """Zip up a sample directory."""
    file_paths = collect_file_paths(target_dir)
    with ZipFile(ZIPFILE_NAME, "w") as zipfile:
        for file in file_paths:
            zipfile.write(file)
    zipfile.close()

    return zipfile


def upload_file_to_s3(client: S3Client, file_path: Path, bucket_name: str, object_name: str):
    """Upload a file to an S3 bucket.

    Args:
        client (S3Client): an AWS S3 client
        file_path (Path): path of the file that we'd like to upload to S3
        bucket_name (str): name of the S3 bucket we'd like to upload the file to
        object_name (str): name that we'd like the file to have once it's uploaded to the S3 bucket

    Returns:
        bool: whether the upload is successful or not
    """
    try:
        client.upload_file(Filename=str(file_path), Bucket=bucket_name, Key=object_name)
    except ClientError as error:
        logging.error(error)
        return False
    return True


if __name__ == "__main__":
    s3_client: S3Client = boto3.client("s3")
    zipfile = create_zipfile_from_directory("./tests")
    zipfile_path = zipfile.filename
    upload_file_to_s3(s3_client, zipfile_path, BUCKET_NAME, OBJECT_NAME)
