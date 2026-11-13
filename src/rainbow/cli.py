"""
CLI interface for running the different processing and visualization scripts.
(made like so to let the user use 'uv run command')
"""
from __future__ import annotations

# IMPORTs standard
import os
import argparse

# IMPORTs third-party
import yaml

# IMPORTs personal
from common import Decorators

# IMPORTs local
from .config import config
from .commands import Create, K3dAnimation, SDOProject, Contour, PngToVideo, Volume, Fake

# TYPE ANNOTATIONs
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING: from argparse import Namespace

# API public
__all__ = ['create', 'vis', 'project', 'contour', 'video', 'volume', 'fake']



def default_args(
        description: str,
        yaml_path: str,
    ) -> dict[str, Any]:
    """
    Parses the parameters that are common to all the commands.

    Arguments:
        description -- str.
            The description of the command.
        yaml_path -- str.
            Path to the yaml file with the parameters for the command.

    Returns:
        dict[str, Any]. A dictionary of the parameters.
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--yaml',
        type=str,
        default=yaml_path,
        help='Path to the yaml file with the parameters for the command.',
    )
    parser.add_argument(
        '--verbose',
        type=int,
        default=argparse.SUPPRESS,
        help='Verbosity level for the prints.',
    )
    parser.add_argument(
        '--flush',
        type=bool,
        default=argparse.SUPPRESS,
        help='Whether to flush the print outputs.',
    )
    # args = parser.parse_args()
    args, _ = parser.parse_known_args()

    # YAML initialization
    params: dict[str, Any] = {}
    if os.path.isfile(yaml_path):
        with open(args.yaml, 'r') as f: params = yaml.safe_load(f)
    else:
        print(f'No yaml file found at {yaml_path}, using function defaults for other arguments.')

    # OVERRIDE
    for key in vars(args): params[key] = getattr(args, key)
    params.pop('yaml', None)
    return params

@Decorators.running_time
def create() -> None:
    """
    Creates the HDF5 file containing the processed data.
    """

    print('\033[90mCreating the HDF5 data file...\033[0m', flush=True)
    params = default_args('Create the HDF5 data file.', config.file.create)

    # RUN
    Create(**params)

@Decorators.running_time
def fake() -> None:
    """
    Creates fake masks for the 'new_toto.pro' code.
    Done to then be able to visualize the no duplicates processing effects.
    """

    print('\033[90mCreating fake data...\033[0m', flush=True)
    params = default_args('Fake data.', config.file.fake)

    # RUN
    Fake(**params)

@Decorators.running_time
def project() -> None:
    # todo add docstring

    print('\033[90mProjecting SDO data...\033[0m', flush=True)
    params = default_args('Project SDO data.', config.file.project) 

    # RUN
    SDOProject(**params)

@Decorators.running_time
def vis() -> None:
    """
    Function to use in jupyter-notebook to visualize the data cube in 3D.
    """

    print('\033[90mStarting 3D visualization...\033[0m', flush=True)
    params = default_args('3D visualization.', config.file.vis)

    # RUN
    K3dAnimation(**params)

@Decorators.running_time
def contour() -> None:
    """
    Creates the 3*3 contour plot.
    """

    print('\033[90mCreating the 3*3 contours plot...\033[0m', flush=True)
    params = default_args('Create the 3*3 contours plot.', config.file.contour)

    # RUN
    Contour(**params)

@Decorators.running_time
def video() -> None:
    """
    Creates an MP4 video from a given directory full of PNG images.
    """

    print('\033[90mCreating the video...\033[0m', flush=True)
    params = default_args('Create the video.', config.file.video)

    # EXCEPTION
    for no_key in ['verbose', 'flush']: params.pop(no_key, None)

    # RUN
    PngToVideo(**params)

@Decorators.running_time
def volume() -> None:
    """
    Creates the volume plot containing the cubes voxels volume range and the mask surface area for
    STEREO and SDO.
    """

    print('\033[90mCreating the volume plot...\033[0m', flush=True)
    params = default_args('Create the volume plot.', config.file.volume)

    # RUN
    Volume(**params)
