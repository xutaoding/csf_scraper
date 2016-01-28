#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import os.path
#from eggs.utils.xlsx import XlsxWriter


def write(file_abs_path, sequ, replace='\n'):
    """ when storing url failed that re search web source in daily_news file again,
        needing to clear relative TXT file at daily_news file
        note: argument file_path must abs path, otherwise error.
        eg: file_name: dxt.txt, path:D:\Program Files\bank\
    """
    dir_path = os.path.dirname(file_abs_path)
    file_name = os.path.basename(file_abs_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    os.chdir(dir_path)

    with open(file_name + '.txt', 'a') as fd:
        sequence = replace.join(sequ) if isinstance(sequ, (list, tuple)) else sequ + replace
        fd.writelines(sequence)


def read(file_path):
    """ open web or re search fail, you need to open and re search """
    file_name, path = (file_path.split('\\')[-1] + '.txt', file_path[:file_path.rfind('\\') + 1])
    os.chdir(path)
    with open(file_name, 'r') as fd:
        it = iter(list(set(fd.readlines())))
    return it


def to_excel(backup_path, excel_path, headers):
    """
        backup_path: source file include '.txt' data file
        excel_path: generate xls file path and file name.
        headers: one or more sheets have the same title, it is list tuple or iterable, but string.
    """
    excel_name, path = backup_path.split('\\')[-1] + '.xls', backup_path[:backup_path.rfind('\\') + 1]
    if not os.path.exists(excel_path):
        os.makedirs(excel_path)

    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)

    list_dirs = [file_name for file_name in os.listdir(path) if file_name.endswith(r'.txt')]
    for file_name in list_dirs:
        print file_name
        workbook = XlsxWriter(excel_path + file_name.replace('.txt', '.xls'), file_name, headers)
        with open(file_name) as fd:
            for j, line in enumerate(fd):
                data = [item.strip() for item in line.strip().split('$*$*$') if item.strip()]
                workbook.write(data)
        workbook.save()


if __name__ == '__main__':
    pass
