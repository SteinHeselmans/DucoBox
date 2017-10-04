#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
try:
    from configparser import ConfigParser, NoSectionError
except ImportError:
    from ConfigParser import ConfigParser, NoSectionError
import sys
import re
import logging
from setuptools_scm import get_version
from serial import Serial, SerialException

__version__ = get_version()

DEFAULT_LOGLEVEL = 'info'


def set_logging_level(loglevel):
    '''
    Set the logging level

    Args:
        loglevel String representation of the loglevel
    '''
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level, format='%(message)s')


class DucoNode(object):
    '''Class for holding a DucoBox node object'''

    def __init__(self, number, address):
        '''
        Initializer for a Duco Node

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
        '''
        logging.info('Found node {node} at {address}'.format(node=number, address=address))
        self.number = str(number)
        self.address = str(address)
        self.name = 'NoName'

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
            logging.debug('Node {address} not found in network configuration file, adding...'.format(address=self.address))

    def __str__(self):
        '''
        Convert duco node object to string

        Returns:
            str: String representation of the object
        '''
        return self.name + ' @ ' + self.address


class DucoBox(DucoNode):
    '''Class for holding a DucoBox object'''

    LIST_NETWORK_COMMAND = 'network'
    MATCH_NETWORK_COMMAND = re.compile('^\s*(?P<node>\d+)\s*\|\s*(?P<address>\d+).*$')

    def __init__(self, port='/dev/ttyUSB0', cfgfile=None):
        '''
        Initializer for a DucoBox

        Args:
            port (str): Name of the serial port
            cfgfile (str): Name of the network configuration file
        '''
        logging.info('Welcome to DucoBox')
        super(DucoBox, self).__init__('DucoBox', 0)
        self._serial = None
        self.nodes = []
        self._config_serial(port)
        self.cfgfile = cfgfile

    def is_online(self):
        '''
        Check if DucoBox is connected to serial port

        Returns:
            True if DucoBox is connected to given serial port, False otherwise
        '''
        if self._serial:
            return True
        return False

    def store(self):
        '''
        Store to network configuration file
        '''
        logging.debug('Storing network configuration...')
        cfgparser = ConfigParser()
        super(DucoBox, self)._store(cfgparser)
        for node in self.nodes:
            node._store(cfgparser)
        with open(self.cfgfile, 'w') as cfgfile:
            cfgparser.write(cfgfile)
        logging.debug('Store finished')

    def load(self):
        '''
        Load from network configuration file
        '''
        logging.debug('Loading network configuration...')
        cfgparser = ConfigParser()
        cfgparser.read(self.cfgfile)
        super(DucoBox, self)._load(cfgparser)
        for node in self.nodes:
            node._load(cfgparser)
        logging.debug('Load finished')

    def _config_serial(self, port):
        '''
        Configure and open serial port at 115200 in 8N1 mode

        Args:
            port (str): Name of the serial port
        '''
        try:
            self._serial = Serial(port=port, baudrate=115200, timeout=1)
        except SerialException:
            logging.error('Could not open {port}, continuing in offline mode'.format(port=port))
        logging.debug('Opened serial port {port}'.format(port=port))

    def _execute(self, command):
        '''
        Execute a command: send a command, and return the reply

        Args:
            command (str): Command to send to the serial port
        Returns:
            str: Received answer
        '''
        logging.debug('Serial command:\n{command}'.format(command=command))
        self._serial.write(command.encode('utf-8'))
        reply = str(self._serial.readline())
        logging.debug('Serial reply:\n{reply}'.format(reply=reply))
        return reply

    def get_nodes(self):
        '''
        Get nodes in the DucoBox's network
        '''
        if self.is_online():
            logging.info('Searching network...')
            reply = self._execute(self.LIST_NETWORK_COMMAND)
            for line in reply.split('\n'):
                match = self.MATCH_NETWORK_COMMAND.search(line)
                if match:
                    node = DucoNode(match.group('node'), match.group('address'))
                    self.nodes.append(node)
        return self.nodes


def ducobox_wrapper(args):
    '''
    Main wrapper for DucoBox program

    Args:
        args (list): arguments as passed to program

    Returns:
        0 on success, error code otherwise
    '''
    parser = argparse.ArgumentParser(prog='ducobox')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-l', '--loglevel', dest='loglevel', default=DEFAULT_LOGLEVEL,
                        action='store', required=False,
                        help='Level for logging (strings from logging python package)')
    parser.add_argument('-p', '--port', type=str, dest='port',
                        help='Serial port to connect to DucoBox',
                        required=True, action='store',)
    parser.add_argument('-n', '--network', type=str, dest='network',
                        help='File where the network configuration is stored',
                        default='duco_network.ini', action='store',)
    args = parser.parse_args(args)

    set_logging_level(args.loglevel)

    box = DucoBox(port=args.port, cfgfile=args.network)

    box.get_nodes()

    box.load()

    if box.is_online():
        box.store()

    return 0


def main():
    sys.exit(ducobox_wrapper(sys.argv[1:]))


if __name__ == '__main__':
    main()
