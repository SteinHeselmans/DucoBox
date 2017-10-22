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
    def test_network_simple(self, serial_mock):
        serial_mock_object = MagicMock(spec=Serial)
        serial_mock.return_value = serial_mock_object
        itf = dut.DucoInterface(self.MOCK_PORT_NAME)

        self.assertFalse(itf.is_online())

        with open('tests/cmd_network_simple.txt') as cmdfile:
            serial_mock_object.readline.return_value = cmdfile.read().replace('\n', '\r')
        itf.find_nodes()
        # TODO: enable assert when write of command is a single API call again
        # serial_mock_object.write.assert_called_once_with(self.duco_encoded('network'))

        self.assertTrue(itf.is_online())

        node = itf.get_node('1')
        self.assertIsInstance(node, dut.DucoBox)
        self.assertEqual(node.number, '1')
        self.assertEqual(node.address, '1')

        node = itf.get_node('2')
        self.assertIsInstance(node, dut.DucoUserControlBattery)
        self.assertEqual(node.number, '2')
        self.assertEqual(node.address, '102')

        node = itf.get_node('34')
        self.assertIsInstance(node, dut.DucoUserControlHumiditySensor)
        self.assertEqual(node.number, '34')
        self.assertEqual(node.address, '132')

        node = itf.get_node('44')
        self.assertIsInstance(node, dut.DucoUserControlCO2Sensor)
        self.assertEqual(node.number, '44')
        self.assertEqual(node.address, '142')

        node = itf.get_node('99')
        self.assertIsInstance(node, dut.DucoNode)
        self.assertEqual(node.number, '99')
        self.assertEqual(node.address, '999')

        node = itf.get_node('1234')
        self.assertIsNone(node)

    @patch('duco.ducobox.Serial', autospec=True)
    def test_network_complex(self, serial_mock):
        serial_mock_object = MagicMock(spec=Serial)
        serial_mock.return_value = serial_mock_object
        itf = dut.DucoInterface(self.MOCK_PORT_NAME)

        self.assertFalse(itf.is_online())

        with open('tests/cmd_network_complex.txt') as cmdfile:
            serial_mock_object.readline.return_value = cmdfile.read().replace('\n', '\r')
        itf.find_nodes()
        # TODO: enable assert when write of command is a single API call again
        # serial_mock_object.write.assert_called_once_with(self.duco_encoded('network'))

        self.assertTrue(itf.is_online())

        node = itf.get_node('1')
        self.assertIsInstance(node, dut.DucoBox)
        self.assertEqual(node.number, '1')
        self.assertEqual(node.address, '1')

        node = itf.get_node('2')
        self.assertIsInstance(node, dut.DucoValveHumiditySensor)
        self.assertEqual(node.number, '2')
        self.assertEqual(node.address, '2')

        node = itf.get_node('3')
        self.assertIsInstance(node, dut.DucoValve)
        self.assertEqual(node.number, '3')
        self.assertEqual(node.address, '3')

        node = itf.get_node('4')
        self.assertIsInstance(node, dut.DucoValveHumiditySensor)
        self.assertEqual(node.number, '4')
        self.assertEqual(node.address, '4')

        node = itf.get_node('5')
        self.assertIsInstance(node, dut.DucoValve)
        self.assertEqual(node.number, '5')
        self.assertEqual(node.address, '5')

        node = itf.get_node('6')
        self.assertIsInstance(node, dut.DucoValveCO2Sensor)
        self.assertEqual(node.number, '6')
        self.assertEqual(node.address, '6')

        node = itf.get_node('7')
        self.assertIsInstance(node, dut.DucoValve)
        self.assertEqual(node.number, '7')
        self.assertEqual(node.address, '7')

        node = itf.get_node('8')
        self.assertIsInstance(node, dut.DucoValveHumiditySensor)
        self.assertEqual(node.number, '8')
        self.assertEqual(node.address, '8')

        node = itf.get_node('9')
        self.assertIsInstance(node, dut.DucoUserControlHumiditySensor)
        self.assertEqual(node.number, '9')
        self.assertEqual(node.address, '102')

        node = itf.get_node('10')
        self.assertIsInstance(node, dut.DucoUserControlCO2Sensor)
        self.assertEqual(node.number, '10')
        self.assertEqual(node.address, '103')

        node = itf.get_node('11')
        self.assertIsInstance(node, dut.DucoSwitch)
        self.assertEqual(node.number, '11')
        self.assertEqual(node.address, '104')

        node = itf.get_node('12')
        self.assertIsInstance(node, dut.DucoUserControlHumiditySensor)
        self.assertEqual(node.number, '12')
        self.assertEqual(node.address, '105')

        node = itf.get_node('13')
        self.assertIsInstance(node, dut.DucoUserControlCO2Sensor)
        self.assertEqual(node.number, '13')
        self.assertEqual(node.address, '106')

        node = itf.get_node('14')
        self.assertIsInstance(node, dut.DucoUserControlCO2Sensor)
        self.assertEqual(node.number, '14')
        self.assertEqual(node.address, '107')

        node = itf.get_node('15')
        self.assertIsInstance(node, dut.DucoSwitch)
        self.assertEqual(node.number, '15')
        self.assertEqual(node.address, '108')

        node = itf.get_node('16')
        self.assertIsInstance(node, dut.DucoUserControlCO2Sensor)
        self.assertEqual(node.number, '16')
        self.assertEqual(node.address, '109')

        node = itf.get_node('17')
        self.assertIsInstance(node, dut.DucoGrille)
        self.assertEqual(node.number, '17')
        self.assertEqual(node.address, '110')

        node = itf.get_node('18')
        self.assertIsInstance(node, dut.DucoUserControl)
        self.assertEqual(node.number, '18')
        self.assertEqual(node.address, '111')

        node = itf.get_node('19')
        self.assertIsInstance(node, dut.DucoGrille)
        self.assertEqual(node.number, '19')
        self.assertEqual(node.address, '112')

        node = itf.get_node('20')
        self.assertIsInstance(node, dut.DucoGrille)
        self.assertEqual(node.number, '20')
        self.assertEqual(node.address, '113')

        node = itf.get_node('133')
        self.assertIsInstance(node, dut.DucoSwitch)
        self.assertEqual(node.number, '133')
        self.assertEqual(node.address, '132')

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
