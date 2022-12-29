"""
This script is for zipping folders.

TODO: read https://github.com/rootski-io/rootski/blob/trunk/infrastructure/containers/postgres/automatic-backup/backup_or_restore.py
"""

import argparse
import io
import logging
import os
from pathlib import Path
import time
from typing import List, Optional
from zipfile import ZipFile

import boto3
from boto3.exceptions import S3UploadFailedError
from botocore.exceptions import ClientError
from mypy_boto3_s3 import S3Client

# os.environ["AWS_PROFILE"] = "mlops-club"
os.environ["AWS_REGION"] = "us-west-2"

ZIPFILE_NAME = "zipfile.zip"
BUCKET_NAME = "awscdk-minecraft-bucket43879c71-jgojc4mtvl3t"  # this will need to be defined by the stack.
# TODO: pick this up from environment variable.
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


# def create_backup_directory_and_file():
#     os.mkdir(path='./backup')
#     fp = open('./backup/downloaded_zipfile.zip', 'w')
#     fp.close()



def download_file_from_s3(client: S3Client, bucket_name: str, object_name: str) -> Optional[io.BytesIO]:
    # open an io.BytesIO object to write the file to with 'wb' mode
    file_object = io.BytesIO()
    try:
        client.download_fileobj(Bucket=bucket_name, Key=object_name, Fileobj=file_object)
    except ClientError as error:
        logging.error(error)
        return None
    return file_object


def unzip_file(file_object: io.BytesIO, directory_to_extract_to: str):
    with ZipFile(file_object, 'r') as zip_ref:
        zip_ref.extractall(path=directory_to_extract_to)


# argument parsing
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target_dir",
        type=str,
        default="./tests",
        help="The directory that we'd like to zip up.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60*3,
        help="The interval at which we'd like to upload the zipfile to S3.",
    )
    parser.add_argument(
        "--restore",
        action="store_true",
        help="If this flag is present, we'll restore the backup from S3.",
    )
    parser.add_argument(
        "--bucket_name",
        type=str,
        default="awscdk-minecraft-bucket43879c71-jgojc4mtvl3t",  # TODO: change this to a variable.
        help="The name of the S3 bucket we'd like to upload the file to.",
    )
    parser.add_argument(
        "--object_name",
        type=str,
        default="uploaded_zipfile.zip",
        help="The name that we'd like the file to have once it's uploaded to the S3 bucket.",
    )
    # log-level
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help="The log level to use.",
    )
    return parser.parse_args()


def main(args):
    logging.basicConfig(level=args.log_level)
    zipfile_path = create_zipfile_from_directory(args.target_dir).filename
    s3_client: S3Client = boto3.client("s3")
    # run on periodic schedule forever if restore is False, otherwise pull from S3 and unzip.
    if args.restore:
        # pull object_name from S3 and unzip to target_dir.
        file_object = download_file_from_s3(s3_client, args.bucket_name, args.object_name)
        if file_object is None:
            raise Exception("Failed to download file from S3.")
        unzip_file(file_object, "./backup")
        logging.info("Successfully restored backup from S3.")
    else: # use try/except
        while True:
            try:
                upload_file_to_s3(s3_client, Path(zipfile_path), args.bucket_name, args.object_name)
            except S3UploadFailedError as error:
                logging.error(error)
            time.sleep(args.interval)


if __name__ == "__main__":
    args = parse_args()
    main(args)