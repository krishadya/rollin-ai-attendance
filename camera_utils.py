import os

import cv2


def get_camera_indexes() -> list[int]:
    """
    Return camera indexes to try.

    Set ROLLIN_CAMERA_INDEX to force a specific camera, for example:
    ROLLIN_CAMERA_INDEX=1
    """
    preferred_index = os.getenv("ROLLIN_CAMERA_INDEX")

    if preferred_index is not None:
        try:
            return [int(preferred_index)]
        except ValueError:
            pass

    return [1, 0, 2, 3]


def open_camera():
    """
    Try available camera indexes and return an opened OpenCV camera.

    Returns:
        tuple[cv2.VideoCapture | None, int | None]
    """
    for camera_index in get_camera_indexes():
        camera = cv2.VideoCapture(camera_index)

        if camera.isOpened():
            return camera, camera_index

        camera.release()

    return None, None