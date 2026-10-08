"""
Code to get the SDO fits images from the server.
"""
from __future__ import annotations

# IMPORTs standard
import os

# IMPORTs local
from ..config import config

# API public
__all__ = ['sdo_image_finder']



def sdo_image_finder() -> dict[str, str]:
    """
    Gives the relation between a timestamp and the corresponding SDO FITS filepath.

    Returns:
        dict[str, str]
            Dictionary with the keys representing the timestamps and the values the corresponding
            SDO FITS filepath. Timestamps are in the format 'YYYY-MM-DDTHH:MM:SS'.
    """

    # Setup
    filepath_end = '/S00000/image_lev1.fits'
    with open(config.file.timestamps, 'r') as files:
        strings = files.read().splitlines()
    tuple_list = [s.split(" ; ") for s in strings]

    timestamp_to_path = {}
    for s in tuple_list:
        path, timestamp = s
        print(timestamp[:-3])
        timestamp_to_path[timestamp[:-3]] = path + filepath_end
    return timestamp_to_path
