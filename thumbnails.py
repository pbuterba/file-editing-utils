"""
@package   thumbnails
@brief     Script for converting photos into thumbnail size by scaling them down
@copyright 2026 Preston Buterbaugh
@date      7/18/2026
@update    7/18/2026
@author    Preston Buterbaugh

@credit    geeksforgeeks.org/python/python-pil-image-resize-method/
"""
# Imports
from argparse import ArgumentParser
import os
import sys

from PIL import Image

from custom.prestonpython import red, green


def scale_directory(directory: str, scale_factor: float) -> None:
    """
    @brief Recursively searches a directory and scales all JPG images to
    @param directory:    The directory to search
    @param scale_factor: Multiplier to apply to image dimensions
    """
    for item in os.listdir(directory):
        path = f"{directory}\\{item}"

        if os.path.isdir(path):
            # If item is another directory, recursively call this function on it
            scale_directory(path, scale_factor)
        elif item.endswith(".jpg"):
            # Scale image by appropriate amount
            img = Image.open(path)

            # Calculate new dimensions
            width = img.width
            height = img.height
            scaled_width = int(width * scale_factor)
            scaled_height = int(height * scale_factor)

            # Create thumbnail
            thumbnail = img.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
            thumbnail_name = f"{item[0:len(item) - 4]}-thumbnail.jpg"
            thumbnail.save(f"{directory}\\{thumbnail_name}")

            # Close file descriptors
            img.close()
            thumbnail.close()

            # Announce picture resizing
            orig_image_with_size = f"{item} ({width}x{height})"
            scaled_image_with_size = f"{thumbnail_name} ({scaled_width}x{scaled_height})"
            print(f"Resized {green(orig_image_with_size)} to {green(scaled_image_with_size)}")
        else:
            print(f"Skipping {red(item)}, because it is not a JPEG image")


def main(directory: str, percent_scale: int) -> int:
    """
    @brief  Validates the input percentage to which to scale images, and begins recursive directory search
    @param  (str) directory:     The directory in which to scale the photos
    @param  (int) percent_scale: The percentage to which to scale the image's dimensions
    @return (int)
        - 0 if successful
        - 1 otherwise
    """
    # Validate input
    if percent_scale <= 0:
        percent_scale_with_sign = f"{percent_scale}%"
        print(f"{red(percent_scale_with_sign)} is an invalid scale size! Must be positive")
        return 1
    else:
        scale_factor = percent_scale / 100

    # Search directory recursively and scale all images
    if os.path.exists(directory) and os.path.isdir(directory):
        scale_directory(directory, scale_factor)
    else:
        print(f"{red(directory)} is not a valid directory")
        return 1


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--directory", "-d", help="Directory to search")
    parser.add_argument("--percentage", "-p", type=int, help="Percentage to which to scale all pictures")
    args = parser.parse_args()

    sys.exit(main(args.directory, args.percentage))
