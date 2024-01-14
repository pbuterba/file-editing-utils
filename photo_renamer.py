# Piexif info from https://piexif.readthedocs.io/en/latest/functions.html
# Conversion from bytes to string from https://www.pythonpool.com/python-bytes-to-string/

from datetime import datetime
import os
import sys

import piexif

seq_nums = {}


def rename_file(filename) -> int:
    # Create a dictionary of the photo's metadata
    exif_dict = piexif.load(filename)

    # Get date taken
    try:
        date_taken_bytes = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
    except KeyError:
        print(f'{filename} could not be renamed because it has no "date taken" attribute')
        return 1
    date_taken = date_taken_bytes.decode('utf-8')
    date_taken_date_component = date_taken.split(' ')[0]
    date_taken_time_component = date_taken.split(' ')[1]

    date_taken_year = int(date_taken_date_component.split(':')[0])
    date_taken_month = int(date_taken_date_component.split(':')[1])
    date_taken_day = int(date_taken_date_component.split(':')[2])

    date_taken_hour = int(date_taken_time_component.split(':')[0])
    date_taken_minute = int(date_taken_time_component.split(':')[1])

    file_name = f'{date_taken_year}-{str(date_taken_month).zfill(2)}-{str(date_taken_day).zfill(2)} {str(date_taken_hour).zfill(2)}-{str(date_taken_minute).zfill(2)}'

    # Get sequence number if it's a repeated date and time
    try:
        seq_num = seq_nums[file_name]
    except KeyError:
        seq_num = 0

    # Add the sequence number to the file name
    if seq_num:
        # Increment sequence number and append current sequence number to the file name
        seq_nums[file_name] = seq_num + 1
        file_name = f'{file_name} {seq_num}'

    # Rename file
    try:
        os.rename(filename, f'{file_name}.jpg')
    except FileExistsError:
        # If that file name is already in use, change the existing one to 1, and add to sequence number dictionary
        os.rename(f'{file_name}.jpg', f'{file_name} 1.jpg')
        os.rename(filename, f'{file_name} 2.jpg')
        seq_nums[file_name] = 3

    return 0


def main() -> int:
    """
    @brief  Driver function for the script, loops through all files in directory and renames all .JPEGs
    @return: (int)
            - 0 if successful
            - 1 otherwise
    """
    try:
        os.chdir(sys.argv[1])
    except FileNotFoundError:
        print(f'The specified directory "{sys.argv[1]}" does not exist')
        return 1

    file_list = os.listdir(sys.argv[1])
    for filename in file_list:
        if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            rename_file(filename)

    return 0


if __name__ == "__main__":
    sys.exit(main())
