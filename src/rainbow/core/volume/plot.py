"""
Code to plot the voxel volume.
"""
from __future__ import annotations

# IMPORTs standard
import os

# IMPORTs third-party
import numpy as np
import matplotlib.pyplot as plt

# IMPORTs local
from rainbow.config import config

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import numpy.typing as npt

# API public
__all__ = ['Plot']



class Plot:
    """
    To plot the evolution of the voxel volume over time.
    """

    def __init__(
            self,
            hours: npt.NDArray[np.float64],
            volumes: dict[str, npt.NDArray[np.float64]],
        ) -> None:
        """
        To plot each dataset's volume and the region in between them.

        Args:
            hours: the time, in hours since midnight of the first observation, for each date.
            volumes: the total volume (in Mm^3) for each dataset, keyed by the dataset name.
        """

        # PATHs
        self._path = config.dir.output.results.volume
        os.makedirs(self._path, exist_ok=True)

        # RUN
        self._run(hours, volumes)

    def _run(self, hours, volumes) -> None:
        """
        To create the volume plot.
        """

        # ENVELOPE
        values = np.stack(list(volumes.values()))
        lower, upper = values.min(axis=0), values.max(axis=0)

        # SETUP
        fig, ax1 = plt.subplots(figsize=(10, 5))

        # VOLUME range
        ax1.fill_between(
            label='Volume range',
            x=hours,
            y1=lower,
            y2=upper,
            color='blue',
            alpha=0.2,
            zorder=1,
            linewidth=0,
        )

        # VOLUME labels
        ax1.set_xlabel('Time (hours since 23-Jul-2012 00:00)')
        ax1.set_ylabel(r'Volume ($Mm^3$)', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')
        ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

        # VOLUME limits
        ax1.set_xlim(left=0, right=60)
        ax1.set_ylim(bottom=0, top=7e5)
        ax1.legend()



        plt.tight_layout()
        plt.savefig(os.path.join(self._path, 'volume_range.png'), dpi=1000)
        plt.close()

