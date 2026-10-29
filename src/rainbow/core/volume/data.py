"""
Code to open and use the data from the h5py file.
"""
from __future__ import annotations

# IMPORTs third-party
import numpy as np
from dataclasses import dataclass

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import numpy.typing as npt

# API public
__all__ = ['Data']



@dataclass(slots=True, repr=False, eq=False, match_args=False)
class Data:
    """
    The data information.
    """

    coords: npt.NDArray[np.uint16]
    xt_min: np.float32
    yt_min: np.float32
    zt_min: np.float32
    dates: npt.NDArray[np.str_]
    dx: np.float64

    def get_time_index(self, date: str) -> int:
        """
        To get the time index of the cube corresponding to the given date.

        Args:
            date: the date in the format of the 'Dates' dataset in format yyyy-mm-ddThh-mm-ss.

        Returns:
            int: the time index of the cube.
        """

        indexes = np.flatnonzero(self.dates == date)
        if indexes.size == 0:
            raise ValueError(f"date '{date}' not found in the 'Dates' dataset")
        return int(indexes[0])

    def count_voxels(self, date: str) -> int:
        """
        To count the number of voxels of the cube at the given date.

        Args:
            date: the date in the format of the 'Dates' dataset.

        Returns:
            int: the number of voxels in the 'Filtered/No duplicates' cube.
        """

        time_index = self.get_time_index(date)
        return int(np.count_nonzero(self.coords[0] == time_index))

    def voxel_volume_km3(self) -> np.float64:
        """
        To get the volume in km^3 of a single voxel.

        Returns:
            np.float64: the voxel side length cubed (dx^3) in km^3.
        """
        return self.dx ** 3

    def total_volume_km3(self, date: str) -> np.float64:
        """
        To get the total volume in km^3 of the cube at the given date.

        Args:
            date: the date in the format of the 'Dates' dataset.

        Returns:
            np.float64: the number of voxels times the voxel volume.
        """
        return self.count_voxels(date) * self.voxel_volume_km3()
