"""This script is for zipping folders."""

from pathlib import Path
from typing import List
from zipfile import ZipFile


def collect_file_paths(target_dir: str) -> List[Path]:
    """Retun a list of all file paths in target directory.

    :param target_dir: The location of content to be zipped.
    """
    # Convert the path str to a Path object
    target_dir = Path(target_dir)
    # Use rglob method to collect strings for all items in target string
    # including subdirectories and their contents
    file_paths: List[Path] = list(target_dir.rglob("*"))
    # Output the list of complete file paths
    return file_paths


def main():
    """Zip up a sample directory."""
    # Path to target folder
    target_dir = "./"

    # Grab all file paths to be zipped
    file_paths = collect_file_paths(target_dir)

    # Print that paths of the all the files to be zipped
    print("These files will be zipped:\n")
    for path in file_paths:
        print(path)

    # Write the files to a zip file
    with ZipFile("test_zip.zip", "w") as zipfile:
        for file in file_paths:
            zipfile.write(file)

    print("All files zipped successfully!")
    zipfile.close()


if __name__ == "__main__":
    main()
