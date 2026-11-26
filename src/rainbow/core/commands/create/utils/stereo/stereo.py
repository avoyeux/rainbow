"""
To get the STEREO positions.
"""
from __future__ import annotations

# IMPORTs standard
import multiprocessing as mp
from datetime import datetime

# IMPORTs third-party
import sunpy
import sunpy.coordinates
import numpy as np
from scipy.io import readsav
from scipy.interpolate import CubicSpline
from astropy.coordinates import CartesianRepresentation
from astropy import units as u

# IMPORTs personal
from common import CustomDate

# IMPORTs local
from rainbow.config import config
from .plot import Plot

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # IMPORTs third-party
    import numpy.typing as npt

    # IMPORTs local
    from rainbow.typing import QueueType, CounterType

# API public
__all__ = ['Stereo']



class Stereo:
    """
    To get and fit the STEREO positions.
    """

    def __init__(
            self,
            dates: list[datetime],
            processes: int = 1,
            plot: bool = False,
        ) -> None:
        """
        Gets and interpolates the STEREO positions given a list of needed dates.
        To get the corresponding positions, use the 'positions' property.

        Arguments:
            dates -- list[datetime.datetime]
                The dates for which the stereo position is needed.
            processes -- int (default: 1)
                The number of processes to use to get the positions.
            plot -- bool (default: False)
                Whether to plot the positions to visualize the goodness of fit.
        """

        # CONFIG
        self._processes = processes

        # ARGs
        self._dates = dates
        self._nb_files = len(readsav(config.file.stereo_info).datainfos)

        # RUN
        self._positions = self._data()

        # TEST visualization
        if plot: Plot(dates=self._dates, positions=self._positions)

    @property
    def positions(self) -> npt.NDArray[np.float32]:
        """
        Returns:
            npt.NDArray[np.float32]
                The positions in Cartesian coordinates in the Carrington reference frame. The shape
                of the array is (N, 3) where N represents the date indexes.
        """
        return self._positions

    @staticmethod
    def _parse_date(date: str | bytes) -> datetime:
        """
        To parse a date into a datetime.datetime. The date must be in the format
        YYYY/MM/DD hh:mm:ss.

        Args:
            date -- str | bytes
                The date to parse.

        Returns:
            datetime.datetime
                The parsed date.
        """

        if isinstance(date, bytes): date = date.decode()
        return datetime.strptime(date, '%Y/%m/%d %H:%M:%S')

    def _data(self) -> npt.NDArray[np.float32]:
        """
        To get the STEREO positions for the inputted dates.

        For the dates that match a known STEREO position (i.e. present in the datainfos), the exact
        stored position is given. For the other dates, the position is interpolated with a cubic
        spline fitted on the known (date, position) points.

        Returns:
            npt.NDArray[np.float32]
                The positions in Cartesian coordinates in the Carrington reference frame.
        """

        # KNOWN positions
        known = self._known_data()

        # LOOKUP
        lookup = dict(known)
        times = np.array(
            object=[date.timestamp() for date in lookup.keys()],
            dtype=np.float64,
        )
        positions = np.stack(
            arrays=[lookup[date] for date in lookup.keys()],
            axis=0,
            dtype=np.float64,
        )

        # SPLINEs (one per Cartesian axis)
        splines = [
            CubicSpline(times, positions[:, axis]) for axis in range(positions.shape[1])
        ]

        # RESULTs
        results: npt.NDArray[np.float32] = np.empty(shape=(len(self._dates), 3), dtype=np.float32)
        for i, date in enumerate(self._dates):
            result = lookup.get(date, None)

            if result is None:
                result = np.stack(
                    arrays=[spline(date.timestamp()) for spline in splines],
                    axis=0,
                    dtype=np.float32,
                )
            results[i] = result
        return results

    def _known_data(self) -> list[tuple[datetime, npt.NDArray[np.float32]]]:
        """
        To get the STEREO dates and positions for all the datainfos.
        Uses multiprocessing if asked for.

        Returns:
            list[tuple[datetime, npt.NDArray[np.float32]]]
                Ordered list of the dates and positions in Cartesian coordinates in the Carrington
                reference frame.
        """

        # NO MULTIPROCESSING
        if self._processes < 2:
            stereo_info = readsav(config.file.stereo_info).datainfos
            results: list[tuple[datetime, npt.NDArray[np.float32]]] = [None] * self._nb_files  #type:ignore
            for i, info in enumerate(stereo_info): results[i] = self._get_pos(info)
        # MULTIPROCESSING
        else:
            results = self._multiprocess()
        return results

    def _multiprocess(self) -> list[tuple[datetime, npt.NDArray[np.float32]]]:
        """
        Multiprocessing the fetching of the date and satellite position.

        Returns:
            list[tuple[datetime, npt.NDArray[np.float32]]]
                Ordered list of the dates and positions in Cartesian coordinates in the Carrington
                reference frame.
        """

        # SETUP
        manager = mp.Manager()
        counter: CounterType[int] = mp.Value('i', self._nb_files - 1)
        output_queue: QueueType[tuple[int, datetime, npt.NDArray[np.float32]]] = manager.Queue()

        # RUN
        processes: list[mp.Process] = [None] * self._processes  #type:ignore
        for i in range(self._processes):
            p = mp.Process(
                target=self._single_process,
                kwargs=dict(
                    counter=counter,
                    output_queue=output_queue,
                ),
            )
            p.start()
            processes[i] = p
        for p in processes: p.join()

        # FETCH results
        results: list[tuple[datetime, npt.NDArray[np.float32]]] = [None] * self._nb_files  #type:ignore
        while not output_queue.empty():
            i, date, pos = output_queue.get()
            results[i] = (date, pos)
        return results

    @staticmethod
    def _single_process(
            counter: CounterType[int],
            output_queue: QueueType[tuple[int, datetime, npt.NDArray[np.float32]]],
        ) -> None:
        """
        Runs the multiprocessing on a single process.

        Arguments:
            counter -- CounterType[int]
                The counter to track the index of the next file to process.
            output_queue -- QueueType[tuple[int, datetime, npt.NDArray[np.float32]]]
                The queue to store the index, date and position.
        """

        # OPEN file
        stereo_info = readsav(config.file.stereo_info).datainfos

        while True:
            # NEXT
            with counter.get_lock():
                index = counter.value
                if index < 0: return
                counter.value -= 1

            # RUN
            date, pos = Stereo._get_pos(stereo_info[index])

            # SAVE
            output_queue.put((index, date, pos))

    @staticmethod
    def _get_pos(info: np.recarray) -> tuple[datetime, npt.NDArray[np.float32]]:
        """
        Reformats the date and gives the STEREO satellite position in Cartesian coordinates in the
        Carrington reference frame.

        Arguments:
            info -- np.recarray
                The STEREO information for at a single time.

        Returns:
            tuple[datetime, npt.NDArray[np.float32]]
                The date and the position in Cartesian coordinates in the Carrington reference
                frame.
        """

        # DATA
        date = Stereo._parse_date(info.strdate)
        stereo_date = (
            f'{date.year}-{date.month}-{date.day}T{date.hour}:{date.minute}:{date.second}'
        )
        coords = sunpy.coordinates.frames.HeliographicCarrington(
            info.lon * u.deg,
            info.lat * u.deg,
            info.dist * u.km,
            obstime=stereo_date,
            observer='self',
        )
        coords = coords.represent_as(CartesianRepresentation)

        # CONVERSION to km
        result = np.array(
            object=[
                coords.x.to(u.km).value,
                coords.y.to(u.km).value,
                coords.z.to(u.km).value,
            ],
            dtype=np.float32,
        )
        return date, result
