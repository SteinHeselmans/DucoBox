from unittest import TestCase
try:
    from unittest.mock import MagicMock, patch, call
except ImportError as err:
    from mock import MagicMock, patch, call

import duco.ducobox as dut


class TestDucoUserControlCO2SensorExtended(TestCase):

    node_paraget_cmd = 'nodeparaget {device} {para}'

    def nodeparaget_co2(self, device):
        return self.node_paraget_cmd.format(device=device, para=dut.CO2_PARAGET_ID)

    def nodeparaget_temperature(self, device):
        return self.node_paraget_cmd.format(device=device, para=dut.TEMPERATURE_PARAGET_ID)

    def callback_execute_cmd_nodeparaget(self, cmd):
        if cmd == self.nodeparaget_co2(1):
            with open('tests/cmd_paraget_co2.txt') as cmdfile:
                return cmdfile.read()
        elif cmd == self.nodeparaget_temperature(1):
            with open('tests/cmd_paraget_temperature.txt') as cmdfile:
                return cmdfile.read()
        elif cmd == self.nodeparaget_co2(255) or cmd == self.nodeparaget_temperature(255):
            with open('tests/cmd_paraget_failed.txt') as cmdfile:
                return cmdfile.read()
        self.fail('unknown nodeparaget command')
        return None

    @patch('duco.ducobox.DucoInterface', autospec=True)
    def test_happy(self, itf_mock):
        sensor = dut.DucoUserControlCO2Sensor(1, 2)
        itf_mock_object = MagicMock(spec=dut.DucoInterface)
        sensor.bind_serial(itf_mock_object)

        itf_mock_object.execute_command.side_effect = self.callback_execute_cmd_nodeparaget
        sensor.sample()
        co2_call = call(self.nodeparaget_co2(1))
        temperature_call = call(self.nodeparaget_temperature(1))
        itf_mock_object.execute_command.assert_has_calls([co2_call, temperature_call], any_order=True)

        self.assertEqual(sensor.get_value(dut.CO2_STR), 512)
        self.assertEqual(sensor.get_value(dut.TEMPERATURE_STR), 27.5)

    @patch('duco.ducobox.DucoInterface', autospec=True)
    def test_no_values(self, itf_mock):
        sensor = dut.DucoUserControlCO2Sensor(255, 2)
        itf_mock_object = MagicMock(spec=dut.DucoInterface)
        sensor.bind_serial(itf_mock_object)

        itf_mock_object.execute_command.side_effect = self.callback_execute_cmd_nodeparaget
        sensor.sample()
        co2_call = call(self.nodeparaget_co2(255))
        temperature_call = call(self.nodeparaget_temperature(255))
        itf_mock_object.execute_command.assert_has_calls([co2_call, temperature_call], any_order=True)

        self.assertEqual(sensor.get_value(dut.CO2_STR), None)
        self.assertEqual(sensor.get_value(dut.TEMPERATURE_STR), None)
