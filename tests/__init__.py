import unittest
import doctest
import ebaysdk

def getTestSuite():
    suite = unittest.TestSuite()
 
    suite.addTest(doctest.DocTestSuite(ebaysdk))
    return suite

runner = unittest.TextTestRunner()
runner.run(getTestSuite())
