from unittest import TestCase
try:
    from unittest.mock import MagicMock, patch
except ImportError as err:
    from mock import MagicMock, patch

from serial import Serial
import duco.ducobox as dut


class TestDucoBox(TestCase):

    MOCK_PORT_NAME = '/dev/my/mocked_serial_port'

    @staticmethod
    def duco_encoded(c):
        return c.encode('utf-8')

    @patch('duco.ducobox.Serial', autospec=True)
    def test_ducobox(self, serial_mock):
        serial_mock_object = MagicMock(spec=Serial)
        serial_mock.return_value = serial_mock_object
        box = dut.DucoBox(self.MOCK_PORT_NAME)

        with open('tests/cmd_network.txt') as cmdfile:
            serial_mock_object.readline.return_value = cmdfile.read()
        nodes = box.get_nodes()
        serial_mock_object.write.assert_called_once_with(self.duco_encoded('network'))
        self.assertEqual(nodes[0].number, '1')
        self.assertEqual(nodes[0].address, '1')
        self.assertEqual(nodes[1].number, '2')
        self.assertEqual(nodes[1].address, '102')
        self.assertEqual(nodes[2].number, '34')
        self.assertEqual(nodes[2].address, '132')
