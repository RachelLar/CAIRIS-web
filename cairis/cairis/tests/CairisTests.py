import unittest
import cairisd

__author__ = 'Robin Quetin'


class CairisTests(unittest.TestCase):
    app = cairisd.start(['-d', '--unit-test'])