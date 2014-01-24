# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import unittest
import doctest
import ebaysdk2.utils
import ebaysdk2.config
import ebaysdk2.connection
import ebaysdk2.finding
import ebaysdk2.shopping
import ebaysdk2.trading
import ebaysdk2.merchandising
import ebaysdk2.soa.finditem

def getTestSuite():
    suite = unittest.TestSuite()

    suite.addTest(doctest.DocTestSuite(ebaysdk2.connection))
    suite.addTest(doctest.DocTestSuite(ebaysdk2.config))
    suite.addTest(doctest.DocTestSuite(ebaysdk2.utils))
    suite.addTest(doctest.DocTestSuite(ebaysdk2.finding))
    suite.addTest(doctest.DocTestSuite(ebaysdk2.shopping))
    suite.addTest(doctest.DocTestSuite(ebaysdk2.trading))
    suite.addTest(doctest.DocTestSuite(ebaysdk2.merchandising))
    suite.addTest(doctest.DocTestSuite(ebaysdk2.soa.finditem))
    return suite

runner = unittest.TextTestRunner()
runner.run(getTestSuite())
