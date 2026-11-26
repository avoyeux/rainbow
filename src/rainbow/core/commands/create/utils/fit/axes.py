"""
To change the axes ordering.
Done like so because the fit needed a specific order to work as intended.
"""
from __future__ import annotations

# API public
__all__ = ['Axes']



class Axes:
    """
    To get the correct axes order depending on the data input shape.
    Done like this as the fit needed a specific order to work as intended.
    """

    __slots__ = ['order']

    def __init__(self, shape: tuple[int, int]) -> None:
        """
        Gives the correct axes ordering.
        Done like so as the fit needed a specific order to work as intended.
        ! Not sure if this is still true.

        Arguments:
            shape -- tuple[int, int]
                The shape of the input data (n, m) where n (t, x, y, z) or (x, y, z) and m the 
                number of points.

        Raises:
            ValueError: if the input shape is not the usual shape.
        """

        if shape[0] == 4:
            self.order = [0, 3, 2, 1]
        elif shape[0] == 3:
            self.order = [2, 1, 0]
        else:
            raise ValueError(f"\033[1;31mThe shape {shape} is not recognized.\033[0m")
