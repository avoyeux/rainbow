"""
To 3D visualize the rainbow filament data and the corresponding polynomial fitting.
"""
from __future__ import annotations

# IMPORTs standard
import os
import re
import time
import threading

# IMPORTs third-party
import k3d
import h5py
import IPython
import typeguard
import ipywidgets
import numpy as np
from matplotlib import colors as mcolors

# IMPORTs personal
from common import Decorators, Plot

# IMPORTs local
from rainbow.config import config
from .utils import Setup, Camera, CameraInfo, Screenshot, Sun, CubeInfo, UniqueCubeInfo

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING, Any, overload, Literal, cast
if TYPE_CHECKING:
    # IMPORTs third-party
    import numpy.typing as npt

    # IMPORTs local
    from rainbow.typing import VoxelAlias, JsLinkAlias, ImageExtension

# API public
__all__ = ['Vis']

# todo need to improve the names of the different datasets in the visualization
# todo need to be able to add the extended version of the polynomial fit



class Vis(Setup):
    """
    Creates the corresponding k3d animation to then be used in a Jupyter notebook file.
    """

    @typeguard.typechecked
    def __init__(
            self,
            name: str = '',
            compression_level: int = 9,
            sleep_time: int | float = 1, 
            camera_zoom_speed: int | float = 0.7, 
            camera_pos: tuple[float, float, float] | None = None,
            camera_fov: float = 0.23,
            up_vector: tuple[int, int, int] = (0, 0, 1), 
            visible_grid: bool = False, 
            outlines: bool = False,
            texture_resolution: int = 960,  
            offscreen: bool = False,
            px: int = 1080,
            extension: ImageExtension = '.png',
            **kwargs,
        ) -> None:
        """
        todo update docstring
        To visualize the data in k3d. The fetching and naming of the data is done in the parent
        class.

        Args:
            compression_level (int, optional): the compression level used in k3d. The higher the
                value, the more compressed it is (max is 9). Defaults to 9.
            plot_height (int, optional): the height in pixels of the jupyter display plot.
                Defaults to 1260.
            sleep_time (int | float, optional): the sleep time used when playing through the cubes.
                Used when trying to save screenshots of the display. Defaults to 2.
            camera_zoom_speed (int | float, optional): the zoom speed when trying to zoom in on the
                display. Defaults to 0.7.
            camera_pos (tuple[int | float, int | float, int | float] | None, optional): the index
                position of the camera. Automatically set if 'pov_sdo' or 'pov_stereo' is chosen.
                Defaults to None.
            camera_fov (float, optional): the field of view, in degrees. Defaults to 0.23.
            up_vector (tuple[int, int, int], optional): the up vector when displaying the
                protuberance. Defaults to (0, 0, 1).
            visible_grid (bool, optional): deciding to make the k3d grid visible or not.
                Defaults to False.
            outlines (bool, optional): deciding to add the voxel outlines when displaying the data.
                Defaults to False.
            texture_resolution (int, optional): the resolution of the sun's texture, i.e. how many
                points need to be displayed phi direction. Defaults to 960.
            offscreen (bool, optional): deciding to render every frame to a PNG sequence with a
                headless browser. Defaults to False.
            px (int, optional): the width and height in pixels. Defaults to 1080.
            **kwargs: the other arguments to pass to the parent class.
            extension (ImageExtension, optional): the extension of the screenshots. Defaults to '.png'.
        """

        # PARENT init
        super().__init__(**kwargs)

        # ATTRIBUTEs
        self.sleep_time = sleep_time  # sets the time between each frames (in seconds)
        self.texture_resolution = texture_resolution
        self.compression_level = compression_level
        self.outlines = outlines

        # PLACEHOLDERs
        self.plot_alldata: list[VoxelAlias] # voxels plot of the all data 
        self.plot_dupli_new: list[VoxelAlias]  # same for the second method
        self.plot_full_alldata: list[VoxelAlias]  # voxels plot for the full integration
        self.plot_full_no_duplicate: list[VoxelAlias]  # same for the no duplicate data
        self.plot_interv_new: list[VoxelAlias]  # same for the second method
        self.plot_interv_dupli_new: list[VoxelAlias]  # same for the second method
        self.plot_los_sdo: list[VoxelAlias]
        self.plot_los_stereo: list[VoxelAlias]
        self.play_pause_button: ipywidgets.ToggleButton  # Play/Pause widget initialization
        self.time_slider: ipywidgets.IntSlider # time slider widget
        self.date_dropdown: ipywidgets.Dropdown  # Date dropdown widget to show the date
        self.time_link: JsLinkAlias  # JavaScript Link between the two widgets

        # RUN
        self._plot: Any = k3d.plot(grid_visible=visible_grid, screenshot_scale=1)  # black: background_color=0x000000 #type:ignore
        self._plot.height = px
        self._plot.axes_helper = 400
        self._plot.axes = ['x', 'y', 'z']

        self._camera = self._get_camera(
            zoom=camera_zoom_speed,
            speed=camera_zoom_speed,
            fov=camera_fov,
            up=up_vector,
            default_pos=camera_pos,
        )
        self._animation()

        # OFFSCREEN
        if offscreen: self._save_offscreen(name=name, px=px, extension=extension)

    def _get_camera(
            self,
            zoom: float,
            speed: float,
            fov: float,
            up: tuple[int, int, int],
            default_pos: tuple[float, float, float] | None,
        ) -> Camera:
        # todo add docstring

        # POS
        if self._cubes.sdo_pos is not None:
            satellite = 'sdo'
            pos = self._cubes.sdo_pos
        elif self._cubes.stereo_pos is not None:
            satellite = 'stereo'
            pos = self._cubes.stereo_pos
        else:
            satellite = None
            if default_pos is not None:
                position = default_pos
            else:
                au_in_solar_r = 215  # 1 au in solar radii
                distance_to_sun = au_in_solar_r * self._solar_r / self.constants.dx
                print("No 'camera_pos', setting default values.")
                position = (- distance_to_sun, -0.5 * distance_to_sun, 0)

            pos = np.array(
                object=[position for _ in range(len(self.constants.dates))],
                dtype=np.float32,
            )

        cube: CubeInfo = self.find_first_cube()  #type:ignore # todo change this weird patch
        # CAMERA
        camera = Camera(
            plot=self._plot,
            info=CameraInfo(
                dx=self.constants.dx,
                solar_r=self._solar_r,
                shape=cube.shape[1:],
                bounds=(cube.xt_min_index, cube.yt_min_index, cube.zt_min_index),
            ),
            pos=pos,
            satellite=satellite,
            zoom=zoom,
            speed=speed,
            fov=fov,
            up=up,
        )
        return camera

    def _animation(self) -> None:
        """
        Creates the 3D animation using k3d. 
        """

        # DEFAULT params
        kwargs = {
            'compression_level': self.compression_level,
            'outlines': self.outlines,
        }

        # SUN add
        if self._choices['sun']:
            sun = Sun(
                radius=self._solar_r,
                dx=self.constants.dx,
                resolution=self.texture_resolution,
                grid=15.,
            )
            self._plot += sun.points(compression_lvl=self.compression_level)

        # ALL DATA add
        if self._cubes.all_data is not None:
            # VOXELS create
            self.plot_alldata = self.create_voxels(self._cubes.all_data, **kwargs)
            for plot in self.plot_alldata: self._plot += plot     

        # NO DUPLICATES add
        if self._cubes.no_duplicate is not None:
            # VOXELs create
            self.plot_dupli_new = self.create_voxels(self._cubes.no_duplicate, **kwargs)
            for plot in self.plot_dupli_new: self._plot += plot

        # TIME INTEGRATION add
        if self._cubes.integration_all_data is not None:
            # VOXELs create
            self.plot_interv_new = self.create_voxels(self._cubes.integration_all_data, **kwargs)
            for plot in self.plot_interv_new: self._plot += plot

        # TIME NO DUPLICATES add
        if self._cubes.integration_no_duplicate is not None:
            # VOXELs create
            self.plot_interv_dupli_new = self.create_voxels(
                self._cubes.integration_no_duplicate,
                **kwargs,
            )
            for plot in self.plot_interv_dupli_new: self._plot += plot  

        # FULL INTEGRATION add
        if self._cubes.full_integration_all_data is not None:
            # VOXELs create
            self.plot_full_alldata = self.create_voxels(
                self._cubes.full_integration_all_data,
                **kwargs,
            )
            for plot in self.plot_full_alldata: self._plot += plot

        # FULL NO DUPLICATES add
        if self._cubes.full_integration_no_duplicate is not None:
            # VOXELs create
            self.plot_full_no_duplicate = self.create_voxels(
                self._cubes.full_integration_no_duplicate,
                **kwargs,
            )
            for plot in self.plot_full_no_duplicate: self._plot += plot

        # SDO LINE OF SIGHT add
        if self._cubes.los_sdo is not None:
            # VOXELs create
            self.plot_los_sdo = self.create_voxels(self._cubes.los_sdo, **kwargs)
            for plot in self.plot_los_sdo: self._plot += plot

        # STEREO LINE OF SIGHT add
        if self._cubes.los_stereo is not None:
            # VOXELs create
            self.plot_los_stereo = self.create_voxels(self._cubes.los_stereo, **kwargs)
            for plot in self.plot_los_stereo: self._plot += plot

        # BUTTON play/pause
        self.play_pause_button = ipywidgets.ToggleButton(
            value=False,
            description='Play',
            icon='play',
        )

        # SETUP time-slider and play/pause
        self.time_slider = ipywidgets.IntSlider(
            min=0,
            max=len(self.constants.dates)-1,
            description='Frame:',
        )
        self.date_dropdown = ipywidgets.Dropdown(
            options=self.constants.dates,
            description='Date:',
        )
        self.time_slider.observe(self.update_plot, names='value')
        self.time_link = ipywidgets.jslink(
            (self.time_slider,'value'),
            (self.date_dropdown, 'index'),
        )
        self.play_pause_button.observe(self.play_pause_handler, names='value')

        # DISPLAY
        IPython.display.display(
            self._plot,
            self.time_slider,
            self.date_dropdown,
            self.play_pause_button,
        )

    def create_voxels(
            self,
            cube: CubeInfo | UniqueCubeInfo,
            index: int = 0,
            **kwargs,
        ) -> list[VoxelAlias]:
        """
        Creates the initial k3d voxels and the corresponding polynomial fit voxels for the
        visualization.  

        Args:
            cube (CubeInfo | UniqueCubeInfo): the cube information to visualize.
            index (int, optional): the index of the time value to visualize. Defaults to 0.

        Returns:
            list[VoxelAlias]: the corresponding voxels for the k3d visualization.
        """

        # PLACEHOLDER voxels
        plots: list[VoxelAlias] = [None] * (
            1 + (len(cube.polynomials) if cube.polynomials is not None else 0)
        )

        # INDEX translation
        index = int(self.constants.time_indexes[index])
        translation = (cube.xt_min_index, cube.yt_min_index, cube.zt_min_index)

        plots[0] = k3d.voxels(
            voxels=cube[index][0].transpose((2, 1, 0)),
            name=cube.name,
            opacity=cube.opacity,
            color_map=[self.color_str_to_hex(cube.colour)],  #type:ignore
            translation=translation,
            bounds=[
                0, cube.shape[1],
                0, cube.shape[2],
                0, cube.shape[3],
            ],
            **kwargs,
        )

        if cube.polynomials is not None:
            # INTERPOLATIONs setup
            polynomials = cube.polynomials

            # INTERPOLATION orders
            for i, polynomial_data in enumerate(polynomials):
                plots[i + 1] = k3d.voxels(
                    voxels=polynomial_data[index].transpose((2, 1, 0)),
                    name=polynomial_data.name,
                    opacity=cube.opacity_polynomial,
                    color_map=[polynomial_data.color_hex],  #type:ignore
                    translation=translation,
                    **kwargs,
                )
        return plots

    def find_first_cube(self) -> CubeInfo | None:
        """
        Finds the first cube that has data in it.

        Returns:
            CubeInfo | None: the first cube that has data in it. None if no data found.
        """

        # FIND cube
        for attr_name in self._cubes.__slots__:
            if attr_name in ['hdf5File', 'sdo_pos', 'stereo_pos']: continue
            if getattr(self._cubes, attr_name) is not None: return getattr(self._cubes, attr_name)

        # NO DATA
        return None

    def update_plot(self, change: dict[str, Any]) -> None:
        """
        Updates the voxels depending on which time value is chosen.

        Args:
            change (dict[str, Any]): the time value, with the 'new' key being the new value and
                'old' key being the old value.
        """

        # CAMERA
        self._camera.update(change['new'])

        # ALL DATA
        if self._cubes.all_data is not None:
            self.update_voxel(self.plot_alldata, self._cubes.all_data, change['new'])
        # NO DUPLICATES
        if self._cubes.no_duplicate is not None:
            self.update_voxel(self.plot_dupli_new,self._cubes.no_duplicate,change['new'])
        # TIME INTEGRATION
        if self._cubes.integration_all_data is not None:
            self.update_voxel(self.plot_interv_new, self._cubes.integration_all_data, change['new'])
        # TIME NO DUPLICATES
        if self._cubes.integration_no_duplicate is not None:     
            self.update_voxel(
                self.plot_interv_dupli_new, self._cubes.integration_no_duplicate, change['new'],
            )        
        # SDO LINE OF SIGHT
        if self._cubes.los_sdo is not None:
            self.update_voxel(self.plot_los_sdo, self._cubes.los_sdo, change['new'])
        # STEREO LINE OF SIGHT
        if self._cubes.los_stereo is not None:
            self.update_voxel(self.plot_los_stereo, self._cubes.los_stereo, change['new'])

    def update_voxel(
            self,
            plots: list[VoxelAlias],
            cube_info: CubeInfo,
            index: int | None,
        ) -> None:
        """
        Updates the k3d plot voxels for each cube and the corresponding polynomials.

        Args:
            plots (list[VoxelAlias]): the different voxel plots for each cube type.
            cube_info (CubeInfo): the data cubes. None if it doesn't exist.
            index (int | None): the data cube index. If None, then no data exists for data index.
        """

        if index is None:
            # NO DATA
            cubes = [np.zeros((1, 1, 1), dtype='uint8')] * len(plots)
        else:
            index = int(self.constants.time_indexes[index])

            # DATA cube and polynomials
            cubes = cube_info[index]

        # PLOTs add data
        for i, plot in enumerate(plots):
            plot.voxels = cubes[i].transpose((2, 1, 0))

    def play(self) -> None:
        """
        Params for the play button.
        """

        if self.play_pause_button.value and self.time_slider.value < len(self.constants.dates) - 1:
            self.time_slider.value += 1
            threading.Timer(self.sleep_time, self.play).start()

        else:
            self.play_pause_button.description = 'Play'
            self.play_pause_button.icon = 'play'

    def play_pause_handler(self, change: dict[str, Any]) -> None:
        """
        Changes the play button to pause when it is clicked.

        Args:
            change (dict[str, Any]): the dictionary representing the value.
        """

        if change['new']:  # if clicked play
            self.play()
            self.play_pause_button.description = 'Pause'
            self.play_pause_button.icon = 'pause'

    def _save_offscreen(
            self,
            name: str,
            px: int,
            extension: ImageExtension,
        ) -> None:
        """
        Renders every frame to a PNG sequence with a headless browser.

        Args:
            name -- str
                The start of the name of the output file.
            px -- int
                Frame width and height in pixels.
        """

        if self._verbose > 0:
            print("Saving frames...", flush=self._flush)

        # RENDERER headless
        with Screenshot(
            plot=self._plot,
            name=name,
            px=px,
            only_canvas=False,
            axes_helper_pos=(0.05, 0.05),
            extension=extension,
            ) as screenshots:

            # CUBEs loop
            for i in range(len(self.constants.dates)):
                # UPDATE
                self.update_plot({'new': i})

                # SAVE
                screenshots.save(ID=f'{i:04d}', sync=True)

                # PRINT
                if self._verbose > 1: print(f"{i:04d} -- SAVED PNG.", flush=self._flush)

        if self._verbose > 0: print("All frames saved", flush=self._flush)
