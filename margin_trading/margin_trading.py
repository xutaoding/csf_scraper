# -*- coding: utf-8 -*-
import sys
import os.path
from time import sleep, strftime

module_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(module_path)

from sha_mt import ShaMarginTrading
from szx_mt import SzxMarginTrading


def block_fs():
    ShaMarginTrading().main()
    SzxMarginTrading().main()


if __name__ == '__main__':
    while 1:
        if strftime('%H%M') not in ['0930', '1130', '14030', '1630']:
            print strftime('%Y-%m-%d %H:%M:%S %A')
            sleep(20.0)
            continue
        else:
            try:
                block_fs()
            except Exception as e:
                print 'Exception class: {0}, Error: {1}'.format(e.__class__, e.message)

