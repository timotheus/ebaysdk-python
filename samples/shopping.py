# -*- coding: utf-8 -*-
'''
Copyright 2012-2019 eBay Inc.
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os
import sys
from optparse import OptionParser

try:
    input = raw_input
except NameError:
    pass

sys.path.insert(0, '%s/../' % os.path.dirname(__file__))

from common import dump, get_one_item

import ebaysdk
from ebaysdk.exception import ConnectionError
from ebaysdk.shopping import Connection as Shopping


def init_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="Enabled debugging [default: %default]")
    parser.add_option("-y", "--yaml",
                      dest="yaml", default='ebay.yaml',
                      help="Specifies the name of the YAML defaults file. [default: %default]")
    parser.add_option("-a", "--appid",
                      dest="appid", default=None,
                      help="Specifies the eBay application id to use.")
    parser.add_option("-n", "--domain",
                      dest="domain", default='open.api.ebay.com',
                      help="Specifies the eBay domain to use (e.g. open.api.ebay.com).")

    (opts, args) = parser.parse_args()
    return opts, args


def run(opts):
    api = Shopping(debug=opts.debug, appid=opts.appid, config_file=opts.yaml, domain=opts.domain,
                   warnings=True)

    print("Shopping samples for SDK version %s" % ebaysdk.get_version())

    try:
        ItemID = get_one_item(opts)

        response = api.execute('GetSingleItem', {'ItemID': ItemID})
        print("EndTime: %s" % response.reply.Item.EndTime)

        dump(api)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def popularSearches(opts):

    api = Shopping(debug=opts.debug, appid=opts.appid, config_file=opts.yaml, domain=opts.domain,
                   warnings=True)

    mySearch = {
        "MaxKeywords": 10,
        "QueryKeywords": 'shirt',
    }

    try:
        response = api.execute('FindPopularSearches', mySearch)

        dump(api, full=False)

        print("Related: %s" %
              response.reply.PopularSearchResult.RelatedSearches)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def categoryInfo(opts):

    try:
        api = Shopping(debug=opts.debug, appid=opts.appid, config_file=opts.yaml, domain=opts.domain,
                       warnings=True)

        response = api.execute('GetCategoryInfo', {"CategoryID": 11450})

        print("Category Name: %s" %
              response.reply.CategoryArray.Category[0].CategoryName)

        dump(api)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())


def using_attributes(opts):

    try:
        api = Shopping(debug=opts.debug, appid=opts.appid,
                       config_file=opts.yaml, warnings=True)

        response = api.execute('FindProducts', {
            "ProductID": {'@attrs': {'type': 'ISBN'},
                          '#text': '0596154488'}})

        dump(api, full=False)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())

if __name__ == "__main__":
    (opts, args) = init_options()
    run(opts)
    popularSearches(opts)
    categoryInfo(opts)
    using_attributes(opts)
