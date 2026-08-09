"""
Directory containing code to setup the whole repository structure.
"""
from __future__ import annotations

# IMPORTs standard
import os

# IMPORTs personal
from common import root_path, ConfigToObject

# API public
__all__ = ['config']



# PATH to config
config_path = os.path.join(root_path, 'config', 'config.yml')

# CONFIG
config = ConfigToObject(config_path).config
