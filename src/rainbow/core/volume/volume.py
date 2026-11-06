"""
Contains code related to the creation of the plot showing the voxel volume.
"""
from __future__ import annotations

# IMPORTs standard
import re
import os
from glob import glob
from dataclasses import dataclass
from datetime import datetime, time

# IMPORTs third-party
import h5py
import numpy as np
from PIL import Image
from astropy.io import fits

# IMPORTs personal
from common import Decorators

# IMPORTs local
from .data import Data, PData
from .plot import Plot
from rainbow.config import config

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    import numpy.typing as npt

# API public
__all__ = ['Volume']



class Volume:
    """
    To compute the voxel volume of each dataset and create the corresponding plot.
    """

    @Decorators.running_time
    def __init__(
            self,
            verbose: int = 0,
            flush: bool = False,
        ) -> None:
        """
        Computes the voxel volumes and the satellites' field of views.
        From there, it creates the corresponding plot.

        Arguments:
            verbose -- int (default: 0)
                The verbosity level for the prints.
            flush -- bool (default: False)
                Whether to flush the prints.
        """

        # CONFIG
        self._verbose = verbose
        self._flush = flush

        # INIT
        self._data = {
            'All data': self._get_data('All data'),
            'No duplicates': self._get_data('No duplicates'),
        }
        self._num = self._date_to_num()

        # RUN
        self._run()

        if verbose > 0: print('\033[90mVolume plot created.\033[0m', flush=flush)

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

        hours = self._get_hours(self._data['All data'].dates)
        fov_dates = list(self._num.keys())
        volume = PData(
            hours=hours,
            values=np.stack(
                arrays=[self._get_volumes(data) for data in self._data.values()],
                dtype=np.float32,
            ),
        )
        stereo = PData(
            hours=self._get_hours(np.array(fov_dates, dtype=np.str_)),
            values=np.stack(
                arrays=[
                    surface
                    if (surface := self._get_surface(date, 'Stereo')) is not None
                    else 0
                    for date in fov_dates
                ]
            )
        )
        sdo = PData(
            hours=self._get_hours(np.array(fov_dates, dtype=np.str_)),
            values=np.stack(
                arrays=[
                    surface
                    if (surface := self._get_surface(date, 'SDO')) is not None
                    else 0
                    for date in fov_dates
                ]
            )
        )

        # PLOT
        Plot(
            volume=volume,
            stereo=stereo,
            sdo=sdo,
        )

    def _get_hours(self, dates: npt.NDArray[np.str_]) -> npt.NDArray[np.float32]:
        """
        todo update docstring
        To get the time of each observation in hours since midnight of the first observation.

        Returns:
            npt.NDArray[np.float32]: the hours since midnight of the first date.
        """

        datetimes = [
            datetime.strptime(date, '%Y-%m-%dT%H-%M-%S')
            for date in dates
        ]
        midnight = datetime.combine(datetimes[0].date(), time.min)
        seconds = np.array(
            object=[(date - midnight).total_seconds() / 3600. for date in datetimes],
            dtype=np.float32,
        )
        return seconds

    @staticmethod
    def _get_volumes(data: Data) -> npt.NDArray[np.float32]:
        """
        To get the total volume (in Mm^3) of each observation of a dataset.

        Args:
            data: the data information of the dataset.

        Returns:
            npt.NDArray[np.float32]: the total volume in Mm^3 for each date.
        """

        counts = np.bincount(data.coords[0], minlength=data.dates.size)
        return (counts * data.voxel_volume_km3() * 1e-9).astype(np.float32)

    def _date_to_num(self) -> dict[str, int]:
        """
        To get the image number corresponding to a stereo date.

        Returns:
            dict[str, int]: the image number corresponding to each date.
        """

        pattern = re.compile(
            r'(?P<number>\d{4})_(?P<date>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})\.\d{3}\.png'
        )
        files: list[str] = sorted(glob(
            pathname=os.path.join(config.dir.input.stereo.wave304.int, '*.png'),
        ))

        date_to_num: dict[str, int] = {
            matched.group('date'): int(matched.group('number'))
            for file in files
            if (matched := pattern.match(os.path.basename(file))) is not None
        }
        return date_to_num

    def _get_surface(self, date: str, choice: Literal['Stereo', 'SDO']) -> float | None:
        # todo add docstring
        # * the dates saved are the ones in stereo B, so use that as the reference.

        # CHECK
        nb = self._num.get(date, None)
        if nb is None: return

        if choice == 'SDO':
            hdul = fits.open(os.path.join(
                config.dir.input.sdo.mask, f'AIA_fullhead_{nb:03d}.fits.gz',
            ))
            surface = float(np.sum(hdul[0].data * hdul[0].header['CDELT1'] ** 2)) / 3600
        else:
            # CHECK
            path = os.path.join(
                config.dir.input.stereo.wave304.mask_karine,
                f'frame{nb:04d}.png',
            )
            if not os.path.exists(path): return

            # SURFACE
            d_lon = 0.075
            mask = ~np.asarray(Image.open(path)).max(axis=-1).astype(np.bool_)
            surface = float(mask.sum() * d_lon ** 2)
        return surface


if __name__ == '__main__':
    volume = Volume()
