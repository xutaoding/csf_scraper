# -*- coding: utf-8 -*-

from time import sleep, strftime
from sha_mt import ShaMarginTrading
from szx_mt import SzxMarginTrading


def block_fs():
    ShaMarginTrading().main()
    SzxMarginTrading().main()


if __name__ == '__main__':
    while 1:
        if strftime('%H%M') not in ['0930', '1400']:
            print strftime('%Y-%m-%d %H:%M:%S %A')
            sleep(20.0)
            continue

        try:
            block_fs()
        except Exception as e:
            print 'Exception class: {0}, Error: {1}'.format(e.__class__, e.message)

