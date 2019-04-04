#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
try:
    from configparser import ConfigParser, NoSectionError, NoOptionError
except ImportError:
    from ConfigParser import ConfigParser, NoSectionError, NoOptionError
import sys
import re
import logging
import time
from serial import Serial, SerialException
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBServerError

try:
    from .__ducobox_version__ import version as ducobox_version
except ImportError:
    ducobox_version = 'version not available from scm'

__version__ = ducobox_version

DEFAULT_LOGLEVEL = 'info'
DEFAULT_INTERVAL = 300
SERIAL_CHAR_INTERVAL = 0.001

CO2_STR = 'CO2'
HUMIDITY_STR = 'humidity'
TEMPERATURE_STR = 'temperature'
FANSPEED_STR = 'fanspeed'

CO2_PARAGET_ID = 74
HUMIDITY_PARAGET_ID = 75
TEMPERATURE_PARAGET_ID = 73

HUMIDITY_UNIT = '%'
CO2_UNIT = 'ppm'
TEMPERATURE_UNIT = 'degC'
FANSPEED_UNIT = 'rpm'

HUMIDITY_SCALING = 100.0
CO2_SCALING = 1
TEMPERATURE_SCALING = 10.0
FANSPEED_SCALING = 1.0


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


class DucoNodeParameter(object):
    '''Class for holding a parameter for Duco Nodes'''

    def __init__(self, name, unit='', scaling=1.0):
        '''
        Initializer for a node parameter

        Args:
            name (str): Name of the parameter
            unit (str): Unit of the parameter
            scaling (float): Dividing factor for rescaling parsed value
        '''
        self.name = name
        self.unit = unit
        self.scaling = float(scaling)
        self.value = None

    def set_value(self, value):
        '''
        Set the value for the node parameter

        Args:
            value (float): New value for the parameter
        Returns:
            float: Scaled floating point value for the given value
        '''
        self.value = float(value) / self.scaling
        logging.info('    - {msg}: {value} {unit}'.format(msg=self.name, value=self.value, unit=self.unit))
        return self.value

    def get_value(self):
        '''
        Set the value for the node parameter

        Returns:
            Float value for the parameter, or None
        '''
        return self.value

    def __str__(self):
        '''
        Convert duco node parameter to string

        Returns:
            str: String representation of the object
        '''
        return '{value} {unit}'.format(value=self.value, unit=self.unit, address=self.address)


class DucoNodeFanSpeed(DucoNodeParameter):
    '''Class for holding a fan speed parameter for Duco Nodes'''

    def __init__(self):
        '''Initializer for a fan speed parameter'''
        super(DucoNodeFanSpeed, self).__init__('fanspeed', FANSPEED_UNIT, FANSPEED_SCALING)


class DucoNodeParaGetParameter(DucoNodeParameter):
    '''Class for holding a parameter for Duco Nodes, that can be retrieved through the nodeparaget command'''

    def __init__(self, name, unit, scaling, getter_id):
        '''
        Initializer for a node parameter

        Args:
            name (str): Name of the parameter
            unit (str): Unit of the parameter
            scaling (float): Dividing factor for rescaling parsed value
            getter_id (int): Number to be used during the nodeparaget command as ID
        '''
        super(DucoNodeParaGetParameter, self).__init__(name, unit, scaling)
        self.getter_id = int(getter_id)


class DucoNodeHumidityParaGet(DucoNodeParaGetParameter):
    '''Class for holding a humidity-paraget parameter for Duco Nodes'''

    def __init__(self):
        '''Initializer for a humidity parameter'''
        super(DucoNodeHumidityParaGet, self).__init__('humidity', HUMIDITY_UNIT, HUMIDITY_SCALING,
                                                      HUMIDITY_PARAGET_ID)


class DucoNodeCO2ParaGet(DucoNodeParaGetParameter):
    '''Class for holding a CO2-paraget parameter for Duco Nodes'''

    def __init__(self):
        '''Initializer for a CO2 parameter'''
        super(DucoNodeCO2ParaGet, self).__init__('CO2', CO2_UNIT, CO2_SCALING, CO2_PARAGET_ID)


class DucoNodeTemperatureParaGet(DucoNodeParaGetParameter):
    '''Class for holding a temperature-paraget parameter for Duco Nodes'''

    def __init__(self):
        '''Initializer for a temperature parameter'''
        super(DucoNodeTemperatureParaGet, self).__init__('temperature', TEMPERATURE_UNIT, TEMPERATURE_SCALING,
                                                         TEMPERATURE_PARAGET_ID)


class DucoNode(object):
    '''Class for holding a DucoNode object: a generic device in the Duco network'''

    KIND = None
    SENSOR_INFO_COMMAND = r'sensorinfo'
    PARAGET_COMMAND = r'nodeparaget {node} {para}'
    PARAGET_REGEX = r'-->\s*(?P<value>\d+)'

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
        self.blacklist = False
        self.parameters = {}
        self.bind_serial(interface)
        logging.info('Found node {node} at {address} ({name})'.format(node=self.number, address=self.address, name=self.name))

    def bind_serial(self, interface):
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
        cfgparser.set(section, 'blacklist', self.blacklist)

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
            self.blacklist = cfgparser.getboolean(section, 'blacklist')
            logging.info('Node {number} ({name}) found in network configuration file at address {address}'.format(number=self.number, name=self.name, address=self.address))
        except (NoSectionError, NoOptionError):
            logging.info('Node {number} not found in network configuration file, adding...'.format(number=self.number))

    def sample(self):
        '''
        Take a sample from the DucoNode
        '''
        if not self.blacklist:
            if self.interface:
                logging.info('  - {name}'.format(name=self.name))
                self._perform_sample()
            else:
                logging.error('No interface to duco')

    def _perform_sample(self):
        '''
        Take a sample from the DucoNode and store it
        '''
        for name in self.parameters:
            parameter = self.parameters[name]
            cmd = self.PARAGET_COMMAND.format(node=self.number, para=parameter.getter_id)
            reply = self.interface.execute_command(cmd)
            value = self._parse_reply(reply, self.PARAGET_REGEX, 'value', unit=parameter.unit, scaling=parameter.scaling)
            self.set_value(name, value)

    def set_value(self, parameter, value):
        '''
        Store a sample datapoint in database

        Args:
            parameter (str): Type of measurement performed
            value (str): Value for the datapoint
        '''
        if value is not None and parameter in self.parameters:
            scaled = self.parameters[parameter].set_value(value)
            self.interface.store_sample(self, parameter, scaled)

    def get_value(self, parameter):
        '''
        Get value for parameter

        Args:
            parameter (str): String for the name of the parameter to get
        '''
        if parameter in self.parameters:
            return self.parameters[parameter].get_value()
        return None

    def __str__(self):
        '''
        Convert duco node object to string

        Returns:
            str: String representation of the object
        '''
        return '{name} ({number}) @ {address}'.format(name=self.name, number=self.number, address=self.address)

    def _parse_reply(self, reply, regex, group, scaling=None, unit=''):
        '''
        Parse the reply on a command

        Args:
            reply (str): The reply from the duco interface on your command
            regex (str): Regular expression to get the data from the reply
            group (str): Named group within the regex to get the data from the reply
            scaling (float): Dividing factor for rescaling parsed value
            unit (str): Unit of the sampled information

        Returns:
            String with parsed value from reply, if regex matched. None otherwise.
        '''
        match = re.compile(regex).search(reply)
        if match:
            return match.group(group)
        return None


class DucoBox(DucoNode):
    '''Class for a Duco box device'''

    KIND = 'BOX'

    FAN_SPEED_COMMAND = r'fanspeed'
    MATCH_FAN_SPEED = r'Actual\s*(?P<actual>\d+).*Filtered\s*(?P<filtered>\d+)'
    BOARD_INFO_COMMAND = r'boardinfo'
    MATCH_BOOT_SOFTWARE = r'BootSW\s*:\s*(?P<bootsw>.+)'
    MATCH_SERIAL = r'Serial\s*:\s*(?P<serial>.+)'
    MATCH_BOARD_NAME = r'Board\s*:\s*(?P<board>.+)'
    MATCH_BOARD_TYPE = r'Type\s*:\s*(?P<type>.+)'
    MATCH_DEVICE_ID = r'DevId\s*:\s*(?P<deviceid>.+)'

    def __init__(self, number, address, interface=None):
        '''
        Initializer for a Duco box device

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
            interface (DucoInterface): Interface object to use when executing commands
        '''
        super(DucoBox, self).__init__(number, address, interface)
        self.parameters[FANSPEED_STR] = DucoNodeFanSpeed()
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
            self.boot_software = self._parse_reply(reply, self.MATCH_BOOT_SOFTWARE, 'bootsw')
            self.serial = self._parse_reply(reply, self.MATCH_SERIAL, 'serial')
            self.board_name = self._parse_reply(reply, self.MATCH_BOARD_NAME, 'board')
            self.board_type = self._parse_reply(reply, self.MATCH_BOARD_TYPE, 'type')
            self.device_id = self._parse_reply(reply, self.MATCH_DEVICE_ID, 'deviceid')
            if self.board_name and "BASIC" not in self.board_name:
                self.interface.set_extended()
        else:
            logging.error('No interface to duco')

    def _perform_sample(self):
        '''
        Take a sample from the DucoBox
        '''
        reply = self.interface.execute_command(DucoBox.FAN_SPEED_COMMAND)
        speed = self._parse_reply(reply, self.MATCH_FAN_SPEED, 'filtered', unit='rpm (filtered)')
        self.set_value(FANSPEED_STR, speed)


class DucoNodeWithTemperature(DucoNode):
    '''Class for a duco node with temperature sensing'''

    def __init__(self, number, address, interface=None):
        '''
        Initializer for a temperature sensor inside the Duco box

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
            interface (DucoInterface): Interface object to use when executing commands
        '''
        super(DucoNodeWithTemperature, self).__init__(number, address, interface)
        self.temperature = None
        self.parameters[TEMPERATURE_STR] = DucoNodeTemperatureParaGet()


class DucoNodeWithHumidity(DucoNode):
    '''Class for a duco node with humidity sensing'''

    def __init__(self, number, address, interface=None):
        '''
        Initializer for a humidity sensor inside the Duco box

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
            interface (DucoInterface): Interface object to use when executing commands
        '''
        super(DucoNodeWithHumidity, self).__init__(number, address, interface)
        self.humidity = None
        self.parameters[HUMIDITY_STR] = DucoNodeHumidityParaGet()


class DucoNodeWithCO2(DucoNode):
    '''Class for a duco node with CO2 sensing'''

    def __init__(self, number, address, interface=None):
        '''
        Initializer for a CO2 sensor inside the Duco box

        Args:
            number (str): Number of the node in the network
            address (str): Address of the node within the network
            interface (DucoInterface): Interface object to use when executing commands
        '''
        super(DucoNodeWithCO2, self).__init__(number, address, interface)
        self.co2 = None
        self.parameters[CO2_STR] = DucoNodeCO2ParaGet()


class DucoUserControl(DucoNode):
    '''Class for a user control device inside the Duco box network'''

    KIND = 'UC'


class DucoUserControlBattery(DucoUserControl):
    '''Class for a user control with battery inside the Duco box network'''

    KIND = 'UCBAT'


class DucoUserControlHumiditySensor(DucoUserControl, DucoNodeWithHumidity, DucoNodeWithTemperature):
    '''Class for a user control with a humidity sensor inside the Duco box network'''

    KIND = 'UCRH'

    MATCH_SENSOR_INFO_HUMIDITY = r'RH\s*\:\s*(?P<humidity>\d+)'
    MATCH_SENSOR_INFO_TEMPERATURE = r'TEMP\s*\:\s*(?P<temperature>\d+)'

    def _perform_sample(self):
        '''
        Take a sample from the DucoUserControlHumiditySensor
        '''
        if self.interface.is_extended():
            super(DucoUserControlHumiditySensor, self)._perform_sample()
        else:
            reply = self.interface.execute_command(self.SENSOR_INFO_COMMAND)
            humidity = self._parse_reply(reply, self.MATCH_SENSOR_INFO_HUMIDITY, 'humidity',
                                         unit=HUMIDITY_UNIT, scaling=HUMIDITY_SCALING)
            self.set_value(HUMIDITY_STR, humidity)
            temperature = self._parse_reply(reply, self.MATCH_SENSOR_INFO_TEMPERATURE,
                                            'temperature', unit=TEMPERATURE_UNIT, scaling=TEMPERATURE_SCALING)
            self.set_value(TEMPERATURE_STR, temperature)


class DucoUserControlCO2Sensor(DucoNodeWithCO2, DucoNodeWithTemperature):
    '''Class for a user control with a CO2 sensor inside the Duco box network'''

    KIND = 'UCCO2'


class DucoValve(DucoNode):
    '''Class for a valve device inside the Duco box network'''

    KIND = 'VLV'


class DucoValveHumiditySensor(DucoNodeWithHumidity, DucoNodeWithTemperature):
    '''Class for a valve with a humidity sensor inside the Duco box network'''

    KIND = 'VLVRH'


class DucoValveCO2Sensor(DucoNodeWithCO2, DucoNodeWithTemperature):
    '''Class for a valve with a CO2 sensor inside the Duco box network'''

    KIND = 'VLVCO2'


class DucoSwitch(DucoNode):
    '''Class for a switch inside the Duco box network'''

    KIND = 'SWITCH'


class DucoGrille(DucoNodeWithTemperature):
    '''Class for a 'Tronic' ventilation grille with motor and temperature sensor inside the Duco box network'''

    KIND = 'CLIMA'


class DucoDatabase(object):
    '''
    Class for a generic database where we want to store the samples from our ducobox
    '''

    def __init__(self):
        pass

    def store_sample(self, node, measurement, value):
        '''
        Store a sample in the database

        Args:
            node (DucoNode): Node for which to store the sample
            measurement (str): Parameter to store
            value (float): Scaled value to store in database
        '''
        pass


class InfluxDb(DucoDatabase):
    '''
    Class for the InfluxDB database where we want to store the samples from our ducobox
    '''

    def __init__(self, cfgfile):
        '''
        Create a connection (and initialize) the influxDB database

        Args:
            cfgfile (str): Configuration file for connection to influxdb
        '''
        super(InfluxDb, self).__init__()
        try:
            cfgparser = ConfigParser()
            cfgparser.read(cfgfile)
            section = 'InfluxDB'
            url = cfgparser.get(section, 'url')
            port = cfgparser.get(section, 'port')
            user = cfgparser.get(section, 'user')
            password = cfgparser.get(section, 'password')
            dbname = cfgparser.get(section, 'database')
            logging.info('InfluxDB connection to {url}:{port}, {name}'.format(url=url, port=port, name=dbname))
            self.configure(url, port, user, password, dbname)
        except (NoSectionError, NoOptionError):
            logging.warning('InfluxDB configuration file {file} incomplete'.format(file=cfgfile))

    def configure(self, url, port, user, password, dbname):
        '''
        Create a connection (and initialize) the influxDB database

        Args:
            url (str): URL of the influxDB server
            port (str): Port of the influxDB server
            user (str): Username for the influxDB server
            password (str): Password for the user
            dbname (str): Name of the influxDB to write to
        '''
        super(InfluxDb, self).__init__()
        self.database = InfluxDBClient(url, port, user, password, dbname)
        self.database.create_database(dbname)

    def store_sample(self, node, measurement, value):
        '''
        Store a sample in the database

        Args:
            node (DucoNode): Node for which to store the sample
            measurement (str): Parameter to store
            value (float): Scaled value to store in database
        '''
        super(InfluxDb, self).store_sample(node, measurement, value)
        json_data = [
            {
                "measurement": measurement,
                "tags":
                    {
                        "node": node.number,
                        "name": node.name,
                    },
                "fields":
                    {
                        "value": value
                    }
            }
        ]
        try:
            self.database.write_points(json_data)
        except InfluxDBServerError:
            logging.warning('Could not write to influxDB')


class DucoInterface(object):
    '''Class for interfacing with Duco devices'''

    LIST_NETWORK_COMMAND = r'network'
    MATCH_NETWORK_COMMAND = r'^\s*(?P<node>\d+)\s*\|\s*(?P<address>\d+)\s*\|\s*(?P<kind>\w+).*$'

    def __init__(self, port='/dev/ttyUSB0', cfgfile=None):
        '''
        Initializer for a DucoInterface

        Args:
            port (str): Name of the serial port
            cfgfile (str): Name of the network configuration file
        '''
        logging.info('Welcome to Duco Interface')
        self._serial = None
        self._database = None
        self.nodes = []
        self.bind_serial(port)
        self.cfgfile = cfgfile
        self._live = False
        self._extended = False

    def is_online(self):
        '''
        Check if DucoInterface is connected to serial port

        Returns:
            True if DucoInterface is connected to given serial port, False otherwise
        '''
        if self._live:
            return True
        return False

    def is_extended(self):
        '''
        Check if the the attached interface is extended

        Returns:
            True if the interface is extended, false otherwise
        '''
        return self._extended

    def set_extended(self, extended=True):
        '''
        Mark the attached interface to be extended

        Extended interface means the nodeparalist command (and friends) are available

        Args:
            extended (bool): True if the interface is extended
        '''
        self._extended = extended

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

    def bind_serial(self, port):
        '''
        Bind serial port: configure and open serial port at 115200 in 8N1 mode

        Args:
            port (str): Name of the serial port
        '''
        try:
            self._serial = Serial(port=port, baudrate=115200, timeout=0.1)
        except SerialException:
            logging.error('Could not open {port}, continuing in offline mode'.format(port=port))
        logging.info('Opened serial port {port}'.format(port=port))

    def bind_database(self, db):
        '''
        Bind to the database for logging sample data

        Args:
        - db (DucoDatabase): Database object to bind to
        '''
        self._database = db

    def store_sample(self, node, measurement, value):
        '''
        Store a sample in the database

        Args:
            node (DucoNode): Node for which to store the sample
            measurement (str): Parameter to store
            value (float): Scaled value to store in database
        '''
        if self._database:
            self._database.store_sample(node, measurement, value)

    def execute_command(self, command):
        '''
        Execute a command: send a command, and return the reply

        Args:
            command (str): Command to send to the serial port
        Returns:
            str: Received answer
        '''
        logging.debug('Serial command:\n{command}'.format(command=command))
        reply = ''
        if self._serial:
            self._serial.write('\r'.encode())
            time.sleep(SERIAL_CHAR_INTERVAL)
            self._serial.readline()
            cmd = command.encode('utf-8')
            for c in cmd:
                time.sleep(SERIAL_CHAR_INTERVAL)
                self._serial.write(c)
            time.sleep(SERIAL_CHAR_INTERVAL)
            self._serial.write('\r'.encode())
            reply = str(self._serial.readline()).replace('\r', '\n')
            logging.debug('Serial reply:\n{reply}'.format(reply=reply))
        else:
            logging.warning('No serial device')
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
        '''
        Take samples from all nodes in the network
        '''
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
                        help='Level for logging (error, warning, debug, info)')
    parser.add_argument('-i', '--interval', type=float, dest='interval', default=DEFAULT_INTERVAL,
                        action='store', required=False,
                        help='Level for logging (strings from logging python package)')
    parser.add_argument('-p', '--port', type=str, dest='port',
                        help='Serial port to connect to DucoInterface',
                        required=True, action='store',)
    parser.add_argument('-n', '--network', type=str, dest='network',
                        help='File where the network configuration is stored',
                        default='duco_network.ini', action='store',)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--influxdb', type=str, dest='influxdb',
                       help='Configuration file of the influxdb database to write to',
                       default=None, action='store',)
    args = parser.parse_args(args)

    set_logging_level(args.loglevel)

    itf = DucoInterface(port=args.port, cfgfile=args.network)

    if args.influxdb is not None:
        itf.bind_database(InfluxDb(args.influxdb))

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
