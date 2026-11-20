"""
Set the camera information for the 3D visualization.
"""
from __future__ import annotations

# IMPORTs standard
import os
import time
from dataclasses import dataclass

# IMPORTs third-party
import numpy as np
from astropy.io import fits

# IMPORTs local
from rainbow.config import config

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    # IMPORTs third-party
    import numpy.typing as npt
    from k3d.plot import Plot

# API public
__all__ = ['Camera', 'CubeInfo']



@dataclass(slots=True, repr=False, eq=False, match_args=False)
class CubeInfo:
    """
    Single data cube information.
    """

    shape: tuple[int, int, int]
    bounds: tuple[float, float, float]


class Camera:
    """
    To set up the camera for the k3d visualization.
    """

    def __init__(
            self,
            plot: Plot,
            cube: CubeInfo,
            pos: tuple[float, float, float] | npt.NDArray[np.float32],
            satellite: Literal['sdo', 'stereo'] | None = None,
            zoom: float = 3,
            speed: float = .7,
            fov: float = 0.23,
            up: tuple[int, int, int] = (0, 0, 1),
            sleep: float = 0.2,
        ) -> None:
        # todo add docstring

        # ARGs
        self._plot = plot
        self._zoom = zoom
        self._pos = pos
        self._speed = speed
        self._up = up
        self._sleep = sleep

        # RUN
        self._fov = self._get_fov(satellite) if satellite is not None else fov
        self._ref = tuple(
            bound + shape / 2
            for bound, shape in zip(cube.bounds, cube.shape)
        )
        self._setup()

    def update(self, index: int) -> None:
        """
        Updates the camera position.

        Args:
            index -- int.
                The index of the position to use.
        """

        # CAMERA pos and view
        if not isinstance(self._pos, tuple):
            camera: list[float] = [
                *tuple(float(pos) for pos in self._pos[index]),
                *self._ref,
                *self._up,
            ]
            self._plot.camera = camera
            time.sleep(self._sleep)
        elif index==0:
            camera: list[float] = [
                *tuple(ref + pos for ref, pos in zip(self._ref, self._pos)),
                *self._ref,
                *self._up, 
            ] #type:ignore
            self._plot.camera = camera

    def _get_fov(self, satellite: Literal['sdo', 'stereo']) -> float:
        """
        Gets the field of view of the camera for a given satellite.

        Args:
            satellite -- Literal['sdo', 'stereo'].
                The satellite to use for the FOV.

        Returns:
            float.
                The field of view of the camera.
        """

        if satellite == 'sdo': return self._sdo_fov()
        return self._stereo_fov()

    def _stereo_fov(self) -> float:
        """
        ! wrong. NEED fov degrees not carrington ones.
        Gets the field of view of STEREO.

        Returns:
            float.
                The field of view of STEREO.
        """
        return 1.

    def _sdo_fov(self) -> float:
        """
        Gets the field of view of SDO.

        Returns:
            float.
                The field of view of SDO.
        """

        # FOV get
        hdul = fits.open(
            name=os.path.join(config.dir.input.sdo.mask, 'AIA_fullhead_000.fits.gz'),
        )
        image_shape = hdul[0].data.shape
        fov_degrees = image_shape[0] * hdul[0].header['CDELT1'] / 3600
        hdul.close()
        return fov_degrees / 3

    def _setup(self) -> None:
        """
        Set ups the camera.
        """

        # PARAMs constant
        self._plot.camera_auto_fit = False
        self._plot.camera_fov = self._fov  # FOV in degrees
        self._plot.camera_zoom_speed = self._speed  # zoom speed (default=1.2)

        # UPDATE
        self.update(0)
