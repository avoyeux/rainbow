"""
To store parent class(es) to process the fit and the corresponding envelopes to then be used in the
final plots.
"""
from __future__ import annotations

# IMPORTs standard
from dataclasses import dataclass, field

# IMPORTs third-party
import numpy as np



@dataclass(slots=True, repr=False, eq=False)
class BaseFitProcessing:
    """
    Base to create and easily access the uniform coordinates for the fit and the envelope.
    """

    # DATA unprocessed
    polar_r: np.ndarray
    polar_theta: np.ndarray

    # PARAMETERs
    nb_of_points: int

    # PLACEHOLDERs
    cumulative_distance: np.ndarray = field(init=False)
    polar_r_normalized: np.ndarray = field(init=False)
    polar_theta_normalized: np.ndarray = field(init=False)

    def normalize_coords(self) -> None:
        """
        Normalize the coordinates so that they are between 0 and 1. As such, the cumulative
        distance won't only depend on one axis.
        """

        # COORDs
        coords = np.stack([self.polar_r, self.polar_theta], axis=0)

        # NORMALIZE
        min_vals = np.min(coords, axis=1, keepdims=True)
        max_vals = np.max(coords, axis=1, keepdims=True)
        coords = (coords - min_vals) / (max_vals - min_vals)

        # COORDs update
        self.polar_r_normalized, self.polar_theta_normalized = coords
    
    def cumulative_distance_normalized(self) -> None:
        """
        To calculate the cumulative distance of the data and normalize it.
        """
        
        # COORDs
        coords = np.stack([self.polar_theta_normalized, self.polar_r_normalized], axis=0)

        # DISTANCE cumulative
        t = np.empty(coords.shape[1], dtype='float64')
        t[0] = 0
        for i in range(1, coords.shape[1]):
            t[i] = t[i - 1] + np.linalg.norm(coords[:, i] - coords[:, i - 1])
        t /= t[-1]  # normalize

        # DISTANCE update
        self.cumulative_distance = t
