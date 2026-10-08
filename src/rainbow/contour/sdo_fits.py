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
            SDO FITS filepath. Timestamps are in the format 'YYYY-MM-DDTHH:MM'.
    """

    # Setup
    filepath_end = '/S00000/image_lev1.fits'
    with open(config.file.timestamps, 'r') as files:
        strings = files.read().splitlines()
    tuple_list = [s.split(" ; ") for s in strings]

    timestamp_to_path = {}
    for s in tuple_list:
        path, timestamp = s

        # EXCEPTIONs
        without_seconds = timestamp[:-6]
        if without_seconds == '2012-07-24T20:07':
            without_seconds = '2012-07-24T20:06'
        elif without_seconds == '2012-07-24T20:20':
            without_seconds = '2012-07-24T20:16'

        # POPULATE
        timestamp_to_path[without_seconds] = path + filepath_end
    return timestamp_to_path
