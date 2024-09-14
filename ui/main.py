from typing import Any

from numpy import ndarray

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QMainWindow,
    QWidget, QToolBar, QLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QHeaderView,
    QTabWidget
    # QListWidgetItem
    # QMessageBox, QFileDialog, QDialog
)

from utils import image_process
from ui.process import (
    Process_UI,
    Resize_Block, Flip_Block, Remove_Background_Block, Rotate_Block
)
from ui.ui_utils.widget import (
    Horizontal_Line, Vertical_Line, Titled_Block,
    Custom_Basewidget, Image_Display_with_Dir_n_Table)


class Image_Process_Edit(Titled_Block):
    # signal
    Apply_process: Signal = Signal(list)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Image Process", (), parent)

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
        _process_list: list[Process_UI | list[Process_UI]] = [
            Resize_Block(),
            [Flip_Block(), Rotate_Block()],
            Remove_Background_Block()
        ]
        for _w in _process_list:
            if isinstance(_w, list):
                _widget = QWidget()
                _title: str = ""

                _temp_layout = QVBoxLayout()
                for _com in _w:
                    _temp_layout.addWidget(_com, 1)
                    _com.Add_process.connect(self.Add)
                    _title = f"{_title}, {_com.title}"

                _widget.setLayout(_temp_layout)
                _process_tab.addTab(_widget, _title[2:])
            else:
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


class Image_File_Display(Custom_Basewidget):
    def __init__(self, parent: QWidget | None = None, **kwarg) -> None:
        self.input_list: list[tuple[str, ndarray, tuple[int, int], bool]]
        self.output_list: list[tuple[str, ndarray, tuple[int, int], bool]]

        self.input_ui: Image_Display_with_Dir_n_Table
        self.output_ui: Image_Display_with_Dir_n_Table
        super().__init__(parent, **kwarg)

    def _User_interface_init(self) -> QLayout:
        _main_layout = QHBoxLayout()
        _input_ui = Image_Display_with_Dir_n_Table(
            "input", ".\\data\\input", 500, self)
        _input_ui.is_refreshed.connect(self._Get_input_data)
        _input_ui.Refresh()

        _input_table = _input_ui.file_table_widget
        _input_table.currentCellChanged.connect(
            self._Select_the_input_img)
        _input_table.cellDoubleClicked.connect(
            self._Call_process_page)
        _main_layout.addWidget(_input_ui, 99)

        _main_layout.addWidget(Vertical_Line(), 1)

        _output_ui = Image_Display_with_Dir_n_Table(
            "output", ".\\data\\output", 500, self)
        _output_ui.is_refreshed.connect(self._Get_output_data)
        _output_ui.Refresh()
        _output_table = _output_ui.file_table_widget
        _output_table.currentCellChanged.connect(
            self._Select_the_output_img)
        _output_table.cellDoubleClicked.connect(
            self._Call_process_page)
        _main_layout.addWidget(_output_ui, 99)

        self.input_ui = _input_ui
        self.output_ui = _output_ui

        return _main_layout

    def _Get_input_data(
        self,
        data: list[tuple[str, ndarray, tuple[int, int], bool]]
    ):
        self.input_list = data

    def _Get_output_data(
        self,
        data: list[tuple[str, ndarray, tuple[int, int], bool]]
    ):
        self.output_list = data

    def _Select_the_input_img(
            self, row: int):
        _input_widget = self.input_ui.img_widget
        _input_list = self.input_list

        if row >= 0:
            _input_widget.Set_img(_input_list[row][1])

            _output_table = self.output_ui.file_table_widget
            if _output_table.rowCount() >= (row + 1):
                _output_table.setCurrentCell(row, 0)
        else:
            _input_widget.clear()

    def _Select_the_output_img(
            self, row: int):
        _output_widget = self.output_ui.img_widget
        _output_list = self.output_list
        if row >= 0:
            _output_widget.Set_img(_output_list[row][1])
        else:
            _output_widget.clear()

    def _Call_process_page(self):
        ...


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

        self.img_display: Image_File_Display

    def _Set_tool_bar(
        self, default_opt: dict[str, dict[str, Any]] | None = None
    ) -> QToolBar | None:
        return default_opt

    def _Set_main_widget(self) -> QWidget:
        _main_widget = QWidget(self)
        _main_layout = QVBoxLayout(_main_widget)

        _img_process_edit = Image_Process_Edit(_main_widget)
        _img_process_edit.Apply_process.connect(self.Image_process)
        _main_layout.addWidget(_img_process_edit, 15)

        _main_layout.addWidget(Horizontal_Line(), 1)

        _file_dis_display = Image_File_Display(self)
        _main_layout.addWidget(_file_dis_display, 150)
        _main_widget.setLayout(_main_layout)

        self.img_display = _file_dis_display

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
