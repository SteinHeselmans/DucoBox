from unittest import TestCase
try:
    from unittest.mock import MagicMock, patch
except ImportError as err:
    from mock import MagicMock, patch

import duco.ducobox as dut


class TestDucoBox(TestCase):

    @patch('duco.ducobox.DucoInterface', autospec=True)
    def test_happy(self, itf_mock):
        box = dut.DucoBox(1, 2)
        itf_mock_object = MagicMock(spec=dut.DucoInterface)
        box.bind_serial(itf_mock_object)

        with open('tests/cmd_fanspeed.txt') as cmdfile:
            itf_mock_object.execute_command.return_value = cmdfile.read()
        box.sample()
        itf_mock_object.execute_command.assert_called_once_with('fanspeed')

        self.assertEqual(int(box.parameters[dut.FANSPEED_STR].get_value()), 1449)

    @patch('duco.ducobox.DucoInterface', autospec=True)
    def test_no_values(self, itf_mock):
        box = dut.DucoBox(1, 2)
        itf_mock_object = MagicMock(spec=dut.DucoInterface)
        box.bind_serial(itf_mock_object)

        itf_mock_object.execute_command.return_value = 'invalid command'
        box.sample()
        itf_mock_object.execute_command.assert_called_once_with('fanspeed')

        self.assertEqual(box.parameters[dut.FANSPEED_STR].get_value(), None)
