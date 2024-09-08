""" ### Frequently used features for handling system-related tasks

------------------------------------------------------------------------
### Requirement
    None

### Structure
    OperatingSystem: ...
    Path: ...
    File: ...

"""
from __future__ import annotations
from enum import Enum, auto

import sys
from glob import glob
from os import path, getcwd, makedirs
import platform

import yaml


# -- DEFINE CONSTANT -- #
# Data type for hint
TYPE_NUMBER = int | float

# System Constant
PYTHON_VERSION = sys.version_info


class String_Enum(str, Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __repr__(self):
        return self.name.lower()

    def __str__(self):
        return self.name.lower()


class OperatingSystem():
    """### Frequently used features for handling OS-related tasks
    --------------------------------------------------------------------
    ### Requirement
        None

    ### Structure
        ...

    """

    THIS_STYLE = platform.system().lower()

    class Name(String_Enum):
        """
        각 OS 별 처리 문자열
        ----------------------------------------------------------------
        """
        WINDOW = auto()
        LINUX = auto()

    @staticmethod
    def Is_it_running(like_this_os: OperatingSystem.Name):
        """
        #### 제시된 OS와 프로그램이 돌아가는 OS를 비교하는 함수
        ----------------------------------------------------------------
        """
        return OperatingSystem.THIS_STYLE == like_this_os


class Path():
    """ ### 파일 및 디렉토리 경로 관련 기능 모음

    ---------------------------------------------------------------------------
    """
    WORK_SPACE = getcwd()

    class Type(String_Enum):
        """ ### 작업 대상 구분 상수
        -----------------------------------------------------------------------
        ### Attributes
        - `DIR`: 디렉토리 -> (value = "dir")
        - `FILE`: 파일 -> (value = "file")
        """
        DIR = auto()
        FILE = auto()

    @staticmethod
    def Separate_check(obj_path: str):
        """
        #### 경로 문자열에 존재하는 구분자 확인
        ----------------------------------------------------------------
        """
        _is_linux = OperatingSystem.Is_it_running(OperatingSystem.Name.LINUX)
        _old_sep = "\\" if _is_linux else "/"
        return obj_path.replace(_old_sep, path.sep)

    @staticmethod
    def Join(obj_path: str | list[str], root_path: str | None = None):
        """
        #### 경로 문자열 연결
        ----------------------------------------------------------------
        """
        _path_comp = [] if root_path is None else [root_path]
        _path_comp += obj_path if isinstance(obj_path, list) else [obj_path]
        return path.join(*_path_comp)

    @staticmethod
    def Divide(obj_path: str, level: int = -1):
        """
        #### 주어진 경로 문자열 분할
        ----------------------------------------------------------------
        """
        _path_comp = obj_path.split(path.sep)
        return Path.Join(_path_comp[:level]), Path.Join(_path_comp[level:])

    @staticmethod
    def Exist_check(obj_path: str, target: Path.Type | None = None):
        """
        #### 해당 경로의 존재 여부 확인
        ----------------------------------------------------------------
        #### Parameter

        """
        if target is Path.Type.DIR:
            return path.isdir(obj_path)
        if target is Path.Type.FILE:
            return path.isfile(obj_path)
        return path.isdir(obj_path) or path.isfile(obj_path)

    @staticmethod
    def Make_directory(
        obj_dir: str | list[str],
        root_dir: str | None = None,
        is_force: bool = False
    ):
        """ ### Function feature description
        Note

        ------------------------------------------------------------------
        ### Args
        - `arg_name`: Description of the input argument

        ### Returns or Yields
        - `data_format`: Description of the output argument

        ### Raises
        - `error_type`: Method of handling according to error issues

        """
        if root_dir is not None:  # root directory check
            _exist = Path.Exist_check(root_dir, Path.Type.DIR)
            if _exist:
                pass
            elif is_force:
                _front, _back = Path.Divide(root_dir)
                Path.Make_directory(_back, _front)
            else:
                raise ValueError(
                    "\n".join((
                        f"!!! Root directory {root_dir} is NOT EXIST !!!",
                        f"{obj_dir} can't make in {root_dir}")
                    )
                )

        else:  # use relative root directory (= cwd)
            root_dir = Path.WORK_SPACE

        _obj_dir = Path.Join(obj_dir, root_dir)
        makedirs(_obj_dir, exist_ok=True)
        return _obj_dir

    @staticmethod
    def Get_file_directory(file_path: str):
        """ ### Function feature description
        Note

        ------------------------------------------------------------------
        ### Args
        - `arg_name`: Description of the input argument

        ### Returns or Yields
        - `data_format`: Description of the output argument

        ### Raises
        - `error_type`: Method of handling according to error issues

        """
        _file_path = file_path
        _exist = Path.Exist_check(file_path, Path.Type.FILE)

        return _exist, *Path.Divide(_file_path)

    @staticmethod
    def Search(
        obj_path: str,
        target: Path.Type | None = None,
        keyword: str | None = None,
        ext_filter: str | list[str] | None = None
    ) -> list[str]:
        """ ### Function feature description
        Note

        ------------------------------------------------------------------
        ### Args
        - `arg_name`: Description of the input argument

        ### Returns or Yields
        - `data_format`: Description of the output argument

        ### Raises
        - `error_type`: Method of handling according to error issues

        """
        assert Path.Exist_check(obj_path, Path.Type.DIR)

        # make keyword
        _obj_keyword = "*" if keyword is None else keyword

        # make ext list
        if isinstance(ext_filter, list):
            _ext_list = [
                _ext[1:] if _ext[0] == "." else _ext for _ext in ext_filter
            ]
        elif isinstance(ext_filter, str):
            _ext_list = [
                ext_filter[1:] if ext_filter[0] == "." else ext_filter
            ]
        else:
            _ext_list = [""]

        _searched_list = []

        for _ext in _ext_list:
            _list = sorted(glob(
                Path.Join(
                    _obj_keyword if _ext == "" else f"{_obj_keyword}.{_ext}",
                    obj_path
                ))
            )
            _searched_list += [
                _file for _file in _list if Path.Exist_check(_file, target)
            ]
        return _searched_list


class File():
    class Support_Format(String_Enum):
        YAML = auto()

    @staticmethod
    def Extension_checker(file_name: str, file_format: File.Support_Format):
        _format = str(file_format)
        if "." in file_name:
            _ext = file_name.split(".")[-1]
            if _ext != _format:
                _file_name = file_name.replace(_ext, _format)
            else:
                _file_name = file_name
        else:
            _file_name = f"{file_name}.{_format}"

        return _file_name

    class YAML():
        @staticmethod
        def Read(
            file_name: str,
            file_dir: str,
            encoding_type: str = "UTF-8"
        ) -> dict:
            # make file path
            _file = Path.Join(
                File.Extension_checker(file_name, File.Support_Format.YAML),
                file_dir)
            _is_exist = Path.Exist_check(_file, Path.Type.FILE)

            # read the file
            if _is_exist:
                with open(_file, "r", encoding=encoding_type) as _file:
                    _load_data = yaml.load(_file, Loader=yaml.FullLoader)
                return _load_data
            print(f"file {file_name} is not exist in {file_dir}")
            return {}

        @staticmethod
        def Write(
            file_name: str,
            file_dir: str,
            data,
            encoding_type: str = "UTF-8"
        ):
            raise NotImplementedError
