"""
File to save the types used globally inside this project.
"""
from __future__ import annotations

# IMPORTs standard
import queue
import multiprocessing.shared_memory
import multiprocessing.sharedctypes
from typing import Any, Literal

# API public
__all__ = [
    'VoxelAlias',
    'JsLinkAlias',
    'CounterType',
    'QueueType',
    'SharedMemoryType',
    'ImageExtension',
]

# TYPEs
type ImageExtension = Literal['.png', '.pdf']
type VoxelAlias = Any
type JsLinkAlias = Any
type CounterType[T] = multiprocessing.sharedctypes.Synchronized[T]
type QueueType[T] = queue.Queue[T]
type SharedMemoryType = multiprocessing.shared_memory.SharedMemory
