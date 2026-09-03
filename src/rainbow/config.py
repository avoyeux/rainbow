"""
Sets up the whole repository directory structure and creates a corresponding object to easily
have access to the fullpath of each directory.
"""
from __future__ import annotations

# IMPORTs standard
import os

# IMPORTs personal
from common import root_path, ConfigToObject

# API public
__all__ = ['config']



# CONFIG
config_path = os.path.join(root_path, 'config', 'config.yml')
config = ConfigToObject(config_path).config
