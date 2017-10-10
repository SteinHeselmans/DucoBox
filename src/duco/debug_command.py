#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ducobox import DucoInterface

if __name__ == '__main__':
    itf = DucoInterface(port='/dev/ttyUSB0')

    for a in range(255):
        for b in range(255):
            cmd = 'nodeparaget {a} {b}\r'.format(a=a, b=b)
            print(itf.execute_command(cmd))

