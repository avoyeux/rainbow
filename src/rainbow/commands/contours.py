"""
Code to plot the raw input image data and the corresponding contours.
Done like so so that the viewer can better understand what the input data looks like.

The generated figure is a 3x3 grid:
    columns: left = STEREO, middle = STEREO (running), right = SDO.
    rows: top = 171 nm (blank), middle = 304 nm, bottom = 304 nm + mask contours.
! Top row is left blank because there is no 171 nm data.
"""
from __future__ import annotations

# IMPORTs standard
import multiprocessing as mp

# IMPORTs personal
from common import Decorators

# IMPORTs local
from ..contour import Create, Stereo

# TYPE ANNOTATIONs
from ..typing import CounterType

# API public
__all__ = ['Contours']



class Contours:
    """
    To plot the STEREO and SDO images with their corresponding mask contours.
    """

    @Decorators.running_time
    def __init__(
            self,
            lon_cen: float = 195,
            lat_cen: float = 0,
            lon_width: float = 45,
            lat_width: float = 45,
            d_lon: float = 0.075,
            d_lat: float = 0.075,
            deg_grid_width: float = 15,
            processes: int = 1,
            verbose: int = 0,
            flush: bool = False,
        ) -> None:
        """
        To setup the class attributes and find the data.
        """

        # CONFIG
        self._processes = processes
        self._verbose = verbose
        self._flush = flush

        # CARRINGTON grid parameters
        self._lon_cen = lon_cen
        self._lat_cen = lat_cen
        self._lon_width = lon_width
        self._lat_width = lat_width
        self._d_lon = d_lon
        self._d_lat = d_lat
        self._deg_grid_width = deg_grid_width

        # RUN
        self.run()

    def run(self) -> None:
        """
        To loop over all the STEREO images and create the corresponding figure.
        """

        # SETUP
        filepaths = Stereo.int_paths
        nb_processes = min(self._processes, len(filepaths))

        # MULTIPROCESSING
        if nb_processes > 1:
            index: CounterType[int] = mp.Value('i', len(filepaths))

            # MULTIPROCESSING run
            processes: list[mp.Process] = [None] * nb_processes  #type:ignore
            for i in range(nb_processes):
                p = mp.Process(target=self.multiprocessing, args=(index,))
                p.start()
                processes[i] = p
            for p in processes: p.join()

        # NO MULTIPROCESSING
        else:
            for i in range(len(filepaths)): Create(i)

    def multiprocessing(self, counter: CounterType[int]) -> None:
        """
        Loops over all the STEREO images and create the corresponding figure.
        """

        while True:
            # NEXT
            with counter.get_lock():
                counter.value -= 1
                index = counter.value
                if index < 0: break

            # RUN
            Create(index)
