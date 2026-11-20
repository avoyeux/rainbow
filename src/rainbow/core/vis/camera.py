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
__all__ = ['Camera', 'Info']



@dataclass(slots=True, repr=False, eq=False, match_args=False)
class Info:
    """
    Single data cube information.
    """

    dx: float
    solar_r: float
    shape: tuple[int, int, int]
    bounds: tuple[float, float, float]


class Camera:
    """
    To set up the camera for the k3d visualization.
    """

    def __init__(
            self,
            plot: Plot,
            info: Info,
            pos: npt.NDArray[np.float32],
            satellite: Literal['sdo', 'stereo'] | None = None,
            zoom: float = 3,
            speed: float = .7,
            fov: float = 0.23,
            up: tuple[int, int, int] = (0, 0, 1),
            sleep: float = 0.2,
        ) -> None:
        # todo add docstring
        # ! need to add the distance to the satellite.

        # ARGs
        self._fov = fov
        self._plot = plot
        self._zoom = zoom
        self._pos = pos
        self._speed = speed
        self._up = up
        self._sleep = sleep
        self._info = info
        self._satellite = satellite

        # RUN
        self._ref = tuple(
            bound + shape / 2
            for bound, shape in zip(info.bounds, info.shape)
        )
        self._setup()

    def update(self, index: int) -> None:
        """
        Updates the camera position.

        Args:
            index -- int.
                The index of the position to use.
        """

        # FOV
        self._plot.camera_fov = self._get_fov(index)

        # CAMERA pos and view
        camera: list[float] = [
            *tuple(float(pos) for pos in self._pos[index]),
            *self._ref,
            *self._up,
        ]
        self._plot.camera = camera
        time.sleep(self._sleep)

    def _get_fov(self, index: int) -> float:
        """
        Gets the field of view of the camera for a given satellite.

        Args:
            index -- int.
                The index of the position to use.

        Returns:
            float.
                The field of view of the camera.
        """

        if self._satellite is None: return self._fov
        if self._satellite == 'sdo': return self._sdo_fov()
        return self._stereo_fov(index)

    def _stereo_fov(self, index: int) -> float:
        """
        Gets the field of view of STEREO.

        Args:
            index -- int.
                The index of the position to use.

        Returns:
            float.
                The field of view of STEREO.
        """
        pos = self._pos[index]
        print(f'solar r is {self._info.solar_r}', flush=True)

        d_sun: float = np.sqrt(np.dot(pos, pos))
        print(f'd_sun is {d_sun}', flush=True)

        carrington_fov = np.deg2rad(45)

        sun = self._info.solar_r / self._info.dx * np.tan(carrington_fov / 2)
        fov = 2 * np.arctan(sun / d_sun)
        print(f'fov is {fov}', flush=True)
        return np.rad2deg(fov)

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
        self._plot.camera_zoom_speed = self._speed  # zoom speed (default=1.2)

        # UPDATE
        self.update(0)
