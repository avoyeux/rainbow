"""
Code to add the Sun's surface to the 3D animation.
"""
from __future__ import annotations

# IMPORTs third-party
import k3d
import numpy as np

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    # IMPORTs third-party
    import numpy.typing as npt

# API public
__all__ = ['Sun']



class Sun:
    """
    To add the Sun's surface to the k3d animation.
    """

    def __init__(
            self,
            radius: float,  # in km
            dx: float,  # in km
            resolution: int,
            verbose: int = 0,
            flush: bool = False,
        ) -> None:
        """
        Creates the Sun's surface to use in the k3d animation.
        To access the created k3d Points object, use the 'points' method.

        Arguments:
            radius -- float.
                Radius of the Sun in km.
            dx -- float.
                Grid spacing in km.
            resolution -- int.
                Number of points on the surface of the Sun in the theta direction.
                (Double in the phi direction)
            verbose -- int. Default = 0.
                Verbosity level for the prints.
            flush -- bool. Default = False.
                Whether to flush the prints.
        """

        # CONFIG
        self._verbose = verbose
        self._flush = flush

        # ARGs
        self._resolution = resolution
        self._radius_to_index = radius / dx

        # RUN
        self._positions = self._get_positions()

    def points(
            self,
            shader: Literal['flat', 'dot', '3d', 'mesh'] = 'flat',
            compression_lvl: int = 0,
        ) -> k3d.objects.Points:
        """
        Points object from k3d containing the Sun's surface information.

        Arguments:
            shader -- Literal['flat', 'dot', '3d', 'mesh']. Default = 'flat'.
                Shader to use for the points.
            compression_lvl -- int. Default = 0.
                 Compression level for the points object.

        Returns:
            k3d.objects.Points.
                Points object from k3d containing the Sun's surface information.
        """

        points = k3d.points(
            positions=self._positions,
            point_size=0.7,
            colors=[0xffff00] * len(self._positions),
            shader=shader,
            name='SUN',
            compression_level=compression_lvl,
        )
        return points

    def _get_positions(self) -> npt.NDArray[np.float32]:
        """
        Gives positions on the surface of the Sun in the k3d animation space.

        Returns:
            npt.NDArray[np.float32].
                Positions on the surface of the Sun in the k3d animation space.
        """

        # COORDs spherical
        phi = np.linspace(0, np.pi, self._resolution)
        theta = np.linspace(0, 2 * np.pi, 2 * self._resolution)
        phi, theta = np.meshgrid(phi, theta)

        # COORDs cartesian
        x = self._radius_to_index * np.sin(phi) * np.cos(theta)
        y = self._radius_to_index * np.sin(phi) * np.sin(theta)
        z = self._radius_to_index * np.cos(phi)

        # SAVE coords
        positions = np.array([x.ravel(), y.ravel(), z.ravel()], dtype=np.float32).T
        return positions
