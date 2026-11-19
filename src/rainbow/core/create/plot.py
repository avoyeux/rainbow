"""
Testing plots to make sure that the code is doing what is being intended.
"""
from __future__ import annotations

# IMPORTs standard
import os

# IMPORTs third-party
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# IMPORTs local
from rainbow.config import config

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # IMPORTs third-party
    import numpy.typing as npt

# API public
__all__ = ['StereoPos']



class StereoPos:
    """
    To visually see if the fit of the STEREO positions is correct.
    """

    def __init__(
            self,
            dates: list[datetime],
            positions: npt.NDArray[np.float32],
        ) -> None:
        """
        Creates a plot to visually see if the fit of the STEREO positions is correct.

        Arguments:
            dates -- list[datetime.datetime].
                The dates of the positions.
            positions -- npt.NDArray[np.float32].
                The positions of STEREO.
        """

        # ARGs
        self._path: str = config.dir.temp
        self._dates = dates
        self._positions = positions

    def _run(self) -> None:
        """
        Runs the plot on each axis.
        """

        # DATEs as num
        dates = [date.timestamp() for date in self._dates]

        # PLOT for each axis
        axes = ('x', 'y', 'z')
        for axis, x in zip(axes, self._positions.T): self._plot(axis, x, dates)  #type:ignore

    def _plot(self, axis: str, x: npt.NDArray[np.float32], y: list[float]) -> None:
        """
        Test plot for a given axis.
        """

        plt.figure()
        plt.plot(x, y)
        plt.xlabel('Time (s)')
        plt.ylabel(f'{axis} (m)')
        plt.title(f'{axis} position')
        plt.savefig(os.path.join(self._path, f'stereo_pos_{axis}.png'), dpi=1000)
        plt.close()
