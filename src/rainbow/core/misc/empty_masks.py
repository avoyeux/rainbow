"""
To add empty STEREO masks for cube indices where there is no mask available.
"""
from __future__ import annotations

# IMPORTs standard
import os
import re
from glob import glob

# IMPORTs third-party
from PIL import Image

# IMPORTs personal
from common import Decorators

# IMPORTs local
from rainbow.config import config

# API public
__all__ = ['Mask']



class Mask:
    """
    To add empty STEREO masks for cube indices where there is no mask available.
    """

    @Decorators.running_time
    def __init__(self) -> None:
        """
        To add empty STEREO masks for cube indices where there is no mask available.
        """

        self._dir = config.dir.input.stereo.wave304.mask_karine

        # RUN
        self._run()

    def _run(self) -> None:
        """
        Creates the empty masks where a mask is missing
        """

        files = sorted(glob(os.path.join(self._dir, '*.png')))
        shape = Image.open(files[0]).size

        for i in range(412):
            # CHECK
            filename = f'frame{i:04d}.png'
            filepath = os.path.join(self._dir, filename)
            if os.path.isfile(filepath): continue

            # CREATE
            mask = Image.new('RGB', shape, (255, 255, 255))
            mask.save(filepath)


if __name__ == '__main__': Mask()
