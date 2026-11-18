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
            radius: float,
            dx: float,
            resolution: int,
            grid: float | None = 30.,
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
            grid -- float | None. Default = 30.
                Grid spacing in degrees. When None, no grid is added.
        """

        # ARGs
        self._grid = grid
        self._resolution = resolution
        self._radius_to_index = radius / dx

        # RUN
        self._phi, self._theta = self._get_angles()
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
            point_size=2.5,
            colors=self._get_colors(),
            shader=shader,
            name='SUN',
            compression_level=compression_lvl,
        )
        return points

    def _get_angles(self) -> tuple[npt.NDArray[np.float32], npt.NDArray[np.float32]]:
        """
        Gives the angles of the points on the surface of the Sun.

        Returns:
            tuple[npt.NDArray[np.float32], npt.NDArray[np.float32]].
                Angles of the points on the surface of the Sun.
        """

        # COORDs spherical
        phi = np.linspace(0, np.pi, self._resolution, dtype=np.float32)
        theta = np.linspace(0, 2 * np.pi, 2 * self._resolution, dtype=np.float32)
        phi, theta = np.meshgrid(phi, theta)
        return phi, theta

    def _get_colors(self) -> list[int]:
        """
        Gives the colors of the points on the surface of the Sun.

        Returns:
            list[int].
                Colors of the points on the surface of the Sun (in hexadecimal format).
        """

        # YELLOW
        if self._grid is None: return [0xffff00] * self._positions.size

        # GRID
        spacing = np.deg2rad(self._grid)
        tol_phi = np.deg2rad(180.0 / (self._resolution - 1)) / 2 * 1.01
        tol_theta = np.deg2rad(360.0 / (2 * self._resolution - 1)) / 2 * 1.01

        d_phi = np.abs(self._phi - np.round(self._phi / spacing) * spacing)
        d_theta = np.abs(self._theta - np.round(self._theta / spacing) * spacing)

        on_grid = (d_phi <= tol_phi) | (d_theta <= tol_theta)
        return np.where(on_grid, 0x000000, 0xffffff).tolist()

    def _get_positions(self) -> npt.NDArray[np.float32]:
        """
        Gives positions on the surface of the Sun in the k3d animation space.

        Returns:
            npt.NDArray[np.float32].
                Positions on the surface of the Sun in the k3d animation space.
        """

        # COORDs cartesian
        x = self._radius_to_index * np.sin(self._phi) * np.cos(self._theta)
        y = self._radius_to_index * np.sin(self._phi) * np.sin(self._theta)
        z = self._radius_to_index * np.cos(self._phi)

        # SAVE coords
        positions = np.array([x.ravel(), y.ravel(), z.ravel()], dtype=np.float32).T
        return positions
