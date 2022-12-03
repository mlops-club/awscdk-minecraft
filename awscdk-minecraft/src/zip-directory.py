import os
from zipfile import ZipFile

from typing import List


def collect_file_paths(target_dir: str) -> List[str]:
    # Initialize a list for adding filepath strings to
    file_paths = []
    # Walk through the target directory and subdirectories generating file paths
    for root, directories, files in os.walk(target_dir):
        # For each directory or sub directory create a full length path for each file
        for filename in files:
            # Create a complete file path
            filepath = os.path.join(root, filename)
            # Append the file path to the list of filepaths
            file_paths.append(filepath)

    # Output the list of complete file paths
    return file_paths

def main():
    # Path to target folder
    target_dir = './'

    # Grab all file paths to be zipped
    file_paths = collect_file_paths(target_dir)

    # Print that paths of the all the files to be zipped
    print('These files will be zipped:\n')
    for paths in file_paths:
        print(paths)

    # Write the files to a zip file
    with ZipFile('test_zip.zip','w') as zip:
        for file in file_paths:
            zip.write(file)

    print('All files zipped successfully!')
    zip.close()

if __name__ == '__main__':
            main()