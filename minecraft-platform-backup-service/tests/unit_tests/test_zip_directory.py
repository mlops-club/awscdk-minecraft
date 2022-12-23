"""Unit tests for zip_directory.py."""
import os
from pathlib import Path, PosixPath
from zipfile import ZipFile

import boto3
from moto import mock_s3
from mypy_boto3_s3 import S3Client
from s3_backup_service.zip_directory import (
    ZIPFILE_NAME,
    collect_file_paths,
    create_zipfile_from_directory,
    upload_file_to_s3,
)

CONTENT = "content"

OUTER_DIRECTORY_NAME = "outer-directory"
INNER_DIRECTORY_NAME = "inner-directory"
OUTER_FILE_NAME = "outer_file.txt"
INNER_FILE_NAME = "inner_file.txt"

TEST_ZIPFILE_NAME = "test_zipfile.zip"


def create_mock_directories(tmp_path: PosixPath):
    """Create a mock directory and another one nested inside of it.

    Args:
        tmp_path (PosixPath): a mock path

    Returns:
        PosixPath, PosixPath: the nested mock directories
    """
    outer_directory = tmp_path / OUTER_DIRECTORY_NAME
    outer_directory.mkdir()

    inner_directory = outer_directory / INNER_DIRECTORY_NAME
    inner_directory.mkdir()

    return outer_directory, inner_directory


def create_mock_files(outer_directory: PosixPath, inner_directory: PosixPath):
    """Create a mock file in each of the two nested directories.

    Args:
        outer_directory (PosixPath): the outer mock directory
        inner_directory (PosixPath): the inner mock directory

    Returns:
        PosixPath, PosixPath: the mock files
    """
    outer_file = outer_directory / OUTER_FILE_NAME
    outer_file.touch()

    inner_file = inner_directory / INNER_FILE_NAME
    inner_file.touch()

    return outer_file, inner_file


def test_collect_file_paths(tmp_path: PosixPath):
    """Make sure zip_directory.py's collect_file_paths() work as expected.

    Args:
        tmp_path (PosixPath): a mock path
    """
    outer_directory, inner_directory = create_mock_directories(tmp_path)
    _, _ = create_mock_files(outer_directory, inner_directory)

    file_paths = collect_file_paths(target_dir=f"{tmp_path}/{OUTER_DIRECTORY_NAME}")
    file_path_strings = [str(file_path) for file_path in file_paths]
    file_names = sorted([file_path_string.split("/")[-1] for file_path_string in file_path_strings])

    assert file_names == sorted([OUTER_FILE_NAME, INNER_FILE_NAME])


def test_create_zipfile_from_directory(tmp_path: PosixPath):
    """Make sure zip_directory.py's create_zipfile_from_directory() work as expected.

    Args:
        tmp_path (PosixPath): a mock path
    """
    outer_directory, inner_directory = create_mock_directories(tmp_path)
    outer_file, inner_file = create_mock_files(outer_directory, inner_directory)

    with ZipFile(TEST_ZIPFILE_NAME, "w") as zipfile:
        zipfile.write(Path(outer_file))
        zipfile.write(Path(inner_file))
    zipfile.close()
    zipfile_archive_members = zipfile.namelist()
    os.remove(TEST_ZIPFILE_NAME)

    mock_zipfile = create_zipfile_from_directory(target_dir=f"{tmp_path}/{OUTER_DIRECTORY_NAME}")
    mock_zipfile_archive_members = mock_zipfile.namelist()
    os.remove(ZIPFILE_NAME)

    assert sorted(mock_zipfile_archive_members) == sorted(zipfile_archive_members)


def test_upload_file_to_s3(tmp_path: PosixPath):
    """Make sure zip_directory.py's upload_file_to_s3() work as expected.

    Args:
        tmp_path (PosixPath): a mock path
    """
    outer_directory, inner_directory = create_mock_directories(tmp_path)
    _, _ = create_mock_files(outer_directory, inner_directory)

    test_zipfile = create_zipfile_from_directory(target_dir=f"{tmp_path}/{OUTER_DIRECTORY_NAME}")
    test_zipfile_path = test_zipfile.filename
    test_bucket_name = "test_bucket"
    test_object_name = "test_uploaded_zipfile.zip"

    with mock_s3():
        s3_client: S3Client = boto3.client("s3")
        s3_client.create_bucket(
            Bucket=test_bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "us-west-2"},
        )
        assert upload_file_to_s3(s3_client, test_zipfile_path, test_bucket_name, test_object_name)
