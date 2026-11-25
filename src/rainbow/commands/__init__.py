"""
Repository contains commands to be used with uv.
If uv is not installed, you can use these files as the direct executables to run the code.
"""

#todo move the if __main__ blocks to these files.

from .create import Create
from .vis import K3dAnimation
from .project import SDOProject
from .contour import Contour
from .video import PngToVideo
from .volume import Volume
from .fake import Fake
from .vis_fig import Plot as VisPlot
