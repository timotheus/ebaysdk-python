# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import sys
import unittest
import doctest
import ebaysdk.utils
import ebaysdk.config
import ebaysdk.response
import ebaysdk.connection
import ebaysdk.http
import ebaysdk.shopping
import ebaysdk.trading
import ebaysdk.merchandising
import ebaysdk.soa.finditem
import ebaysdk.finding

# does not pass with python3.3
try:
    import ebaysdk.parallel
except ImportError:
    pass

def getTestSuite():
    suite = unittest.TestSuite()

    suite.addTest(doctest.DocTestSuite(ebaysdk.utils))
    suite.addTest(doctest.DocTestSuite(ebaysdk.config))
    suite.addTest(doctest.DocTestSuite(ebaysdk.response))
    suite.addTest(doctest.DocTestSuite(ebaysdk.connection))
    suite.addTest(doctest.DocTestSuite(ebaysdk.http))
    suite.addTest(doctest.DocTestSuite(ebaysdk.shopping))
    suite.addTest(doctest.DocTestSuite(ebaysdk.trading))
    suite.addTest(doctest.DocTestSuite(ebaysdk.merchandising))
    suite.addTest(doctest.DocTestSuite(ebaysdk.finding))

    if not sys.version_info[0] >= 3 \
        and sys.modules.has_key('grequests') is True:

        suite.addTest(doctest.DocTestSuite(ebaysdk.parallel))    
    
    
    # inside only
    #suite.addTest(doctest.DocTestSuite(ebaysdk.soa.finditem))
    
    return suite

runner = unittest.TextTestRunner()
runner.run(getTestSuite())

