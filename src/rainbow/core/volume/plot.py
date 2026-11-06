"""
Code to plot the voxel volume and the satellite surfaces.
"""
from __future__ import annotations

# IMPORTs standard
import os

# IMPORTs third-party
import numpy as np
import matplotlib.pyplot as plt

# IMPORTs local
from rainbow.config import config
from .data import PData

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import numpy.typing as npt

# API public
__all__ = ['Plot']



class Plot:
    """
    To plot the evolution of the voxel volume and the satellite surfaces over time.
    """

    def __init__(
            self,
            volume: PData,
            stereo: PData,
            sdo: PData,
        ) -> None:
        """
        To plot the voxel volume and the satellite surfaces.

        Args:
            volume -- PData
                The voxel volume.
            stereo -- PData
                The satellite surface in km2.
            sdo -- PData
                The satellite surface in km2.
        """

        # PATHs
        self._path = config.dir.output.results.volume
        os.makedirs(self._path, exist_ok=True)

        # DATA
        self._volume = volume
        self._stereo = stereo
        self._sdo = sdo

        # RUN
        self._run()

    def _run(self) -> None:
        """
        To create the volume plot.
        """

        # SETUP
        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax2 = ax1.twinx()
        ax3 = ax2.twinx()

        # VOLUME range
        lower = self._volume.surface.min(axis=0)
        upper = self._volume.surface.max(axis=0)
        ax1.fill_between(
            label='Volume range',
            x=self._volume.hours,
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
        ax1.tick_params(axis='y', labelcolor='blue', colors='blue')
        ax1.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))  # ? what is this ?

        # VOLUME limits
        ax1.set_xlim(left=0, right=60)
        ax1.set_ylim(bottom=0, top=6.5e5)

        # SDO plot
        ax2.plot(
            self._sdo.hours,
            self._sdo.surface,
            label='SDO fov',
            color='red',
            linewidth=1,
            alpha=0.8,
            dashes=(3, 3, 7, 1),
        )

        # SDO limits
        ax2.set_ylim(bottom=0)

        # SDO labels
        ax2.yaxis.set_ticks_position('right')
        ax2.tick_params(
            axis='y',
            left=False,
            right=True,
            labelleft=False,
            labelright=True,
            labelcolor='red',
            colors='red',
        )

        # STEREO plot
        ax3.plot(
            self._stereo.hours,
            self._stereo.surface,
            color='green',
            label='STEREO fov',
            linewidth=1,
            alpha=0.8,
            dashes=(2, 1, 5, 3),
        )

        # STEREO limits
        ax3.set_ylim(bottom=0)

        # STEREO labels
        ax3.spines['right'].set_position(('axes', 1.04))
        ax3.yaxis.set_ticks_position('right')
        ax3.yaxis.set_label_position('right')
        ax3.tick_params(
            axis='y',
            left=False,
            right=True,
            labelleft=False,
            labelright=True,
            labelcolor='green',
            colors='green',
        )
        ax3.set_ylabel('Surface ($km^2$)', color='black')

        # LEGEND shared
        handles1, labels1 = ax1.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        handles3, labels3 = ax3.get_legend_handles_labels()
        handles = handles1 + handles2 + handles3
        labels = labels1 + labels2 + labels3
        fig.legend(handles, labels, loc='upper left')

        # SAVE
        plt.tight_layout()
        plt.savefig(os.path.join(self._path, 'volume.png'), dpi=1000)
        plt.close()
