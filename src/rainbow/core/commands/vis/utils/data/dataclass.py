"""
To save the dataclasses for the needed information in the animation.
This was created to make it easier to swap between the real and fake protuberance data.
"""
from __future__ import annotations

# IMPORTs standard
from dataclasses import dataclass, field

# IMPORTs third-party
import h5py
import numpy as np

# TYPE ANNOTATIONs
from typing import Any, Self, TypedDict

# API public
__all__ = [
    'Show',
    'ShowTD',
    'CubesConstants',
    'CubesData',
    'PolynomialData',
    'UniquePolynomialData',
    'CubeInfo',
    'UniqueCubeInfo',
]



class ShowTD(TypedDict):
    """
    Whether to show the data and/or the fit.
    """

    data: bool
    fit: bool


@dataclass(slots=True, frozen=True, repr=False, eq=False)
class Show:
    """
    Whether to display the data and/or the polynomial fit of a data group.
    """

    data: bool = True
    fit: bool = False

    def __bool__(self) -> bool:  # ? Do I really need this
        """
        Truthy wether either is True.

        Returns:
            bool
                True if either is True, False otherwise.
        """
        return self.data or self.fit


@dataclass(slots=True, frozen=True, repr=False, eq=False)
class CubesConstants:
    """
    Stores the basic global information for the protuberance.
    It is an immutable class without a __dict__  method (cf. dataclasses.dataclass).
    """

    dx: float
    dates: list[str]
    time_indexes: np.ndarray[tuple[int], np.dtype[np.int_]]


@dataclass(slots=True, frozen=True, repr=False, eq=False)
class PolynomialData:
    """
    Stores the polynomial results and some corresponding information.
    It is an immutable class without a __dict__ method (cf. dataclasses.dataclass).
    """

    # INFO
    name: str
    order: int
    color_hex: int

    # DATA
    dataset: h5py.Dataset

    def __getitem__(self, index: int) -> np.ndarray[tuple[int, int, int], np.dtype[np.uint8]]:
        """
        To get a single cube from the polynomial data.

        Args:
            index (int): the time index needed to be fetched.

        Returns:
            np.ndarray: the polynomial data.
        """

        # FILTER
        cube_filter = self.dataset[0] == index
        cube_coords = self.dataset[1:, cube_filter]

        # NO DATA
        if cube_coords.size == 0: return np.zeros((1, 1, 1), dtype='uint8')

        # DATA 3D
        cube_shape = np.max(cube_coords, axis=1) + 1
        cube = np.zeros(cube_shape, dtype='uint8')
        cube[tuple(cube_coords)] = 1
        return cube


@dataclass(slots=True, frozen=True, repr=False, eq=False)
class UniquePolynomialData(PolynomialData):

    def __getitem__(self, index: Any) -> np.ndarray[tuple[int, int, int], np.dtype[np.uint8]]:
        """
        Just gives back the dense representation of the polynomial data.
        The index argument is not used as in this case, there is only one fit in the dataset.
        The index is here to be consistent with the other __getitem__ methods.

        Args:
            index (Any): just a placeholder to look like the other __getitem__ methods.

        Returns:
            np.ndarray: the polynomial data.
        """

        # 3D array
        cube_shape = np.max(self.dataset, axis=1) + 1
        cube = np.zeros(cube_shape, dtype='uint8')
        cube[tuple(self.dataset)] = 1
        return cube


@dataclass(slots=True, repr=False, eq=False)
class ParentInfo:
    """
    Stores the data and information related to each different data group chosen.
    """

    # METADATA
    group_path: str
    opacity: float
    opacity_polynomial: float
    colour: str

    # BORDERs index
    xt_min_index: float
    yt_min_index: float
    zt_min_index: float

    # DATA
    dataset_coords: h5py.Dataset
    dataset_values: h5py.Dataset

    # DISPLAY
    show: Show = field(default_factory=Show)

    # COORDs shape
    name: str = field(init=False)
    shape: tuple = field(init=False)

    def __post_init__(self) -> None:

        self.name = self.get_name()
        self.shape = tuple(int(val) for val in np.max(self.dataset_coords, axis=1) + 1)

    def get_name(self) -> str:
        """
        To create the name of the dataset depending on the group path.

        Returns:
            str: the name of the dataset.
        """

        group_names = self.group_path.split('/')

        if 'Fake' in group_names: return 'Fake ' + group_names[-1]
        return group_names[-1]


@dataclass(slots=True, repr=False, eq=False)
class CubeInfo(ParentInfo):
    """
    Stores the data and information related to the 'real' data cubes.
    """

    # DATA
    polynomials: list[PolynomialData] | None = field(default=None)

    def __getitem__(self, index: int) -> list[np.ndarray]:
        """
        To get a single cube from each the protuberance and polynomials data.

        Args:
            index (int): the time index needed to be fetched.

        Returns:
            list[np.ndarray]: the protuberance and polynomials data.
        """

        # FILTER
        cube_filter = self.dataset_coords[0] == index
        cube_coords = self.dataset_coords[1:, cube_filter]
        if self.dataset_values.shape == ():
            values = self.dataset_values[...]
        else:
            values = self.dataset_values[cube_filter.ravel()]

        # NO DATA
        if cube_coords.size == 0: # todo check this
            result: list[np.ndarray] = []
            if self.show.data:
                result.append(np.zeros((1, 1, 1), dtype=np.uint8))
            if self.polynomials is not None:
                result += [np.zeros((1, 1, 1), dtype=np.uint8) for _ in self.polynomials]
            return result

        # DATA 3D
        result: list[np.ndarray] = []  # todo check this
        if self.show.data:
            cube = np.zeros(self.shape[1:], dtype=np.uint8)
            cube[tuple(cube_coords)] = values
            result.append(cube)

        # POLYNOMIALs
        if self.polynomials is not None:
            result += [polynomial[index] for polynomial in self.polynomials]
        return result


@dataclass(slots=True, repr=False, eq=False)
class UniqueCubeInfo(ParentInfo):
    """
    Stores the data and information related to the 'test' data cube.
    """

    # PLACEHOLDER
    polynomials: list[UniquePolynomialData] | None = field(default=None)

    def __getitem__(self, index: Any) -> list[np.ndarray]:
        """
        To get the dense array corresponding to the test data.
        Always gives to the user the same cube but the method was defined so the class can be used
        the same way as the ones for the real and the fake data.

        Args:
            index (Any): can be anything as it is not used.

        Returns:
            list[np.ndarray]: the dense test cube inside a list.
        """

        # CUBE
        result: list[np.ndarray] = []  # todo check this
        if self.show.data:
            cube = np.zeros(self.shape, dtype=np.uint8)
            cube[tuple(self.dataset_coords)] = self.dataset_values[...]
            result.append(cube)

        # POLYNOMIALs
        if self.polynomials is not None:  # ! could be wrong as there is only one index here
            result += [polynomial[0] for polynomial in self.polynomials]
        return result


@dataclass(slots=True, repr=False, eq=False)
class CubesData:
    """
    Stores all the data and information needed to name and position the solar protuberance for the
    k3d animation.
    This class doesn't have a __dict__() method (cf. dataclasses.dataclass).
    """

    # FILE
    hdf5File: h5py.File

    # POS satellites
    sdo_pos: np.ndarray[tuple[int], np.dtype[np.float32]] | None = field(default=None, init=False)
    stereo_pos: np.ndarray[tuple[int], np.dtype[np.float32]] | None = field(
        default=None,
        init=False,
    )

    # CUBES data
    all_data: CubeInfo | None = field(default=None, init=False)
    no_duplicate: CubeInfo | None = field(default=None, init=False)
    integration_all_data: CubeInfo | None = field(default=None, init=False)
    integration_no_duplicate: CubeInfo | None = field(default=None, init=False)
    full_integration_all_data: UniqueCubeInfo | None = field(default=None, init=False)
    full_integration_no_duplicate: UniqueCubeInfo | None = field(default=None, init=False)
    los_sdo: CubeInfo | None = field(default=None, init=False)
    los_stereo: CubeInfo | None = field(default=None, init=False)

    # FAKE data
    sun_surface: CubeInfo | None = field(default=None, init=False)

    # TEST data
    test_cube: UniqueCubeInfo | None = field(default=None, init=False)

    def __enter__(self) -> Self: return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None: self.hdf5File.close()

    def close(self):
        """
        To close the hdf5 file.
        """
        self.hdf5File.close()
