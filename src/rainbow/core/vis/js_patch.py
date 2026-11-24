"""
Javascript code patches.
These are used to be able to move the triad position and set the triad label size.
Fully written with AI as its Javascript and its getting embeded in the k3d plot...
"""
from __future__ import annotations


class JSPatch:
    """
    Javascript code patches.
    """

    @staticmethod
    def axes_pos() -> str:
        """
        Returns the Javascript code patch to move the triad position.

        Returns:
            str.
                The code patch.
        """

        js = ("""
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
        """)
        return js

    @staticmethod
    def label_size() -> str:
        """
        Returns the Javascript code patch to set the triad label size.

        Returns:
            str.
                The code patch.
        """

        js = ("""
            const s = document.createElement('style');
            s.textContent = 'div[style*="position: absolute"]{font-size: 1.4em !important;}';
            document.head.appendChild(s);
        """)
        return js

    @staticmethod
    def label_sync() -> str:
        """
        Returns the Javascript code patch to sync the triad label position.

        Returns:
            str.
                The code patch.
        """

        js = ("""
            var world = K3DInstance.getWorld();
            var scale = K3DInstance.parameters.screenshotScale || 1;

            return world.renderOffScreen(
                Math.floor(world.width * scale),
                Math.floor(world.height * scale),
            ).then(function () { return 'primed'; });
        """)
        return js

    @staticmethod
    def check_k3d() -> str:
        """
        Returns the Javascript code patch to check if the k3d instance is setup.

        Returns:
            str.
                The code patch.
        """

        js = ("""
            return typeof K3DInstance !== 'undefined' && K3DInstance !== null && typeof K3DInstance.getWorld === 'function';
        """)
        return js

