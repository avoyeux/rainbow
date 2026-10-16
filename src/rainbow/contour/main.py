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
        number_171: int = Stereo.number(wave='171', index=self._index)  #type:ignore
        number_304: int = Stereo.number(wave='304', index=self._index)  #type:ignore

        # CHECK for None
        if any(number is None for number in [number_171, number_304]):
            raise ValueError(
                f"The string {os.path.basename(Stereo.int_304[self._index])} has the wrong format."
            )
        timestamp_304 = Stereo.timestamp(wave='304', number=number_304)

        # DATA
        stereo_171_raw = Stereo.get_image_raw(wave='171', number=number_171)
        stereo_171_avg = Stereo.get_image_avg(wave='171', number=number_171)
        stereo_304_raw = Stereo.get_image_raw(wave='304', number=number_304)
        stereo_304_avg = Stereo.get_image_avg(wave='304', number=number_304)
        stereo_304_mask = Stereo.get_mask(number_304)

        sdo_304 = Sdo.get_fits(timestamp_304, nice=False)
        sdo_304_header = sdo_304[0]
        sdo_304_data = sdo_304[1]
        sdo_304_mask = Sdo.get_mask(number_304)

        # FORMAT
        stereo_171 = Data(
            raw=stereo_171_raw, # ! check timestamp value first
            avg=stereo_171_avg,
            mask=None,
        )
        stereo_304 = Data(
            raw=stereo_304_raw,
            avg=stereo_304_avg,
            mask=stereo_304_mask,
        )
        sdo_304 = Data(
            raw=sdo_304_data,
            avg=None, #type:ignore #! no avg exists 
            mask=sdo_304_mask,
            header=sdo_304_header,
        )

        # PLOT
        Plot(
            number_304,
            stereo_171,
            stereo_304,
            sdo_304,
            verbose=self._verbose - 1,
            flush=self._flush,
        )
