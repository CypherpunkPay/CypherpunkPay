import os
from pathlib import Path


def dir_of(file_path: str) -> Path:
    absolute_file_path = os.path.realpath(file_path)
    absolute_dir_path = os.path.dirname(absolute_file_path)
    return Path(absolute_dir_path)
