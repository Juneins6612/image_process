from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QMainWindow, QFileDialog,
    QWidget, QToolBar, QLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QHeaderView,
    QTabWidget
    # QListWidgetItem
    # QMessageBox, QFileDialog, QDialog
)

from utils.system import Path
from utils import image_process
from ui.process import (
    Process_User_Interface,
    Resize_Block, Flip_Block, Remove_Background_Block,  # Rotate_Block
)
from ui.ui_utils.widget import (
    Horizontal_Line, Vertical_Line, Titled_Block, Image_Widget)


class Image_in_Directory_Viewer(Titled_Block):
    def __init__(
        self, data_type: str, default_dir: str, parent: QWidget | None = None
    ) -> None:
        if Path.Exist_check(default_dir, Path.Type.DIR):
            self.file_dir: str = default_dir
        else:
            self.file_dir: str = Path.WORK_SPACE
        self.file_list: list[str] = []

        super().__init__(
            data_type,
            [
                QPushButton("Set directory"),
                QPushButton("Refresh")
            ],
            parent
        )

        self.img_widget: Image_Widget
        self.file_table_widget: QTableWidget

    def _Title_init(
            self, title: str, process_btn: list[QPushButton]) -> QHBoxLayout:
        _title = QHBoxLayout()
        _title.setContentsMargins(5, 0, 0, 0)

        _title.addWidget(
            QLabel(f"{title} directory"), 1, Qt.AlignmentFlag.AlignLeft)
        _dir_edit = QLineEdit()
        _dir_edit.setPlaceholderText(self.file_dir)
        _title.addWidget(_dir_edit, 999)

        for _btn in process_btn:
            _title.addWidget(_btn, 1, Qt.AlignmentFlag.AlignRight)
            _btn.clicked.connect(getattr(self, _btn.text().replace(" ", "_")))

            # self.__dict__.

        return _title

    def _Contents_init(self) -> QLayout:
        _layout = QVBoxLayout()
        _layout.setContentsMargins(0, 0, 0, 0)

        _file_info_list = [
            "file", "is_read", "size"
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
        _file_table_widget.currentCellChanged.connect(self.Selected)
        _layout.addWidget(_file_table_widget, 1)

        _img_widget = Image_Widget()
        _layout.addWidget(_img_widget, 5)

        self.img_widget = _img_widget
        self.file_table_widget = _file_table_widget

        self.Refresh()

        return _layout

    def Set_directory(self):
        _new_dir = QFileDialog.getExistingDirectory(
            self, f"select the {self.title} directry", self.file_dir)

        self.file_dir = _new_dir
        self.Refresh()

    def Refresh(self):
        _default_dir = self.file_dir
        _new_files = Path.Search(
            _default_dir, Path.Type.FILE, ext_filter=["jpg", "png"])

        _table = self.file_table_widget
        _table.clearContents()
        _table.setRowCount(len(_new_files))

        for _ct, _file in enumerate(_new_files):
            _file_name = Path.Get_file_directory(_file)[-1]

            _table.setCellWidget(_ct, 0, QLabel(_file_name))
            _table.setCellWidget(_ct, 1, QLabel("False"))
            _table.setCellWidget(_ct, 2, QLabel())

        if _new_files:
            _table.setCurrentCell(0, 0)
        self.file_list = _new_files

    def Selected(self, row: int, colum: int, pre_row: int, pre_colum: int):
        _table = self.file_table_widget
        _img_widget = self.img_widget

        if _table.currentColumn() >= 0:
            _img_widget.Set_img(Path.Join(
                _table.cellWidget(row, 0).text(),
                self.file_dir
            ))
        else:
            _img_widget.clear()


class Image_Process_Edit(Titled_Block):
    # signal
    Apply_process: Signal = Signal(list)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Image Process", [], parent)

        self.process_table: QTableWidget
        self.process_list = []

    def Apply(self):
        self.Apply_process.emit(self.process_list)

    def Add(self, argument: dict):
        _process_name: str = argument["process"]
        _process_name = _process_name.capitalize()
        _process_name = _process_name.replace(" ", "_")

        _arg: dict[str, Any] = argument["arg"]

        self.process_list.append({
            "process": _process_name,
            "arg": _arg
        })

        _table = self.process_table
        _this_ct = _table.rowCount()
        _table.setRowCount(_this_ct + 1)

        _table.setCellWidget(_this_ct, 0, QLabel(_process_name))
        _table.setCellWidget(
            _this_ct,
            1,
            QLabel(
                "".join(f"{_k}: {_v}" for _k, _v in _arg.items())))

    def _Contents_init(self):
        _layout = QHBoxLayout()

        # process tab
        _process_tab = QTabWidget(self)
        _process_list: list[Process_User_Interface] = [
            Resize_Block(),
            Flip_Block(),
            # Rotate_Block(),
            Remove_Background_Block()
        ]
        for _w in _process_list:
            _w.Add_process.connect(self.Add)
            _process_tab.addTab(_w, _w.title)
        _layout.addWidget(_process_tab, 2)

        # process table
        _table_layout = QGridLayout()
        _process_table = QTableWidget(self)
        _process_table.verticalHeader().setVisible(False)

        _process_info_list = [
            "process name", "argument"
        ]
        _len_info = len(_process_info_list)
        _process_table.setColumnCount(_len_info)
        _ = [
            _process_table.horizontalHeader().setSectionResizeMode(
                _ct, QHeaderView.ResizeMode.Stretch if (
                    _ct
                ) else QHeaderView.ResizeMode.ResizeToContents
            ) for _ct in range(_len_info)
        ]
        _process_table.setHorizontalHeaderLabels(_process_info_list)
        _apply_btn = QPushButton("Apply")
        _apply_btn.clicked.connect(self.Apply)
        _remove_btn = QPushButton("remove")
        _clear_btn = QPushButton("clear")

        _table_layout.addWidget(_process_table, 0, 0, 4, 3)
        _table_layout.addWidget(_apply_btn, 4, 0)
        _table_layout.addWidget(_remove_btn, 4, 1)
        _table_layout.addWidget(_clear_btn, 4, 2)
        _layout.addLayout(_table_layout, 3)

        self.process_table = _process_table

        return _layout


class Main_Page(QMainWindow):
    def __init__(
        self,
        title: str,
        position: list[int],
        default_opt: dict[str, dict[str, Any]] | None = None
    ) -> None:
        super().__init__()

        self.setWindowTitle(title)
        _main_widget = self._Set_main_widget()
        self.setCentralWidget(_main_widget)

        _toolbar = self._Set_tool_bar(default_opt)
        if _toolbar is QToolBar:
            self.addToolBar(_toolbar)
        self.setGeometry(*position)

        self.input_ui: Image_in_Directory_Viewer
        self.output_ui: Image_in_Directory_Viewer

    def _Set_tool_bar(
        self, default_opt: dict[str, dict[str, Any]] | None = None
    ) -> QToolBar | None:
        return default_opt

    def _Set_main_widget(self) -> QWidget:
        _main_widget = QWidget(self)
        _main_layout = QGridLayout(_main_widget)

        _img_process_edit = Image_Process_Edit(_main_widget)
        _img_process_edit.Apply_process.connect(self.Image_process)
        _main_layout.addWidget(_img_process_edit, 0, 0, 1, 3)

        _main_layout.addWidget(Horizontal_Line(), 1, 0, 1, 3)

        _input_ui = Image_in_Directory_Viewer(
            "input", "./data/input", _main_widget)
        _main_layout.addWidget(_input_ui, 2, 0, 999, 1)
        _main_layout.addWidget(Vertical_Line(), 2, 1, 999, 1)
        _output_ui = Image_in_Directory_Viewer(
            "output", "./data/output", _main_widget)
        _main_layout.addWidget(_output_ui, 2, 2, 999, 1)

        _main_widget.setLayout(_main_layout)

        self.input_ui = _input_ui
        self.output_ui = _output_ui

        return _main_widget

    def Image_process(self, process_arg_list: list[dict]):
        _img_table = self.input_ui.file_table_widget
        _img_viewer = self.input_ui.img_widget
        _save_dir = self.output_ui.file_dir
        _img_ct = _img_table.rowCount()

        for _ct in range(_img_ct):
            _img_table.setCurrentCell(_ct, 0)
            _img = _img_viewer.img.copy()
            _file_name: str = _img_table.cellWidget(_ct, 0).text()

            for _process in process_arg_list:
                _process_name = _process["process"]
                _process_kwagr = _process["arg"]

                _img = image_process.__dict__[_process_name](
                    _img,
                    **_process_kwagr
                )

            image_process.Write(_img, _save_dir, _file_name)

        self.output_ui.Refresh()
