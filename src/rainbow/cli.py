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
from .commands import DataSaver

# TYPE ANNOTATIONs
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING: from argparse import Namespace

# API public
__all__ = ['create']



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
        help='Verbosity level for the prints.',
    )
    parser.add_argument(
        '--flush',
        type=bool,
        help='Whether to flush the print outputs.',
    )
    args = parser.parse_args()

    # YAML initialization
    params: dict[str, Any] = {}
    if os.path.exists(yaml_path):
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

    print('\033[1;0mCreating the HDF5 data file...\033[0m')
    parser = argparse.ArgumentParser(description='Create the HDF5 data file.')

    # KWARGs
    params = default_args(parser, config.file.config.hdf5)

    # RUN
    DataSaver(**params)
