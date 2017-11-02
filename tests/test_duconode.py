from unittest import TestCase
try:
    from unittest.mock import MagicMock, patch
except ImportError as err:
    from mock import MagicMock, patch

try:
    from configparser import NoSectionError, NoOptionError
except ImportError:
    from ConfigParser import NoSectionError, NoOptionError

import duco.ducobox as dut


class TestDucoNode(TestCase):

    def test_creation_int(self):
        node = dut.DucoNode(333, 444)
        self.assertEqual(int(node.number), 333)
        self.assertEqual(int(node.address), 444)
        self.assertIsNotNone(node.name)

    def test_creation_str(self):
        node = dut.DucoNode('333', '444')
        self.assertEqual(int(node.number), 333)
        self.assertEqual(int(node.address), 444)

    def test_creation_float(self):
        node = dut.DucoNode(333.0, 444.0)
        self.assertEqual(int(float(node.number)), 333)
        self.assertEqual(int(float(node.address)), 444)

    def test_equality(self):
        node1 = dut.DucoNode(333, 444)
        node2 = dut.DucoNode(222, 444)
        self.assertEqual(node1, node2)

    def test_no_equality(self):
        node1 = dut.DucoNode(333, 444)
        node2 = dut.DucoNode(222, 445)
        self.assertNotEqual(node1, node2)

    @patch('duco.ducobox.ConfigParser', autospec=True)
    def test_store(self, cfgparser_mock):
        node = dut.DucoNode(111, 222)
        cfgparser_mock_object = MagicMock(spec=dut.ConfigParser)
        node._store(cfgparser_mock_object)
        section = 'Node111'
        cfgparser_mock_object.add_section.assert_called_once_with(section)
        cfgparser_mock_object.set.assert_any_call(section, 'number', '111')
        cfgparser_mock_object.set.assert_any_call(section, 'address', '222')
        cfgparser_mock_object.set.assert_any_call(section, 'blacklist', False)

    def load_test_side_effect(*args, **kwargs):
        if args[2] == 'name':
            return 'mocked device for utest'
        elif args[2] == 'number':
            return '888'
        elif args[2] == 'address':
            return '666'
        elif args[2] == 'blacklist':
            return True
        raise Exception('ConfigParser with unexpected argument')

    @patch('duco.ducobox.ConfigParser', autospec=True)
    def test_load(self, cfgparser_mock):
        node = dut.DucoNode(111, 222)
        cfgparser_mock_object = MagicMock(spec=dut.ConfigParser)
        cfgparser_mock_object.get.side_effect = self.load_test_side_effect
        cfgparser_mock_object.getboolean.side_effect = self.load_test_side_effect
        node._load(cfgparser_mock_object)
        self.assertEqual(node.name, 'mocked device for utest')
        self.assertEqual(int(node.number), 888)
        self.assertEqual(int(node.address), 666)
        self.assertEqual(node.blacklist, True)

    @patch('duco.ducobox.ConfigParser', autospec=True)
    def test_load_fail_no_section(self, cfgparser_mock):
        node = dut.DucoNode(111, 222)
        cfgparser_mock_object = MagicMock(spec=dut.ConfigParser)
        cfgparser_mock_object.get.side_effect = NoSectionError('some message for missing config parser section')
        node._load(cfgparser_mock_object)
        self.assertEqual(int(node.number), 111)
        self.assertEqual(int(node.address), 222)
        self.assertEqual(node.blacklist, False)

    @patch('duco.ducobox.ConfigParser', autospec=True)
    def test_load_fail_no_option(self, cfgparser_mock):
        node = dut.DucoNode(111, 222)
        cfgparser_mock_object = MagicMock(spec=dut.ConfigParser)
        cfgparser_mock_object.get.side_effect = NoOptionError('blacklist', 'some message for missing config parser option')
        node._load(cfgparser_mock_object)
        self.assertEqual(int(node.number), 111)
        self.assertEqual(int(node.address), 222)
        self.assertEqual(node.blacklist, False)

    def test_sample(self):
        node = dut.DucoNode(111, 222)
        node.sample()
        self.assertEqual(node.get_value(dut.HUMIDITY_STR), None)
        self.assertEqual(node.get_value(dut.CO2_STR), None)
        self.assertEqual(node.get_value(dut.TEMPERATURE_STR), None)

    def test_stringify(self):
        node = dut.DucoNode(111, 222)
        self.assertTrue('111' in str(node))
        self.assertTrue('222' in str(node))
