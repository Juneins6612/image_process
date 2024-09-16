from typing import Any

from numpy import ndarray

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QVBoxLayout,
    QMainWindow,
    QWidget, QToolBar, QLayout, QGridLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QTabWidget
    # QListWidgetItem
    # QMessageBox, QFileDialog, QDialog
)

from utils.image_process import Apply_Block
from ui.process import (
    Process_UI,
    Resize_Block, Crop, Flip_Block, Mask_Block,
    Background_Block, Rotate_Block
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

    def _Contents_init(self):
        _layout = QHBoxLayout()

        # process tab
        _process_tab = QTabWidget(self)
        _process_list: list[Process_UI | list[Process_UI]] = [
            Resize_Block(self),
            Rotate_Block(self),
            Crop(self),
            Flip_Block(self),
            [Mask_Block(self), Background_Block(self)]
        ]
        for _w in _process_list:
            if isinstance(_w, list):
                _widget = QWidget()
                _title: str = _w[0].title

                _temp_layout = QVBoxLayout()
                for _com in _w:
                    _temp_layout.addWidget(_com, 1)
                    _com.Add_process.connect(self.Add)

                _widget.setLayout(_temp_layout)
                _process_tab.addTab(_widget, _title)
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
        _remove_btn.clicked.connect(self.Remove)
        _clear_btn = QPushButton("clear")
        _clear_btn.clicked.connect(self.Clear)

        _table_layout.addWidget(_process_table, 0, 0, 4, 3)
        _table_layout.addWidget(_apply_btn, 4, 0)
        _table_layout.addWidget(_remove_btn, 4, 1)
        _table_layout.addWidget(_clear_btn, 4, 2)
        _layout.addLayout(_table_layout, 3)

        self.process_table = _process_table

        return _layout

    def Add(self, argument: dict):
        self.process_list.append(argument)

        _table = self.process_table
        _this_ct = _table.rowCount()
        _table.setRowCount(_this_ct + 1)

        _table.setItem(_this_ct, 0, QTableWidgetItem(argument["process"]))
        _table.setItem(_this_ct, 1, QTableWidgetItem(
            " ".join(f"{_k}: {_v}" for _k, _v in argument["arg"].items())
        ))

    def Apply(self):
        self.Apply_process.emit(self.process_list)

    def Remove(self):
        _table = self.process_table
        _process_list = self.process_list
        _selected = _table.selectedRanges()

        _selected_list = []

        for _range in _selected:
            _t = _range.topRow()
            _b = _range.bottomRow()

            if _t == _b:
                _selected_list.append(_t)
            else:
                _selected_list += list(
                    range(_range.topRow(), _range.bottomRow() + 1))

        _selected_list = sorted(_selected_list, reverse=True)

        for _pick_ct in _selected_list:
            del _process_list[_pick_ct]

        self.Clear()

        for _data in _process_list:
            self.Add(_data)

    def Clear(self):
        self.process_list = []
        self.process_table.clearContents()
        self.process_table.setRowCount(0)


class Image_File_Display(Custom_Basewidget):
    def __init__(self, parent: QWidget | None = None, **kwarg) -> None:
        self.apply_blocks: list[Apply_Block] = []

        self.input_ui: Image_Display_with_Dir_n_Table
        self.output_ui: Image_Display_with_Dir_n_Table
        super().__init__(parent, **kwarg)

        self.input_ui.Refresh()
        self.output_ui.Refresh()

    def _User_interface_init(self) -> QLayout:
        _main_layout = QHBoxLayout()
        _input_ui = Image_Display_with_Dir_n_Table(
            "input", ".\\data\\input", 500, self)
        _input_ui.is_refreshed.connect(self._Get_input_data)
        _main_layout.addWidget(_input_ui, 99)

        _main_layout.addWidget(Vertical_Line(), 1)

        _output_ui = Image_Display_with_Dir_n_Table(
            "output", ".\\data\\output", 500, self)
        _output_ui.is_refreshed.connect(self._Get_output_data)
        _main_layout.addWidget(_output_ui, 99)

        self.input_ui = _input_ui
        self.output_ui = _output_ui

        _input_table = _input_ui.file_table_widget
        _input_ui.Refresh()
        _input_table.currentCellChanged.connect(self._Select_the_input_img)
        _input_table.cellDoubleClicked.connect(self._Call_process_page)
        _output_ui.Refresh()
        _output_table = _output_ui.file_table_widget
        _output_table.currentCellChanged.connect(self._Select_the_output_img)
        _output_table.cellDoubleClicked.connect(self._Call_process_page)

        return _main_layout

    def _Get_input_data(
        self,
        data: list[tuple[str, ndarray]]
    ):
        _save_dir = self.output_ui.file_dir

        self.apply_blocks = [
            Apply_Block(
                _save_dir, _file_name, _img) for _file_name, _img in data
        ]

    def _Get_output_data(
        self,
        data: list[tuple[str, ndarray]]
    ):
        _apply_list = self.apply_blocks
        _apply_ids = list(range(len(_apply_list)))
        _data_ids = list(range(len(data)))

        _rm_ct = 0

        for _data_ct, (_file_name, _img) in enumerate(data):
            for _apply_ct, _apply_id in enumerate(_apply_ids):
                _this_block = _apply_list[_apply_id]

                if _this_block.file_name == _file_name:
                    _this_block.output_img = _img

                    _apply_ids.pop(_apply_ct)
                    _data_ids.pop(_data_ct - _rm_ct)
                    _rm_ct += 1
                    break

        self.output_ui.Remove(_data_ids)

    def _Select_the_input_img(self, row: int):
        _input_widget = self.input_ui.img_widget
        _pick_img = self.apply_blocks[row].input_img

        if row >= 0 and len(_pick_img.shape) >= 2:
            _input_widget.Set_img(_pick_img)

            _output_table = self.output_ui.file_table_widget
            if _output_table.rowCount() >= (row + 1):
                _output_table.setCurrentCell(row, 0)
        else:
            _input_widget.clear()

    def _Select_the_output_img(self, row: int):
        _output_widget = self.output_ui.img_widget
        _pick_img = self.apply_blocks[row].output_img

        if row >= 0 and len(_pick_img.shape) >= 2:
            _output_widget.Set_img(_pick_img)
        else:
            _output_widget.clear()

    def Get_process_info(self, process_arg_list: list[dict]):
        for _block in self.apply_blocks:
            _block.Set_process(process_arg_list)
            _block()

        self.output_ui.Refresh()

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
        _main_layout.addWidget(_img_process_edit, 15)

        _main_layout.addWidget(Horizontal_Line(), 1)

        _file_dis_display = Image_File_Display(self)
        _main_layout.addWidget(_file_dis_display, 150)
        _main_widget.setLayout(_main_layout)

        _img_process_edit.Apply_process.connect(
            _file_dis_display.Get_process_info)

        self.img_display = _file_dis_display

        return _main_widget
