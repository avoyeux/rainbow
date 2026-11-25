"""
To add the different create 'vis' png frames in a single matplotlib figure.
"""
from __future__ import annotations

# IMPORTs standard
import os
from glob import glob
import multiprocessing as mp

# IMPORTs third-party
import matplotlib.pyplot as plt

# IMPORTs local
from rainbow.config import config

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # IMPORTs local
    from rainbow.typing import CounterType

# API public
__all__ = ['Plot']



class Plot:
    """
    To add the different created 'vis' png frames in a single matplotlib figure.
    """

    def __init__(
            self,
            name: str,
            folders: list[str],
            px: int = 1280,
            processes: int = 1,
            verbose: int = 0,
            flush: bool = False,
        ) -> None:
        """
        Adds the different created 'vis' png frames together in a single matplotlib figure.

        Arguments:
            name -- str
                Folder name to save the figures in.
            folders -- list[str]
                List of folder names containing the input png frames.
            px -- int (default: 1280)
                Number of width pixels of the input images. Used for the figure dpi.
            processes -- int (default: 1)
                Number of processes to use for the multiprocessing.
            verbose -- int (default: 0)
                Verbosity level for the prints.
            flush -- bool (default: False)
                Whether to flush the prints.
        """

        # CONFIG
        self._processes = processes
        self._verbose = verbose
        self._flush = flush

        # ARGs
        self._dpi = px
        self._save = os.path.join(config.dir.output.k3d.fig, name)
        self._files: tuple[tuple[str, ...], ...] = tuple(zip(*[
            sorted(glob(os.path.join(config.dir.output.k3d.frame, folder, '*.png')))
            for folder in folders
        ]))
        os.makedirs(self._save, exist_ok=True)

        # PRINT
        if self._verbose > 0: print(f"Found {len(self._files)} files.", flush=self._flush)

        # RUN
        self._run()

    def _run(self) -> None:
        """
        Run the plotting process.
        """

        # MULTIPROCESSING
        if self._processes > 1:
            # SETUP
            nb_processes = min(len(self._files), self._processes)
            counter: CounterType[int] = mp.Value('i', len(self._files) - 1)
            processes: list[mp.Process] = [None] * nb_processes  #type:ignore

            # RUN
            for i in range(nb_processes):
                p = mp.Process(
                    target=self._single_process,
                    args=(counter,),
                )
                p.start()
                processes[i] = p
            for p in processes: p.join()
        # NO MULTIPROCESSING
        else:
            for i in range(len(self._files)): self._plot(i)

    def _single_process(self, counter: CounterType[int]) -> None:
        """
        Single process to plot the figures.

        Arguments:
            counter -- CounterType[int]
                Tracks which set of png frames to process.
        """

        while True:
            # NEXT
            with counter.get_lock():
                index = counter.value
                if index < 0: return
                counter.value -= 1

            # RUN
            self._plot(index)

    def _plot(self, index: int) -> None:
        """
        Plot the figure for the given index.

        Arguments:
            index -- int
                Index of the figure to plot.
        """

        # PATHS
        files = self._files[index]

        # FIG setup
        fig = plt.figure(figsize=(len(files), 1))
        grid = fig.add_gridspec(
            nrows=1,
            ncols=len(files),
            wspace=0.,
            hspace=0.,
            left=0.,
            right=1.,
            bottom=0.,
            top=1.,
        )

        # ADD images
        for i, path in enumerate(files):  self._add_image(fig, grid, (0, i), path)

        # SAVE
        filepath = os.path.join(self._save, f'fig{index:04d}.png')
        plt.savefig(
            fname=filepath,
            pad_inches=0.,
            dpi=self._dpi,
        )
        fig.clear()
        plt.close()

        # PRINT
        if self._verbose > 1: print(f"{index:04d} -- SAVED PLOT.", flush=self._flush)

    def _add_image(
        self,
        fig: plt.Figure,
        grid: plt.GridSpec,
        pos: tuple[int, int],
        path: str,
    ) -> None:
        """
        Add the image at the given path to the figure at the given position.

        Arguments:
            fig -- plt.Figure
                Figure to add the image to.
            grid -- plt.GridSpec
                Gridspec to use for the position.
            pos -- tuple[int, int]
                Position to add the image at.
            path -- str
                Path to the image file.
        """

        # FETCH
        image = plt.imread(path)

        # ADD
        ax = fig.add_subplot(grid[pos])
        ax.set_facecolor('none')
        ax.imshow(image, interpolation='none')
        ax.axis('off')
