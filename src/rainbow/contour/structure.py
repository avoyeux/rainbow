"""
Contains the codes related to the structure of the files related to the 'contour' plot.
"""
from __future__ import annotations

# IMPORTs standard
import os
import re
from glob import glob

# IMPORTs third-party
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits

# IMPORTs local
from ..config import config
from .sdo_fits import sdo_image_finder

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import numpy.typing as npt

# API public
__all__ = ['Data', 'Stereo', 'Sdo']

# todo add the opening of the images directly here



class Data:
    # todo add docstring
    # todo add the method to get the numpy array corresponding to the images.
    __slots__ = ('raw', 'avg', 'mask', 'header')

    def __init__(
            self,
            raw: npt.NDArray[np.float64],
            avg: npt.NDArray[np.float64],
            mask: npt.NDArray[np.bool_] | None = None,
            header: dict[str, str] | None = None,
        ) -> None:
        # todo add docstring

        self.raw = raw
        self.avg = avg
        self.mask = mask
        self.header = header


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
            f"{match.group('hour')}:{match.group('minute')}"
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

    @staticmethod
    def get_image_raw(number: int) -> npt.NDArray[np.float64]:
        """
        Gives the image data as a numpy array.

        Arguments:
            number -- int.
                Number of the image.

        Returns:
            npt.NDArray[np.float64]
                Image data as a numpy array. Shape: (height, width)
        """
        return plt.imread(Stereo.int_paths[number]).mean(axis=-1)

    @staticmethod
    def get_image_avg(number: int) -> npt.NDArray[np.float64]:
        """
        Gives the average image data as a numpy array.

        Arguments:
            number -- int.
                Number of the image.

        Returns:
            npt.NDArray[np.float64]
                Average image data as a numpy array. Shape: (height, width)
        """
        return plt.imread(Stereo.avg_paths[number]).mean(axis=-1)

    @staticmethod
    def get_mask(number: int) -> npt.NDArray[np.bool_] | None:
        """
        Gives the mask data as a numpy array.

        Arguments:
            number -- int.
                Number of the image.

        Returns:
            npt.NDArray[np.bool_] | None
                Mask data as a numpy array. Shape: (height, width) if it exists, None otherwise.
        """

        path = Stereo.mask_path(number)
        if path is None: return
        return plt.imread(path).max(axis=-1).astype(np.bool_)


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
                Timestamp of the image with the format 'YYYY-MM-DDTHH:MM'.

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

    @staticmethod
    def get_fits(
            timestamp: str,
            nice: bool = True,
        ) -> tuple[dict[str, str], npt.NDArray[np.float64]]:
        """
        Gives the SDO FITS file header and image information.

        Arguments:
            timestamp -- str.
                Timestamp of the image with the format 'YYYY-MM-DDTHH:MM'.
            nice -- bool. (default: True)
                Whether to apply visualization processing to the data.

        Returns:
            tuple[dict[str, str], npt.NDArray[np.float64]]
                Header and image data.
        """

        # OPEN FITS file
        filepath = Sdo.fits_path(timestamp)
        hdul = fits.open(filepath)
        header = hdul[1].header
        data = hdul[1].data.astype(np.float64)  # todo make sure this doesn't fuck up
        hdul.close()

        # VISUALIZATION processing
        if nice:
            low, high = np.percentile(data, (0.5, 99.5))
            data = np.clip(data, max(low, 1), high)
            data = np.log(data)
        return header, data

    @staticmethod
    def get_mask(number: int) -> npt.NDArray[np.bool_] | None:
        """
        Gives the mask data as a numpy array.

        Arguments:
            number -- int.
                Number of the image.

        Returns:
            npt.NDArray[np.bool_] | None
                Mask data as a numpy array. Shape: (height, width) if it exists, None otherwise.
        ! For header information: use the header info from the corresponding data FITS.
        """

        # CHECK if it exists
        path = Sdo.mask_path(number)
        if path is None: return

        # OPEN fits file
        mask = fits.getdata(path, 0).astype(np.bool_)
        return mask
