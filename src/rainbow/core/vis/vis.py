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
from .sun import Sun
from .camera import Camera, Info as CameraInfo
from .dataclass import (
    CubesData, CubesConstants, CubeInfo, UniqueCubeInfo,
    PolynomialData, UniquePolynomialData,
)
from .screenshot import Screenshot

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING, Any, overload, Literal, cast
if TYPE_CHECKING:
    # IMPORTs third-party
    import numpy.typing as npt

    # IMPORTs local
    from rainbow.typing import VoxelAlias, JsLinkAlias

# API public
__all__ = ['K3dAnimation']

# todo need to improve the names of the different datasets in the visualization
# todo need to be able to add the extended version of the polynomial fit



class Setup:
    """
    Manipulates the HDF5 filament data file to setup the necessary data choices for the
    visualization.
    This class is the parent class to the k3d visualization class named K3dAnimation.
    """

    @typeguard.typechecked
    def __init__(
            self,
            filepath: str = config.file.data,
            choices: list[str] = ['sdo pov', 'sun', 'no duplicate', 'fit'],
            time_interval: int = 24,
            polynomial_order: list[int] = [4],
            verbose: int = 0,
            flush: bool = False,
        ) -> None:
        """
        todo update docstring
        To setup the necessary data for the visualization.

        Args:
            filepath (str optional): the filepath to the HDF5 file. Defaults to config.file.data.
            choices (list[str], optional): the choices for the visualization.
                Defaults to ['sdo pov', 'sun', 'no duplicate', 'fit'].
            time_interval (int, optional): time interval use for the data integration (in hours).
                Defaults to 24.
            polynomial_order (list[int], optional): the polynomial order(s) used for the fitting.
                Defaults to [4].
            verbose (int | None, optional): the verbosity level for the prints. If None, it will
                use the config file. Defaults to None.
            flush (int | None, optional): deciding to flush the buffer each time there is a print.
                If None, it will use the config file. Defaults to None.
        """

        # CONSTANTs
        self._solar_r = 6.96e5

        # CONFIGURATION attributes
        self._filepath = filepath
        self._verbose = verbose
        self._flush = flush

        # ATTRIBUTEs other
        self._time_interval = time_interval
        self._polynomial_order = polynomial_order

        # ATTRIBUTES new
        self._choices = self._get_choices(choices)
        self._plot_polynomial_colors = [
            next(Plot.random_hexadecimal_int_color_generator())
            for _ in self._polynomial_order
        ]
        self._feet = ' with feet' if self._choices['with feet'] else ''

        # RUN
        self._cubes = self._get_data()

    def _get_choices(self, plot_choices: list[str]) -> dict[str, bool]:
        """
        Checks and formats the choices given by the user.

        Args:
            plot_choices (list[str]): the choices given by the user.

        Raises:
            ValueError: if the choice is not recognized.

        Returns:
            dict[str, bool]: the formatted choices.
        """

        # CHOICES
        possibilities = [ 
            'sun', 'all dates',
            'all data', 'all data integration', 'all data full integration',
            'no duplicate', 'no duplicate integration', 'no duplicate full integration',
            'line of sight sdo', 'line of sight stereo',
            'pov sdo', 'pov stereo',
            'fit', 'with feet', 'extended fit',
        ]
        choices_kwargs = {
            key: False 
            for key in possibilities
        }

        # DICT reformatting
        for key in plot_choices: 
            if key in possibilities: 
                choices_kwargs[key] = True
            else: 
                raise ValueError(
                    f"\033[1;0mChoices argument '{key}' not recognized. "
                    f"Valid choices are ['{'\', \''.join(possibilities)}'].\033[0m"
                ) 
        return choices_kwargs

    @Decorators.running_time
    def _get_data(self) -> CubesData:
        """
        Opens the HDF5 file to get the necessary data for visualization.
        """

        # DATA init
        HDF5File = h5py.File(self._filepath, 'r')
        cubes = CubesData(hdf5File=HDF5File)

        # DATA main
        self.constants = self.get_default_data(HDF5File)

        # CHOICES data
        if self._choices['all data']: 
            path = 'Filtered/All data' + self._feet
            cubes.all_data = self.get_cube_info(
                HDF5File=HDF5File,
                group_path=path,
                colour='brown',
                opacity=0.3,
                interpolate=False,
            )

        if self._choices['no duplicate']: 
            path = 'Filtered/No duplicates' + self._feet
            cubes.no_duplicate = self.get_cube_info(
                HDF5File=HDF5File,
                group_path=path,
                colour='red',
                opacity=1,
                interpolate=False,
            )

        if self._choices['all data integration']: 
            path = (
                'Time integrated/All data' + self._feet +
                f'/Time integration of {self._time_interval} hours'
            )
            cubes.integration_all_data = self.get_cube_info(
                HDF5File=HDF5File,
                group_path=path,
                colour='red',
                opacity=0.2,
            )

        if self._choices['all data full integration']:
            path = (
                'Time integrated/All data' + self._feet +
                '/Full integration'
            )
            cubes.full_integration_all_data = self.get_cube_info(
                HDF5File=HDF5File,
                group_path=path,
                colour='black',
                opacity=0.1,
                cube_type='unique',
            )

        if self._choices['no duplicate integration']:
            path = (
                'Time integrated/No duplicates' + self._feet +
                f'/Time integration of {self._time_interval} hours'
            )
            cubes.integration_no_duplicate = self.get_cube_info(
                HDF5File=HDF5File,
                group_path=path,
                colour='orange',
                opacity=0.3,
            )

        if self._choices['no duplicate full integration']:
            path = (
                'Time integrated/No duplicates' + self._feet +
                '/Full integration'
            )
            cubes.full_integration_no_duplicate = self.get_cube_info(
                HDF5File=HDF5File,
                group_path=path,
                colour='grey',
                opacity=0.1,
                cube_type='unique',
            )

        if self._choices['line of sight sdo']:
            path = 'Filtered/SDO line of sight'
            cubes.los_sdo = self.get_cube_info(
                HDF5File=HDF5File,
                group_path=path,
                colour='green',
                opacity=0.02,
                interpolate=False,
            )

        if self._choices['line of sight stereo']:
            path = 'Filtered/STEREO line of sight'
            cubes.los_stereo = self.get_cube_info(
                HDF5File=HDF5File,
                group_path=path,
                colour='blue',
                opacity=0.02,
                interpolate=False,
            )

        # POVs sdo, stereo
        if self._choices['pov sdo']:
            # SDO positions
            sdo_positions: npt.NDArray = HDF5File['SDO positions'][...]

            # DATA formatting
            cubes.sdo_pos = (
                sdo_positions[self.constants.time_indexes] / self.constants.dx
            ).astype(np.float32)
        if self._choices['pov stereo']:
            # STEREO positions
            stereo_positions: np.ndarray = cast(h5py.Dataset, HDF5File['STEREO B positions'])[...]

            # DATA formatting
            cubes.stereo_pos = (
                stereo_positions[self.constants.time_indexes] / self.constants.dx
            ).astype(np.float32)
            # todo will need to add the POV center

        return cubes

    def get_default_data(self, HDF5File: h5py.File) -> CubesConstants:
        """
        Gives the global information for the data.

        Args:
            HDF5File (h5py.File): the HDF5 file where the data is stored.

        Returns:
            CubesConstants: the global information of protuberance.
        """

        # DATEs
        dates_bytes: np.ndarray[tuple[int], np.dtype[np.bytes_]] = cast(
            h5py.Dataset,
            HDF5File['Dates'],
        )[...]

        if self._choices['all dates']:
            # TIME INDEXEs all
            time_indexes: np.ndarray[tuple[int], np.dtype[np.int_]] = np.arange(
                0,
                len(dates_bytes),
            )
        else:
            # TIME INDEXEs with data
            time_indexes: np.ndarray[tuple[int], np.dtype[np.int_]] = cast(
                h5py.Dataset,
                HDF5File['Time indexes'],
            )[...]

        dates_str: list[str] = [date.decode('utf-8') for date in dates_bytes[time_indexes]]
        constants = CubesConstants(
            dx=float(cast(h5py.Dataset, HDF5File['dx'])[...]),
            time_indexes=time_indexes,
            dates=dates_str,
        )
        return constants

    @overload
    def get_cube_info(
            self,
            HDF5File: h5py.File,
            group_path: str,
            opacity: float = ...,
            interpolate: bool = ...,
            colour: str = ...,
            *,
            cube_type: Literal['real'] = ...,
        ) -> CubeInfo: ...

    @overload
    def get_cube_info(
            self,
            HDF5File: h5py.File,
            group_path: str,
            opacity: float = ...,
            interpolate: bool = ...,
            colour: str = ...,
            *,
            cube_type: Literal['unique'],
        ) -> UniqueCubeInfo: ...

    @overload # fallback
    def get_cube_info(
            self,
            HDF5File: h5py.File,
            group_path: str,
            opacity: float = ...,
            interpolate: bool = ...,
            colour: str = ...,
            opacity_polynomial: float = ...,
            cube_type: str = ...,
        ) -> CubeInfo | UniqueCubeInfo: ...

    def get_cube_info(
            self,
            HDF5File: h5py.File,
            group_path: str,
            opacity: float = 1.,
            interpolate: bool = True,
            colour: str = 'blue',
            opacity_polynomial: float = 1.,
            cube_type: str = 'real',
        ) -> CubeInfo | UniqueCubeInfo:
        """
        Gives the protuberance and polynomial fit information for a chosen cube 'type'.

        Args:
            HDF5File (h5py.File): the HDF5 file where the data is stored.
            group_path (str): the group path to the group where the needed datasets are stored.
            opacity (float, optional): the opacity of the voxels in the visualization.
                Defaults to 1..
            opacity_polynomial (float, optional): the opacity of the polynomial fits in the visualization.
                Defaults to 1.
            interpolate (bool, optional): if there is interpolation data in the group to visualize.
                Defaults to True.
            colour (str, optional): the colour of the voxels in the visualization.
                Defaults to 'blue'.
            cube_type (str, optional): the type of cube to visualize. Defaults to 'real'.

        Returns:
            CubeInfo | UniqueCubeInfo: the protuberance and polynomial fit
                information.
        """

        # BORDERs as index
        xt_min_index = (
            float(cast(h5py.Dataset, HDF5File[group_path + '/xt_min'])[...]) / self.constants.dx
        )
        yt_min_index = (
            float(cast(h5py.Dataset, HDF5File[group_path + '/yt_min'])[...]) / self.constants.dx
        )
        zt_min_index = (
            float(cast(h5py.Dataset, HDF5File[group_path + '/zt_min'])[...]) / self.constants.dx
        )

        # COO data
        data_coords: h5py.Dataset = cast(h5py.Dataset, HDF5File[group_path + '/coords'])
        data_values: h5py.Dataset = cast(h5py.Dataset, HDF5File[group_path + '/values'])

        # FORMATTING data
        if cube_type == 'real':
            # POLYNOMIAL data
            polynomials = self.get_polynomial_data(
                HDF5File=HDF5File,
                group_path=group_path,
                cube_type=cube_type,
                interpolate=interpolate,
            )

            cube_info = CubeInfo(
                group_path=group_path,
                colour=colour,
                opacity=opacity,
                opacity_polynomial=opacity_polynomial,
                xt_min_index=xt_min_index,
                yt_min_index=yt_min_index,
                zt_min_index=zt_min_index,
                dataset_coords=data_coords,
                dataset_values=data_values,
                polynomials=polynomials,
            )
        elif cube_type == 'unique':
            # POLYNOMIAL data
            polynomials = self.get_polynomial_data(
                HDF5File=HDF5File,
                group_path=group_path,
                cube_type=cube_type,
                interpolate=interpolate,
            )

            cube_info = UniqueCubeInfo(
                group_path=group_path,
                opacity=opacity,
                opacity_polynomial=opacity_polynomial,
                colour=colour,
                xt_min_index=xt_min_index,
                yt_min_index=yt_min_index,
                zt_min_index=zt_min_index,
                dataset_coords=data_coords,
                dataset_values=data_values,
                polynomials=polynomials,
            )
        else:
            raise ValueError(f'cube_type {cube_type} is not implemented.')
        print(f'FETCHED -- {cube_info.name}.', flush=True)
        return cube_info

    @overload
    def get_polynomial_data(
            self,
            HDF5File: h5py.File,
            group_path: str,
            cube_type: str = ...,
            *,
            interpolate: Literal[False],
        ) -> None: ...

    @overload
    def get_polynomial_data(
            self,
            HDF5File: h5py.File,
            group_path: str,
            cube_type: Literal['real'],
            interpolate: Literal[True] = ...,
        ) -> list[PolynomialData]: ...

    @overload
    def get_polynomial_data(
            self,
            HDF5File: h5py.File,
            group_path: str,
            cube_type: Literal['unique'] = ...,
            interpolate: Literal[True] = ...,
        ) -> list[UniquePolynomialData]: ...
    
    @overload # fallback 1
    def get_polynomial_data(
            self,
            HDF5File: h5py.File,
            group_path: str,
            cube_type: Literal['real'],
            interpolate: bool = ...,
        ) -> list[PolynomialData] | None: ...

    @overload # fallback 2
    def get_polynomial_data(
            self,
            HDF5File: h5py.File,
            group_path: str,
            cube_type: Literal['unique'] = ...,
            interpolate: bool = ...,
        ) -> list[UniquePolynomialData] | None: ...

    @overload  # fallback main
    def get_polynomial_data(
            self,
            HDF5File: h5py.File,
            group_path: str,
            cube_type: str = ...,
            interpolate: bool = ...,
        ) -> list[PolynomialData] | list[UniquePolynomialData] | None: ...

    def get_polynomial_data(
            self,
            HDF5File: h5py.File,
            group_path: str,
            cube_type: str = 'unique',
            interpolate: bool = True,
        ) -> list[PolynomialData] | list[UniquePolynomialData] | None:
        """
        To get the polynomial data corresponding to the HDF5 group path.

        Args:
            group_path (str): the main group path where all the different corresponding polynomial
                fits are stored.
            cube_type (str, optional): the type of cube to visualize. Defaults to 'unique'.
            interpolate (bool, optional): if the fit data exits for that group path.
                Defaults to True.

        Returns:
            list[PolynomialData] | list[UniquePolynomialData] | None: the corresponding polynomial
                fits information. If there is no polynomial data, it returns None.
        """

        # ! need to change this so that I can also decide to visualize the extended polynomial fit

        if self._choices['fit'] and interpolate:  # todo add 'or self.choices['extended fit']'
            # POLYNOMIALs setup
            polynomials: list[PolynomialData | UniquePolynomialData] = cast(
                list[PolynomialData | UniquePolynomialData],
                [None] * len(self._polynomial_order)
            )  # the union shouldn't be inside but no choice as the IDE will complain

            for i, order in enumerate(self._polynomial_order):
                # DATA get
                dataset_path = group_path + f'/{order}th order polynomial'
                interpolation_coords = cast(h5py.Dataset, HDF5File[dataset_path + '/coords'])

                if cube_type != 'unique':
                    # DATA formatting
                    polynomials[i] = PolynomialData(  # ? type check requirements are weird ...
                        dataset=interpolation_coords,
                        order=order,
                        name=self.name_data(dataset_path),
                        color_hex=self._plot_polynomial_colors[i],
                    )
                else:
                    # DATA formatting
                    polynomials[i] = UniquePolynomialData(
                        dataset=interpolation_coords,
                        order=order,
                        name=self.name_data(dataset_path),
                        color_hex=self._plot_polynomial_colors[i],
                    )
                print(f'FETCHED -- {polynomials[i].name}.')
            return cast(list[PolynomialData] | list[UniquePolynomialData], polynomials)
        else:
            return None

    def name_data(self, group_path: str) -> str:
        """
        To name the data depending on the group path.

        Args:
            group_path (str): the hdf5 group path to the data being named.

        Raises:
            ValueError: if the group path is not recognized.

        Returns:
            str: the name for the corresponding dataset.
        """

        # INIT name
        name = ''

        # FIT check
        if 'polynomial' in group_path:
            name += 'FIT'

            # PATTERN
            pattern_fit = r'(\d+)th'
            result = re.search(pattern_fit, group_path)

            if result is not None:
                name += f'({result.group(1)}th) '
            else:
                raise ValueError(
                    f"\033[1;31m The group path '{group_path}' pattern not recognized. \033[0m"
                )

        # GROUP check
        if 'All data' in group_path:
            name += 'all data'
        elif 'No duplicates' in group_path:
            name += 'no dupli'

        # INTEGRATION check
        if 'integration' in group_path:
            name += ' integration'
            
            if 'Full' in group_path:
                name += '(full) '
            else:
                # PATTERN
                pattern_integration_time = r'(\d+)\s*hours'
                result = re.search(pattern_integration_time, group_path)

                if result is not None:
                    name += f'({result.group(1)}h) '
                else:
                    raise ValueError(
                        f"\033[1;31m The group path '{group_path}' pattern not recognized. \033[0m"
                    )
        return name

    def color_str_to_hex(self, colour: str) -> int:
        """
        Converts a colour string to hexadecimal int value.

        Args:
            colour (str): the colour name to convert.

        Returns:
            int: the corresponding hexadecimal int value.
        """
        return int(mcolors.to_hex(mcolors.CSS4_COLORS[colour])[1:], 16)

    def close(self) -> None:
        """
        To close the HDF5 file.
        """
        self._cubes.close()


class K3dAnimation(Setup):
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
            width: int = 1920,
            height: int = 1080,
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
            **kwargs: the other arguments to pass to the parent class.
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
        self._plot: Any = k3d.plot(grid_visible=visible_grid)  # black: background_color=0x000000 #type:ignore
        self._plot.height = height
        self._plot.axes_helper = 500
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
        if offscreen: self._save_offscreen(name=name, width=width, height=height)

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
            width: int,
            height: int,
        ) -> None:
        """
        Renders every frame to a PNG sequence with a headless browser.

        Args:
            name -- str
                The start of the name of the output PNG files.
            width -- int
                Browser width in pixels. Defaults to 1920.
            height -- int
                Browser height in pixels. Defaults to 1080.
        """

        if self._verbose > 0:
            print("Saving frames...", flush=self._flush)

        # RENDERER headless
        with Screenshot(
            plot=self._plot,
            width=width,
            height=height,
            only_canvas=False,
            axes_helper_pos=(0.05, 0.05),
            ) as screenshots:

            # CUBEs loop
            for i in range(len(self.constants.dates)):
                # UPDATE
                self.update_plot({'new': i})

                # SAVE
                screenshots.save(name=f'{name}{i:04d}.png', sync=True)

                # PRINT
                if self._verbose > 1: print(f"{i:04d} -- SAVED PNG.", flush=self._flush)

        if self._verbose > 0: print("All frames saved", flush=self._flush)
