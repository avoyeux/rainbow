"""
Contains the main code to do the processing for a given plot.
"""
from __future__ import annotations

# IMPORTs standard
import os

# IMPORTs local
from .plot import Plot
from .structure import Data, Stereo, Sdo

# API public
__all__ = ['Create']



class Create:
    # todo add docstring

    def __init__(self, index: int, verbose: int = 0, flush: bool = False) -> None:
        # todo add docstring

        # CONFIG
        self._verbose = verbose
        self._flush = flush

        # ARGs
        self._index = index

        # RUN
        self._run()

    def _run(self) -> None:
        """
        Creates a single 3*3 image plot.
        """

        # INFO general
        number = Stereo.number(self._index)
        if number is None:
            raise ValueError(
                f"The string {os.path.basename(Stereo.int_paths[self._index])} has the wrong format."
            )
        timestamp = Stereo.timestamp(number)

        # DATA
        stereo_304_raw = Stereo.get_image_raw(number)
        stereo_304_avg = Stereo.get_image_avg(number)
        stereo_304_mask = Stereo.get_mask(number)

        sdo_304 = Sdo.get_fits(timestamp, nice=False)
        sdo_304_header = sdo_304[0]
        sdo_304_data = sdo_304[1]
        sdo_304_mask = Sdo.get_mask(number)

        # FORMAT
        stereo_171 = Data(
            raw='', # ! placeholder
            avg='', # ! placeholder
            mask=None,
        )
        stereo_304 = Data(
            raw=stereo_304_raw,
            avg=stereo_304_avg,
            mask=stereo_304_mask,
        )
        sdo_171 = Data(
            raw='', # ! placeholder
            avg='', # ! placeholder
            mask=None,
        )
        sdo_304 = Data(
            raw=sdo_304_data,
            avg=None, #type:ignore #! no avg exists 
            mask=sdo_304_mask,
            header=sdo_304_header,
        )

        # PLOT
        Plot(
            number,
            stereo_171,
            stereo_304,
            sdo_171,
            sdo_304,
            verbose=self._verbose - 1,
            flush=self._flush,
        )
