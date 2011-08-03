import unittest
import doctest
import sys
import os

sys.path.append('.')
import ebaysdk

def runtests():
   unittest.main()
   
class Test(unittest.TestCase):
    """Unit tests for ebaysdk."""

    def test_doctests(self):
        """Run ebaysdk doctests"""
        #doctest.testmod(ebaysdk)

if __name__ == "__main__":
    unittest.main()


