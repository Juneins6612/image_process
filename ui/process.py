from numpy import ndarray, empty

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QLayout, QVBoxLayout,
    QLabel, QComboBox, QCheckBox, QPushButton
    # QListWidgetItem
    # QMessageBox, QFileDialog, QDialog
)

from .ui_utils.widget import (
    Num_edit, Titled_Block, Labeling
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
        # shape
        _h_size_edit = Num_edit(0, min_limit=0, parent=self)
        _w_size_edit = Num_edit(0, min_limit=0, parent=self)
        _pose_layer = Labeling(
            "resize shape",
            [
                Labeling("w:", [_w_size_edit, QLabel("px")], space_rate=0),
                Labeling("h: ", [_h_size_edit, QLabel("px")], space_rate=0)
            ]
        )
        # resize - interpolation  !!! not yet !!!
        _inter_combo = QComboBox(self)
        _inter_combo.setEnabled(False)
        _inter_layout = Labeling("interpolation\n(Not Yet)", [_inter_combo, ])

        _layout = QVBoxLayout()
        _layout.addLayout(_pose_layer)
        _layout.addLayout(_inter_layout)

        self.h_size_edit = _h_size_edit
        self.w_size_edit = _w_size_edit
        self.interpolation_combo = _inter_combo

        return _layout

    def Add(self):
        self.Add_process.emit(
            {
                "process": "Resize",
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
        # flip - vertical flip
        _v_flip_check = QCheckBox("vertical", self)
        # flip - horizontal flip
        _h_flip_check = QCheckBox("horizontal", self)
        _flip_layout = Labeling(
            "axis option",
            [_v_flip_check, _h_flip_check])

        _layout = QVBoxLayout()
        _layout.addLayout(_flip_layout)
        self.v_flip_check = _v_flip_check
        self.h_flip_check = _h_flip_check

        return _layout

    def Add(self):
        self.Add_process.emit(
            {
                "process": "Flip",
                "arg": {
                    "vertical": self.v_flip_check.isChecked(),
                    "horizontal": self.h_flip_check.isChecked()
                }
            }
        )


class Rotate_Block(Process_UI):
    def __init__(self, parent: QWidget | None = None) -> None:
        self.rotate_edit: Num_edit
        self.pose_x_edit: Num_edit
        self.pose_y_edit: Num_edit

        super().__init__("Rotate", parent)

    def _Contents_init(self):
        _rotate_edit = Num_edit(0.0, min_limit=0, max_limit=360, parent=self)
        _rotate_layer = Labeling("rotate angle", [_rotate_edit, QLabel("deg")])
        _pose_x_edit = Num_edit(0.0, max_limit=1.0, min_limit=0, parent=self)
        _pose_y_edit = Num_edit(0.0, max_limit=1.0, min_limit=0, parent=self)
        _pose_layer = Labeling(
            "center position rate",
            [
                Labeling("x: ", [_pose_x_edit,], space_rate=0),
                Labeling("y: ", [_pose_y_edit,], space_rate=0)
            ]
        )

        _layout = QVBoxLayout()
        _layout.addLayout(_rotate_layer)
        _layout.addLayout(_pose_layer)

        self.rotate_edit = _rotate_edit
        self.pose_x_edit = _pose_x_edit
        self.pose_y_edit = _pose_y_edit
        return _layout

    def Add(self):
        self.Add_process.emit(
            {
                "process": "Rotate",
                "arg": {
                    "rotate": self.rotate_edit.value,
                    "center_rate": (
                        self.pose_x_edit.value,
                        self.pose_y_edit.value
                    )
                }
            }
        )


class Mask_Block(Process_UI):
    def __init__(
        self,
        parent: QWidget | None = None
    ) -> None:
        self.img_mask: ndarray = empty(0)

        self.masking_edit_btn: QComboBox
        self.positive_check: QCheckBox

        super().__init__("Masking", parent)

    def _Contents_init(self) -> QLayout:
        _masking_edit_btn = QPushButton("edit", self)
        _positive_check = QCheckBox("positive", self)
        _masking_layer = Labeling(
            "masking option", [_masking_edit_btn, _positive_check])

        _layout = QVBoxLayout()
        _layout.addLayout(_masking_layer)

        self.masking_edit_btn = _masking_edit_btn
        self.positive_check = _positive_check

        return _layout

    def Add(self):
        self.Add_process.emit(
            {
                "process": "Masking",
                "arg": {
                    "mask": self.img_mask,
                    "is_positive": self.positive_check.isChecked()
                }
            }
        )


class Background_Block(Process_UI):
    def __init__(self, parent: QWidget | None = None) -> None:
        self.mode_combobox: QComboBox
        self.positive_check: QCheckBox
        super().__init__("Background", parent)

    def _Contents_init(self) -> QLayout:
        _auto_masking = QComboBox(self)
        _auto_masking.addItems(["rembg"])
        _positive_check = QCheckBox("positive", self)
        _rotate_layer = Labeling(
            "masking option", [_auto_masking, _positive_check])

        _layout = QVBoxLayout()
        _layout.addLayout(_rotate_layer)

        self.mode_combobox = _auto_masking
        self.positive_check = _positive_check

        return _layout

    def Add(self):
        self.Add_process.emit(
            {
                "process": "Background_Masking",
                "arg": {
                    "mode": self.mode_combobox.currentText(),
                    "is_positive": self.positive_check.isChecked()
                }
            }
        )


class Crop(Process_UI):
    def __init__(self, parent: QWidget | None = None) -> None:
        self.auto_check: QCheckBox
        self.crop_x_edit: Num_edit
        self.crop_y_edit: Num_edit
        self.crop_h_edit: Num_edit
        self.crop_w_edit: Num_edit
        super().__init__("Crop", parent)

    def _Contents_init(self) -> QLayout:
        _auto_check = QCheckBox("Use auto crop", self)
        _auto_check.setChecked(False)
        _auto_check.stateChanged.connect(self.Set_mode)

        _corp_x_edit = Num_edit(0.0, max_limit=1.0, min_limit=0, parent=self)
        _corp_y_edit = Num_edit(0.0, max_limit=1.0, min_limit=0, parent=self)
        _crop_lt_layer = Labeling(
            "crop left top rate",
            [
                Labeling("x: ", [_corp_x_edit,], space_rate=0),
                Labeling("y: ", [_corp_y_edit,], space_rate=0)
            ]
        )

        _corp_h_edit = Num_edit(0.0, max_limit=1.0, min_limit=0, parent=self)
        _corp_w_edit = Num_edit(0.0, max_limit=1.0, min_limit=0, parent=self)
        _crop_size_layer = Labeling(
            "crop size",
            [
                Labeling("h: ", [_corp_h_edit,], space_rate=0),
                Labeling("w: ", [_corp_w_edit,], space_rate=0)
            ]
        )

        _layout = QVBoxLayout()
        _layout.addWidget(_auto_check, Qt.AlignmentFlag.AlignLeft)
        _layout.addLayout(_crop_lt_layer)
        _layout.addLayout(_crop_size_layer)

        self.auto_check = _auto_check
        self.crop_x_edit = _corp_x_edit
        self.crop_y_edit = _corp_y_edit
        self.crop_h_edit = _corp_h_edit
        self.crop_w_edit = _corp_w_edit

        return _layout

    def Set_mode(self, state: int):
        _is_checked = state != 2

        self.crop_x_edit.setEnabled(_is_checked)
        self.crop_y_edit.setEnabled(_is_checked)
        self.crop_h_edit.setEnabled(_is_checked)
        self.crop_w_edit.setEnabled(_is_checked)

    def Add(self):
        self.Add_process.emit(
            {
                "process": "Crop",
                "arg": {
                    "is_auto": self.auto_check.isChecked(),
                    "lt_position_rate": (
                        self.crop_x_edit.value, self.crop_y_edit.value),
                    "crop_size_rate": (
                        self.crop_w_edit.value, self.crop_h_edit.value)
                }
            }
        )
