#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os.path
from time import strftime, sleep

module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(module_path)

from er_update import ErUpdate


if __name__ == '__main__':
    update_time = ['0800', '0930', '1130', '1400', '1630', '1700', '1830']
    query_date = ['2015-09-27']
    while 1:
        if strftime('%H%M') not in update_time:
            print strftime('%Y-%m-%d %H:%M:%S %A')
            sleep(5.0)
        else:
            try:
                ErUpdate().main()
            except:
                pass
    # ErUpdate().main(query_date)
