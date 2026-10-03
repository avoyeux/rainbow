"""
Code to create a video from a given set of images.
"""
from __future__ import annotations

import glob
import os

import cv2

from ..config import config



class Video:
    # todo add docstring

    def __init__(
            self,
            image_dir: str,
            video_fullpath: str,
            fps: float = 5.0,
        ) -> None:
        # todo add docstring

        self._dir = image_dir
        self._video_fullpath = video_fullpath
        self._fps = fps

    def create(self) -> None:
        """
        Create the video by reading the sorted images from the
        directory and writing them to the video file.
        """
        image_paths = sorted(glob.glob(os.path.join(self._dir, '*.png')))
        if not image_paths:
            raise FileNotFoundError(
                f'No images found in directory: {self._dir}'
            )

        os.makedirs(os.path.dirname(self._video_fullpath), exist_ok=True)

        first = cv2.imread(image_paths[0])
        height, width = first.shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(
            self._video_fullpath, fourcc, self._fps, (width, height)
        )

        for path in image_paths:
            image = cv2.imread(path)
            if image is None:
                continue
            writer.write(image)

        writer.release()


if __name__ == '__main__':
    video = Video(
        image_dir=config.dir.output.results.contours,
        video_fullpath='/home/avoyeux/Codes/work/rainbow/test.mp4',
    )
    video.create()
