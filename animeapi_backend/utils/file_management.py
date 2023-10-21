"""
SPDX-License-Identifier: MIT

A module to manage files
"""

def check_file_exist(filename: str) -> bool:
    """
    Check if a file exist

    :param filename: The filename
    :type filename: str
    :return: True if exist, False if not
    :rtype: bool
    """
    try:
        with open(filename, "r"):
            pass
    except FileNotFoundError:
        return False
    return True

def check_file_diff(source: str, target: str, is_path: bool = True) -> bool:
    """
    Check if a file is different from another file

    :param source: The source file
    :type source: str
    :param target: The target file
    :type target: str
    :param is_path: Whether the source and target is a path, defaults to True
    :type is_path: bool, optional
    :return: True if different, False if not
    :rtype: bool
    """
    if is_path:
        with open(source, "r") as f:
            source_data = f.read()
        with open(target, "r") as f:
            target_data = f.read()
        return source_data != target_data
    else:
        return source != target
