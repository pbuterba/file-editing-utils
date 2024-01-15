"""
@package    date_manager
@brief      A script to allow editing the datestamps in JPG photo files either manually, or by copying the "Date taken" field
            to other date fields

@date       1/9/2022
@updated    1/14/2024

@author     Preston Buterbaugh
@credit     Adjust date code from https://stackoverflow.com/questions/33031663/how-to-change-image-captured-date-in-python
@credit     Piexif info from https://piexif.readthedocs.io/en/latest/functions.html
@credit     Conversion from bytes to string from https://www.pythonpool.com/python-bytes-to-string/
"""

# Imports
from datetime import datetime
import os
import sys

import piexif
from piexif import InvalidImageDataError


from custom.prestonpython import red, green


def copy_date_taken(filename: str) -> int:
    """
    @brief  Takes the name of a JPG file and copies its "Date Taken" field to the picture's date field
    @param  filename (str): The filename of the photo to be edited, including the extension
    @return (int)
            - 0 if successful
            - 1 otherwise
    """
    # Create a dictionary of the photo's metadata
    try:
        exif_dict = piexif.load(filename)
    except InvalidImageDataError:
        print(f'{red("ERROR")} - {filename} is not a JPG image')
        return 1

    # Create a datetime variable with the new date and time
    new_date = datetime(year, month, day, hour, minute, second).strftime("%Y:%m:%d %H:%M:%S")

    # Update date created with new date
    date_taken_bytes = exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal]
    date_taken = date_taken_bytes.decode('utf-8')
    date_taken_date_component = date_taken.split(' ')[0]
    date_taken_time_component = date_taken.split(' ')[1]

    date_taken_year = int(date_taken_date_component.split(':')[0])
    date_taken_month = int(date_taken_date_component.split(':')[1])
    date_taken_day = int(date_taken_date_component.split(':')[2])

    date_taken_hour = int(date_taken_time_component.split(':')[0])
    date_taken_minute = int(date_taken_time_component.split(':')[1])
    date_taken_second = int(date_taken_time_component.split(':')[2])

    date_taken = f'{date_taken_year}:{date_taken_month}:{date_taken_day} {date_taken_hour}:{date_taken_minute}:{date_taken_second}'

    # Set date created
    exif_dict['0th'][piexif.ImageIFD.DateTime] = bytes(date_taken, 'utf-8')
    # exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = new_date
    # exif_dict['Exif'][piexif.ExifIFD.DateTimeDigitized] = new_date
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, filename)


def date_change_single(Tagline):
    # Read in date string, and split on '/' characters into variables for month day and year
    DateStringList = input('Enter the new date to apply to the photo: ').split('/')
    Month = int(DateStringList[0])
    Day = int(DateStringList[1])
    Year = int(DateStringList[2])

    # Update the date
    adjust_date(Tagline, Year, Month, Day, 0, 0 ,0)


def date_change(Tagline, StartNum, EndNum):
    # Read in date string, and split on '/' characters into variables for month day and year
    DateStringList = input('Enter the new date to apply to all photos: ').split('/')
    Month = int(DateStringList[0])
    Day = int(DateStringList[1])
    Year = int(DateStringList[2])

    # Iterate over each photo and update the date
    for i in range(StartNum, EndNum + 1, 1):
        PhotoNum = i
        Name = Tagline + '-' + str(PhotoNum) + '.jpg'
        if PhotoNum < 10 and not os.path.isfile(Name):
            Name = Tagline + '-0' + str(PhotoNum) + '.jpg'
        adjust_date(Name, Year, Month, Day, 0, 0, 0)
    
def time_change_single(Tagline, isApproximate):
    # Create variables to hold the date and timestamp obtained from the photo's current timestamp
    PhotoMetaData = piexif.load(Tagline)
    InternalDateTimeStamp = ''.join(map(chr, PhotoMetaData['Exif'][piexif.ExifIFD.DateTimeOriginal]))
    InternalDateStamp = InternalDateTimeStamp.split(' ')[0]
    InternalTimeStamp = InternalDateTimeStamp.split(' ')[1]

    # Read in the time to set the photo to, and create variables for all components of the new date and time
    TimeStringList = input('Enter the time for the photo: ').split(':')
    Year = int(InternalDateStamp.split(':')[0])
    Month = int(InternalDateStamp.split(':')[1])
    Day = int(InternalDateStamp.split(':')[2])
    Hour = int(TimeStringList[0])
    Minute = int(TimeStringList[1])
    if len(TimeStringList) == 3:
        Second = int(TimeStringList[2])
    else:
        Second = 0
    adjust_date(Name, Year, Month, Day, Hour, Minute, Second)

    # Create a marker file if times are approximate
    if isApproximate:
        target = open("Times Approximate", 'a')
        target.close()

def time_change(Tagline, StartNum, EndNum, isApproximate):
    # Iterate over each photo
    for i in range(StartNum, EndNum + 1, 1):
        PhotoNum = i
        if PhotoNum < 10:
            Name = Tagline + '-0' + str(PhotoNum) + '.jpg'
        else:
            Name = Tagline + '-' + str(PhotoNum) + '.jpg'
        # Create variables to hold the date and timestamp obtained from the photo's current timestamp
        PhotoMetaData = piexif.load(Name)
        InternalDateTimeStamp = ''.join(map(chr, PhotoMetaData['Exif'][piexif.ExifIFD.DateTimeOriginal]))
        InternalDateStamp = InternalDateTimeStamp.split(' ')[0]
        InternalTimeStamp = InternalDateTimeStamp.split(' ')[1]

        # Read in the time to set the photo to, and create variables for all components of the new date and time
        TimeStringList = input('Enter the time for ' + Name + ': ').split(':')
        Year = int(InternalDateStamp.split(':')[0])
        Month = int(InternalDateStamp.split(':')[1])
        Day = int(InternalDateStamp.split(':')[2])
        Hour = int(TimeStringList[0])
        Minute = int(TimeStringList[1])
        if len(TimeStringList) == 3:
            Second = int(TimeStringList[2])
        else:
            Second = 0
        adjust_date(Name, Year, Month, Day, Hour, Minute, Second)

    # Create a marker file if times are approximate
    if isApproximate:
        target = open("Times Approximate", 'a')
        target.close()

def time_change_series(Tagline, StartNum, EndNum):
    # Obtain interval
    inter = int(input('Enter the number of seconds to increase the timestamp of each photo by: '))

    # Follow normal process for first photo
    Name = Tagline + '-' + str(StartNum) + '.jpg'
    
    # Create variables to hold the date and timestamp obtained from the photo's current timestamp
    PhotoMetaData = piexif.load(Name)
    InternalDateTimeStamp = ''.join(map(chr, PhotoMetaData['Exif'][piexif.ExifIFD.DateTimeOriginal]))
    InternalDateStamp = InternalDateTimeStamp.split(' ')[0]
    InternalTimeStamp = InternalDateTimeStamp.split(' ')[1]

    # Read in the time to set the photo to, and create variables for all
    # components of the new date and time
    TimeStringList = input('Enter the time for ' + Name + ': ').split(':')
    Year = int(InternalDateStamp.split(':')[0])
    Month = int(InternalDateStamp.split(':')[1])
    Day = int(InternalDateStamp.split(':')[2])
    Hour = int(TimeStringList[0])
    Minute = int(TimeStringList[1])
    if len(TimeStringList) == 3:
        Second = int(TimeStringList[2])
    else:
        Second = 0
    adjust_date(Name, Year, Month, Day, Hour, Minute, Second)

    # Iterate over each photo
    for i in range(StartNum + 1, EndNum + 1, 1):
        # Increase all time variables
        Second += inter
        if Second >= 60:
            Second -= 60
            Minute += 1
        if Minute >= 60:
            Minute -= 60
            Hour += 1
        if Hour >= 24:
            raise Exception("Error - The specified interval will carry photo times into the next day. Please re-run the program and use an earlier time for the first photo or a smaller interval between photos.")
        PhotoNum = i
        if PhotoNum < 10:
            Name = Tagline + '-0' + str(PhotoNum) + '.jpg'
        else:
            Name = Tagline + '-' + str(PhotoNum) + '.jpg'

        # Create variables to hold the date and timestamp obtained from the photo's current timestamp
        PhotoMetaData = piexif.load(Name)
        InternalDateTimeStamp = ''.join(map(chr, PhotoMetaData['Exif'][piexif.ExifIFD.DateTimeOriginal]))
        InternalDateStamp = InternalDateTimeStamp.split(' ')[0]
        InternalTimeStamp = InternalDateTimeStamp.split(' ')[1]
        
        # Read the Year, Month, and Day from the photo's timestamp
        # Technically this is not necessary since all photos in a batch must have been taken on the same day
        Year = int(InternalDateStamp.split(':')[0])
        Month = int(InternalDateStamp.split(':')[1])
        Day = int(InternalDateStamp.split(':')[2])
        
        adjust_date(Name, Year, Month, Day, Hour, Minute, Second)

    # Create a marker file
    target = open("Times approximate.txt", 'a')
    target.write("Times were determined for these photos by approximating a time for the first photo in the series, and increasing the time by " + str(inter) + " seconds for each subsequent photo")
    target.close()


os.chdir(sys.argv[1])
print('Preston\'s photo timestamp editor. Edit the date of photos in batches or for a single photo, and edit the timestamps of each photo individually. If the exact times are unknown and you do not wish to approximate times for every photo, choose to separate each photo by a fixed increment of time. The utility will also generate a file to indicate if times are exact or have been approximated.') 
print('Type a letter followed by enter to select a function: ')
print('s - Edit single photo')
print('u - Edit single photo with an approximate time')
print('b - Edit a batch of photos')
print('a - Edit a batch of photos with approximated times for each')
print('i - Edit a batch of photos with an equal interval of time between photos')
choice = input()

while choice != 's' and choice != 'u' and choice != 'b' and choice != 'a' and choice != 'i':
    choice = input('Please select a valid option from the menu above:\n')

if choice == 's' or choice == 'u':
    group = False
else:
    group = True

if choice == 's' or choice == 'b':
    approx = False
else:
    approx = True

if group:
    Tagline = input('Enter the tagline of the photo (e.g "Cape Cod"): ')
    StartNum = int(input('Enter the starting photo number: '))
    EndNum = int(input('Enter the ending photo number: '))
    while EndNum < StartNum:
        EndNum = int(input('Ending photo number must be equal or greater than the starting photo number. Please enter a new ending number: '))
    date_change(Tagline, StartNum, EndNum)
    # if choice == 'i':
        # time_change_series(Tagline, StartNum, EndNum)
    # else:
        # time_change(Tagline, StartNum, EndNum, approx)
else:
    PhotoName = input('Enter the photo name (e.g. "Snow on the Commons"): ')
    date_change_single(PhotoName)
    time_change_single(PhotoName, approx)
