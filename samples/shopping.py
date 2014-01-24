# -*- coding: utf-8 -*-
'''
© 2012-2013 eBay Software Foundation
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

from common import dump

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

    (opts, args) = parser.parse_args()
    return opts, args

def run(opts):
    api = Shopping(debug=opts.debug, appid=opts.appid, config_file=opts.yaml,
                   warnings=True)

    print("Shopping samples for SDK version %s" % ebaysdk.get_version())

    try:
        api.execute('FindPopularItems', {'QueryKeywords': 'Python'})

        if api.response_content():
            print("Call Success: %s in length" % len(api.response_content()))

        print("Response code: %s" % api.response_code())
        print("Response DOM: %s" % api.response_dom())

        dictstr = "%s" % api.response_dict()
        print("Response dictionary: %s..." % dictstr[:50])

        print("Matching Titles:")
        for item in api.response_dict().ItemArray.Item:
            print(item.Title)

    except ConnectionError as e:
        print e 


def popularSearches(opts):

    api = Shopping(debug=opts.debug, appid=opts.appid, config_file=opts.yaml,
                   warnings=True)


    choice = True

    while choice:

        choice = input('Search: ')

        if choice == 'quit':
            break

        mySearch = {
            # "CategoryID": " string ",
            # "IncludeChildCategories": " boolean ",
            "MaxKeywords": 10,
            "QueryKeywords": choice,
        }

        try:
            api.execute('FindPopularSearches', mySearch)

            #dump(api, full=True)

            print("Related: %s" % api.response_dict().PopularSearchResult.RelatedSearches)

            for term in api.response_dict().PopularSearchResult.AlternativeSearches.split(';')[:3]:
                api.execute('FindPopularItems', {'QueryKeywords': term, 'MaxEntries': 3})

                print("Term: %s" % term)

                try:
                    for item in api.response_dict().ItemArray.Item:
                        print(item.Title)
                except AttributeError:
                    pass

                # dump(api)

            print("\n")
        except ConnectionError as e:
            print e

def categoryInfo(opts):

    try:
        api = Shopping(debug=opts.debug, appid=opts.appid, config_file=opts.yaml,
                       warnings=True)

        api.execute('GetCategoryInfo', {"CategoryID": 3410})
        dump(api, full=False)
    
    except ConnectionError as e:
        print e

def with_affiliate_info(opts):
    try:
        api = Shopping(debug=opts.debug, appid=opts.appid,
                       config_file=opts.yaml, warnings=True,
                       trackingid=1234, trackingpartnercode=9)

        mySearch = {    
            "MaxKeywords": 10,
            "QueryKeywords": 'shirt',
        }

        api.execute('FindPopularSearches', mySearch)
        dump(api, full=True)

    except ConnectionError as e:
        print e

def using_attributes(opts):

    try:
        api = Shopping(debug=opts.debug, appid=opts.appid,
                       config_file=opts.yaml, warnings=True)

        api.execute('FindProducts', {
            "ProductID": {'@attrs': {'type': 'ISBN'}, 
                          '#text': '0596154488'}})

        dump(api, full=False)

    except ConnectionError as e:
        print e

if __name__ == "__main__":
    (opts, args) = init_options()
    run(opts)
    popularSearches(opts)
    categoryInfo(opts)
    with_affiliate_info(opts)
    using_attributes(opts)
