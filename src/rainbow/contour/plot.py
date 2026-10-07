"""
Code to create the 3*3 contours plot.
"""
from __future__ import annotations

# IMPORTs standard
import os

# IMPORTs third-party
import numpy as np
import matplotlib.pyplot as plt

# IMPORTs personal
from common import Plot as cPlot

# IMPORTs local
from ..config import config
from .structure import Data

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING, Literal, Any
if TYPE_CHECKING:
    import numpy.typing as npt

# API public
__all__ = ['Plot']

# todo make the dpi and fig size dependent on input images nb pixels



class Plot:
    # todo add docstring

    # ? keep the constants here or in another class ?
    _lon_cen: float = 195.
    _lat_cen: float = 0.
    _lon_width: float = 45.
    _lat_width: float = 45.
    _d_lon: float = 0.075
    _d_lat: float = 0.075

    def __init__(
            self,
            number: int,
            stereo_171: Data,
            stereo_304: Data,
            sdo_171: Data,
            sdo_304: Data,
            fig_size: tuple[int, int] = (10, 10),
            grid_ticks: float = 15.,
            grid_kwargs: dict[str, Any] = {
                'color': 'white',
                'linestyle': '--',
                'linewidth': 0.6,
                'alpha': 0.4,
            },  # todo just put in the the function itself
            dpi: int = 500,
            verbose: int = 0,
            flush: bool = False,
        ) -> None:
        # todo add docstring

        # DATA
        self._stereo_171 = stereo_171
        self._stereo_304 = stereo_304
        self._sdo_171 = sdo_171
        self._sdo_304 = sdo_304

        # ARGs
        self._dpi = dpi
        self._number = number
        self._fig_size = fig_size
        self._grid_ticks = grid_ticks
        self._grid_kwargs = grid_kwargs

        # RUN
        self._run()

        # PRINT
        if verbose > 0: print(f'{self._number:04d} - Plot created.', flush=flush)

    def _run(self) -> None:
        """
        Creates the plot and saves it.
        """

        fig = plt.figure(figsize=self._fig_size)
        grid = plt.GridSpec(3, 3, wspace=0.001, hspace=0.001)

        # TOP  # ! still don't have the data for that
        # ax_top0 = fig.add_subplot(grid[0, 0])

        # MID
        self._add_stereo_304_plot(
            fig,
            grid,
            plot_pos=(1, 0), 
            image=plt.imread(self._stereo_304.raw).mean(axis=-1),
            mask=None,
            add_grid_label=True,
        )
        self._add_stereo_304_plot(
            fig,
            grid,
            plot_pos=(1, 1), 
            image=plt.imread(self._stereo_304.avg).mean(axis=-1),
            mask=None,
            add_grid_label=False,
        )
        # todo add sdo values.

        # DOWN
        self._add_stereo_304_plot(
            fig,
            grid,
            plot_pos=(2, 0), 
            image=plt.imread(self._stereo_304.raw).mean(axis=-1),
            mask=(
                plt.imread(self._stereo_304.mask).max(axis=-1)
                if self._stereo_304.mask is not None
                else None
            ),
            add_grid_label=True,
        )
        self._add_stereo_304_plot(
            fig,
            grid,
            plot_pos=(2, 1), 
            image=plt.imread(self._stereo_304.avg).mean(axis=-1),
            mask=(
                plt.imread(self._stereo_304.mask).max(axis=-1)
                if self._stereo_304.mask is not None
                else None
            ),
            add_grid_label=False,
        )

        # SAVE
        filepath = os.path.join(
            config.dir.output.results.contours,
            f"frame{self._number:04d}.png",
        )
        plt.savefig(
            fname=filepath,
            bbox_inches='tight',
            pad_inches=0.01,
            dpi=self._dpi,
        )
        plt.close()

    def _add_stereo_304_plot(  # ! could be also for 171 if same image lon lat
            self,
            fig: plt.Figure,
            grid: plt.GridSpec,
            plot_pos: tuple[int, int],
            image: npt.NDArray[np.float64],
            mask: npt.NDArray[np.bool_] | None,
            add_grid_label: bool = False,
        ) -> None:
        # todo add docstring
        # print(f"image shape is {image.shape}")

        # ADD
        ax = fig.add_subplot(grid[plot_pos])
        ax.axis('off')

        # IMAGE
        ax.imshow(image, interpolation='none', cmap='gray')

        # CONTOUR
        if mask is not None: self._add_contour(ax, mask)

        # GRID
        self._add_grid_stereo(ax, add_grid_label)

    def _add_contour(self, ax: plt.Axes, mask: npt.NDArray[np.bool_]) -> None:
        """
        Adds the contours of a given mask in a given plot.

        Arguments:
            ax -- plt.Axes.
                The axes to add the contours to.
            mask -- npt.NDArray[np.bool_].
                The mask to add the contours of.
        """

        lines = cPlot.contours(mask)
        for line in lines: ax.plot(line[1], line[0], color='r', linewidth=.5, alpha=.6)

    def _add_grid_stereo(self, ax: plt.Axes, add_label: bool = False) -> None:
        """
        Adding the grid-lines and corresponding labels (if asked for) to a given plot.

        Arguments:
            ax -- plt.Axes.
                The axes to add the grid-lines and labels to.
            add_label -- bool (default: False)
                Whether to add the labels to the grid-lines.
        """

        # POS n LABELs
        lon_pos, lon_text = self._grid_position(
            self._d_lon, self._lon_cen, self._lon_width, 'lon',
        )
        lat_pos, lat_text = self._grid_position(
            self._d_lat, self._lat_cen, self._lat_width, 'lat',
        )

        # ADD
        for pos, text in zip(lon_pos, lon_text):
            ax.axvline(x=pos, **self._grid_kwargs)
            if add_label:
                ax.text(
                    x=pos,
                    y=10,
                    s=text,
                    size=10,
                    color=self._grid_kwargs['color'],
                    alpha=0.6,
                )
        for pos, text in zip(lat_pos, lat_text):
            ax.axhline(y=pos, **self._grid_kwargs)
            if add_label:
                ax.text(
                    x=590,
                    y=pos,
                    s=text,
                    size=10,
                    color=self._grid_kwargs['color'],
                    alpha=0.6,
                )

    def _grid_position(
            self,
            dx: float,
            cen: float,
            width: float,
            direction: Literal['lon', 'lat'],
        ) -> tuple[list[int], list[str]]:
        """
        Computes and gives the grid-line positions and corresponding labels.

        Arguments:
            dx -- float.
                The pixel size in degrees.
            cen -- float.
                The center value of the image in degrees.
            width -- float.
                The width of the image in degrees.
            direction -- Literal['lon', 'lat'].
                The direction of the grid-line.

        Returns:
            tuple[list[int], list[str]].
                The grid-line positions (in pixels) and corresponding labels.
        """

        # POSITIONs
        border = cen - width / 2
        rest = border % self._grid_ticks
        nb_of_lines = int((width + rest) / self._grid_ticks)
        positions = [
            ((index + 1) * self._grid_ticks - rest) / dx
            for index in range(nb_of_lines)
        ] # in pixels

        # LABELs
        labels: list[str] = [None] * nb_of_lines  #type:ignore
        for i, pos in enumerate(positions):
            value = pos * dx + border
            if direction == 'lat':
                label = f'{value:.1f}° S' if value > 0 else f'{abs(value):.1f}° N'
            else:
                value = value - 360 if value > 180 else value
                label = f'{value:.1f}° E' if value > 0 else f'{abs(value):.1f}° W'
            labels[i] = label
        return [round(pos) for pos in positions], labels
