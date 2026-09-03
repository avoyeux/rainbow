"""
Code to create and open a shared memory object.
"""
from __future__ import annotations

# IMPORTs standard
import multiprocessing as mp
from multiprocessing.shared_memory import SharedMemory

# IMPORTs third-party
import numpy as np

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING: import numpy.typing as npt

# API public
__all__ = ['Shared']



class Shared:
    """
    Code to create and open a shared memory object.
    """

    @staticmethod
    def create(data: npt.NDArray[Any]) -> tuple[SharedMemory, dict]:
        """
        Creates a shared memory objects and returns the necessary information to find and clean up
        the shared memory.

        Arguments:
            data -- npt.NDArray[Any]. The data to share.

        Returns:
            tuple[SharedMemory, dict]: the shared memory object and the information to open it.
        """

        # SHARED
        shm = SharedMemory(create=True, size=data.nbytes)
        info = {
            'name': shm.name,
            'dtype': data.dtype,
            'shape': data.shape,
        }

        # POPULATE
        array = np.ndarray(data.shape, dtype=data.dtype, buffer=shm.buf)
        array[...] = data 
        return shm, info

    @staticmethod
    def open(info: dict[str, Any]) -> tuple[SharedMemory, npt.NDArray[Any]]:
        """
        Opens a shared memory object and returns the data.

        Arguments:
            info -- dict[str, Any]. The information to open the shared memory object.

        Returns:
            tuple[SharedMemory, npt.NDArray[Any]]: the shared memory object and the data.
        """

        shm = SharedMemory(name=info['name'])
        data = np.ndarray(info['shape'], dtype=info['dtype'], buffer=shm.buf)
        return shm, data
