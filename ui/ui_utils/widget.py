import numpy as np
import cv2

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QImage

from PySide6.QtWidgets import (
    QWidget, QLabel, QFrame,
    QLayout, QHBoxLayout, QVBoxLayout,
    QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog
)

from utils.system import Path
from utils.image_process import Process


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


class Labeling(QHBoxLayout):
    def __init__(
        self,
        label: str | QLabel,
        objects: list[QWidget | QLayout],
        spacing_mode: str = "empty",
        space_rate: int = 99,
        parent: QWidget | None = None
    ):
        super().__init__(parent)
        if isinstance(label, str):
            self.addWidget(QLabel(label), 1, Qt.AlignmentFlag.AlignLeft)
        else:
            self.addWidget(label, 1, Qt.AlignmentFlag.AlignLeft)

        if space_rate:
            _spacing = QWidget() if (
                spacing_mode == "empty") else Horizontal_Line()
            self.addWidget(_spacing, space_rate)

        for _obj in objects:
            if isinstance(_obj, QHBoxLayout):
                self.addLayout(_obj, 1)
            else:
                self.addWidget(_obj, 1, Qt.AlignmentFlag.AlignRight)


class Custom_Basewidget(QWidget):
    def __init__(self, parent: QWidget | None = None, **kwarg) -> None:
        super().__init__(parent)
        self.setLayout(
            self._User_interface_init(**kwarg)
        )

    def _User_interface_init(self) -> QLayout:
        raise NotImplementedError


class Titled_Block(Custom_Basewidget):
    def __init__(
        self,
        title: str,
        process_btn: tuple[str, ...],
        parent: QWidget | None = None
    ) -> None:

        self.title_label: QLabel

        super().__init__(parent, title=title, process_btn=process_btn)

    def _Title_init(
        self, title: str, process_btn: tuple[str, ...]
    ) -> QHBoxLayout:

        _title_layout = QHBoxLayout()
        _title_label = QLabel(title, self)
        _btn_list = []

        for _btn_string in process_btn:
            _btn = QPushButton(_btn_string, self)
            _btn.clicked.connect(getattr(self, _btn_string.replace(" ", "_")))
            _btn_list.append(_btn)

        _title_layout = Labeling(
            _title_label,
            _btn_list,
            "line"
        )
        _title_layout.setContentsMargins(5, 0, 0, 0)

        self.title_label = _title_label
        return _title_layout

    def _Contents_init(self) -> QLayout:
        raise NotImplementedError

    def _User_interface_init(
        self, title: str = "title", process_btn: tuple[str, ...] = ()
    ) -> QLayout:
        _contents = self._Contents_init()
        _contents.setContentsMargins(15, 0, 10, 0)
        _title = self._Title_init(title, process_btn)

        _layout = QVBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addLayout(_title, 1)
        _layout.addLayout(_contents, 999)

        return _layout

    @property
    def title(self):
        return self.title_label.text()

    @title.setter
    def title(self, title: str):
        self.title_label.setText(title)


class Image_Viewer(QLabel):
    # signal
    is_init_fail: Signal = Signal(int)

    def __init__(
        self,
        img: np.ndarray | str | None = None,
        shape_limit: int = -1,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            "border-style: solid;"
            "border-width: 2px;"
            "border-color: #000000;"
        )

        self.shape_limit = shape_limit
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

    def _Img_to_pixmap(self, img: np.ndarray):
        _h, _w = img.shape[:2]

        _limit = self.shape_limit

        if (_limit > 0) and max(_h, _w) > self.shape_limit:
            _v = self.shape_limit
            if _h > _w:
                _h, _w = _v, round(_w * _v / _h)
            else:
                _h, _w = round(_h * _v / _w), _v

            img = cv2.resize(img, [_w, _h])

        if len(img.shape) == 2:  # gray
            _v = _w * 1
            if img.dtype == np.uint8:
                _format = QImage.Format.Format_Grayscale8
            else:
                _format = QImage.Format.Format_Grayscale16
        elif img.shape[-1] == 3:  # color
            _v = _w * 3
            img = self._Img_converter(img)
            _format = QImage.Format.Format_RGB888
        else:  # color with a channel
            _v = _w * 4
            img = self._Img_converter(img, "BGRA2RGBA")
            _format = QImage.Format.Format_RGBA8888

        return QPixmap(QImage(img.data, _w, _h, _v, _format))

    def Set_img(self, img: np.ndarray | str | None = None) -> bool:
        if img is not None:
            _is_file = isinstance(img, str)
            _img: np.ndarray = self._Read_file(img) if _is_file else img

            # set image
            if len(_img.shape) in [2, 3, 4]:  # gray, color, with alpha
                self.setPixmap(self._Img_to_pixmap(_img))
                return True

            self.is_init_fail.emit(1)  # image data has problem
        self.is_init_fail.emit(2)  # set empty init

        return False


class Image_Display_with_Dir_n_Table(Titled_Block):
    is_refreshed = Signal(list)  # (file_name, image)

    def __init__(
        self,
        data_type: str,
        default_dir: str,
        img_shape_limit: int,
        parent: QWidget | None = None
    ) -> None:
        if Path.Exist_check(default_dir, Path.Type.DIR):
            self.file_dir: str = default_dir
        else:
            self.file_dir: str = Path.WORK_SPACE

        super().__init__(data_type, ["Set directory", "Refresh"], parent)

        self.img_widget: Image_Viewer
        self.img_widget.shape_limit = img_shape_limit
        self.file_table_widget: QTableWidget

    def _Title_init(
            self, title: str, process_btn: tuple[str, ...]) -> QHBoxLayout:
        _title_layout = QHBoxLayout()
        _title_layout.setContentsMargins(5, 0, 0, 0)

        _title_label = QLabel(f"{title} directory")
        _title_layout.addWidget(
            _title_label, 1, Qt.AlignmentFlag.AlignLeft)
        _dir_edit = QLineEdit()
        _dir_edit.setPlaceholderText(self.file_dir)
        _title_layout.addWidget(_dir_edit, 999)

        for _btn_string in process_btn:
            _btn = QPushButton(_btn_string, self)
            _title_layout.addWidget(_btn, 1, Qt.AlignmentFlag.AlignRight)
            _btn.clicked.connect(getattr(self, _btn_string.replace(" ", "_")))

            # self.__dict__.

        self.title_label = _title_label
        return _title_layout

    def _Contents_init(self) -> QLayout:
        _layout = QVBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)

        _file_info_list = [
            "file", "size", "is_applied"
        ]
        _len_info = len(_file_info_list)
        _file_table_widget = QTableWidget(self)
        _file_table_widget.verticalHeader().setVisible(False)
        _file_table_widget.setColumnCount(_len_info)
        _ = [
            _file_table_widget.horizontalHeader().setSectionResizeMode(
                _ct, QHeaderView.ResizeMode.Stretch if (
                    not _ct
                ) else QHeaderView.ResizeMode.ResizeToContents
            ) for _ct in range(_len_info)
        ]
        _file_table_widget.setHorizontalHeaderLabels(_file_info_list)
        _file_table_widget.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        _layout.addWidget(_file_table_widget, 2)

        _img_widget = Image_Viewer()
        _layout.addWidget(_img_widget, 3)

        self.img_widget = _img_widget
        self.file_table_widget = _file_table_widget

        return _layout

    def Set_directory(self):
        _dir_type = self.title_label.text()
        _new_dir = QFileDialog.getExistingDirectory(
            self, f"select the {_dir_type}", self.file_dir)

        self.file_dir = _new_dir
        self.Refresh()

    def Refresh(self):  # read file in directory
        _default_dir = self.file_dir
        _new_files = Path.Search(
            _default_dir, Path.Type.FILE, ext_filter=["jpg", "png"])

        _table = self.file_table_widget
        _table.clearContents()
        _table.setRowCount(len(_new_files))

        _read_data = []

        for _ct, _file in enumerate(_new_files):
            _file_name = Path.Get_file_directory(_file)[-1]

            _img = Process.Read(_file)
            _shape = _img.shape[:2]

            _str_list = [_file_name, f"{_shape[0]}, {_shape[1]}", "False"]

            for _col_ct, _data in enumerate(_str_list):
                _table.setItem(_ct, _col_ct, QTableWidgetItem(_data))

            _read_data.append((
                _file_name,
                _img
            ))

        if _new_files:
            _table.setCurrentCell(0, 0)
            self.img_widget.Set_img(_read_data[0][1])

        self.is_refreshed.emit(_read_data)

    def Remove(self, row_num_list: list[int]):
        _table = self.file_table_widget
        for _id in sorted(row_num_list, reverse=True):
            for _col_ct in range(_table.columnCount()):
                _table.takeItem(_id, _col_ct)

        _table.setRowCount(_table.rowCount() - len(row_num_list))

        if not _table.rowCount():
            self.img_widget.clear()


class Num_edit(QLineEdit):
    def __init__(
        self,
        default_value: int | float = -1,
        max_limit: int | float | None = None,
        min_limit: int | float | None = None,
        parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self.default_value = default_value
        self.value: int | float = default_value

        self.max_limit = max_limit
        self.min_limit = min_limit

        self.setPlaceholderText(str(default_value))
        self.editingFinished.connect(self.Value_checker)

    def Value_checker(self):
        text = self.text()

        try:
            if text == "":
                self.value = self.default_value
            else:
                _insert_v = type(self.value)(text)

                _max_limit = self.max_limit
                _insert_v = _insert_v if (
                    _max_limit is None) else min(_insert_v, _max_limit)
                _min_limit = self.min_limit
                _insert_v = _insert_v if (
                    _min_limit is None) else max(_insert_v, _min_limit)

                self.value = _insert_v
            _text = str(self.value)
            self.setText(_text)

        except ValueError:
            self.setText(str(self.value))
