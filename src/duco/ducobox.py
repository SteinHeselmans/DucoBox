#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools_scm import get_version
from serial import Serial

__version__ = get_version()


class DucoBox(object):
    '''Class for holding a DucoBox object'''

    LIST_NETWORK_COMMAND = 'network'

    def __init__(self, tty='/dev/ttyUSB0'):
        '''Initializer for a DucoBox'''
        self.nodes = []
        self._config_serial(tty)

    def _config_serial(self, tty):
        '''
        Configure and open serial port at 115200 in 8N1 mode

        Args:
            tty (str): Reference to the serial port
        '''
        self.tty = Serial(port=tty, baudrate=115200, timeout=1)

    def _execute(self, command):
        '''
        Execute a command: send a command, and return the reply

        Args:
            command (str): Command to send to the serial port
        Returns:
            str: Received answer
        '''
        self.tty.write(command.encode('utf-8'))
        reply = self.tty.readline().decode('utf-8')
        print(reply)
        return reply

    def get_nodes(self):
        '''
        Get and store nodes in the DucoBox's network
        '''
        reply = self._execute(self.LIST_NETWORK_COMMAND)
        # TODO: parse reply and store nodes information
        return self.nodes


class DucoNode(object):
    '''Class for holding a DucoBox node object'''

    def __init__(self):
        '''Initializer for a Duco Node'''
        pass


def main():
    box = DucoBox()
    box.get_nodes()


if __name__ == '__main__':
    main()
