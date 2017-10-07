from unittest import TestCase
try:
    from unittest.mock import MagicMock, patch
except ImportError as err:
    from mock import MagicMock, patch

import duco.ducobox as dut


class TestDucoBoxHumiditySensor(TestCase):

    @patch('duco.ducobox.DucoInterface', autospec=True)
    def test_happy(self, itf_mock):
        sensor = dut.DucoBoxHumiditySensor(1, 2)
        itf_mock_object = MagicMock(spec=dut.DucoInterface)

        with open('tests/cmd_sensorinfo.txt') as cmdfile:
            itf_mock_object._execute.return_value = cmdfile.read().replace('\n', '\r')
        sensor.sample(itf_mock_object)
        itf_mock_object._execute.assert_called_once_with('sensorinfo\r')

        self.assertEqual(sensor.humidity, 68.37)
        self.assertEqual(sensor.temperature, 18.9)
