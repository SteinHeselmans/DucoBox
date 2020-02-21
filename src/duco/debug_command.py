#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ducobox import DucoInterface

if __name__ == '__main__':
    itf = DucoInterface(port='/dev/ttyUSB0')

    print(itf.execute_command('network\r'))

    addresses = [1, 2, 34, 102, 132]
    params = [74, 75]

    addresses = range(255)
    params = range(255)

    for a in addresses:
        for b in params:
            cmd = 'nodeparaget {a} {b}\r'.format(a=a, b=b)
            print(itf.execute_command(cmd))

