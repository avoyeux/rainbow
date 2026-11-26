"""
Javascript code patches.
These are used to be able to move the triad position and set the triad label size.
The JS part is fully written with AI as its getting embedded in the k3d plot...
"""
from __future__ import annotations

# IMPORTs standard
import time

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # IMPORTs third-party
    from k3d.headless import k3d_remote

# API public
__all__ = ['JSPatch']



class TriadPatch:
    """
    Patches to set the helper triad position and corresponding label size.
    There patches were written in JS using DeepSeek v4.1.
    """

    def __init__(
            self,
            remote: k3d_remote,
            label: float,
            pos: tuple[float, float],
            timeout: float = 30.0,
        ) -> None:
        """
        Sets up the triad position and corresponding label size.

        Arguments:
            remote -- k3d_remote
                Remote k3d instance.
            label -- float
                Triad label size in em (CSS unit).
            pos -- tuple[float, float]
                Triad position relative to the created image.
            timeout -- float (default: 30.0)
                Timeout in seconds for the plot to be ready. If passed, raises TimeoutError.
        """

        # ARGs
        self._label = label
        self._pos = pos
        self._timeout = timeout
        self._remote = remote
        self._primed: bool = False

        # RUN
        self._set_triad()

    def _set_triad(self) -> None:
        """
        Waits for the plot to be ready and sets the triad position and label size.
        """

        self._wait_for_instance()

        # AXES label size
        self._label_size()

        # AXES pos
        self._move_triad()

    def label_sync(self) -> None:
        """
        Moves the label position once the plot is synced.
        """

        if not self._primed:
            js = """
                var world = K3DInstance.getWorld();
                var scale = K3DInstance.parameters.screenshotScale || 1;

                return world.renderOffScreen(
                    Math.floor(world.width * scale),
                    Math.floor(world.height * scale),
                ).then(function () { return 'primed'; });
            """

            self._remote.browser.execute_script(js)  #type:ignore
            self._primed = True

    def _wait_for_instance(self) -> None:
        """
        Blocks until k3d's ``K3DInstance`` exists in the page.

        Raises:
            TimeoutError: If ``K3DInstance`` never appears.
        """

        deadline = time.monotonic() + self._timeout
        while not self._check_k3d():
            if time.monotonic() > deadline:
                raise TimeoutError(
                    "k3d's K3DInstance was not created in the page within %g s." % self._timeout
                )
            time.sleep(0.1)

    def _move_triad(self) -> None:
        """
        Moves the triad position.
        """

        js = """
        (function (FX, FY) {
            var world = K3DInstance.getWorld();
            if (world.__rainbowAxesPos) return 'already installed';
            world.__rainbowAxesPos = true;

            // (1) relocate the axes-helper layer that renderOffScreen returns.
            var original = world.renderOffScreen.bind(world);
            world.renderOffScreen = function (width, height) {
                return original(width, height).then(function (layers) {
                    var helper = layers[2];
                    if (!(helper instanceof Uint8ClampedArray) || helper.length !== width * height * 4) {
                        return layers;
                    }

                    // Bounding box of the drawn (non-transparent) pixels.
                    var r0 = Infinity, r1 = -1, c0 = Infinity, c1 = -1;
                    for (var y = 0; y < height; y++) {
                        for (var x = 0; x < width; x++) {
                            if (helper[(y * width + x) * 4 + 3] > 8) {
                                if (y < r0) r0 = y;
                                if (y > r1) r1 = y;
                                if (x < c0) c0 = x;
                                if (x > c1) c1 = x;
                            }
                        }
                    }
                    if (r1 < 0) return layers;

                    // Move the triad's bottom-left corner to the requested fraction of the output.
                    var dx = Math.round(FX * width - c0);
                    var dy = Math.round((1 - FY) * height - (height - 1 - r0));

                    // The label divs are positioned in the plot's CSS-pixel space, so record the same
                    // shift there. Deriving it from this render's scale (not from screenshotScale) keeps
                    // the two consistent when the capture scale differs from the install-time one.
                    var to_css = world.width ? world.width / width : 1;
                    world.__rainbowAxesDelta = [dx * to_css, dy * to_css];
                    if (dx === 0 && dy === 0) return layers;

                    var drow = -dy;  // image rows run opposite to layer rows
                    var moved = new Uint8ClampedArray(width * height * 4);
                    for (var sy = r0; sy <= r1; sy++) {
                        var ty = sy + drow;
                        if (ty < 0 || ty >= height) continue;
                        for (var sx = c0; sx <= c1; sx++) {
                            var src = (sy * width + sx) * 4;
                            if (helper[src + 3] <= 8) continue;
                            var tx = sx + dx;
                            if (tx < 0 || tx >= width) continue;
                            var dst = (ty * width + tx) * 4;
                            moved[dst] = helper[src];
                            moved[dst + 1] = helper[src + 1];
                            moved[dst + 2] = helper[src + 2];
                            moved[dst + 3] = helper[src + 3];
                        }
                    }
                    layers[2] = moved;
                    return layers;
                });
            };

            // (2) shift the x/y/z HTML labels by the same amount. k3d lays the labels out during
            // BEFORE_RENDER (before the triad layer is produced) and rewrites their transform there,
            // having registered its own listener first, so appending here lands after k3d's update.
            K3DInstance.on(K3DInstance.events.BEFORE_RENDER, function () {
                var delta = world.__rainbowAxesDelta;
                if (!delta) return;
                ['x', 'y', 'z'].forEach(function (axis) {
                    var label = world.axesHelper[axis];
                    if (!label || !label.domElements) return;
                    label.domElements.forEach(function (element) {
                        element.style.transform +=
                            ' translate(' + delta[0] + 'px, ' + delta[1] + 'px)';
                    });
                });
            });

            return 'installed';
        })(arguments[0], arguments[1]);
        """

        # RUN
        self._remote.browser.execute_script(js, *self._pos)  #type:ignore

    def _label_size(self) -> None:
        """
        Sets the triad label size.
        """

        js = f"""
            const s = document.createElement('style');
            s.textContent = 'div[style*="position: absolute"]{{font-size: {self._label}em !important;}}';
            document.head.appendChild(s);
        """

        # RUN
        self._remote.browser.execute_script(js)  #type:ignore

    def _check_k3d(self) -> bool:
        """
        Checks if the k3d instance is setup.

        Returns:
            bool
                Whether the instance is setup or not.
        """

        js = """
            return typeof K3DInstance !== 'undefined' && K3DInstance !== null && typeof K3DInstance.getWorld === 'function';
        """

        # RUN
        res = self._remote.browser.execute_script(js)  #type:ignore
        return res

