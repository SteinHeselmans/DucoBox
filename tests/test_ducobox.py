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
        box.bind(itf_mock_object)

        with open('tests/cmd_fanspeed.txt') as cmdfile:
            itf_mock_object.execute_command.return_value = cmdfile.read()
        box.sample()
        itf_mock_object.execute_command.assert_called_once_with('fanspeed')

        self.assertEqual(box.fanspeed, 1449)
