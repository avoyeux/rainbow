"""
Headless frame capture for the k3d visualization.
"""
from __future__ import annotations

# IMPORTs standard
import io
import os

# IMPORTs third-party
from PIL import Image
from k3d.headless import get_headless_driver, k3d_remote

# IMPORTs local
from .js_patch import TriadPatch
from rainbow.config import config

# TYPE ANNOTATIONS
from typing import TYPE_CHECKING, Any, Self
if TYPE_CHECKING:
    # IMPORTs third-party
    from k3d.plot import Plot

    # IMPORTs local
    from rainbow.typing import ImageExtension

# API public
__all__ = ['Screenshot']



def _headless_extra_args() -> list[str]:
    """
    Chrome switches that headless rendering needs on snap Chromium.

    Returns:
        list[str]: the switches to append to the driver's arguments.
    """

    profile = os.path.realpath(os.path.join(config.dir.temp, 'chrome-profile'))
    os.makedirs(profile, exist_ok=True)

    return ['--disable-dev-shm-usage', '--user-data-dir=' + profile]


class Screenshot:
    """
    To capture frames of a ``k3d.plot`` with a headless browser and save them.

    Usage:
        with Screenshot(plot, name='frames', px=1920) as shots: shots.save('0001')
    """

    def __init__(
            self,
            plot: Plot,
            name: str = '',
            px: int = 1280,
            label_size: float = 1.2,
            only_canvas: bool = True,
            extra_args: list[str] | None = None,
            driver: Any = None,
            axes_helper_pos: tuple[float, float] | None = None,
            extension: ImageExtension = '.png',
        ) -> None:
        """
        Captures frames of a ``k3d.plot`` with a headless browser.
        Use the 'save' method to save the frames.

        Args:
            plot -- k3d.plot.Plot
                The plot to render.
            name -- str (default: '')
                The chosen name for the capture session.
            px -- int (default: 1280)
                Output image width and height in pixels.
            label_size -- float (default: 1.2)
                Triad label size in em (CSS unit).
            only_canvas -- bool (default: True)
                Whether to capture only the WebGL canvas instead of the whole page.
            extra_args -- list[str] | None (default: None)
                The extra Chrome switches appended after the ones
                this module needs, e.g. ``['--enable-precise-memory-info']``.
            driver -- Any | None (default: None)
                The pre-built Selenium driver to use instead of creating one.
            axes_helper_pos -- tuple[float, float] | None (default: None)
                Where to place the orientation triad in the saved image, as the fraction
                ``(x, y)`` of the image, measured from its bottom-left corner. None keeps k3d
                defaults.
            extension -- ImageExtension (default: '.png')
                The file extension to use for the saved images.
        """

        # ARGs
        self._plot = plot
        self._px = px
        self._label_size = label_size
        self._only_canvas = only_canvas
        self._extension = extension
        self._extra_args = extra_args
        self._driver = driver
        self._axes_helper_pos = axes_helper_pos
        self._remote: k3d_remote = None  #type:ignore
        self._dir = os.path.join(config.dir.output.k3d.frame, name)
        os.makedirs(self._dir, exist_ok=True)

        # PLACEHOLDER
        self._patch: TriadPatch

    def __enter__(self) -> Self:
        """
        Enters the context.
        Sets up the drive and the remote session.

        Returns:
            Self
                the instance with the driver and remote session open.
        """

        if self._driver is None:
            self._driver = get_headless_driver(
                extra_args=_headless_extra_args() + (self._extra_args or []),
            )

        self._remote = k3d_remote(
            k3d_plot=self._plot,
            driver=self._driver,
            width=self._px,
            height=self._px,
        )

        # MOVE the orientation triad
        if self._axes_helper_pos is not None:
            self._patch = TriadPatch(
                remote=self._remote,
                label=self._label_size,
                pos=self._axes_helper_pos,
            )
        return self

    def __exit__(self, *exceptions: Any) -> None: self.close()

    def save(self, ID: str, sync: bool = True) -> str:
        """
        Renders the current scene and saves it.

        Args:
            ID -- str
                The unique identifier of the frame. Used to name the file.
            sync -- bool (default: True)
                Block until the render is complete. Keep True for frame-by-frame capture.

        Returns:
            str: the resolved path written to.
        """

        # CHECK
        self._require_session()

        # SYNC
        path = os.path.join(self._dir, f'frame{ID}{self._extension}')
        if sync: self._sync()

        # AXES label pos
        if self._axes_helper_pos is not None: self._patch.label_sync()

        # SAVE
        self._capture(path)
        return path

    def close(self) -> None:
        """
        Shuts down the headless browser and its HTTP server.
        """

        self._driver = None
        if self._remote is not None:
            # CLOSE session
            self._remote.close()
            self._remote = None  #type:ignore
            self._patch = None  #type:ignore

    def _sync(self, hold: bool = True) -> None:
        """
        Pushes the plot's current state to the browser and waits for it to render.
        Must be called after changing the voxels/camera and before `_capture`.

        Args:
            hold -- bool (default: True)
                Block until the render is complete. Keep True for frame-by-frame capture.
        """

        self._require_session()
        self._remote.sync(hold_until_refreshed=hold)

    def _capture(self, path: str) -> None:
        """
        Renders the current scene and saves it.

        Args:
            path -- str
                The file to write.
        """

        png: bytes = self._remote.get_screenshot(only_canvas=self._only_canvas)

        if self._extension == '.png':
            with open(path, 'wb') as file: file.write(png)
        else:
            img = Image.open(io.BytesIO(png)).convert('RGB')
            img.save(path)

    def _require_session(self) -> None:
        """
        Checks that a headless session is open.

        Raises:
            RuntimeError: If no headless session is open.
        """

        if self._remote is None:
            raise RuntimeError("No headless session is open. Use Screenshot as a context manager.")
