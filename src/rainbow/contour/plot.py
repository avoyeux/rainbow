"""
Code to create the 3*3 contours plot.
"""
from __future__ import annotations

# IMPORTs third-party
import matplotlib.pyplot as plt

# IMPORTs local
from .structure import Data

# API public
__all__ = ['Plot']



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
            grid_ticks: int = 15,
            verbose: int = 0,
            flush: bool = False,
        ) -> None:
        # todo add docstring

        # DATA
        self._number = number
        self._stereo_171 = stereo_171
        self._stereo_304 = stereo_304
        self._sdo_171 = sdo_171
        self._sdo_304 = sdo_304

        # ARGs
        self._fig_size = fig_size
        self._grid_ticks = grid_ticks

        # RUN
        self._run()

        # PRINT
        if verbose > 0: print(f'{self._number:04d} - Plot created.', flush=flush)

    def _run(self) -> None:
        # todo add docstring

        fig = plt.figure(figsize=self._fig_size)
        grid = plt.GridSpec(3, 3, wspace=0.001, hspace=0.001)

        # TOP LEFT
        ax_top0 = fig.add_subplot(grid[0, 0])

    def _add_plot(
            self,
            fig: plt.Figure,
            grid: plt.GridSpec,
            pos: tuple[int, int],
            image: str | None,
            sdo: bool = False,
        ) -> None:
        # todo add docstring

        # ADD
        ax = fig.add_subplot(grid[pos])
        ax.axis('off')

        # IMAGE
        if image is not None: ax.imshow(image, interpolation='none')

        # GRID
        if not sdo:
            pass

        def _add_grid(self, ax: plt.Axes) -> None:
            # todo add docstring

            pass

        def _grid_position(
                self,
                dx: float,
                cen: float,
                width: float,
                size: int,
            ) -> tuple[np.ndarray, list[str]]:
            # todo add docstring

            # BORDER image
            border = cen - width / 2

            # POSITION first
            first_pos = border
            img_idx = 0
            for loop in range(size):
                if round(first_pos, 2) % self._grid_ticks == 0:

