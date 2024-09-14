import numpy as np

import cv2
from rembg import remove

from utils.system import Path


def Resize(
    img: np.ndarray,
    height: int | float, width: int | float, interpolation: int
):
    _h, _w = img.shape[:2]
    if height > 0 or width > 0:
        if height <= 0:
            _to_w = width if isinstance(width, int) else round(width * _w)
            _to_h = round(_to_w / _w * _h)

        else:
            _to_h = height if isinstance(height, int) else round(height * _h)
            _to_w = round(_to_h / _h * _w)

        return cv2.resize(img, (_to_w, _to_h))
    return img


def Flip(img: np.ndarray, vertical: bool, horizontal: bool):
    _img = cv2.flip(img, 1) if vertical else img
    return cv2.flip(img, 0) if horizontal else _img


def Read(img_file: str):
    return cv2.imread(img_file, cv2.IMREAD_UNCHANGED)


def Write(img: np.ndarray, file_path: str, file_name: str):
    cv2.imwrite(Path.Join(file_name, file_path), img)


def Remove_background(img: np.ndarray):
    return remove(img)


class Masking():
    def __init__(self, is_positive: bool = False) -> None:
        self.mask = np.empty(0)
        self.is_positive = is_positive

    def Set_mask(self, new_mask: np.ndarray, is_force: bool = True):
        _this_mask = self.mask

        _is_force = is_force or not _this_mask.shape

        if _is_force or all(new_mask.shape == _this_mask.shape):
            self.mask = new_mask

    def __call__(self, img: np.ndarray):
        pass
