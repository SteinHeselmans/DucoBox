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

        with open('tests/cmd_fanspeed.txt') as cmdfile:
            itf_mock_object._execute.return_value = cmdfile.read().replace('\n', '\r')
        box.sample(itf_mock_object)
        itf_mock_object._execute.assert_called_once_with('fanspeed\r')

        self.assertEqual(box.fanspeed, 1449)
