"""
Contains the main code to do the processing for a given plot.
"""
from __future__ import annotations

# IMPORTs standard
import os

# IMPORTs local
from .plot import Plot
from .structure import Data, Stereo, Sdo

# API public
__all__ = ['Create']



class Create:
    # todo add docstring

    def __init__(self, index: int, verbose: int = 0, flush: bool = False) -> None:
        # todo add docstring

        # CONFIG
        self._verbose = verbose
        self._flush = flush

        # ARGs
        self._index = index

        # RUN
        self._run()

    def _run(self) -> None:
        """
        Creates a single 3*3 image plot.
        """

        # INFO general
        number = Stereo.number(self._index)
        if number is None:
            raise ValueError(
                f"The string {os.path.basename(Stereo.int_paths[self._index])} has the wrong format."
            )
        timestamp = Stereo.timestamp(number)

        # DATA
        stereo_304_raw = Stereo.get_image_raw(number)
        stereo_304_avg = Stereo.get_image_avg(number)
        stereo_304_mask = Stereo.get_mask(number)

        sdo_304 = Sdo.get_fits(timestamp)
        sdo_304_header = sdo_304[0]
        sdo_304_data = sdo_304[1]
        sdo_304_mask = Sdo.get_mask(number)

        # FORMAT
        stereo_171 = Data(
            raw='', # ! placeholder
            avg='', # ! placeholder
            mask=None,
        )
        stereo_304 = Data(
            raw=stereo_304_raw,
            avg=stereo_304_avg,
            mask=stereo_304_mask,
        )
        sdo_171 = Data(
            raw='', # ! placeholder
            avg='', # ! placeholder
            mask=None,
        )
        sdo_304 = Data(
            raw=sdo_304_data,
            avg=None, #type:ignore #! no avg exists 
            mask=sdo_304_mask,
        )

        # PLOT
        Plot(
            number,
            stereo_171,
            stereo_304,
            sdo_171,
            sdo_304,
            verbose=self._verbose - 1,
            flush=self._flush,
        )

    # def _plot_figure(
    #         self,
    #         stereo_int: str,
    #         stereo_avg: str,
    #         sdo_image: str | None,
    #         sdo_mask: str | None,
    #         number: int,
    #     ) -> None:
    #     """
    #     To create the 3x3 plots with the data given at the input.
    #     """

    #     # LOAD stereo images
    #     int_image = plt.imread(stereo_int)
    #     avg_image = plt.imread(stereo_avg)

    #     # LOAD stereo mask (RGB -> bool)
    #     mask_path = os.path.join(
    #         self._paths['stereo mask'],
    #         f'frame{number:04d}.png',
    #     )
    #     mask = self._mask_to_bool(plt.imread(mask_path))
    #     mask_lines = Plot.contours(mask)

    #     # LOAD SDO image (sunpy map) and mask, carved to a Carrington submap matching STEREO FOV
    #     sdo_map: GenericMap | None = None
    #     sdo_lines: list[tuple[list[float], list[float]]] = []
    #     if sdo_image is not None:
    #         sdo_map = self._sdo_submap(self._load_sdo_map(sdo_image))

    #     # LOAD SDO mask and zoom it the same way as the STEREO FOV
    #     if sdo_mask is not None:
    #         sdo_mask_array = fits.getdata(sdo_mask, 0).astype(np.float64)
    #         sdo_mask_bool = self._zoom_sdo(self._mask_to_bool(sdo_mask_array))
    #         sdo_lines = Plot.contours(sdo_mask_bool)

    #     # FIGURE setup with a grid spec so the SDO column can use WCS axes
    #     fig = plt.figure(figsize=(10, 10))
    #     gs = gridspec.GridSpec(3, 3, wspace=0.005, hspace=0.005)

    #     # (row, col) = (top) -> blank for all three datasets (no 171 nm data)
    #     axs_top0 = fig.add_subplot(gs[0, 0]); axs_top0.axis('off')
    #     axs_top1 = fig.add_subplot(gs[0, 1]); axs_top1.axis('off')
    #     axs_top2 = fig.add_subplot(gs[0, 2]); axs_top2.axis('off')

    #     # (row, col) = (304nm, stereo col) -> stereo int
    #     ax10 = fig.add_subplot(gs[1, 0])
    #     ax10.imshow(int_image, interpolation='none')
    #     ax10.axis('off')
    #     self._grid_lines(ax10, int_image.shape)

    #     # (row, col) = (304nm, running col) -> stereo avg
    #     ax11 = fig.add_subplot(gs[1, 1])
    #     ax11.imshow(avg_image, interpolation='none')
    #     ax11.axis('off')
    #     self._grid_lines(ax11, avg_image.shape)

    #     # (row, col) = (304nm, sdo col) -> SDO image with Carrington grid
    #     if sdo_map is not None:
    #         ax12 = fig.add_subplot(gs[1, 2], projection=sdo_map.wcs)
    #         sdo_map.plot(axes=ax12, clip_interval=(1, 99.99) * u.percent, annotate=False,
    #                      title=False, interpolation='none', cmap='gray')
    #         self._hide_wcs_ticks(ax12)
    #         sdo_map.draw_grid(axes=ax12, grid_spacing=15 * u.deg, annotate=False, system='carrington')
    #     else:
    #         ax12 = fig.add_subplot(gs[1, 2]); ax12.axis('off')

    #     # (row, col) = (304+mask, stereo col)
    #     ax20 = fig.add_subplot(gs[2, 0])
    #     ax20.imshow(int_image, interpolation='none')
    #     for line in mask_lines: ax20.plot(line[1], line[0], color='r', linewidth=0.5, alpha=0.4)
    #     ax20.axis('off')
    #     self._grid_lines(ax20, int_image.shape)

    #     # (row, col) = (304+mask, running col)
    #     ax21 = fig.add_subplot(gs[2, 1])
    #     ax21.imshow(avg_image, interpolation='none')
    #     for line in mask_lines: ax21.plot(line[1], line[0], color='r', linewidth=0.5, alpha=0.4)
    #     ax21.axis('off')
    #     self._grid_lines(ax21, avg_image.shape)

    #     # (row, col) = (304+mask, sdo col) -> SDO image + mask with Carrington grid
    #     if sdo_map is not None:
    #         ax22 = fig.add_subplot(gs[2, 2], projection=sdo_map.wcs)
    #         sdo_map.plot(axes=ax22, clip_interval=(1, 99.99) * u.percent, annotate=False,
    #                      title=False, interpolation='none', cmap='gray')
    #         for line in sdo_lines: ax22.plot(line[1], line[0], color='r', linewidth=0.5, alpha=0.4, transform=ax22.get_transform('world'))
    #         self._hide_wcs_ticks(ax22)
    #         sdo_map.draw_grid(axes=ax22, grid_spacing=15 * u.deg, annotate=False, system='carrington')
    #     else:
    #         ax22 = fig.add_subplot(gs[2, 2]); ax22.axis('off')

    #     # SAVE
    #     fig_name = f'contour_{number:04d}.png'
    #     os.makedirs(config.dir.output.results.contours, exist_ok=True)
    #     print(config.dir.output.results.contours)
    #     plt.savefig(
    #         os.path.join(config.dir.output.results.contours, fig_name),
    #         bbox_inches='tight',
    #         pad_inches=0.05,
    #         dpi=400,
    #     )
    #     plt.close()

    #     # PROGRESS
    #     print(f'Plot for stereo image nb {number} done.', flush=True)

    # @staticmethod
    # def _mask_to_bool(mask: np.ndarray) -> np.ndarray:
    #     """
    #     To convert a (possibly RGB) mask image to a boolean array.
    #     """

    #     if mask.ndim == 3:
    #         mask = np.mean(mask, axis=2)
    #     normalised = (mask > 0).astype(bool)
    #     return normalised

    # @staticmethod
    # def _load_sdo_image(filepath: str) -> np.ndarray:
    #     """
    #     To load the real SDO image data from its FITS file (data stored in HDU 1, as is
    #     standard for image_lev1.fits).

    #     Args:
    #         filepath (str): the filepath to the SDO image FITS file.

    #     Returns:
    #         np.ndarray: the SDO image data as a 2D float array.
    #     """

    #     with fits.open(filepath) as hdul:
    #         data = hdul[1].data if len(hdul) > 1 else hdul[0].data
    #     return np.asarray(data, dtype=np.float64)

    # @staticmethod
    # def _treat_sdo_image(image: np.ndarray) -> np.ndarray:
    #     """
    #     To pre-treat the SDO image for better visualisation (clip the percentiles and log).
    #     """

    #     lower_cut = np.nanpercentile(image, 1)
    #     upper_cut = np.nanpercentile(image, 99.99)
    #     image = np.where(np.isnan(image), lower_cut, image)
    #     image[image < lower_cut] = lower_cut
    #     image[image > upper_cut] = upper_cut
    #     return np.log(image)

    # @staticmethod
    # def _zoom_sdo(image: np.ndarray, size: tuple[int, int] = (1200, 1200)) -> np.ndarray:
    #     """
    #     To crop and resize the SDO image/mask so that its north-south FOV matches STEREO.
    #     The full-disk SDO is cropped to the central 2/3 vertically and the left 1/3
    #     horizontally (the sub-field seen by STEREO), flipped to solar orientation, then
    #     resized to a consistent square.
    #     """

    #     index = round(image.shape[0] / 3)
    #     image = image[index:index * 2 + 1, :]
    #     index = round(image.shape[1] / 3)
    #     image = image[:, :index + 1]
    #     image = np.flip(image, axis=0)

    #     pil_image = PIL.Image.fromarray(image)
    #     return np.array(pil_image.resize(size, PIL.Image.Resampling.LANCZOS))

    # @staticmethod
    # def _load_sdo_map(filepath: str) -> GenericMap:
    #     """
    #     To load the real SDO image FITS into a sunpy Map (data stored in HDU 1).

    #     Args:
    #         filepath (str): the filepath to the SDO image FITS file.

    #     Returns:
    #         GenericMap: the sunpy map of the SDO image.
    #     """

    #     with fits.open(filepath) as hdul:
    #         hdul[1].verify('fix')
    #         sunpy_map = Map(np.asarray(hdul[1].data), hdul[1].header)
    #     return sunpy_map

    # def _sdo_submap(self, sunpy_map: GenericMap) -> GenericMap:
    #     """
    #     To carve the full-disk SDO map down to a Carrington-centered submap matching the STEREO
    #     field of view (centered on lon_cen/lat_cen and spanning lon_width/lat_width).

    #     Args:
    #         sunpy_map (GenericMap): the full-disk SDO map.

    #     Returns:
    #         GenericMap: the submap centered on the STEREO field of view.
    #     """

    #     half_lon = self._lon_width / 2
    #     half_lat = self._lat_width / 2
    #     observer = sunpy_map.observer_coordinate
    #     bottom_left = coord.SkyCoord(
    #         self._lon_cen - half_lon,
    #         self._lat_cen - half_lat,
    #         unit=(u.deg, u.deg),
    #         frame='heliographic_carrington',
    #         obstime=observer.obstime,
    #         observer=observer,
    #     )
    #     top_right = coord.SkyCoord(
    #         self._lon_cen + half_lon,
    #         self._lat_cen + half_lat,
    #         unit=(u.deg, u.deg),
    #         frame='heliographic_carrington',
    #         obstime=observer.obstime,
    #         observer=observer,
    #     )
    #     return sunpy_map.submap(bottom_left=bottom_left, top_right=top_right)

    # @staticmethod
    # def _hide_wcs_ticks(ax: WCSAxes) -> None:
    #     """
    #     To hide the tick marks and labels added by a WCS axis (WCSAxes).
    #     """

    #     ax.grid(False)
    #     ax.coords[0].set_axislabel('')
    #     ax.coords[1].set_axislabel('')
    #     ax.coords[0].set_ticks_visible(False)
    #     ax.coords[1].set_ticks_visible(False)
    #     ax.coords[0].set_ticklabel_visible(False)
    #     ax.coords[1].set_ticklabel_visible(False)
