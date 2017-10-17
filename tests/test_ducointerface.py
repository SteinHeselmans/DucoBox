from unittest import TestCase
try:
    from unittest.mock import MagicMock, patch, mock_open
except ImportError as err:
    from mock import MagicMock, patch, mock_open

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

    def test_store_no_file(self):
        itf = dut.DucoInterface(self.MOCK_PORT_NAME)
        itf.store()

    def test_store_invalid_file(self):
        open_mock = mock_open()
        itf = dut.DucoInterface(self.MOCK_PORT_NAME, self.MOCK_CFG_FILE)
        with patch('duco.ducobox.open', open_mock, create=True):
            itf.store()
        open_mock.assert_called_once_with(self.MOCK_CFG_FILE, 'w')

    def test_store_no_nodes(self):
        open_mock = mock_open()
        itf = dut.DucoInterface(self.MOCK_PORT_NAME, self.MOCK_CFG_FILE)
        with patch('duco.ducobox.open', open_mock, create=True):
            itf.store()
        open_mock.assert_called_once_with(self.MOCK_CFG_FILE, 'w')

    @patch('duco.ducobox.ConfigParser', autospec=True)
    def test_store_single_node(self, cfgparser_mock):
        cfgparser_mock_object = MagicMock(spec=dut.ConfigParser)
        cfgparser_mock.return_value = cfgparser_mock_object
        print(cfgparser_mock_object)
        open_mock = mock_open()
        itf = dut.DucoInterface(self.MOCK_PORT_NAME, self.MOCK_CFG_FILE)
        node = dut.DucoNode('11', '22', itf)
        itf.nodes.append(node)
        with patch('duco.ducobox.open', open_mock, create=True):
            itf.store()
        open_mock.assert_called_once_with(self.MOCK_CFG_FILE, 'w')
        # cfgparser_mock_object.add_section.assert_called_once()
        # cfgparser_mock_object.write.assert_called_once()
