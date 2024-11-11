#!/usr/bin/env python3.10

import os
import sys

from collections import defaultdict
from dataclasses import dataclass
from operator import attrgetter

from PIL import Image
from PIL import ExifTags

DATE_TAGS = (
    ExifTags.Base.DateTimeOriginal.value,
    ExifTags.Base.DateTime.value,
    ExifTags.Base.DateTimeDigitized.value,
)


@dataclass(frozen=True)
class ImagePath:
    path: str
    created_date: str

    @staticmethod
    def from_path(path: str):
        with open(path, "rb") as f:
            created_date = get_date(f)
            return ImagePath(path, created_date)


def main(args):
    items = [ImagePath.from_path(path) for path in args.images]
    groups = group_by(items, [lambda item: attrgetter("created_date")(item)])
    do_rename(
        groups, new_extension=args.extension, verbose=args.verbose, dry_run=args.dry_run
    )


def group_by(images, groupers):
    result = defaultdict(list)
    for image in images:
        key = tuple(grouper(image) for grouper in groupers)
        result[key].append(image)
    return result


def get_date(image) -> str | None:
    result = _get_created_date(image)
    if result is None:
        return None
    return format_date(result)


def _get_created_date(path: str) -> str | None:
    tags = Image.open(path).getexif()
    for key in DATE_TAGS:
        if key in tags:
            return tags.get(key)
    return None


def format_date(date_str: str) -> str | None:
    if not date_str:
        return None
    return date_str.split()[0].replace(":", "-")


def do_rename(
    data: dict[str, list[ImagePath]], new_extension=None, verbose=False, dry_run=True
):
    for _, paths in data.items():
        if not paths:
            raise Exception("Unexpectedly found empty group")
        indexed = len(paths) > 1
        for i, metadata in enumerate(paths):
            old = metadata.path
            date = metadata.created_date
            if date:
                path, extension = get_name_info(old)
                if new_extension:
                    extension = new_extension
                if extension[0] != ".":
                    extension = "." + extension
                new = os.path.join(
                    *path[:-1],
                    f"{date}_{i + 1}{extension}" if indexed else date + extension,
                )
                if verbose:
                    print(f"\t{old} => {new}")
                if not dry_run:
                    os.rename(old, new)
            else:
                print(f"failed to process {metadata}", file=sys.stderr)


def get_name_info(old):
    path = os.path.split(old)
    _, extension = os.path.splitext(old)
    return path, extension


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        "Rename the given images' to their content created dates"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="print the old and new file paths"
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="only calculate, don't change files",
    )
    parser.add_argument(
        "-x",
        "--extension",
        type=str,
        help="change the extension to the given extension",
    )
    parser.add_argument("images", type=str, nargs="+", help="images to rename")
    args = parser.parse_args()

    main(args)
