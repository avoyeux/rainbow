"""
Code to create the 3*3 contours plot.
"""
from __future__ import annotations

# IMPORTs standard
import os

# IMPORTs third-party
import sunpy
import sunpy.map
import numpy as np
import astropy.units as u
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.coordinates import SkyCoord
from sunpy.coordinates import HeliographicCarrington, SphericalScreen

# IMPORTs personal
from common import Plot as cPlot

# IMPORTs local
from ..config import config
from .structure import Data

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING, Literal, Any
if TYPE_CHECKING: import numpy.typing as npt

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
    _lat_half_width: float = 22.5  # stereo lat fov / 2 ; matches _lat_width = 45.

    def __init__(
            self,
            number: int,
            stereo_171: Data,
            stereo_304: Data,
            sdo_171: Data,
            sdo_304: Data,
            grid_ticks: float = 15.,
            grid_kwargs: dict[str, Any] = {
                'color': 'white',
                'linestyle': '--',
                'linewidth': 0.06,
                'alpha': 0.4,
            },  # todo just put in the the function itself
            same_fov: bool = True,
            verbose: int = 0,
            flush: bool = False,
        ) -> None:
        # todo add docstring

        # DATA
        self._stereo_171 = stereo_171
        self._stereo_304 = stereo_304
        # self._sdo_171 = sdo_171
        self._sdo_304 = sdo_304

        # ARGs
        self._number = number
        self._same_fov = same_fov
        self._grid_ticks = grid_ticks
        self._grid_kwargs = grid_kwargs

        # DPI
        self._sdo_shape = self._sdo_304.raw.shape

        # RUN
        self._run()

        # PRINT
        if verbose > 0: print(f'{self._number:04d} - Plot created.', flush=flush)

    @property
    def _dpi(self) -> int:
        # todo add docstring
        # todo need to find a way to get the final size of the sdo image being used.

        # SHAPE max final size
        # row = int(
        #     max(self._stereo_171.raw.shape[0], self._stereo_171.avg.shape[0]) +
        #     max(self._stereo_304.raw.shape[0], final_sdo_shape[0]) * 2
        # )
        # column = (
        #     max(self._stereo_171.raw.shape[1], self._stereo_304.raw.shape[1]) +
        #     max(self._stereo_304.avg.shape[1], self._stereo_171.avg.shape[1]) +
        #     final_sdo_shape[1]
        # )
        row = int(
            max(self._stereo_304.raw.shape[0], self._sdo_shape[0]) * 2
        )
        column = (
            max(0, self._stereo_304.raw.shape[1]) +
            max(self._stereo_304.avg.shape[1], 0) +
            self._sdo_shape[1]
        )
        return int(max(row, column) * 1.1)  #? should I change it or keep (1, 1) for figsize ?

    def _run(self) -> None:
        """
        Creates the plot and saves it.
        """

        # PLOT config
        fig = plt.figure(figsize=(1, 1))
        grid = plt.GridSpec(3, 3, wspace=0., hspace=0.)

        # TOP  # ! still don't have the data for that

        # MID
        self._add_stereo_304_plot(
            fig,
            grid,
            plot_pos=(1, 0), 
            image=self._stereo_304.raw,
            mask=None,
        )
        self._add_sdo_304_plot(  #! placeholder
            fig,
            grid,
            plot_pos=(1, 2), 
            data=self._sdo_304.raw,
            mask=None,
        )
        # todo add sdo values.

        # DOWN
        self._add_stereo_304_plot(
            fig,
            grid,
            plot_pos=(2, 0), 
            image=self._stereo_304.raw,
            mask=self._stereo_304.mask if self._stereo_304.mask is not None else None,
        )
        self._add_stereo_304_plot(
            fig,
            grid,
            plot_pos=(2, 1), 
            image=self._stereo_304.avg,
            mask=self._stereo_304.mask if self._stereo_304.mask is not None else None,
        )
        self._add_sdo_304_plot(  #! placeholder
            fig,
            grid,
            plot_pos=(2, 2), 
            data=self._sdo_304.raw,
            mask=self._sdo_304.mask,
        )

        # MID with grid
        self._add_stereo_304_plot(
            fig,
            grid,
            plot_pos=(1, 1), 
            image=self._stereo_304.avg,
            mask=None,
            add_grid_label=True,
        )

        # SAVE
        filepath = os.path.join(
            config.dir.output.results.contours,
            f"frame{self._number:04d}.png",
        )
        plt.savefig(
            fname=filepath,
            bbox_inches='tight',
            pad_inches=0.,
            dpi=self._dpi,
        )  # todo change the images to pdf when for the paper
        plt.close()

    def _add_sdo_304_plot(
            self,
            fig: plt.Figure,
            grid: plt.GridSpec,
            plot_pos: tuple[int, int],
            data: npt.NDArray[np.float64],
            mask: npt.NDArray[np.bool_] | None,
        ) -> None:
        # todo add docstring

        # MAP for grid and zoom
        sdo_map = sunpy.map.Map(data, self._sdo_304.header)

        # ZOOM like STEREO
        if self._same_fov:
            sdo_map = self._crop_sdo_304(sdo_map)
            self._sdo_shape = sdo_map.data.shape

        # PLOT
        ax = fig.add_subplot(grid[plot_pos], projection=sdo_map)
        sdo_map.plot(axes=ax, interpolation='none', cmap='gray', title=False)

        # CONTOUR
        if mask is not None:
            mask_map = sunpy.map.Map(mask.astype(np.uint8), self._sdo_304.header)
            mask_map = self._crop_sdo_304(mask_map)
            self._add_contour(ax, mask_map.data.astype(np.bool_))

        # GRID
        sdo_map.draw_grid(
            grid_spacing=np.array(tuple(self._grid_ticks for _ in range(2))) * u.deg,
            system='carrington',
            annotate=False,
            axes=ax,
            color='white',
            linestyle='--',
            linewidth=0.1,
            alpha=0.6,
            zorder=101,
        )

        # HIDE axes frame
        ax.patch.set_visible(False)
        ax.coords.frame.set_color('none') #type:ignore

        # HIDE labels/ticks
        for coord in ax.coords: #type:ignore
            coord.set_ticks_visible(False)
            coord.set_ticklabel_visible(False)
        ax.grid(False)

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

        # ADD
        ax = fig.add_subplot(grid[plot_pos])
        ax.axis('off')

        # IMAGE
        ax.imshow(image, interpolation='none', cmap='gray')

        # CONTOUR
        if mask is not None: self._add_contour(ax, mask)

        # GRID
        self._add_grid_stereo(ax, add_grid_label)

    def _crop_sdo_304(self, sdo_map: sunpy.map.GenericMap) -> sunpy.map.GenericMap:
        # todo add docstring

        # HELIOGRAPHIC CARRINGTON latitude
        half = self._lat_half_width * u.deg
        frame = HeliographicCarrington(
            obstime=sdo_map.date, observer=sdo_map.observer_coordinate,
        )
        lat_lo = SkyCoord(0 * u.deg, -half, frame=frame)
        lat_hi = SkyCoord(0 * u.deg, +half, frame=frame)

        # TRANSFORM
        with SphericalScreen(sdo_map.observer_coordinate):
            lam = lat_lo.transform_to(sdo_map.coordinate_frame)
            ham = lat_hi.transform_to(sdo_map.coordinate_frame)

        # PIXEL space
        _, row_lo = sdo_map.world_to_pixel(lam)
        _, row_hi = sdo_map.world_to_pixel(ham)
        row_lo = int(round(float(np.ravel(row_lo.to_value(u.pix))[0])))
        row_hi = int(round(float(np.ravel(row_hi.to_value(u.pix))[0])))

        # LEFT anchored
        r0, r1 = sorted((row_lo, row_hi))
        height = r1 - r0

        corner_a = sdo_map.pixel_to_world(0 * u.pix, r0 * u.pix)
        corner_b = sdo_map.pixel_to_world(height * u.pix, r1 * u.pix)
        return sdo_map.submap(corner_a, top_right=corner_b)

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
        for line in lines: ax.plot(line[1], line[0], color='r', linewidth=.03, alpha=.6)

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
                    x=pos - 45,
                    y=610,
                    s=text,
                    size=1,
                    color='black',
                    alpha=0.8,
                )
        for pos, text in zip(lat_pos, lat_text):
            ax.axhline(y=pos, **self._grid_kwargs)
            if add_label:
                ax.text(
                    x=-25,
                    y=pos + 15,
                    s=text,
                    size=1,
                    color='black',
                    alpha=0.8,
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
                label = f'{value:.0f}°S' if value > 0 else f'{abs(value):.0f}°N'
            else:
                value = value - 360 if value > 180 else value
                label = f'{value:.0f}°E' if value > 0 else f'{abs(value):.0f}°W'
            labels[i] = label
        return [round(pos) for pos in positions], labels
