"""
To compute the difference between the new and old STEREO B images.
Differences seem to come from updates in the SolarSoft STEREO pipeline.
"""
from __future__ import annotations

# IMPORTs standard
import os
from glob import glob

# IMPORTs third-party
import numpy as np
import matplotlib.pyplot as plt

# IMPORTs local
from ..config import config

# TYPE ANNOTATIONs
from typing import Literal

# API public
__all__ = ['StereoDiff']



class StereoDiff:
    """
    To plot the value differences between the old STEREO B images and the new ones
    (using '/pointing_off'). 
    """

    def __init__(self, choice: Literal['avg', 'int']) -> None:
        """
        Plots the value differences between the old STEREO B images and the new ones
        (using '/pointing_off'). 

        Arguments:
            choice -- Literal['avg', 'int'].
                Choosing to plot the differences for the average or the intensity images.
        """

        if choice == 'int':
            self._path_old = config.dir.input.stereo.int
        else:
            self._path_old = config.dir.input.stereo.avg
        self._path_new = os.path.join(config.dir.temporary, f'idl_304_{choice}')
        self._save_path = os.path.join(config.dir.temporary, f'diff_{choice}')
        os.makedirs(self._save_path, exist_ok=True)

        # RUN
        self._run()

    def _run(self) -> None:
        """
        Runs the differences plotting for all images found in the corresponding folders.
        """

        filepaths_old = sorted(glob(os.path.join(self._path_old, '*.png')))
        filepaths_new = sorted(glob(os.path.join(self._path_new, '*.png')))

        # CHECK
        assert len(filepaths_old) == len(filepaths_new)

        # PRINT
        print(f"Computing diff for {len(filepaths_old)} images...")

        for i, (old, new) in enumerate(zip(filepaths_old, filepaths_new)):
            # LOAD
            img_old = plt.imread(old).mean(axis=-1).astype(np.float64)
            img_new = plt.imread(new).mean(axis=-1).astype(np.float64)

            # DIFF
            diff = img_new - img_old

            # SAVE
            plt.figure(figsize=(5, 5))
            plt.imshow(diff, interpolation='none', cmap='gray')
            plt.colorbar()
            plt.axis('off')
            plt.savefig(os.path.join(self._save_path, os.path.basename(new)), dpi=512)
            plt.close()

            # PRINT
            print(f"{i:03d} - DIFF {os.path.basename(new)}")



if __name__ == '__main__': StereoDiff(choice='avg')
