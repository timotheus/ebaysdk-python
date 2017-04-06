# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

from __future__ import absolute_import
import os
import unittest
import ebaysdk.shopping
import lxml

os.environ.setdefault("EBAY_YAML", "ebay.yaml")

class TestErrors(unittest.TestCase):

    def test_single_item(self):
        connection = ebaysdk.shopping.Connection(debug=True, version='799')

        for i in range(20):
            connection.execute('GetSingleItem', {
                'ItemID': '262809803926',
                'version': '981',
                'IncludeSelector': ['Variations']
            })
            self.assertEqual(connection.response.status_code, 200)
            self.assertEqual(type(connection.response.dom()), lxml.etree._Element)

if __name__ == '__main__':
    unittest.main()
