#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
from setuptools_scm import get_version
from serial import Serial

__version__ = get_version()


class DucoBox(object):
    '''Class for holding a DucoBox object'''

    LIST_NETWORK_COMMAND = 'network'

    def __init__(self, port='/dev/ttyUSB0'):
        '''Initializer for a DucoBox'''
        self.nodes = []
        self._config_serial(port)

    def _config_serial(self, port):
        '''
        Configure and open serial port at 115200 in 8N1 mode

        Args:
            port (str): Reference to the serial port
        '''
        self.serial = Serial(port=port, baudrate=115200, timeout=1)

    def _execute(self, command):
        '''
        Execute a command: send a command, and return the reply

        Args:
            command (str): Command to send to the serial port
        Returns:
            str: Received answer
        '''
        self.serial.write(command.encode('utf-8'))
        reply = str(self.serial.readline())
        print(reply)
        return reply

    def get_nodes(self):
        '''
        Get and store nodes in the DucoBox's network
        '''
        self._execute(self.LIST_NETWORK_COMMAND)
        # TODO: parse reply and store nodes information
        return self.nodes


class DucoNode(object):
    '''Class for holding a DucoBox node object'''

    def __init__(self):
        '''Initializer for a Duco Node'''
        pass


def ducobox_wrapper(args):
    parser = argparse.ArgumentParser(prog='ducobox')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-p', '--port', type=str, dest='port',
                        help='Serial port to connect to DucoBox',
                        required=True, action='store',)
    args = parser.parse_args(args)

    box = DucoBox(port=args.port)
    box.get_nodes()


def main():
    sys.exit(ducobox_wrapper(sys.argv[1:]))


if __name__ == '__main__':
    main()
