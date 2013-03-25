# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import unittest
import doctest
import ebaysdk
import os

def getTestSuite():
    suite = unittest.TestSuite()

    suite.addTest(doctest.DocTestSuite(ebaysdk))
    return suite

runner = unittest.TextTestRunner()
runner.run(getTestSuite())
