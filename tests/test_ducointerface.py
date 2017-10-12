from unittest import TestCase
try:
    from unittest.mock import MagicMock, patch
except ImportError as err:
    from mock import MagicMock, patch

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser
from serial import Serial
import duco.ducobox as dut


class TestDucoInterface(TestCase):

    MOCK_PORT_NAME = '/dev/my/mocked_serial_port'
    MOCK_CFG_FILE = '/tmp/my/mocked_config_file'

    @staticmethod
    def duco_encoded(c):
        return c.encode('utf-8')

    @patch('duco.ducobox.Serial', autospec=True)
    def test_network_happy(self, serial_mock):
        serial_mock_object = MagicMock(spec=Serial)
        serial_mock.return_value = serial_mock_object
        itf = dut.DucoInterface(self.MOCK_PORT_NAME)

        self.assertFalse(itf.is_online())

        with open('tests/cmd_network.txt') as cmdfile:
            serial_mock_object.readline.return_value = cmdfile.read().replace('\n', '\r')
        itf.find_nodes()
        # TODO: enable assert when write of command is a single API call again
        # serial_mock_object.write.assert_called_once_with(self.duco_encoded('network'))

        self.assertTrue(itf.is_online())

        node = itf.get_node('1')
        self.assertIsInstance(node, dut.DucoBox)
        self.assertEqual(node.number, '1')
        self.assertEqual(node.address, '1')

        node = itf.get_node('102')
        self.assertIsInstance(node, dut.DucoUserControl)
        self.assertEqual(node.number, '2')
        self.assertEqual(node.address, '102')

        node = itf.get_node('132')
        self.assertIsInstance(node, dut.DucoBoxHumiditySensor)
        self.assertEqual(node.number, '34')
        self.assertEqual(node.address, '132')

        node = itf.get_node('142')
        self.assertIsInstance(node, dut.DucoBoxCO2Sensor)
        self.assertEqual(node.number, '44')
        self.assertEqual(node.address, '142')

        node = itf.get_node('999')
        self.assertIsInstance(node, dut.DucoNode)
        self.assertEqual(node.number, '99')
        self.assertEqual(node.address, '999')

    @patch('duco.ducobox.ConfigParser', autospec=True)
    def test_store_no_file(self, cfgparser_mock):
        cfgparser_mock_object = MagicMock(spec=ConfigParser)
        cfgparser_mock.return_value = cfgparser_mock_object
        itf = dut.DucoInterface(self.MOCK_PORT_NAME)

        itf.store()

    @patch('duco.ducobox.ConfigParser', autospec=True)
    def test_store_invalid_file(self, cfgparser_mock):
        cfgparser_mock_object = MagicMock(spec=ConfigParser)
        cfgparser_mock.return_value = cfgparser_mock_object
        itf = dut.DucoInterface(self.MOCK_PORT_NAME, self.MOCK_CFG_FILE)

        # TODO: mock the file open to fail

        itf.store()

    @patch('duco.ducobox.ConfigParser', autospec=True)
    def test_store_no_nodes(self, cfgparser_mock):
        cfgparser_mock_object = MagicMock(spec=ConfigParser)
        cfgparser_mock.return_value = cfgparser_mock_object
        itf = dut.DucoInterface(self.MOCK_PORT_NAME, self.MOCK_CFG_FILE)

        # TODO: mock the file open to pass

        itf.store()
