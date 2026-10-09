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
from .commands import DataSaver, K3dAnimation, SDOProject, Contour, PngToVideo

# TYPE ANNOTATIONs
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING: from argparse import Namespace

# API public
__all__ = ['create', 'vis', 'project', 'contour', 'video']



def default_args(
        parser: argparse.ArgumentParser,
        yaml_path: str,
    ) -> dict[str, Any]:
    """
    Parses the parameters that are common to all the commands.

    Arguments:
        parser -- argparse.ArgumentParser object.
        yaml_path -- str. Path to the yaml file with the parameters for the command.

    Returns:
        dict[str, Any]. A dictionary of the parameters.
    """

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
    args = parser.parse_args()

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
    ? should I add more arguments ?
    """

    print('\033[90mCreating the HDF5 data file...\033[0m', flush=True)
    parser = argparse.ArgumentParser(description='Create the HDF5 data file.')

    # KWARGs
    params = default_args(parser, config.file.create)

    # RUN
    DataSaver(**params)

@Decorators.running_time
def project() -> None:
    # todo add docstring

    print('\033[90mProjecting SDO data...\033[0m', flush=True)
    parser = argparse.ArgumentParser(description='Project SDO data.')

    # KWARGs
    params = default_args(parser, config.file.project)

    # RUN
    SDOProject(**params)

@Decorators.running_time
def vis() -> None:
    # todo add docstring

    print('\033[90mStarting 3D visualization...\033[0m', flush=True)
    parser = argparse.ArgumentParser(description='3D visualization.')

    # KWARGs
    params = default_args(parser, config.file.vis)

    # RUN
    K3dAnimation(**params)

@Decorators.running_time
def contour() -> None:
    """
    Creates the 3*3 contour plot.
    """

    print('\033[90mCreating the 3*3 contours plot...\033[0m', flush=True)
    parser = argparse.ArgumentParser(description='Create the 3*3 contours plot.')

    # KWARGs
    params = default_args(parser, config.file.contour)

    # RUN
    Contour(**params)

@Decorators.running_time
def video() -> None:
    """
    Creates an MP4 video from a given directory full of PNG images.
    """

    print('\033[90mCreating the video...\033[0m', flush=True)
    parser = argparse.ArgumentParser(description='Create the video.')

    # KWARGs
    params = default_args(parser, config.file.video)

    # EXCEPTION
    for no_key in ['verbose', 'flush']: params.pop(no_key, None)

    # RUN
    PngToVideo(**params)
