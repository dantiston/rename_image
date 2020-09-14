#!/usr/bin/env python3

import os

from collections import defaultdict
from typing import Dict, List, Optional

from PIL import Image

# From PIL.ExifTags.TAGS
CREATED_TIME_TAG = 36867


def main(args):
    images = defaultdict(list)
    for image in args.images:
        date = get_date(image)
        if date is not None:
            date = format_date(date)
            images[date].append(image)
    do_rename(images, args.verbose)


def get_date(image):
    return get_created_date(image)


def do_rename(data: Dict[str, List], verbose=False):
    for date, images in data.items():
        if not images:
            raise Exception("Bad things happened")
        if len(images) == 1:
            old = images[0].name
            path, extension = get_name_info(old)
            new = os.path.join(*path[:-1], date + extension)

            if verbose: print(f"{old} => {new}")
            os.rename(old, new)
        else:
            for i, image in enumerate(images):
                old = image.name
                path, extension = get_name_info(old)
                new = os.path.join(*path[:-1], f"{date}_{i + 1}{extension}")

                if verbose: print(f"\t{old} => {new}")
                os.rename(old, new)


def get_name_info(old):
    path = os.path.split(old)
    _, extension = os.path.splitext(old)
    return path, extension


def get_created_date(f) -> Optional[str]:
    try:
        return Image.open(f).getexif().get(CREATED_TIME_TAG, None)
    except Exception as e:
        return None


def format_date(date_str: str) -> Optional[str]:
    if not date_str:
        return None
    return date_str.split()[0].replace(":", "-")


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser("Rename the given images' to their content created dates")
    parser.add_argument("-v", "--verbose", type=bool, help="print the old and new file paths")
    parser.add_argument("images", type=argparse.FileType('rb'), nargs='+', help="images to rename")
    args = parser.parse_args()

    main(args)

