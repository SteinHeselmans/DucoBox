from unittest import TestCase
try:
    from unittest.mock import MagicMock, patch
except ImportError as err:
    from mock import MagicMock, patch

import duco.ducobox as dut


class TestDucoUserControlBoxHumiditySensor(TestCase):

    @patch('duco.ducobox.DucoInterface', autospec=True)
    def test_happy(self, itf_mock):
        sensor = dut.DucoUserControlHumiditySensor(1, 2)
        itf_mock_object = MagicMock(spec=dut.DucoInterface)
        sensor.bind(itf_mock_object)

        with open('tests/cmd_sensorinfo.txt') as cmdfile:
            itf_mock_object.execute_command.return_value = cmdfile.read()
        sensor.sample()
        itf_mock_object.execute_command.assert_called_once_with('sensorinfo')

        self.assertEqual(float(sensor.humidity), 68.37)
        self.assertEqual(float(sensor.temperature), 18.9)

    @patch('duco.ducobox.DucoInterface', autospec=True)
    def test_no_values(self, itf_mock):
        sensor = dut.DucoUserControlHumiditySensor(1, 2)
        itf_mock_object = MagicMock(spec=dut.DucoInterface)
        sensor.bind(itf_mock_object)

        itf_mock_object.execute_command.return_value = 'invalid command'
        sensor.sample()
        itf_mock_object.execute_command.assert_called_once_with('sensorinfo')

        self.assertEqual(sensor.humidity, None)
        self.assertEqual(sensor.temperature, None)
