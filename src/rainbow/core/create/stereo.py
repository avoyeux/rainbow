"""
To get the STEREO positions.
"""
from __future__ import annotations

# IMPORTs standard
import multiprocessing as mp

# IMPORTs third-party
import sunpy
import sunpy.coordinates
import numpy as np
from scipy.io import readsav
from astropy.coordinates import CartesianRepresentation
from astropy import units as u

# IMPORTs personal
from common import CustomDate

# IMPORTs local
from rainbow.config import config

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # IMPORTs third-party
    import numpy.typing as npt

    # IMPORTs local
    from rainbow.typing import QueueType

# API public
__all__ = ['Stereo']



class Stereo:
    # todo add docstring

    def __init__(
            self,
            processes: int = 1,
        ) -> None:
        # todo add docstring
        # CONFIG
        self._processes = processes

        # RUN
        self._stereo_info: np.recarray = readsav(config.file.stereo_info).datainfos


    def _run(self) -> None:
        # todo add docstring
        pass

    def _multiprocess(self) -> None:
        # todo add docstring

        # SETUP
        manager = mp.Manager()
        input_queue: QueueType[tuple[int, np.recarray] | None] = manager.Queue()
        output_queue: QueueType[tuple[int, npt.NDArray[np.float32]]] = manager.Queue()

    @staticmethod
    def _single_process(  # todo change it to an int counter and open the file here
            input_queue: QueueType[tuple[int, np.recarray] | None],
            output_queue: QueueType[tuple[int, npt.NDArray[np.float32]]],
        ) -> None:
        # todo add docstring

        while True:
            # CHECK
            args = input_queue.get()
            if args is None: return
            index, info = args

            # RUN
            result = Stereo._get_pos(info)

            # SAVE
            output_queue.put((index, result))

    @staticmethod
    def _get_pos(info: np.recarray) -> npt.NDArray[np.float32]:
        # todo add docstring

        # DATA
        date = CustomDate(info.strdate)
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
        return result
