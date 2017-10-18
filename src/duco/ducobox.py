#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
try:
    from configparser import ConfigParser, NoSectionError
except ImportError:
    from ConfigParser import ConfigParser, NoSectionError
import sys
import os
import re
import logging
import time
from serial import Serial, SerialException

# Get version from file
__version__ = 'unknown'
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "__version__.py")).read())

DEFAULT_LOGLEVEL = 'info'
DEFAULT_INTERVAL = 300
SERIAL_CHAR_INTERVAL = 0.1
CO2_PARAGET_VALUE_PARAMETER = 74
HUMIDITY_PARAGET_VALUE_PARAMETER = 75
HUMIDITY_UNIT = '%'
CO2_UNIT = 'ppm'
TEMPERATURE_UNIT = 'degC'
HUMIDITY_SCALING = 100.0
CO2_SCALING = 1
TEMPERATURE_SCALING = 10.0


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
    PARAGET_COMMAND = 'nodeparaget {node} {para}'
    PARAGET_VALUE_PARAMETER = 0
    PARAGET_REGEX = '-->\s*(?P<value>\d+)'
    PARAGET_UNIT = ''
    PARAGET_SCALING = None

    def __init__(self, number, address, interface=None):
        '''
        Initializer for a Duco Node

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
            interface (DucoInterface): Interface object to use when executing commands
        '''
        self.number = str(number)
        self.address = str(address)
        self.name = 'My {classname}'.format(classname=self.__class__.__name__)
        self.value = None
        self.bind(interface)
        logging.info('Found node {node} at {address} ({name})'.format(node=self.number, address=self.address, name=self.name))

    def bind(self, interface):
        '''
        Bind the DucoNode to an interface

        Args:
            interface (DucoInterface): Interface object to use when executing commands
        '''
        self.interface = interface

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

    def sample(self):
        '''
        Take a sample from the DucoNode
        '''
        if self.interface:
            cmd = self.PARAGET_COMMAND.format(node=self.number, para=self.PARAGET_VALUE_PARAMETER)
            reply = self.interface.execute_command(cmd)
            self.value = self._parse_reply(reply, 'value', self.PARAGET_REGEX, 'value', unit=self.PARAGET_UNIT, scaling=self.PARAGET_SCALING)
        else:
            logging.error('No interface to duco')

    def __str__(self):
        '''
        Convert duco node object to string

        Returns:
            str: String representation of the object
        '''
        return '{name} ({number}) @ {address}'.format(name=self.name, number=self.number, address=self.address)

    def _parse_reply(self, reply, msg, regex, group, scaling=None, unit=''):
        '''
        Parse the reply on a command

        Args:
            reply (str): The reply from the duco interface on your command
            msg (str): Message of the information to be printed
            regex (str): Regular expression to get the data from the reply
            group (str): Named group within the regex to get the data from the reply
            scaling (float): Dividing factor for rescaling parsed value
            unit (str): Unit of the sampled information

        Returns:
            String with parsed value from reply, if regex matched. None otherwise.
        '''
        match = re.compile(regex).search(reply)
        if match:
            value = match.group(group)
            if value:
                if scaling:
                    value = float(value) / scaling
                logging.info('- {msg}: {value} {unit}'.format(msg=msg, value=value, unit=unit))
                return str(value)
        return None


class DucoBox(DucoNode):
    '''Class for a Duco box device'''

    KIND = 'BOX'

    FAN_SPEED_COMMAND = 'fanspeed'
    MATCH_FAN_SPEED = 'Actual\s*(?P<actual>\d+).*Filtered\s*(?P<filtered>\d+)'
    BOARD_INFO_COMMAND = 'boardinfo'
    MATCH_BOOT_SOFTWARE = 'BootSW\s*:\s*(?P<bootsw>.+)'
    MATCH_SERIAL = 'Serial\s*:\s*(?P<serial>.+)'
    MATCH_BOARD_NAME = 'Board\s*:\s*(?P<board>.+)'
    MATCH_BOARD_TYPE = 'Type\s*:\s*(?P<type>.+)'
    MATCH_DEVICE_ID = 'DevId\s*:\s*(?P<deviceid>.+)'

    def __init__(self, number, address, interface=None):
        '''
        Initializer for a Duco box device

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
            interface (DucoInterface): Interface object to use when executing commands
        '''
        super(DucoBox, self).__init__(number, address, interface)
        self.fanspeed = None
        self.fanspeed_act = None
        self.boot_software = None
        self.serial = None
        self.board_name = None
        self.board_type = None
        self.device_id = None
        self._store_board_info()

    def _store_board_info(self):
        '''
        Store board information
        '''
        if self.interface:
            logging.info('Getting board information...')
            reply = self.interface.execute_command(self.BOARD_INFO_COMMAND)
            self.boot_software = self._parse_reply(reply, 'software version', self.MATCH_BOOT_SOFTWARE, 'bootsw')
            self.serial = self._parse_reply(reply, 'serial number', self.MATCH_SERIAL, 'serial')
            self.board_name = self._parse_reply(reply, 'board name', self.MATCH_BOARD_NAME, 'board')
            self.board_type = self._parse_reply(reply, 'board type', self.MATCH_BOARD_TYPE, 'type')
            self.device_id = self._parse_reply(reply, 'device ID', self.MATCH_DEVICE_ID, 'deviceid')

    def sample(self):
        '''
        Take a sample from the DucoBox
        '''
        reply = self.interface.execute_command(DucoBox.FAN_SPEED_COMMAND)
        speed = self._parse_reply(reply, 'fan speed (filtered)', self.MATCH_FAN_SPEED, 'filtered', unit='rpm')
        if speed:
            self.fanspeed = int(speed)
        speed = self._parse_reply(reply, 'fan speed (actual)', self.MATCH_FAN_SPEED, 'actual', unit='rpm')
        if speed:
            self.fanspeed_act = int(speed)


class DucoUserControl(DucoNode):
    '''Class for a user control device inside the Duco box network'''

    KIND = 'UC'
    SENSOR_INFO_COMMAND = 'sensorinfo'


class DucoUserControlBattery(DucoUserControl):
    '''Class for a user control with battery inside the Duco box network'''

    KIND = 'UCBAT'


class DucoUserControlHumiditySensor(DucoUserControl):
    '''Class for a user control with a humidity sensor inside the Duco box network'''

    KIND = 'UCRH'
    PARAGET_VALUE_PARAMETER = HUMIDITY_PARAGET_VALUE_PARAMETER
    PARAGET_UNIT = HUMIDITY_UNIT
    PARAGET_SCALING = HUMIDITY_SCALING

    MATCH_SENSOR_INFO_HUMIDITY = 'RH\s*\:\s*(?P<humidity>\d+)'
    MATCH_SENSOR_INFO_TEMPERATURE = 'TEMP\s*\:\s*(?P<temperature>\d+)'

    def __init__(self, number, address, interface=None):
        '''
        Initializer for a humidity sensor inside the Duco box

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
            interface (DucoInterface): Interface object to use when executing commands
        '''
        super(DucoUserControlHumiditySensor, self).__init__(number, address, interface)
        self.humidity = None
        self.temperature = None

    def sample(self):
        '''
        Take a sample from the DucoUserControlHumiditySensor
        '''
        if 0:
            super(DucoUserControlHumiditySensor, self).sample()
        else:
            reply = self.interface.execute_command(DucoUserControlHumiditySensor.SENSOR_INFO_COMMAND)
            humidity = self._parse_reply(reply, 'humidity', self.MATCH_SENSOR_INFO_HUMIDITY, 'humidity', unit=HUMIDITY_UNIT, scaling=HUMIDITY_SCALING)
            if humidity:
                self.value = humidity
            temperature = self._parse_reply(reply, 'temperature', self.MATCH_SENSOR_INFO_TEMPERATURE, 'temperature', unit=TEMPERATURE_UNIT, scaling=TEMPERATURE_SCALING)
            if temperature:
                self.temperature = temperature


class DucoUserControlCO2Sensor(DucoUserControl):
    '''Class for a user control with a CO2 sensor inside the Duco box network'''

    KIND = 'UCCO2'
    PARAGET_VALUE_PARAMETER = CO2_PARAGET_VALUE_PARAMETER
    PARAGET_UNIT = CO2_UNIT
    PARAGET_SCALING = CO2_SCALING


class DucoValve(DucoNode):
    '''Class for a valve device inside the Duco box network'''

    KIND = 'VLV'


class DucoValveHumiditySensor(DucoValve):
    '''Class for a valve with a humidity sensor inside the Duco box network'''

    KIND = 'VLVRH'
    PARAGET_VALUE_PARAMETER = HUMIDITY_PARAGET_VALUE_PARAMETER
    PARAGET_UNIT = HUMIDITY_UNIT
    PARAGET_SCALING = HUMIDITY_SCALING


class DucoValveCO2Sensor(DucoValve):
    '''Class for a valve with a CO2 sensor inside the Duco box network'''

    KIND = 'VLVCO2'
    PARAGET_VALUE_PARAMETER = CO2_PARAGET_VALUE_PARAMETER
    PARAGET_UNIT = CO2_UNIT
    PARAGET_SCALING = CO2_SCALING


class DucoSwitch(DucoNode):
    '''Class for a switch inside the Duco box network'''

    KIND = 'SWITCH'


class DucoGrille(DucoNode):
    '''Class for a 'Tronic' ventilation grille with motor and temperature sensor inside the Duco box network'''

    KIND = 'CLIMA'


class DucoInterface(object):
    '''Class for interfacing with Duco devices'''

    LIST_NETWORK_COMMAND = 'network'
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
        self.bind(port)
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
        if self.cfgfile:
            with open(self.cfgfile, 'w') as cfgfile:
                logging.info('Storing network configuration...')
                cfgparser = ConfigParser()
                for node in self.nodes:
                    node._store(cfgparser)
                cfgparser.write(cfgfile)
                logging.debug('Store finished')
        else:
            logging.warning('Not storing: no network configuration file given')

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

    def bind(self, port):
        '''
        Bind serial port: configure and open serial port at 115200 in 8N1 mode

        Args:
            port (str): Name of the serial port
        '''
        try:
            self._serial = Serial(port=port, baudrate=115200, timeout=1)
        except SerialException:
            logging.error('Could not open {port}, continuing in offline mode'.format(port=port))
        logging.info('Opened serial port {port}'.format(port=port))

    def execute_command(self, command):
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
        time.sleep(SERIAL_CHAR_INTERVAL)
        self._serial.write('\r')
        reply = str(self._serial.readline()).replace('\r', '\n')
        logging.debug('Serial reply:\n{reply}'.format(reply=reply))
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
        node = nodeclass(number, address, self)
        self.nodes.append(node)
        return node

    def find_nodes(self):
        '''
        Get nodes in the DucoInterface's network

        Searches the network of the DucoBox though the interface, and stores objects for all of the found nodes.
        '''
        if self._serial:
            logging.info('Searching network...')
            reply = self.execute_command(self.LIST_NETWORK_COMMAND)
            for line in reply.split('\n'):
                match = re.compile(self.MATCH_NETWORK_COMMAND).search(line)
                if match:
                    self.add_node(match.group('kind'), match.group('node'), match.group('address'))
                    self._live = True

    def sample(self):
        if self.is_online():
            logging.info('Taking sample {t}'.format(t=time.strftime("%c")))
            for node in self.nodes:
                node.sample()

    def get_node(self, number):
        '''
        Get a node with given node number

        Args:
            number (str): Number for the node to be found
        Returns:
            Node object with matching address
        '''
        for node in self.nodes:
            if node.number == number:
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
    parser.add_argument('-l', '--loglevel', type=str, dest='loglevel', default=DEFAULT_LOGLEVEL,
                        action='store', required=False,
                        help='Interval in between samples [seconds]')
    parser.add_argument('-i', '--interval', type=float, dest='interval', default=DEFAULT_INTERVAL,
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

    itf = DucoInterface(port=args.port, cfgfile=args.network)

    itf.find_nodes()

    itf.load()

    if itf.is_online():
        itf.store()

    while(True):
        itf.sample()
        time.sleep(args.interval)

    return 0


def main():
    sys.exit(ducobox_wrapper(sys.argv[1:]))


if __name__ == '__main__':
    main()
