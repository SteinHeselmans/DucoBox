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
import time
from setuptools_scm import get_version
from serial import Serial, SerialException

__version__ = get_version()

DEFAULT_LOGLEVEL = 'info'
SERIAL_CHAR_INTERVAL = 0.1


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
    '''Class for holding a DucoNode object: a generic device in the Duco network'''

    KIND = None

    def __init__(self, number, address):
        '''
        Initializer for a Duco Node

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
        '''
        self.number = str(number)
        self.address = str(address)
        self.name = 'My {classname}'.format(classname=self.__class__.__name__)
        logging.info('Found node {node} at {address} ({name})'.format(node=self.number, address=self.address, name=self.name))

    @classmethod
    def get_subclasses(cls):
        '''
        Get a list of subclasses (recursively)

        Returns:
            The function returns an iterable containing all subclasses, and sub-subclasses of this class.
        '''
        for subclass in cls.__subclasses__():
            for subcls in subclass.get_subclasses():
                yield subcls
            yield subclass

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
        section = 'Node{number}'.format(number=self.number)
        cfgparser.add_section(section)
        cfgparser.set(section, 'name', self.name)
        cfgparser.set(section, 'number', self.number)
        cfgparser.set(section, 'address', self.address)

    def _load(self, cfgparser):
        '''
        Load Node from given network configuration file

        Args:
            cfgparser (ConfigParser): Configuration object to load the Node from
        '''
        section = 'Node{number}'.format(number=self.number)
        try:
            self.name = cfgparser.get(section, 'name')
            self.number = cfgparser.get(section, 'number')
            self.address = cfgparser.get(section, 'address')
            logging.info('Node {number} ({name}) found in network configuration file at address {address}'.format(number=self.number, name=self.name, address=self.address))
        except NoSectionError:
            logging.info('Node {number} not found in network configuration file, adding...'.format(number=self.number))

    def sample(self, interface):
        '''
        Take a sample from the DucoNode

        Args:
            interface (DucoInterface): Interface to use to the duco network
        '''
        pass

    def __str__(self):
        '''
        Convert duco node object to string

        Returns:
            str: String representation of the object
        '''
        return self.name + ' @ ' + self.address


class DucoBox(DucoNode):
    '''Class for a Duco box device'''

    KIND = 'BOX'

    FAN_SPEED_COMMAND = 'fanspeed\r'
    MATCH_FAN_SPEED = '^.*Actual\s*(?P<actual>\d+).*Filtered\s*(?P<filtered>\d+).*$'

    def __init__(self, number, address):
        '''
        Initializer for a Duco box device

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
        '''
        super(DucoBox, self).__init__(number, address)
        self.fanspeed = None

    def sample(self, interface):
        '''
        Take a sample from the DucoBox

        Args:
            interface (DucoInterface): Interface to use to the duco network
        '''
        super(DucoBox, self).sample(interface)
        reply = interface._execute(DucoBox.FAN_SPEED_COMMAND)
        for line in reply.split('\r'):
            match = re.compile(self.MATCH_FAN_SPEED).search(line)
            if match:
                actual = int(match.group('actual'))
                filtered = int(match.group('filtered'))
                logging.info('- fan speed: {filtered} rpm (act: {actual} rpm)'.format(filtered=filtered, actual=actual))
                self.fanspeed = filtered


class DucoBoxSensor(DucoNode):
    '''Class for a sensor inside the Duco box device'''

    SENSOR_INFO_COMMAND = 'sensorinfo\r'

    pass


class DucoBoxHumiditySensor(DucoBoxSensor):
    '''Class for a humidity sensor inside the Duco box device'''

    KIND = 'UCRH'
    MATCH_SENSOR_INFO_HUMIDITY = '^\s*RH\s*\:\s*(?P<humidity>\d+).*$'
    MATCH_SENSOR_INFO_TEMPERATURE = '^\s*TEMP\s*\:\s*(?P<temperature>\d+).*$'

    def __init__(self, number, address):
        '''
        Initializer for a humidity sensor inside the Duco box

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
        '''
        super(DucoBoxHumiditySensor, self).__init__(number, address)
        self.humidity = None
        self.temperature = None

    def sample(self, interface):
        '''
        Take a sample from the DucoBoxHumiditySensor

        Args:
            interface (DucoInterface): Interface to use to the duco network
        '''
        super(DucoBoxHumiditySensor, self).sample(interface)
        reply = interface._execute(DucoBoxHumiditySensor.SENSOR_INFO_COMMAND)
        for line in reply.split('\r'):
            match = re.compile(self.MATCH_SENSOR_INFO_HUMIDITY).search(line)
            if match:
                humidity = float(match.group('humidity')) / 100.0
                logging.info('- humidity: {humidity} %'.format(humidity=humidity))
                self.humidity = humidity
            match = re.compile(self.MATCH_SENSOR_INFO_TEMPERATURE).search(line)
            if match:
                temperature = float(match.group('temperature')) / 10.0
                logging.info('- temperature: {temperature} degC'.format(temperature=temperature))
                self.temperature = temperature


class DucoBoxCO2Sensor(DucoBoxSensor):
    '''Class for a CO2 sensor inside the Duco box device'''

    KIND = 'UCCO2'

    def __init__(self, number, address):
        '''
        Initializer for a CO2 sensor inside the Duco box

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
        '''
        super(DucoBoxCO2Sensor, self).__init__(number, address)


class DucoUserControl(DucoNode):
    '''Class for a user control device inside the Duco box network'''

    KIND = 'UCBAT'

    def __init__(self, number, address):
        '''
        Initializer for a user control device inside the Duco network

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
        '''
        super(DucoUserControl, self).__init__(number, address)


class DucoInterface(object):
    '''Class for interfacing with Duco devices'''

    LIST_NETWORK_COMMAND = 'network\r'
    MATCH_NETWORK_COMMAND = '^\s*(?P<node>\d+)\s*\|\s*(?P<address>\d+)\s*\|\s*(?P<kind>\w+).*$'

    def __init__(self, port='/dev/ttyUSB0', cfgfile=None):
        '''
        Initializer for a DucoInterface

        Args:
            port (str): Name of the serial port
            cfgfile (str): Name of the network configuration file
        '''
        logging.info('Welcome to Duco Interface')
        self._serial = None
        self.nodes = []
        self._config_serial(port)
        self.cfgfile = cfgfile
        self._live = False

    def is_online(self):
        '''
        Check if DucoInterface is connected to serial port

        Returns:
            True if DucoInterface is connected to given serial port, False otherwise
        '''
        if self._live:
            return True
        return False

    def store(self):
        '''
        Store to network configuration file
        '''
        logging.info('Storing network configuration...')
        cfgparser = ConfigParser()
        for node in self.nodes:
            node._store(cfgparser)
        with open(self.cfgfile, 'w') as cfgfile:
            cfgparser.write(cfgfile)
        logging.debug('Store finished')

    def load(self):
        '''
        Load from network configuration file
        '''
        logging.info('Loading network configuration...')
        cfgparser = ConfigParser()
        cfgparser.read(self.cfgfile)
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
        logging.info('Opened serial port {port}'.format(port=port))

    def _execute(self, command):
        '''
        Execute a command: send a command, and return the reply

        Args:
            command (str): Command to send to the serial port
        Returns:
            str: Received answer
        '''
        logging.debug('Serial command:\n{command}'.format(command=command))
        self._serial.write('\r')
        time.sleep(SERIAL_CHAR_INTERVAL)
        self._serial.readline()
        cmd = command.encode('utf-8')
        for c in cmd:
            time.sleep(SERIAL_CHAR_INTERVAL)
            self._serial.write(c)
        reply = str(self._serial.readline())
        logging.debug('Serial reply:\n{reply}'.format(reply=reply.replace('\r', '\n')))
        return reply

    def add_node(self, kind, number, address):
        '''
        Add a node to the network

        The function finds the right sub-class of DucoNode (based on given kind), instantiates an object
        of that sub-class, and adds it to the list of nodes.

        Args:
            kind (str): the kind of the DucoNode to be added
            number (str): the number of the node within the network
            address (str): the address of the node within the network

        Returns:
            The node object added
        '''
        nodeclass = DucoNode
        for cls in DucoNode.get_subclasses():
            if cls.KIND == kind:
                nodeclass = cls
        if nodeclass == DucoNode:
            logging.warning('Unknown node kind: {kind}, assuming default'.format(kind=kind))
        node = nodeclass(number, address)
        self.nodes.append(node)
        return node

    def find_nodes(self):
        '''
        Get nodes in the DucoInterface's network

        Searches the network of the DucoBox though the interface, and stores objects for all of the found nodes.
        '''
        if self._serial:
            logging.info('Searching network...')
            reply = self._execute(self.LIST_NETWORK_COMMAND)
            for line in reply.split('\r'):
                match = re.compile(self.MATCH_NETWORK_COMMAND).search(line)
                if match:
                    self.add_node(match.group('kind'), match.group('node'), match.group('address'))
                    self._live = True

    def sample(self):
        if self.is_online():
            logging.info('Taking sample {t}'.format(t=time.strftime("%c")))
            for node in self.nodes:
                node.sample(self)

    def get_node(self, address):
        '''
        Get a node with given address

        Args:
            address (str): Address for the node to be found
        Returns:
            Node object with matching address
        '''
        for node in self.nodes:
            if node.address == address:
                return node
        return None


def ducobox_wrapper(args):
    '''
    Main wrapper for DucoInterface program

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
                        help='Serial port to connect to DucoInterface',
                        required=True, action='store',)
    parser.add_argument('-n', '--network', type=str, dest='network',
                        help='File where the network configuration is stored',
                        default='duco_network.ini', action='store',)
    args = parser.parse_args(args)

    set_logging_level(args.loglevel)

    box = DucoInterface(port=args.port, cfgfile=args.network)

    box.find_nodes()

    box.load()

    if box.is_online():
        box.store()

    while(True):
        box.sample()
        time.sleep(300)

    return 0


def main():
    sys.exit(ducobox_wrapper(sys.argv[1:]))


if __name__ == '__main__':
    main()
