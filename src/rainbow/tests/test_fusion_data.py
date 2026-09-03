"""
To test the data in the fusion data file.
For now, it only tests the values in the fake dataset of the fusion data file.
"""
from __future__ import annotations

# IMPORTs standard
import multiprocessing as mp
from dataclasses import dataclass

# IMPORTs third-party
import h5py
import unittest
import numpy as np

# IMPORTs personal
from common import Decorators

# IMPORTs local
from config import config

# TYPE ANNOTATIONs
from typing import Any

# ! WORK IN PROGRESS

@dataclass(slots=True, frozen=True, repr=False, eq=False)
class CubeInformation:

    # METADATA
    name: str

    # BORDERs
    xt_min: float
    yt_min: float
    zt_min: float

    # DATA
    dx: float
    coords: h5py.Dataset

    def __getitem__(self, index: int) -> np.ndarray:

        # FILTER
        cube_filter = self.coords[0] == index
        cube_coords = self.coords[1:, cube_filter]
        return cube_coords


class CheckData:

    def __init__(
            self,
            filepath: str | None = None,
            processes: int | None = None,
            verbose: int | None = None,
            flush: bool | None = None,
        ) -> None:

        # CONFIGURATION attributes
        self.filepath = str(config.path.data.fusion) if filepath is None else filepath
        self.processes = int(config.run.debug.processes) if processes is None else processes
        self.verbose = int(config.run.debug.verbose) if verbose is None else verbose
        self.flush = bool(config.run.debug.flush) if flush is None else flush

    def get_data_information(self, HDF5File: h5py.File, data_type: str) -> CubeInformation:

        # GET GROUP
        group_path = 'Fake/Filtered/' + data_type
        group: h5py.Group = HDF5File[group_path]

        # GET BORDERS
        xt_min = float(group['xt_min'][...])
        yt_min = float(group['yt_min'][...])
        zt_min = float(group['zt_min'][...])

        # GET DATA
        dx = float(HDF5File['dx'][...])
        coords: h5py.Dataset = group['coords']

        # DATA formatting
        data = CubeInformation(
            name=data_type,
            xt_min=xt_min,
            yt_min=yt_min,
            zt_min=zt_min,
            dx=dx,
            coords=coords,
        )
        return data
    
