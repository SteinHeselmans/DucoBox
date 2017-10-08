from unittest import TestCase

from duco.ducobox import ducobox_wrapper


class TestIntegration(TestCase):

    def test_help(self):
        with self.assertRaises(SystemExit) as ex:
            ducobox_wrapper(['--help'])
        self.assertEqual(0, ex.exception.code)

    def test_version(self):
        with self.assertRaises(SystemExit) as ex:
            ducobox_wrapper(['--version'])
        self.assertEqual(0, ex.exception.code)

    def test_no_port(self):
        with self.assertRaises(SystemExit) as ex:
            ducobox_wrapper([])
        self.assertEqual(2, ex.exception.code)

    def test_invalid_loglevel(self):
        with self.assertRaises(ValueError):
            ducobox_wrapper(['--port', '/dev/null', '--loglevel', 'invalid'])

    def test_invalid_interval(self):
        with self.assertRaises(SystemExit) as ex:
            ducobox_wrapper(['--port', '/dev/null', '--interval', 'invalid'])
        self.assertEqual(2, ex.exception.code)
