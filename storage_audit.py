"""
@package    storage_audit
@brief      A tool to scan a computer hard drive to find all files/folders above a specified size

@date       12/15/2024
@updated    12/15/2024

@author     Preston Buterbaugh
"""
# Imports
import os
import sys
from typing import Dict, TextIO

from argparse import ArgumentParser

from custom.prestonpython import red, green


def storage_repr(num_bytes: int) -> str:
    """
    @brief  Converts a number of bytes into the largest possible storage unit >= 1
    @param  num_bytes (int): The total number of bytes
    @return (str) The number of bytes converted to the largest unit greater than 1, along with the unit
    """
    if num_bytes >= 1e12:
        return f'{round(num_bytes/1e12, 2)} TB'
    elif num_bytes >= 1e9:
        return f'{round(num_bytes/1e9, 2)} GB'
    elif num_bytes >= 1e6:
        return f'{round(num_bytes/1e6, 2)} MB'
    elif num_bytes >= 1000:
        return f'{round(num_bytes/1000, 2)} KB'
    else:
        return f'{num_bytes} bytes'


def scan_directory(path: str, threshold: int) -> Dict:
    """
    @brief  Scans a directory for files and folders above the threshold
    @param  path      (str): The full path to the directory being scanned
    @param  threshold (int): The number of bytes at which or above a directory or file will be printed
    @return (Dict) A dictionary containing:
                     - The file/folder name
                     - A list of dictionaries containing all files/folders over the threshold in the directory
                     - The total number of files in the directory
                     - The total number of bytes taken up by the file/folder
    """
    print(f'\rScanning {path}...', end='')
    found_files = []
    num_files = 0
    directory_size = 0
    try:
        files = os.listdir(path)
    except PermissionError:
        files = []

    for file in files:
        full_path = f'{path}/{file}'
        if os.path.isdir(full_path):
            subdirectory_results = scan_directory(full_path, threshold)
            if subdirectory_results['total_size'] >= threshold:
                found_files.append(subdirectory_results)
            num_files = num_files + subdirectory_results['num_files']
            directory_size = directory_size + subdirectory_results['total_size']
        else:
            file_size = os.path.getsize(f'{path}/{file}')
            if file_size >= threshold:
                found_files.append({
                    'name': file,
                    'files': [],
                    'num_files': 0,
                    'total_size': file_size
                })
            num_files = num_files + 1
            directory_size = directory_size + file_size
    return {
        'name': os.path.basename(path),
        'files': found_files,
        'num_files': num_files,
        'total_size': directory_size
    }


def print_scan_results(results: Dict, file: TextIO, indent: int = 0):
    """
    @brief  Prints the results of a directory scan
    @param  results (Dict)  A dictionary containing the results of a scan with the following keys:
                            - 'name' - The file or folder name
                            - 'files' - A list dictionaries representing the scans of subdirectories
                            - 'num_files' - The number of files in the directory
                            - 'total_size' - The size of the directory in bytes
    @param  file   (TextIO) A file object representing the file to which to write output
    @param  indent (int)    An integer representing the number of indentation levels
    """
    for _ in range(indent):
        print('    ', end='')
        file.write('    ')
    print(f'{results["name"]} - {red(storage_repr(results["total_size"]))}', end='')
    file.write(f'{results["name"]} - {storage_repr(results["total_size"])}')
    if results['num_files'] == 1:
        print(green(f' ({results["num_files"]} file)'))
        file.write(f' ({results["num_files"]} file)\n')
    if results['num_files'] > 1:
        print(green(f' ({results["num_files"]} files)'))
        file.write(f' ({results["num_files"]} files)\n')
    else:
        print()
        file.write('\n')

    if results['files']:
        results['files'].sort(key=lambda x: x['total_size'], reverse=True)
    for subdirectory in results['files']:
        print_scan_results(subdirectory, file, indent + 1)


def file_name(name):
    """
    @brief  Converts a file path name into a legal file name ending in .txt
    @param  name (str) The original file path name
    @return (str)
    """
    name = name.replace(':', '')
    name = name.replace('/', '-')

    return f'{name}-audit.txt'


def main(path: str, threshold: int) -> int:
    """
    @brief  Takes a directory and a size threshold and scans the directory for files and folders above the threshold
    @param  path      (str) The name of the directory to scan
    @param  threshold (int) The number of bytes at or above which the program should list a file or folder
    @return (int)
      - 0 if successful
      - 1 otherwise
    """
    try:
        scan_results = scan_directory(path, threshold)
    except FileNotFoundError:
        return 1
    print('\r')
    log_file_name = file_name(path)
    log_file = open(log_file_name, 'w')
    print_scan_results(scan_results, log_file)
    log_file.close()
    return 0


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--directory', '-d', default='C:/', help='The name of the directory to scan')
    parser.add_argument('--threshold', '-t', default=1000000000, help='The number of bytes at which or above a file should be listed')
    args = parser.parse_args()
    sys.exit(main(args.directory, args.threshold))
