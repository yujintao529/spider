# -*- coding: UTF-8 -*-

import os

__base_dir__ = "/Users/yujintao/Downloads"


def note_file(parent_path, file_name):
    """
    :param parent_path: 文件父目录
    :param file_name: 文件名称
    :return: string， 返回
    """
    path = __base_dir__ + os.path.sep + parent_path
    if not os.path.exists(path):
        os.mkdir(path)
    if os.path.isfile(path):
        path = __base_dir__ + os.path.sep + parent_path + "_path"
        os.mkdir(path)

    return path + os.path.sep + file_name


def note_to_disk(file, contents):
    """

    :param file:
    :param contents:
    :return:
    """
    parent_path = os.path.dirname(file)

    if not os.path.exists(parent_path):
        os.mkdir(parent_path)

    fp = open(file, "w")

    for note in contents:
        fp.write(note)
        fp.write('\n')
    fp.close()
