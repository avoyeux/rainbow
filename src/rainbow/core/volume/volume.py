"""
Contains code related to the creation of the plot showing the voxel volume.
"""
from __future__ import annotations

# IMPORTs standard
from dataclasses import dataclass

# IMPORTs third-party
import h5py
import numpy as np
import matplotlib.pyplot as plt

# IMPORTs local
from .data import Data
from .plot import Plot
from rainbow.config import config

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    import numpy.typing as npt

# API public
__all__ = ['Volume']



class Volume:
    # todo add docstring

    def __init__(
            self,
            csv: bool = True,
            plot: bool = True,
            verbose: int = 0,
            flush: bool = False,
        ) -> None:
        # todo add docstring

        # CONFIG
        self._csv = csv
        self._plot = plot
        self._verbose = verbose
        self._flush = flush

        # RUN
        self._all_data = self._get_data('All data')
        self._no_duplicates = self._get_data('No duplicates')

    def _get_data(self, name: Literal['No duplicates', 'All data']) -> Data:
        """
        To get the data information.

        Returns:
            Data: the data information.
        """

        with h5py.File(config.file.data, 'r') as handle:
            group = handle[f'Filtered/{name}']
            data = Data(
                coords=group['coords'][...],
                xt_min=group['xt_min'][...],
                yt_min=group['yt_min'][...],
                zt_min=group['zt_min'][...],
                dates=handle['Dates'][...].astype(str),
                dx=float(handle['dx'][...]),  #type:ignore
            )
        return data

    def _run(self) -> None:
        # todo add docstring

        if self._csv: self._create_csv()
        if self._plot: self.plot()

    def plot(self) -> None:
        pass

    def _create_csv(self) -> None:
        pass