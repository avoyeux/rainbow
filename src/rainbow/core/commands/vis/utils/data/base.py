"""
The parent class for the visualization.
Setups and opens the needed data cubes.
"""
from __future__ import annotations

# IMPORTs standard
import re

# IMPORTs third-party
import h5py
import numpy as np
from matplotlib import colors as mcolors

# IMPORTs personal
from common import Plot, Decorators

# IMPORTs local
from rainbow.config import config
from .dataclass import (
    CubesData, CubesConstants, CubeInfo, UniqueCubeInfo, PolynomialData, UniquePolynomialData,
)

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING, overload, Literal
if TYPE_CHECKING:
    # IMPORTs third-party
    import numpy.typing as npt

# API public
__all__ = ['Setup']



class Setup:
    """
    Manipulates the HDF5 filament data file to setup the necessary data choices for the
    visualization.
    This class is the parent class to the k3d visualization class named K3dAnimation.
    """

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
                colour='grey',
                opacity=0.4,
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
            stereo_positions: npt.NDArray = HDF5File['STEREO B positions'][...]

            # DATA formatting
            cubes.stereo_pos = (
                stereo_positions[self.constants.time_indexes] / self.constants.dx
            ).astype(np.float32)
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
        dates_bytes: np.ndarray[tuple[int], np.dtype[np.bytes_]] = HDF5File['Dates'][...]

        if self._choices['all dates']:
            # TIME INDEXEs all
            time_indexes: np.ndarray[tuple[int], np.dtype[np.int_]] = np.arange(
                0,
                len(dates_bytes),
            )
        else:
            # TIME INDEXEs with data
            time_indexes: np.ndarray[tuple[int], np.dtype[np.int_]] = HDF5File['Time indexes'][...]

        dates_str: list[str] = [date.decode('utf-8') for date in dates_bytes[time_indexes]]
        constants = CubesConstants(
            dx=float(HDF5File['dx'][...]),
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
            float(HDF5File[group_path + '/xt_min'][...]) / self.constants.dx
        )
        yt_min_index = (
            float(HDF5File[group_path + '/yt_min'][...]) / self.constants.dx
        )
        zt_min_index = (
            float(HDF5File[group_path + '/zt_min'][...]) / self.constants.dx
        )

        # COO data
        data_coords: h5py.Dataset = HDF5File[group_path + '/coords']
        data_values: h5py.Dataset = HDF5File[group_path + '/values']

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
            polynomials: list[PolynomialData | UniquePolynomialData] = (
                [None] * len(self._polynomial_order)
            )  #type:ignore  # the union shouldn't be inside but no choice as the IDE will complain

            for i, order in enumerate(self._polynomial_order):
                # DATA get
                dataset_path = group_path + f'/{order}th order polynomial'
                interpolation_coords = HDF5File[dataset_path + '/coords']

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
            return polynomials
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
