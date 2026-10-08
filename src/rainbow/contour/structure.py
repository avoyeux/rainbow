"""
Contains the codes related to the structure of the files related to the 'contour' plot.
"""
from __future__ import annotations

# IMPORTs standard
import os
import re
from glob import glob

# IMPORTs local
from ..config import config
from .sdo_fits import sdo_image_finder

# API public
__all__ = ['Data', 'Stereo', 'Sdo']

# todo add the opening of the images directly here



class Data:
    # todo add docstring
    # todo add the method to get the numpy array corresponding to the images.
    __slots__ = ('raw', 'avg', 'mask')

    def __init__(
            self,
            raw: str,
            avg: str,
            mask: str | None,
        ) -> None:
        # todo add docstring

        self.raw = raw
        self.avg = avg
        self.mask = mask


class Stereo:
    """
    Utilities to find and process the stereo images.
    """

    int_paths: list[str] = sorted(glob(
        os.path.join(config.dir.input.stereo.int, '*.png')
    ))
    avg_paths: list[str] = sorted(glob(
        os.path.join(config.dir.input.stereo.avg, '*.png')
    ))
    mask_dir: str = config.dir.input.stereo.mask_karine

    pattern = re.compile(
        pattern=r'''
            (?P<number>\d{4})_
            (?P<year>\d{4})-
            (?P<month>\d{2})-
            (?P<day>\d{2})T
            (?P<hour>\d{2})-
            (?P<minute>\d{2})-
            (?P<second>\d{2}).
            \d{3}\.png
        ''',
        flags=re.VERBOSE,
    )

    @staticmethod
    def number(index: int) -> int | None:
        """
        Gives the number in the filename given the corresponding image index.
        Should be the same integer than 'index', but using this function so that the code still
        works if some files are lost.

        Arguments:
            index -- int.
                Index of the image.

        Returns:
            int | None
                Number in the filename if it exists, None otherwise.
        """

        match = Stereo.pattern.match(os.path.basename(Stereo.int_paths[index]))
        if match is None: return
        return int(match.group('number'))

    @staticmethod
    def timestamp(number: int) -> str:
        """
        Gives the timestamp in the filename given the corresponding image index.

        Arguments:
            number -- int.
                Number of the image.

        Raises:
            ValueError: If the number is not found in the stereo images.

        Returns:
            str
                Timestamp in the filename if it exists, None otherwise.
        """

        match = Stereo.pattern.match(os.path.basename(Stereo.int_paths[number]))
        if match is None:
            raise ValueError(f"Number {number} not found in the stereo images.")
        stamp = (
            f"{match.group('year')}-{match.group('month')}-{match.group('day')}T"
            f"{match.group('hour')}:{match.group('minute')}:{match.group('second')}"
        )
        return stamp

    @staticmethod
    def mask_path(number: int) -> str | None:
        """
        The fullpath to the mask corresponding to the given image index.

        Arguments:
            number -- int.
                Number of the image.

        Returns:
            str | None
                Fullpath to the mask if it exists, None otherwise.
        """

        filepath = os.path.join(Stereo.mask_dir, f'frame{number:04d}.png')
        if not os.path.isfile(filepath): return
        return filepath


class Sdo:
    """
    Utilities to find and process the SDO images.
    """

    _mask_dir: str = config.dir.input.sdo.mask
    _timestamp_to_path: dict[str, str] = sdo_image_finder()

    @staticmethod
    def mask_path(number: int) -> str | None:
        """
        The fullpath to the mask corresponding to the given image index.

        Arguments:
            number -- int.
                Number of the image.

        Returns:
            str | None
                Fullpath to the mask if it exists, None otherwise.
        """

        filepath = os.path.join(Sdo._mask_dir, f'AIA_fullhead_{number:03d}.fits.gz')
        if not os.path.isfile(filepath): return
        return filepath

    @staticmethod
    def fits_path(timestamp: str) -> str:
        """
        The fullpath to the SDO image corresponding to the given timestamp.

        Arguments:
            timestamp -- str.
                Timestamp of the image with the format 'YYYY-MM-DDTHH:MM:SS'.

        Raises:
            ValueError: If the timestamp is not found in the SDO image finder.

        Returns:
            str
                Fullpath to the SDO image.
        """

        filepath = Sdo._timestamp_to_path.get(timestamp, None)
        if filepath is None:
            raise ValueError(f"Timestamp {timestamp} not found in the SDO image finder.")
        return filepath
