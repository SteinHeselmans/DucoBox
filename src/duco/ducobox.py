#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
try:
    from configparser import ConfigParser, NoSectionError
except ImportError:
    from ConfigParser import ConfigParser, NoSectionError
import sys
from setuptools_scm import get_version
from serial import Serial, SerialException

__version__ = get_version()


class DucoNode(object):
    '''Class for holding a DucoBox node object'''

    def __init__(self, name, address):
        '''
        Initializer for a Duco Node

        Args:
            name (str): Name of the node
            address (str): Address of the node within the network
        '''
        self.address = str(address)
        self.name = name

    def __eq__(self, other):
        '''
        Equal operator

        Args:
            other (DucoNode): Other object to compare for equality
        '''
        return self.address == other.address

    def _store(self, cfgparser):
        '''
        Store Node to given network configuration file

        Args:
            cfgparser (ConfigParser): Configuration object to store the Node to
        '''
        section = 'Node{address}'.format(address=self.address)
        cfgparser.add_section(section)
        cfgparser.set(section, 'name', self.name)
        cfgparser.set(section, 'address', self.address)

    def _load(self, cfgparser):
        '''
        Load Node from given network configuration file

        Args:
            cfgparser (ConfigParser): Configuration object to load the Node from
        '''
        section = 'Node{address}'.format(address=self.address)
        try:
            self.name = cfgparser.get(section, 'name')
            # self.address = cfgparser.get(section, 'address')
        except NoSectionError:
            print('Node {address} not found in network configuration file, adding...'.format(address=self.address))


class DucoBox(DucoNode):
    '''Class for holding a DucoBox object'''

    LIST_NETWORK_COMMAND = 'network'

    def __init__(self, port='/dev/ttyUSB0', cfgfile=None):
        '''
        Initializer for a DucoBox

        Args:
            port (str): Name of the serial port
            cfgfile (str): Name of the network configuration file
        '''
        super(DucoBox, self).__init__('DucoBox', 0)
        self._serial = None
        self.nodes = []
        self._config_serial(port)
        self.cfgfile = cfgfile

    def store(self):
        '''
        Store to network configuration file
        '''
        cfgparser = ConfigParser()
        super(DucoBox, self)._store(cfgparser)
        for node in self.nodes:
            node._store(cfgparser)
        with open(self.cfgfile, 'w') as cfgfile:
            cfgparser.write(cfgfile)

    def load(self):
        '''
        Load from network configuration file
        '''
        cfgparser = ConfigParser()
        cfgparser.read(self.cfgfile)
        super(DucoBox, self)._load(cfgparser)
        for node in self.nodes:
            node._load(cfgparser)

    def _config_serial(self, port):
        '''
        Configure and open serial port at 115200 in 8N1 mode

        Args:
            port (str): Name of the serial port
        '''
        try:
            self._serial = Serial(port=port, baudrate=115200, timeout=1)
        except SerialException:
            print('Could not open {port}, continuing in offline mode'.format(port=port))

    def _execute(self, command):
        '''
        Execute a command: send a command, and return the reply

        Args:
            command (str): Command to send to the serial port
        Returns:
            str: Received answer
        '''
        self._serial.write(command.encode('utf-8'))
        reply = str(self._serial.readline())
        print(reply)
        return reply

    def get_nodes(self):
        '''
        Get nodes in the DucoBox's network
        '''
        if self._serial:
            self._execute(self.LIST_NETWORK_COMMAND)
        # TODO: parse reply and store nodes information
        return self.nodes


def ducobox_wrapper(args):
    parser = argparse.ArgumentParser(prog='ducobox')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-p', '--port', type=str, dest='port',
                        help='Serial port to connect to DucoBox',
                        required=True, action='store',)
    parser.add_argument('-n', '--network', type=str, dest='network',
                        help='File where the network configuration is stored',
                        default='duco_network.ini', action='store',)
    args = parser.parse_args(args)

    box = DucoBox(port=args.port, cfgfile=args.network)
    box.get_nodes()
    box.load()
    box.store()


def main():
    sys.exit(ducobox_wrapper(sys.argv[1:]))


if __name__ == '__main__':
    main()
