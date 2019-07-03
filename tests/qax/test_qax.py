import unittest

from hyo2.qax import __author__, __version__


class TestQAX(unittest.TestCase):

    def test_author(self):
        self.assertGreaterEqual(len(__author__.split(";")), 2)

    def test_version(self):
        self.assertGreaterEqual(int(__version__.split(".")[0]), 1)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestQAX))
    return s
