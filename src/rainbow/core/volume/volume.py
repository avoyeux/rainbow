"""
Contains code related to the creation of the plot showing the voxel volume.
"""
from __future__ import annotations

# IMPORTs standard
import re
import os
import multiprocessing as mp
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
    from rainbow.typing import QueueType
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
            processes: int = 1,
            verbose: int = 0,
            flush: bool = False,
        ) -> None:
        """
        Computes the voxel volumes and the satellites' surfaces.
        From there, it creates the corresponding plot.

        Arguments:
            processes -- int (default: 1)
                The number of processes to use. When < 2, no multiprocessing is used.
            verbose -- int (default: 0)
                The verbosity level for the prints.
            flush -- bool (default: False)
                Whether to flush the prints.
        """

        # CONFIG
        self._processes = processes
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

        # VALUEs
        volume_hours = self._get_hours(self._data['All data'].dates)
        fov_dates = list(self._num.keys())
        surface_hours = self._get_hours(np.array(fov_dates, dtype=np.str_))

        volume = PData(
            hours=volume_hours,
            surface=np.stack(
                arrays=[self._get_volumes(data) for data in self._data.values()],
                dtype=np.float32,
            ),
        )

        # MULTIPROCESSING
        if self._processes > 1:
            # SURFACEs
            stereo_surface = self._multiprocess(choice='stereo', fov_dates=fov_dates)
            sdo_surface = self._multiprocess(choice='sdo', fov_dates=fov_dates)
        # NO MULTIPROCESSING
        else:
            # SURFACEs
            stereo_surface = [
                surface
                if (surface := self._get_surface(self._num, 'stereo', date)) is not None
                else 0
                for date in fov_dates
            ]
            sdo_surface = [
                surface
                if (surface := self._get_surface(self._num, 'sdo', date)) is not None
                else 0
                for date in fov_dates
            ]

        # RE-FORMAT
        stereo = PData(
            hours=surface_hours,
            surface=np.stack(
                arrays=stereo_surface,
                dtype=np.float32,
            ),
        )
        sdo = PData(
            hours=surface_hours,
            surface=np.stack(
                arrays=sdo_surface,
                dtype=np.float32,
            ),
        )

        # PLOT
        Plot(
            volume=volume,
            stereo=stereo,
            sdo=sdo,
        )

    def _get_hours(self, dates: npt.NDArray[np.str_]) -> npt.NDArray[np.float32]:
        """
        To get the time of each observation in hours since midnight of the first observation.

        Args:
            dates -- npt.NDArray[np.str_]
                The dates of the observations.

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

    def _multiprocess(self, choice: Literal['stereo', 'sdo'], fov_dates: list[str]) -> list[float]:
        """
        Using multiprocessing to get the surface sizes of the corresponding satellite image masks.

        Arguments:
            choice -- Literal['stereo', 'sdo']
                The satellite to use.
            fov_dates -- list[str]
                The dates of the observations.

        Returns:
            list[float]: the surface sizes for each date.
        """

        nb = min(len(fov_dates), self._processes)
        manager = mp.Manager()
        input_queue = manager.Queue()
        output_queue = manager.Queue()

        # POPULATE
        for item in enumerate(fov_dates): input_queue.put(item)
        for _ in range(nb): input_queue.put(None)

        # RUN
        processes: list[mp.Process] = [None] * nb  #type:ignore
        for i in range(nb):
            p = mp.Process(
                target=self._loop,
                kwargs=dict(
                    num=self._num,
                    choice=choice,
                    input_queue=input_queue,
                    output_queue=output_queue,
                )
            )
            p.start()
            processes[i] = p
        for p in processes: p.join()

        # OUTPUT
        surfaces: list[float | None] = [None] * len(fov_dates)
        while not output_queue.empty():
            index, surface = output_queue.get()
            surfaces[index] = surface
        return [value if value is not None else 0. for value in surfaces]

    @staticmethod
    def _loop(
            num: dict[str, int],
            choice: Literal['stereo', 'sdo'],
            input_queue: QueueType[tuple[int, str] | None],
            output_queue: QueueType[tuple[int, float | None]],
        ) -> None:
        """
        A single process computing multiple satellite surface mask values.

        Arguments:
            num -- dict[str, int]
                The image number corresponding to each date.
            choice -- Literal['stereo', 'sdo']
                The satellite to use.
            input_queue -- QueueType[tuple[int, str] | None]
                The queue to get the dates to process.
            output_queue -- QueueType[tuple[int, float | None]]
                The queue to put the surface sizes.
        """

        while True:
            # ARGs
            args = input_queue.get()
            if args is None: break
            index, date = args

            # SURFACE
            surface = Volume._get_surface(num, choice, date)

            # OUTPUT
            output_queue.put((index, surface))

    @staticmethod
    def _get_surface(
            num: dict[str, int],
            choice: Literal['stereo', 'sdo'],
            date: str,
        ) -> float | None:
        """
        To get the surface size of a satellite image mask.

        Arguments:
            num -- dict[str, int]
                The image number corresponding to each date.
            choice -- Literal['stereo', 'sdo']
                The satellite to use.
            date -- str
                The date of the observation.

        Returns:
            float | None: the surface size in km^2 for the date, or None if the date is not found.
        """

        # CHECK
        nb = num.get(date, None)
        if nb is None: return

        if choice == 'sdo':
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
    volume = Volume(processes=20)
