"""
File to save the types used globally inside this project.
"""
from __future__ import annotations

# TYPE ANNOTATIONs
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # IMPORTs standard
    import queue
    import multiprocessing.shared_memory

    # TYPEs
    type QueueType[T] = queue.Queue[T]
    type SharedMemoryType = multiprocessing.shared_memory.SharedMemory
