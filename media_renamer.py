"""
@package media_renamer
@brief   A script to re-name JPG and MP4 files based on their "Date Taken" attribute

@date    12/16/2023
@updated 11/10/2026

@author  Preston Buterbaugh
@credit  Piexif info from https://piexif.readthedocs.io/en/latest/functions.html
@credit  Conversion from bytes to string from https://www.pythonpool.com/python-bytes-to-string/
"""

# Imports
from argparse import ArgumentParser
import os
import sys
from typing import Tuple

import piexif
import mutagen.mp4
from mutagen.mp4 import MP4

from custom.prestonpython import red, green

MONTH_FULL_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
""" All month names """

MONTH_ABBREVIATIONS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
""" Month three letter abbreviations"""

seq_nums = {}
"""A dictionary mapping each date-time string to the next number that should be appended to a photo at that time"""


def manual_date_entry(filename: str) -> Tuple[int, int, int, int, int]:
    """
    @brief  Allows the user to manually enter a date, ideally with as little effort as possible
    @param  filename: The name of the file for which the date is being input
    @return (int, int, int, int, int) The components of the date, in order year, month, day, hour, minute
    """
    valid_date = False
    year, month, day, hour, minute = 0, 0, 0, 0, 0

    while not valid_date:
        video_date_string = input(f"Enter the date components for {green(filename)}, separated by spaces (Year, Month, Day, Hour, Minute: ")
        while len(video_date_string.split(" ")) != 5:
            video_date_string = input("Enter all 5 components of the date (Year, Month, Day, Hour, Minute")

        year_string, month_string, day_string, hour_string, minute_string = video_date_string.split(" ")

        # Process year
        try:
            year = int(year_string)
        except ValueError:
            print(f"Invalid year '{red(year_string)}'")
            continue

        # Process month
        if month_string in MONTH_FULL_NAMES:
            month = MONTH_FULL_NAMES.index(month_string) + 1
        elif month_string in MONTH_ABBREVIATIONS:
            month = MONTH_ABBREVIATIONS.index(month_string) + 1
        else:
            # Parse month as number
            try:
                month = int(month_string)
            except ValueError:
                month = -1

            if month < 1 or month > 12:
                print(f"Invalid month '{red(month_string)}' entered")
                continue

        # Process day
        try:
            day = int(day_string)
        except ValueError:
            print(f"Invalid day '{red(day_string)}'")
            continue

        # Process hour
        try:
            hour = int(hour_string)
        except ValueError:
            print(f"Invalid hour '{red(hour_string)}'")
            continue

        # Process minute
        try:
            minute = int(minute_string)
        except ValueError:
            print(f"Invalid minute '{red(minute_string)}'")
            continue

        valid_date = True

    return year, month, day, hour, minute


def military_to_standard_time(hour: int) -> Tuple[int, str]:
    """
    @brief  Converts from an hour on the 24-hour scale to an hour on the twelve-hour scale
    @param  hour: The hour on the 24-hour scale
    @return (int, str) The hour on the 12-hour scale, and "AM" or "PM"
    """
    if hour == 0:
        return 12, "AM"
    elif hour < 12:
        return hour, "AM"
    elif hour == 12:
        return 12, "PM"
    else:
        return hour % 12, "PM"


def rename_file(filename: str) -> int:
    """
    @brief  Re-names a JPG file to the format of YYYY-MM-DD hh:mm.jpg, where date and time information is taken from
            the file's "Date taken" field
    @param  filename (str): The full initial filename of the JPG, including the extension
    @return (int)
            - 0 if the file was successfully renamed
            - 1 if an error occurred
    """
    if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
        # Get date taken from a photo
        extension = ".jpg"
        try:
            exif_dict = piexif.load(filename)
        except piexif.InvalidImageDataError:
            print(f'{red("ERROR")} - Could not load image data from "{filename}"')
            return 1

        # Get date taken
        try:
            date_taken_bytes = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]
        except KeyError:
            print(f'{filename} could not be renamed because it has no "date taken" attribute')
            return 1

        date_taken_string = date_taken_bytes.decode("utf-8")

        date_taken, time_taken = date_taken_string.split(" ")
        year, month, day = [int(i) for i in date_taken.split(":")]
        hour, minute = [int(i) for i in time_taken.split(":")]
    else:
        # Get date taken from a video
        extension = ".mp4"
        try:
            video = MP4(filename)
        except mutagen.mp4.MP4StreamInfoError:
            print(f"{red('ERROR')} - Could not load video data from '{filename}'")
            return 1

        date_stamp = video.get("\xa9day")
        if date_stamp is None:
            # Have the user manually enter the date
            year, month, day, hour, minute = manual_date_entry(filename)
        else:
            if len(date_stamp.split("T")) != 2:
                year, month, day, hour, minute = manual_date_entry(filename)
            else:
                date_taken, time_taken = date_stamp.split("T")
                year, month, day = [int(i) for i in date_taken.split("-")]
                hour, minute = [int(i) for i in time_taken.split(":")[0:2]]

    # Print photo/video taken time
    display_hour, am_pm = military_to_standard_time(hour)
    if hour == 0:
        print(f"{filename} was taken on {month}/{day}/{year} at {display_hour}:{str(minute).zfill(2)} {am_pm}")

    file_name = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)} {str(hour).zfill(2)}-{str(minute).zfill(2)}"

    # Get sequence number if it's a repeated date and time
    try:
        seq_num = seq_nums[file_name]
    except KeyError:
        seq_num = 0

    # Add the sequence number to the file name
    if seq_num > 0:
        # Increment sequence number and append current sequence number to the file name
        seq_nums[file_name] = seq_num + 1
        file_name = f"{file_name} {seq_num}"

    # Rename file
    try:
        os.rename(filename, f"{file_name}{extension}")
        print(f'{green("Renaming")} {filename} -> {file_name}{extension}')
    except FileExistsError:
        # If that file name is already in use, change the existing one to 1, and add to sequence number dictionary
        os.rename(f"{file_name}{extension}", f"{file_name} 1{extension}")
        print(f'{green("Renaming")} {file_name}{extension} -> {file_name} 1{extension}')
        os.rename(filename, f"{file_name} 2{extension}")
        print(f'{green("Renaming")} {filename} -> {file_name} 2{extension}')
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
        if os.path.isdir(filename):
            main(f"{os.getcwd()}\\{filename}")
            os.chdir(directory)
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg") or filename.lower().endswith(".mp4"):
            rename_file(filename)

    return 0


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("directory", help="The directory to search for JPGs to rename")
    args = parser.parse_args()

    sys.exit(main(args.directory))
