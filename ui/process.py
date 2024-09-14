from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QLayout, QGridLayout,
    QLabel, QComboBox, QCheckBox,
    # QListWidgetItem
    # QMessageBox, QFileDialog, QDialog
)

from .ui_utils.widget import (
    Num_edit, Vertical_Line, Titled_Block
)


class Basement(QWidget):
    def __init__(
        self,
        name: str,
        parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self.name = name

        self.setLayout(
            self._User_interface_init()
        )

    def _User_interface_init(self) -> QLayout:
        raise NotImplementedError


class Process_UI(Titled_Block):
    # signal
    Add_process: Signal = Signal(dict)

    def __init__(
        self,
        title: str,
        parent: QWidget | None = None
    ) -> None:
        super().__init__(title, ("Add", ), parent)

    def Add(self):
        raise NotImplementedError


class Resize_Block(Process_UI):
    def __init__(self, parent: QWidget | None = None) -> None:
        self.h_size_edit: Num_edit
        self.w_size_edit: Num_edit
        self.interpolation_combo: QComboBox

        super().__init__("Resize", parent)

    def _Contents_init(self) -> QLayout:
        _layout = QGridLayout()
        # resize - h size
        _layout.addWidget(QLabel("height"), 0, 0, 1, 2)
        _h_size_edit = Num_edit(0, self)
        _layout.addWidget(
            _h_size_edit, 0, 2, Qt.AlignmentFlag.AlignRight)
        # resize - w size
        _layout.addWidget(QLabel("width"), 1, 0, 1, 2)
        _w_size_edit = Num_edit(0, self)
        _layout.addWidget(
            _w_size_edit, 1, 2, Qt.AlignmentFlag.AlignRight)
        # resize - interpolation  !!! not yet !!!
        _layout.addWidget(
            QLabel("interpolation\n(Not Yet)"), 2, 0, 1, 2)
        _interpolation_combo = QComboBox(self)
        _interpolation_combo.setEnabled(False)
        _layout.addWidget(
            _interpolation_combo, 2, 2, Qt.AlignmentFlag.AlignRight)

        self.h_size_edit = _h_size_edit
        self.w_size_edit = _w_size_edit
        self.interpolation_combo = _interpolation_combo

        return _layout

    def Add(self):
        self.Add_process.emit(
            {
                "process": "resize",
                "arg": {
                    "height": self.h_size_edit.value,
                    "width": self.w_size_edit.value,
                    "interpolation": self.interpolation_combo.currentIndex()
                }
            }
        )


class Flip_Block(Process_UI):
    def __init__(self, parent: QWidget | None = None) -> None:
        self.v_flip_check: QCheckBox
        self.h_flip_check: QCheckBox

        super().__init__("Flip", parent)

    def _Contents_init(self):
        _layout = QGridLayout()
        # flip - vertical flip
        _v_flip_check = QCheckBox("vertical", self)
        _layout.addWidget(_v_flip_check, 0, 0)
        # flip - horizontal flip
        _h_flip_check = QCheckBox("horizontal", self)
        _layout.addWidget(_h_flip_check, 0, 1)

        self.v_flip_check = _v_flip_check
        self.h_flip_check = _h_flip_check

        return _layout

    def Add(self):
        self.Add_process.emit(
            {
                "process": "flip",
                "arg": {
                    "vertical": self.v_flip_check.isChecked(),
                    "horizontal": self.h_flip_check.isChecked()
                }
            }
        )


class Rotate_Block(Process_UI):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Rotate", parent)

    def _Contents_init(self):
        _layout = QGridLayout()

        return _layout

    def Add(self):
        ...


class Mask_Block(Process_UI):
    def __init__(
        self,
        title: str,
        parent: QWidget | None = None
    ) -> None:
        super().__init__(title, parent)

    def Add(self):
        self.Add_process.emit(
            {
                "process": "masking",
                "arg": {

                }
            }
        )


class Remove_Background_Block(Process_UI):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Remove Background", parent)

    def _Contents_init(self):
        _layout = QGridLayout()

        return _layout

    def Add(self):
        self.Add_process.emit(
            {
                "process": "remove background",
                "arg": {}
            }
        )


class Base_Process(Basement):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Base Process", parent)

    def _User_interface_init(self) -> QLayout:
        _main_layout = QGridLayout()
        _main_layout.setContentsMargins(0, 5, 0, 5)

        # resize
        _resize_block = Resize_Block()

        # flip
        _flip_block = Flip_Block()

        # rotate
        _rm_b_block = Remove_Background_Block()

        _main_layout.addWidget(_resize_block, 0, 0)
        _main_layout.addWidget(_flip_block, 1, 0)
        _main_layout.addWidget(Vertical_Line(), 0, 1, 2, 1)
        _main_layout.addWidget(_rm_b_block, 0, 2, 2, 1)

        return _main_layout
