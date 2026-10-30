"""
Contains code related to the creation of the plot showing the voxel volume.
"""
from __future__ import annotations

# IMPORTs standard
import os
from dataclasses import dataclass
from datetime import datetime, time

# IMPORTs third-party
import h5py
import numpy as np

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

from common import Decorators

class Volume:
    # todo add docstring

    @Decorators.running_time
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
        self._data = {
            'All data': self._get_data('All data'),
            'No duplicates': self._get_data('No duplicates'),
        }
        self._run()

    def _get_data(self, name: Literal['No duplicates', 'All data']) -> Data:
        """
        To get the data information.

        Returns:
            Data: the data information.
        """

        with h5py.File(config.file.data, 'r') as handle:
            # group = handle[f'Filtered/{name}']
            group = handle[f'Time integrated/{name}/Time integration of 6 hours']
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
        """
        To compute the voxel volume of each dataset and create the outputs.
        """

        self._hours = self._get_hours(next(iter(self._data.values())).dates)
        self._volumes = {name: self._get_volumes(data) for name, data in self._data.items()}

        if self._csv: self._create_csv()
        if self._plot: self.plot()

    @staticmethod
    def _get_hours(dates: npt.NDArray[np.str_]) -> npt.NDArray[np.float64]:
        """
        To get the time of each observation in hours since midnight of the first observation.

        Args:
            dates: the date strings in the 'yyyy-mm-ddThh-mm-ss' format.

        Returns:
            npt.NDArray[np.float64]: the hours since midnight of the first date.
        """

        datetimes = [datetime.strptime(date, '%Y-%m-%dT%H-%M-%S') for date in dates]
        midnight = datetime.combine(datetimes[0].date(), time.min)
        return np.array([(date - midnight).total_seconds() / 3600. for date in datetimes])

    @staticmethod
    def _get_volumes(data: Data) -> npt.NDArray[np.float64]:
        """
        To get the total volume (in Mm^3) of each observation of a dataset.

        Args:
            data: the data information of the dataset.

        Returns:
            npt.NDArray[np.float64]: the total volume in Mm^3 for each date.
        """

        counts = np.bincount(data.coords[0], minlength=data.dates.size)
        return counts * data.voxel_volume_km3() * 1e-9

    def plot(self) -> None:
        """
        To create the volume plot from the computed data.
        """

        Plot(hours=self._hours, volumes=self._volumes)

    def _create_csv(self) -> None:
        """
        To save the hours and the total volume of every dataset in a CSV file.
        """

        path = os.path.join(config.dir.output.results.volume, 'volume.csv')
        columns = np.column_stack([self._hours, *self._volumes.values()])
        header = ','.join(['hours', *self._volumes.keys()])
        np.savetxt(path, columns, delimiter=',', header=header, comments='')


if __name__ == '__main__':
    volume = Volume()
