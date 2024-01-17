"""
@package photo_renamer
@brief   A script to re-name JPG files based on their "Date Taken" attribute

@date    12/16/2023
@updated 1/14/2024

@author  Preston Buterbaugh
@credit  Piexif info from https://piexif.readthedocs.io/en/latest/functions.html
@credit  Conversion from bytes to string from https://www.pythonpool.com/python-bytes-to-string/
"""

# Imports
from argparse import ArgumentParser
import os
import sys

import piexif

from custom.prestonpython import red, green

seq_nums = {}
"""A dictionary mapping each date-time string to the next number that should be appended to a photo at that time"""


def rename_file(filename: str) -> int:
    """
    @brief  Re-names a JPG file to the format of YYYY-MM-DD hh:mm.jpg, where date and time information is taken from
            the file's "Date taken" field
    @param  filename (str): The full initial filename of the JPG, including the extension
    @return (int)
            - 0 if the file was successfully renamed
            - 1 if an error occurred
    """
    # Create a dictionary of the photo's metadata
    try:
        exif_dict = piexif.load(filename)
    except piexif.InvalidImageDataError:
        print(f'{red("ERROR")} - Specified file "{filename}" is not a JPG file')
        return 1

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

    # Print photo taken time
    if date_taken_hour == 0:
        print(f'{filename} was taken on {date_taken_month}/{date_taken_day}/{date_taken_year} at 12:{str(date_taken_minute).zfill(2)} AM')
    elif date_taken_hour == 12:
        print(f'{filename} was taken on {date_taken_month}/{date_taken_day}/{date_taken_year} at 12:{str(date_taken_minute).zfill(2)} PM')
    elif date_taken_hour > 12:
        print(f'{filename} was taken on {date_taken_month}/{date_taken_day}/{date_taken_year} at {date_taken_hour - 12}:{str(date_taken_minute).zfill(2)} PM')
    else:
        print(f'{filename} was taken on {date_taken_month}/{date_taken_day}/{date_taken_year} at {date_taken_hour}:{str(date_taken_minute).zfill(2)} AM')

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
        print(f'{green("Renaming")} {filename} -> {file_name}.jpg')
    except FileExistsError:
        # If that file name is already in use, change the existing one to 1, and add to sequence number dictionary
        os.rename(f'{file_name}.jpg', f'{file_name} 1.jpg')
        print(f'{green("Renaming")} {file_name}.jpg -> {file_name} 1.jpg')
        os.rename(filename, f'{file_name} 2.jpg')
        print(f'{green("Renaming")} {filename} -> {file_name} 2.jpg')
        seq_nums[file_name] = 3

    return 0


def main(directory: str) -> int:
    """
    @brief   Driver function for the script, loops through all files in directory and renames all .JPEGs
    @param   directory (str): The directory to rename all JPGs in
    @return: (int)
            - 0 if successful
            - 1 otherwise
    """
    try:
        os.chdir(directory)
    except FileNotFoundError:
        print(f'The specified directory "{red(directory)}" does not exist')
        return 1

    file_list = os.listdir(directory)
    for filename in file_list:
        if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            rename_file(filename)

    return 0


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('directory', help='The directory to search for JPGs to rename')
    args = parser.parse_args()

    sys.exit(main(args.directory))
