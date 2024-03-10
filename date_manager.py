"""
@package    date_manager
@brief      A script to allow editing the datestamps in JPG photo files either manually, or by copying the "Date taken" field
            to other date fields

@date       1/9/2022
@updated    3/10/2024

@author     Preston Buterbaugh
@credit     Adjust date code from https://stackoverflow.com/questions/33031663/how-to-change-image-captured-date-in-python
@credit     Piexif info from https://piexif.readthedocs.io/en/latest/functions.html
@credit     Conversion from bytes to string from https://www.pythonpool.com/python-bytes-to-string/
"""

# Imports
from argparse import ArgumentParser
import os
import sys
from typing import List

import piexif
from piexif import InvalidImageDataError

from custom.prestonpython import red, green


def adjust_date(filename: str, date: List | None = None) -> int:
    """
    @brief  Takes the name of a JPG file, and the numeric components of a date stamp and sets all date fields on the JPG file
            to this date
    @param filename (str)          The filename for the photo, including the ".jpg" extension
    @param date     (List or None) The new date to apply to the photo in a list formatted as follows:
        - year   (int) The year in which the picture was taken
        - month  (int) The month in which the picture was taken (1-12)
        - day    (int) The day on which the picture was taken (1-31)
        - hour   (int) The hour in which the picture was taken (0-23)
        - minute (int) The minute in which the picture was taken (0-59)
        - second (int) The second at which the picture was taken (0-59)
    @return (int)
        - 0 if the dates were successfully updated
        - 1 otherwise
    @note If "date" parameter is set to its default value of none, the value will be copied out of the "date taken"
          field to populate the "date created" field
    """
    # Create a dictionary of the photo's metadata
    try:
        exif_dict = piexif.load(filename)
    except InvalidImageDataError:
        print(f'{red("ERROR")} - {filename} is not a JPG image')
        return 1

    # Create variables to hold each part of the new date
    if date is not None:
        # Get the date supplied by the user
        try:
            date_taken_month = int(date[1])
            date_taken_day = int(date[2])
            date_taken_year = int(date[0])
            date_taken_hour = int(date[3])
            date_taken_minute = int(date[4])
            date_taken_second = int(date[5])
        except IndexError:
            print(f'{red("ERROR")} - Not enough values provided for new date (must include year, month, day, hour, minute, and second')
            return 1
        except ValueError:
            print(f'{red("ERROR")} - All date values provided must be numeric values')
            return 1
    else:
        # Get the value of the "date taken field"
        try:
            date_taken_bytes = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
        except KeyError:
            print(f'{red(filename)} has no "date taken" field')
            return 1

        # Get the individual date components
        date_taken = date_taken_bytes.decode('utf-8')
        date_taken_date_component = date_taken.split(' ')[0]
        date_taken_time_component = date_taken.split(' ')[1]

        date_taken_year = int(date_taken_date_component.split(':')[0])
        date_taken_month = int(date_taken_date_component.split(':')[1])
        date_taken_day = int(date_taken_date_component.split(':')[2])

        date_taken_hour = int(date_taken_time_component.split(':')[0])
        date_taken_minute = int(date_taken_time_component.split(':')[1])
        date_taken_second = int(date_taken_time_component.split(':')[2])

    # Print date
    if date_taken_hour == 0:
        print(f'Setting date for {filename} to {green(f"{date_taken_month}/{date_taken_day}/{date_taken_year} 12:{str(date_taken_minute).zfill(2)} AM")}')
    elif date_taken_hour == 12:
        print(f'Setting date for {filename} to {green(f"{date_taken_month}/{date_taken_day}/{date_taken_year} 12:{str(date_taken_minute).zfill(2)} PM")}')
    elif date_taken_hour > 12:
        print(f'Setting date for {filename} to {green(f"{date_taken_month}/{date_taken_day}/{date_taken_year} {date_taken_hour - 12}:{str(date_taken_minute).zfill(2)} PM")}')
    else:
        print(f'Setting date for {filename} to {green(f"{date_taken_month}/{date_taken_day}/{date_taken_year} {date_taken_hour}:{str(date_taken_minute).zfill(2)} AM")}')

    date_taken = f'{date_taken_year}:{date_taken_month}:{date_taken_day} {date_taken_hour}:{date_taken_minute}:{date_taken_second}'

    # Set date created
    exif_dict['0th'][piexif.ImageIFD.DateTime] = bytes(date_taken, 'utf-8')

    # Set other date fields if user supplied date to override existing data
    if date is not None:
        exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = bytes(date_taken, 'utf-8')
        exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = bytes(date_taken, 'utf-8')

    # Write EXIF data
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, filename)

    return 0


def get_date_list() -> List:
    """
    @brief  Prompts the user to enter a date and returns it as a list of numbers
    @return (List) The list of numbers representing the date
    """
    # Read in date string, and split on '/' characters into variables for month, day, and year
    while True:
        try:
            month, day, year = input('Enter the new date to apply to the selected photos (in the format MM/DD/YYYY): ').split('/')
            month = int(month)
            day = int(day)
            year = int(year)
            return [year, month, day]
        except ValueError as err:
            error_text = str(err)
            if error_text.startswith('not enough values to unpack'):
                print(f'{red("ERROR")} - Date not formatted correctly, must be MM/DD/YYYY')
            elif error_text.startswith('invalid literal for int() with base 10: '):
                print(f'{red(error_text[41:])} is not a valid numeric value. All date components must be numeric')
            else:
                print(red('Error occurred:'))
                print(err)


def get_time_list(filename: str) -> List:
    """
    @brief  Prompts the user to enter a timestamp and returns it as a list of numbers
    @param  filename (str): The name of the photo being updated (used for prompting)
    @return (List) The list of numbers representing the date
    """
    # Read in timestamp string, and split on ':' characters into variables for hour, minute, and second
    while True:
        try:
            hour, minute, second = input(f'Enter the new time to apply to {filename} (in the format hh:mm:ss): ').split(':')
            hour = int(hour)
            minute = int(minute)
            second = int(second)
            return [hour, minute, second]
        except ValueError as err:
            error_text = str(err)
            if error_text.startswith('not enough values to unpack'):
                print(f'{red("ERROR")} - Timestamp not formatted correctly, must be hh:mm:ss')
            elif error_text.startswith('invalid literal for int() with base 10: '):
                print(f'{red(error_text[41:])} is not a valid numeric value. All timestamp components must be numeric')
            else:
                print(red('Error occurred:'))
                print(err)


def update_sequence(tag_line: str, start_num: int, end_num: int, date: List | None = None) -> int:
    """
    @brief  Applies a new date and time to a sequence of photos all named with a comon tagline, with a hyphen and a number appended
    @param  tag_line (str): The common tagline shared by all photos in the sequence
    @param  start_num (int): The number appended to the first photo
    @param  end_num (int): The number appended to the last photo
    @param  date    (List): The date to apply to all the photos in the sequence formatted as follows:
        - year   (int) The year in which the picture was taken
        - month  (int) The month in which the picture was taken (1-12)
        - day    (int) The day on which the picture was taken (1-31)
    @return (int)
        - 0 if all photos successfully updated
        - 1 otherwise
    @note   Sequences must all take place over the same day. If a single sequence includes photos which were taken on different days
            the function must be called multiple times, with different start and end numbers to update all photos in the sequence.
            Each individual call must only include photos taken on a single day. It is assumed that the sequence includes all the
            numbers between start and end, and only those numbers
    """
    # Iterate over each photo and update the date
    errors = 0
    for i in range(start_num, end_num + 1, 1):
        # Construct file name and check both .jpg and .jpeg extensions
        filename = tag_line + '-' + str(i) + '.jpg'
        if not os.path.isfile(filename):
            filename = f'{filename[0:len(filename) - 1]}eg'

        # Check if single-digit number may need "0" prepended
        if i < 10 and not os.path.isfile(filename):
            filename = tag_line + '-0' + str(i) + '.jpg'
        if not os.path.isfile(filename):
            filename = f'{filename[0:len(filename) - 1]}eg'

        # Check if it is a valid file, and then adjust the date
        if not os.path.isfile(filename):
            print(f'{red(filename)} could not be updated. That file could not be found in the specified directory')
            errors = errors + 1
        elif date is None:
            errors = errors + adjust_date(filename)
        else:
            errors = errors + adjust_date(filename, date + get_time_list(filename))

    # Return depending on if any errors occurred
    if not errors:
        print(f'All photos in the sequence "{green(tag_line)}" were successfully updated')
        return 0
    if errors == (end_num - start_num) + 1:
        print('No photos could be updated')
    else:
        print('Some photos could not be updated')
    return 1
    

def update_directory(date: List | None = None) -> int:
    """
    @brief  Applies a new date and time to all photos in the working directory
    @param  directory (str): The directory which contains the photos to be updated
    @param  date      (List): The date to apply to all the photos in the sequence formatted as follows:
        - year   (int) The year in which the picture was taken
        - month  (int) The month in which the picture was taken (1-12)
        - day    (int) The day on which the picture was taken (1-31)
    @return (int)
        - 0 if all photos successfully updated
        - 1 otherwise
    @note   The directory must contain only take place over the same day. If it includes photos which were taken on different days,
            the user should utilize the update_sequence() function multiple times, instead
    """
    # Iterate over each photo and update the date
    errors = 0
    file_list = os.listdir(os.getcwd())
    for filename in file_list:
        # Update date
        if date is None:
            errors = errors + adjust_date(filename)
        else:
            errors = errors + adjust_date(filename, date + get_time_list(filename))

    # Return depending on if any errors occurred
    if not errors:
        print(f'All photos in the directory were successfully updated')
        return 0
    if errors == len(file_list):
        print('No photos could be updated')
    else:
        print('Some photos could not be updated')
    return 1


def has_date_taken(multiple: bool) -> bool:
    """
    @brief  Helper function to prompt the user if the photo(s) to be edited have the "date taken" field
    @param  multiple (bool): If the user is working with multiple photos (used for prompting)
    @return (bool) If the photos have the "date taken" field
    """
    while True:
        if multiple:
            print('Do the photos have a "date taken" field to copy the date from? If not, you can manually enter the date and time')
        else:
            print('Does the photo have a "date taken" field to copy the date from? If not, you can manually enter the date and time')
        key = input('Type y or n: ')
        if key != 'y' and key != 'n':
            if multiple:
                print('Please type y or n to indicate if the photos have a "date taken" field')
            else:
                print('Please type y or n to indicate if the photo has a "date taken" field')
        else:
            return key == 'y'


def main(directory: str | None = None) -> int:
    """
    @brief  Allows the user to choose a method by which photo dates should be updated
    @param  directory (str or None): The directory containing the photos to be updated. Current directory if None
    @return (int)
        - 0 if program completes successfully
        - 1 otherwise
    """
    # Change working directory
    if directory:
        try:
            os.chdir(directory)
        except FileNotFoundError:
            print(f'{red("ERROR")} - The directory {red(directory)} does not exist')
            return 1

    # Print welcome message
    print("Preston's photo timestamp editor - Allows you to edit the timestamps of JPG photos")

    # Get operating mode
    print('Choose your photo editing mode: ')
    print('s - Single: Edits the date on a single photo')
    print('m - Multiple: Allows you to specify a common name shared by many photos in a numbered sequence of photos to update')
    print('d - Directory: Edits the date of all JPG files in the working directory')
    choice = ''
    while choice != 's' and choice != 'm' and choice != 'd':
        choice = input().lower()
        if choice != 's' and choice != 'm' and choice != 'd':
            print('Please select a valid option from the menu above:')

    if choice == 's':
        print('Single edit')
        filename = input('Please enter the name of the picture to edit (including the .jpg or .jpeg extension')
        if has_date_taken(False):
            return adjust_date(filename)
        else:
            return adjust_date(filename, get_date_list() + get_time_list(filename))
    elif choice == 'm':
        print('Multiple edit')

        # Get name information
        tag_line = input('Enter the tagline of the photos (e.g "Cape Cod"): ')
        start_num = int(input('Enter the starting photo number: '))
        end_num = int(input('Enter the ending photo number: '))
        while end_num < start_num:
            end_num = int(input('Ending photo number must be equal or greater than the starting photo number. Please enter a new ending number: '))

        # Get date information
        if has_date_taken(True):
            return update_sequence(tag_line, start_num, end_num)
        else:
            return update_sequence(tag_line, start_num, end_num, get_date_list())
    else:
        print('Directory edit')
        if has_date_taken(True):
            return update_directory()
        else:
            return update_directory(get_date_list())


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--directory', '-d', default=None, help='The directory containing the photos on which to edit the datestamp')
    args = parser.parse_args()
    sys.exit(main(args.directory))
