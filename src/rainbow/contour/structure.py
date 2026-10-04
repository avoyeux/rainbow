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

# API public
__all__ = ['Stereo', 'Sdo']



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
            int | None: Number in the filename if it exists, None otherwise.
        """

        match = Stereo.pattern.match(os.path.basename(Stereo.int_paths[index]))
        if match is None: return
        return int(match.group('number'))

    @staticmethod
    def timestamp(index: int) -> str | None:
        """
        Gives the timestamp in the filename given the corresponding image index.

        Arguments:
            index -- int.
                Index of the image.

        Returns:
            str | None: Timestamp in the filename if it exists, None otherwise.
        """

        match = Stereo.pattern.match(os.path.basename(Stereo.int_paths[index]))
        if match is None: return
        stamp = (
            f"{match.group('year')}-{match.group('month')}-{match.group('day')}T"
            f"{match.group('hour')}:{match.group('minute')}:{match.group('second')}"
        )
        return stamp

    @staticmethod
    def mask_path(index: int) -> str | None:
        """
        The fullpath to the mask corresponding to the given image index.

        Arguments:
            index -- int.
                Index of the image.

        Returns:
            str | None: Fullpath to the mask if it exists, None otherwise.
        """

        filepath = os.path.join(Stereo.mask_dir, f'frame{index:04d}.png')
        if not os.path.isfile(filepath): return
        return filepath


class Sdo:
    """
    Utilities to find and process the SDO images.
    """

    fits: list[str] = sorted(glob(os.path.join(config.dir.input.sdo.fits, '*.fits.gz')))
    png: list[str] = sorted(glob(os.path.join(config.dir.input.sdo.png, '*.png')))
