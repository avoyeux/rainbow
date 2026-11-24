"""
Headless PNG capture for the k3d visualization.
"""
from __future__ import annotations

# IMPORTs standard
import os

# IMPORTs third-party
from k3d.headless import get_headless_driver, k3d_remote

# IMPORTs local
from rainbow.config import config

# TYPE ANNOTATIONS
from typing import TYPE_CHECKING, Any, Self
if TYPE_CHECKING:
    # IMPORTs third-party
    from k3d.plot import Plot

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
    To capture PNG frames of a ``k3d.plot`` with a headless browser.

    Usage:
        with Screenshot(plot, width=1920, height=1080) as shots: shots.save('frame.png')
    """

    def __init__(
            self,
            plot: Plot,
            width: int = 1920,
            height: int = 1080,
            only_canvas: bool = True,
            extra_args: list[str] | None = None,
            driver: Any = None,
        ) -> None:
        """
        Captures PNG frames of a ``k3d.plot`` with a headless browser.
        Use the 'save' method to save the frames to png.

        Args:
            plot -- k3d.plot.Plot
                The plot to render.
            width -- int (default: 1920)
                Browser width in pixels.
            height -- int (default: 1080)
                Browser height in pixels.
            out_dir -- str | None (default: None)
                The directory that relative capture names are resolved (relative to the current 
                working directory).
            only_canvas -- bool (default: True)
                Whether to capture only the WebGL canvas instead of the whole page.
            extra_args -- list[str] | None (default: None)
                The extra Chrome switches appended after the ones
                this module needs, e.g. ``['--enable-precise-memory-info']``. Defaults to None.
            driver -- Any | None (default: None)
                The pre-built Selenium driver to use instead of creating one.
        """

        # ARGs
        self._plot = plot
        self._width = width
        self._height = height
        self._only_canvas = only_canvas
        self._extra_args = extra_args
        self._driver = driver
        self._remote: k3d_remote = None  #type:ignore
        self._dir = config.dir.output.k3d

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
            width=self._width,
            height=self._height,
        )
        return self

    def __exit__(self, *exceptions: Any) -> None: self.close()

    def save(self, name: str, sync: bool = True) -> str:
        """
        Renders the current scene and saves it as a png.

        Args:
            name -- str
                The name of the png file.
            sync -- bool (default: True)
                Block until the render is complete. Keep True for frame-by-frame capture.

        Returns:
            str: the resolved path written to.
        """

        # CHECK
        self._require_session()

        # SAVE
        path = os.path.join(self._dir, name)
        if sync: self._sync()
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
        Renders the current scene and saves it as a PNG to ``path``.

        Args:
            path -- str
                The file to write.
        """

        png = self._remote.get_screenshot(only_canvas=self._only_canvas)
        with open(path, 'wb') as file: file.write(png)

    def _require_session(self) -> None:
        """
        Checks that a headless session is open.

        Raises:
            RuntimeError: If no headless session is open.
        """

        if self._remote is None:
            raise RuntimeError("No headless session is open. Use Screenshot as a context manager.")
