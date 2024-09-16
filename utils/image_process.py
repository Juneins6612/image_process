from typing import Any
import numpy as np

import cv2
from rembg import remove

from utils.system import Path


class Process():
    @staticmethod
    def Read(img_file: str):
        return cv2.imread(img_file, cv2.IMREAD_UNCHANGED)

    @staticmethod
    def Write(img: np.ndarray, file_path: str, file_name: str):
        cv2.imwrite(Path.Join(file_name, file_path), img)

    class Basement():
        def __init__(self) -> None:
            self.input: np.ndarray = np.empty(0)

        def __call__(self, img: np.ndarray) -> np.ndarray:
            self.input = img

    # @staticmethod
    # def Remove_background(img: np.ndarray):
    #     return remove(img)

    class Resize(Basement):
        def __init__(
            self,
            height: int | float = 0,
            width: int | float = 0,
            interpolation: int | None = None
        ) -> None:
            super().__init__()
            self.height = height
            self.width = width
            self.interpolation = interpolation

        def __call__(self, img: np.ndarray) -> np.ndarray:
            super().__call__(img)

            _h, _w = self.height, self.width

            _img_h, _img_w = img.shape[:2]
            if _h > 0 or _w > 0:
                if _h <= 0:
                    _to_w = _w if isinstance(_w, int) else round(_w * _img_w)
                    _to_h = round(_to_w / _img_w * _img_h)

                else:
                    _to_h = _h if isinstance(_h, int) else round(_h * _img_h)
                    _to_w = round(_to_h / _img_h * _img_w)

                return cv2.resize(img, (_to_w, _to_h))
            return img

    class Flip(Basement):
        def __init__(
            self, vertical: bool = True, horizontal: bool = True
        ) -> None:
            super().__init__()
            self.vertical = vertical
            self.horizontal = horizontal

        def __call__(self, img: np.ndarray) -> np.ndarray:
            super().__call__(img)
            _img = cv2.flip(img, 1) if self.vertical else img
            return cv2.flip(img, 0) if self.horizontal else _img

    class Rotate(Basement):
        def __init__(
            self, rotate: float, center_rate: tuple[float, float]
        ) -> None:
            super().__init__()
            self.rotate = rotate
            self.center_rate = center_rate

        def __call__(self, img: np.ndarray) -> np.ndarray:
            super().__call__(img)
            _h, _w = img.shape[:2]

            _center_rate = self.center_rate
            _center = round(_w * _center_rate[0]), round(_h * _center_rate[1])

            _m = cv2.getRotationMatrix2D(_center, self.rotate, 1)

            return cv2.warpAffine(img, _m, (_w, _h))

    class Masking(Basement):
        def __init__(
            self, mask: np.ndarray, is_positive: bool = False
        ) -> None:
            super().__init__()
            self.mask = mask.astype(np.bool)
            self.is_positive = is_positive

        def Set_mask(self, new_mask: np.ndarray, is_force: bool = True):
            _this_mask = self.mask

            _is_force = is_force or not _this_mask.shape

            if _is_force or all(new_mask.shape == _this_mask.shape):
                self.mask = new_mask

        def __call__(self, img: np.ndarray) -> np.ndarray:
            super().__call__(img)
            _mask = self.mask

            if _mask.shape[:2] == img.shape[:2]:
                if len(img.shape) == 2:
                    _img = img * _mask
                else:
                    _, _, _c = img.shape
                    _img_list = []
                    for _ct in range(_c):
                        _img_list.append(img[:, :, _ct] * _mask)

                    if img.shape[-1] != 4:
                        _img_list.append(_mask)

                    _img = np.stack(_img_list, axis=2)
                return _img
            return img

    class Background_Masking(Basement):
        def __init__(self, mode: str, is_positive: bool = False) -> None:
            super().__init__()
            self.mode = mode
            self.is_positive = is_positive

        def __call__(self, img: np.ndarray) -> np.ndarray:
            super().__call__(img)

            if self.mode == "rembg":
                return remove(img)
            return img

    class Crop(Basement):
        def __init__(
            self,
            is_auto: str,
            lt_position_rate: tuple[float, float],
            crop_size_rate: tuple[float, float]
        ) -> None:
            super().__init__()
            self.is_auto = is_auto
            self.lt_point = lt_position_rate
            self.crop_shape = crop_size_rate

        def __call__(self, img: np.ndarray) -> np.ndarray:
            super().__call__(img)
            _h, _w = img.shape[:2]
            if self.is_auto:
                _gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                _m: float = _gray.mean().item()
                _std: float = _gray.std().item()

                _high = min(round((_m + _std)), 255)
                _low = max(round(_m - _std), 0)

                _y, _x = np.where(cv2.Canny(_gray, _high, _low) != 0)

                _x_mean = _x.mean()
                _x_term = _x.std()
                _l = max(round(_x_mean - 2 * _x_term), 0)
                _r = min(round(_x_mean + 2 * _x_term), _w)

                _y_mean = _y.mean()
                _y_term = _y.std()
                _t = max(round(_y_mean - 2 * _y_term), 0)
                _b = min(round(_y_mean + 2 * _y_term), _h)

                return img[_t: _b, _l: _r]

            else:
                _lt_w_rate, _lt_h_rate = self.lt_point
                _lt_w = round(_lt_w_rate * _w)
                _lt_h = round(_lt_h_rate * _h)
                _c_w_rate, _c_h_rate = self.crop_shape
                _rb_w = min(_lt_w + _w * _c_w_rate, _w - 1)
                _rb_h = min(_lt_h + _h * _c_h_rate, _h - 1)

                return img[_lt_h: _rb_h, _lt_w: _rb_w]


class Apply_Block():
    def __init__(
        self,
        save_dir: str,
        file_name: str,
        input_img: np.ndarray
    ) -> None:
        self.save_dir: str = save_dir
        self.file_name = file_name

        self.input_img = input_img
        self.output_img: np.ndarray = np.empty(0)

        self.process_list: list[Process.Basement] = []
        self.change_log: list[bool]

    def Set_process(self, process_list: list[dict[str, Any]]):
        _process_list: list[Process.Basement] = []

        for _process in process_list:
            _process_name = _process["process"]
            _process_kwarg = _process["arg"]

            _process_list.append(
                Process.__dict__[_process_name](**_process_kwarg)
            )

        self.process_list = _process_list
        self.change_log = [
            True for _p in process_list
        ]

    def Write(self):
        Process.Write(self.output_img, self.save_dir, self.file_name)

    def __call__(self):
        _this_img = self.input_img
        _this_process = self.process_list

        for _process in _this_process:
            _this_img = _process(_this_img)

        self.output_img = _this_img
        self.Write()
