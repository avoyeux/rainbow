"""
To create fake STEREO and SDO masks based on the original data to see visualize the no duplicates
processing.
"""
from __future__ import annotations

# IMPORTs standard
import os
import multiprocessing as mp
from dataclasses import dataclass, field

# IMPORTs third-party
import numpy as np
import PIL.Image
import matplotlib.pyplot as plt
from astropy.io import fits

# IMPORTs local
from rainbow.config import config

# TYPE ANNOTATIONs
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from rainbow.typing import CounterType

# API public
__all__ = ['TotoInputs']



@dataclass(slots=True, repr=False, eq=False)
class SdoHeaderInformation:
    """
    To store the information from the SDO FITS header.
    """
    
    # CONSTANTs
    d_sun: float  # distance to sun in m
    resolution_arcsec: float  # pixel resolution in arcsec
    sun_center: tuple[float, float]  # the center of the sun in the image in pixels
    
    # PLACEHOLDERs
    dx: float = field(init=False)

    def __post_init__(self) -> None:
        # PIXEL size km
        self.dx = ((
            (np.tan(np.deg2rad(self.resolution_arcsec / 3600) / 2) * self.d_sun) * 2
        ) / 1e3)


class TotoInputs:
    """
    To create the fake data inputs (i.e. FITs + PNGs) for Dr. Auchere's new_toto.pro code.
    """

    def __init__(
            self,
            sphere_radius: tuple[float, ...] = (7e5, 7.2e5),
            sphere_width: float = 1e4,
            stereo_radii: tuple[float, ...] = (0.6, 0.8),
            stereo_width: float = 0.05,
            stereo_center: tuple[float, float] = (0.7, 0.5),
            nb_cubes: int = 413,
            processes: int = 1,
            verbose: int = 0,
            flush: bool = False,
        ) -> None:
        """
        To create the fake data inputs for Dr. Auchere's new_toto.pro code.

        Args:
            sphere_radius (tuple[float, ...]): the radius of the sphere in km.
                Defaults to (7e5, 7.2e5).
            sphere_width (float, optional): the radial width of the SDO circles in km.
                Defaults to 1e4.
            stereo_radii (tuple[float, ...], optional): the radius of the SDO circles in km.
                Defaults to (0.6, 0.8).
            stereo_width (float, optional): the radial width of the SDO circles in km.
                Defaults to 0.05.
            stereo_center (tuple[float, float], optional): the center of the SDO circles in pixels.
                Defaults to (0.7, 0.5).
            nb_cubes (int): the number of fake data to create. Defaults to 413.
            processes (int, optional): the number of processes to use. Defaults to 1.
        """

        # CONFIG
        self._processes = processes
        self._verbose = verbose
        self._flush = flush

        # ATTRIBUTEs
        self._nb_cubes = nb_cubes
        self._sphere_radius = sphere_radius
        self._sphere_width = sphere_width
        self._stereo_radii = stereo_radii
        self._stereo_width = stereo_width
        self._stereo_center = stereo_center

        # RUN
        self._paths = self._paths_setup()
        self._create_stereo_fake_data()
        self._create_sdo_fake_data()

    def _paths_setup(self) -> dict[str, str]:
        """
        Gives the paths to the different needed directories.

        Returns:
            dict[str, str]: the paths to the different directories.
        """

        # PATHs formatting
        paths = {
            'stereo files': config.dir.input.stereo.wave304.mask_karine,
            'sdo files': config.dir.input.sdo.mask,
            'save sdo fits': config.dir.output.fake.sdo.fits,
            'save sdo png': config.dir.output.fake.sdo.png,
            'save stereo': config.dir.output.fake.stereo,
        }
        return paths

    def _create_stereo_fake_data(self) -> None:
        """
        To create the fake data for the STEREO masks.
        """

        with PIL.Image.open(os.path.join(self._paths['stereo files'], 'frame0000.png')) as real:
            width, height = real.size  # (W, H)

        for index in range(self._nb_cubes):
            image = self.arc_image(width=width, height=height)
            PIL.Image.fromarray(image).save(
                os.path.join(self._paths['save stereo'], f'frame{index:04d}.png'),
            )

    def arc_image(self, width: int, height: int) -> np.ndarray:
        """
        To create an RGB mask image made of the fake circle arcs.

        Args:
            width (int): the width of the image in pixels.
            height (int): the height of the image in pixels.

        Returns:
            np.ndarray: the (height, width, 3) uint8 mask image. The background (excluded) is
                white and the arcs (kept) are black.
        """

        # BACKGROUND excluded (white)
        image = np.full((height, width, 3), 255, dtype=np.uint8)

        # ARCs kept (black)
        scale = min(width, height) / 2
        center = (width * self._stereo_center[0], height * self._stereo_center[1])
        for radius in self._stereo_radii:
            self.draw_arc(
                image=image,
                center=center,
                radius=radius * scale,
                width=self._stereo_width * scale,
            )
        return image

    def draw_arc(
            self,
            image: np.ndarray,
            center: tuple[float, float],
            radius: float,
            width: float,
        ) -> None:
        """
        To draw a half circle arc (kept pixels) on the mask image, with its apex pointing left.

        Args:
            image (np.ndarray): the (height, width, 3) mask image to draw onto.
            center (tuple[float, float]): the (x, y) center of the arc in pixels.
            radius (float): the radius of the arc in pixels.
            width (float): the radial width of the arc in pixels.
        """

        # COORDs half circle apex left
        num_theta = max(4000, int(radius * np.pi * 4))
        theta = np.linspace(np.pi / 2, 3 * np.pi / 2, num=num_theta)

        # RADII with width
        offsets = np.arange(-width / 2, width / 2 + 0.5, 0.5)
        radii = radius + offsets[:, None]

        # COORDs cartesian
        x = np.round(center[0] + radii * np.cos(theta)).astype(int)
        y = np.round(center[1] + radii * np.sin(theta)).astype(int)

        # INDEXEs in bound
        keep = (x >= 0) & (x < image.shape[1]) & (y >= 0) & (y < image.shape[0])
        image[y[keep], x[keep]] = 0

    def _create_sdo_fake_data(self) -> None:
        """
        To create the fake data for the SDO masks.
        """

        # MULTIPROCESSING setup
        processes_nb = min(self._processes, self._nb_cubes)

        if processes_nb > 1:
            counter = mp.Value('i', 0)

            # MULTIPROCESSING run
            processes: list[mp.Process] = [None] * processes_nb  #type:ignore
            for i in range(processes_nb):
                p = mp.Process(
                    target=self.sdo_fake_data_multiprocessing,
                    args=(counter,),
                )
                p.start()
                processes[i] = p
            for p in processes: p.join()
        else:
            # NO MULTIPROCESSING
            for i in range(self._nb_cubes): self.create_sun_image_sdo(index=i)

    def sdo_fake_data_multiprocessing(self, counter: CounterType[int]) -> None:
        """
        To create the fake data for the SDO masks in multiprocessing.

        Args:
            counter -- CounterType[int]
                A counter proxy from the multiprocessing.Manager class.
        """

        while True:
            # NEXT
            with counter.get_lock():
                index = counter.value
                if index >= self._nb_cubes: return
                counter.value += 1

            self.create_sun_image_sdo(index)

    def create_sun_image_sdo(self, index: int) -> None:
        """
        To create the fake fits file image.

        Args:
            index (int): the index of the SDO FITS file.
        """

        # HDU open
        sdo_file_name = f'AIA_fullhead_{index:03d}.fits.gz'
        sdo_hdul = fits.open(
            os.path.join(self._paths['sdo files'], sdo_file_name),
            mode='readonly',
        )
        fake_hdul = fits.HDUList([hdu.copy() for hdu in sdo_hdul])
        
        # INFO formatting
        hdu = fake_hdul[0] 
        sdo_info = SdoHeaderInformation(
            sun_center=(hdu.header['X0_MP'], hdu.header['Y0_MP']),
            resolution_arcsec=hdu.header['CDELT1'],
            d_sun=hdu.header['DSUN_OBS'],
        )

        # SUN IMAGE creation
        image = np.zeros(hdu.data.shape, dtype=np.uint8)

        for radius in self._sphere_radius:
            # COORDs sun
            x, y = self.circle(radius, self._sphere_width, sdo_info.dx)

            x_indexes = (x / sdo_info.dx) + sdo_info.sun_center[0]
            y_indexes = (y / sdo_info.dx) + sdo_info.sun_center[1]

            # INDEXEs positive integers
            x_indexes = np.round(x_indexes).astype(int)
            y_indexes = np.round(y_indexes).astype(int)

            # SAVE image
            image[y_indexes, x_indexes] = 1

        # CHECK
        png_filename = sdo_file_name.replace('.fits.gz', '.png')
        self.plot(filename=png_filename, image=image)

        # SAVE hdul
        fake_hdul[0].data = image
        fake_hdul.writeto(
            fileobj=os.path.join(self._paths['save sdo fits'], sdo_file_name),
            overwrite=True,
        )
        fake_hdul.close()
        if self._verbose > 0: print(f'SAVED - {sdo_file_name}', flush=self._flush)

    def plot(self, filename: str, image: np.ndarray) -> None:
        """
        To plot the sdo fits mask results for a visual check.

        Args:
            filename (str): the filename of the image to save.
            image (np.ndarray): the image to plot.
        """

        plt.figure()
        plt.imshow(image, cmap='gray', interpolation='none')
        plt.colorbar()
        plt.savefig(os.path.join(self._paths['save sdo png'], filename), dpi=800)
        plt.close()

    def circle(self, radius: float, width: float, resolution: float) -> np.ndarray:
        """
        To create the cartesian coordinates of a circle outline.

        Args:
            radius (float): the radius of the circle in km.
            width (float): the radial width of the circle in km.
            resolution (float): the resolution of the SDO image in km.

        Returns:
            np.ndarray: the cartesian coordinates of the circle.
        """

        # COORDs polar (only the circle outline, not the full disk)
        num_theta = max(4000, int(2 * np.pi * radius / (resolution / 8)))
        theta = np.linspace(0, 2 * np.pi, num=num_theta)

        # RADII with width
        offsets = np.arange(-width / 2, width / 2 + resolution / 8, resolution / 8)
        radii = radius + offsets[:, None]

        # COORDs cartesian
        x = radii * np.cos(theta)
        y = radii * np.sin(theta)
        return np.stack([x.ravel(), y.ravel()], axis=0)



if __name__=='__main__':

    TotoInputs(
        processes=8,
        sphere_radius=(7e5, 7.2e5),
        sphere_width=1e4,
    )
