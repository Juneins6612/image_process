import numpy as np
import cv2

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QImage

from PySide6.QtWidgets import (
    QWidget, QLabel, QFrame,
    QLayout, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton
)


class Horizontal_Line(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)


class Vertical_Line(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)


class Titled_Block(QWidget):
    def __init__(
        self,
        title: str,
        process_btn: list[QPushButton],
        parent: QWidget | None = ...
    ) -> None:
        super().__init__(parent)

        self.title = title

        self.setLayout(
            self._User_interface_init(title, process_btn)
        )

    def _Title_init(
            self, title: str, process_btn: list[QPushButton]) -> QHBoxLayout:
        _title = QHBoxLayout()
        _title.setContentsMargins(5, 0, 0, 0)

        _title.addWidget(
            QLabel(title), 1, Qt.AlignmentFlag.AlignLeft)
        _title.addWidget(Horizontal_Line(), 999)

        for _btn in process_btn:
            _title.addWidget(_btn, 1, Qt.AlignmentFlag.AlignRight)
            _btn.clicked.connect(getattr(self, _btn.text().replace(" ", "_")))

            # self.__dict__.

        return _title

    def _Contents_init(self) -> QLayout:
        raise NotImplementedError

    def _User_interface_init(
            self, title: str, process_btn: list[QPushButton]) -> QLayout:
        _title = self._Title_init(title, process_btn)
        _contents = self._Contents_init()
        _contents.setContentsMargins(15, 0, 10, 0)

        _layout = QVBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addLayout(_title, 1)
        _layout.addLayout(_contents, 999)

        return _layout


class Image_Widget(QLabel):
    # signal
    is_init_fail: Signal = Signal(int)

    def __init__(
        self,
        img: np.ndarray | str | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.img = np.empty(0)
        self.Set_img(img)

    @staticmethod
    def _Read_file(img_file: str) -> np.ndarray:
        return cv2.imread(img_file, cv2.IMREAD_UNCHANGED)

    @staticmethod
    def _Img_converter(img: np.ndarray, flag: str = "BGR2RGB") -> np.ndarray:
        if flag == "BGR2RGB":
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if flag == "RGB2BGR":
            return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        if flag == "BGRA2RGBA":
            return cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        if flag == "RGBA2BGRA":
            return cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA)
        raise ValueError(F"flag '{flag}' is not suit able")

    def _Img_to_pixmap(self):
        _img = self.img
        _h, _w = _img.shape[:2]
        if len(_img.shape) == 2:  # gray
            _v = _w * 1
            if _img.dtype == np.uint8:
                _format = QImage.Format.Format_Grayscale8
            else:
                _format = QImage.Format.Format_Grayscale16
        elif len(_img.shape) == 3:  # color
            _v = _w * 3
            _img = self._Img_converter(_img)
            _format = QImage.Format.Format_RGB888
        else:  # color with a channel
            _v = _w * 4
            _img = self._Img_converter(_img, "BGRA2RGBA")
            _format = QImage.Format.Format_RGBA8888

        return QPixmap(QImage(_img.data, _w, _h, _v, _format))

    def Set_img(
        self,
        img: np.ndarray | str | None = None
    ) -> bool:
        if img:
            _is_file = isinstance(img, str)
            _img: np.ndarray = self._Read_file(img) if _is_file else img

            # set image
            if len(_img.shape) in [2, 3, 4]:  # gray, color, with alpha
                self.img = _img
                self.setPixmap(self._Img_to_pixmap())
                return True

            self.is_init_fail.emit(1)  # image data has problem
        self.is_init_fail.emit(2)  # set empty init

        return False


class Num_edit(QLineEdit):
    def __init__(
        self,
        default_value: int | float = -1,
        parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self.value: int | float = default_value
        self.setPlaceholderText(str(default_value))
        self.textEdited.connect(self.Value_checker)

    def Value_checker(self, text: str):
        try:
            self.value = type(self.value)(text)
            self.setText(text)

        except ValueError:
            self.setText(str(self.value))
