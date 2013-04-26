# -*- coding: utf-8 -*-
'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os
import sys
import json
from optparse import OptionParser

sys.path.insert(0, '%s/../' % os.path.dirname(__file__))

import ebaysdk
from ebaysdk import merchandising


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


def dump(api, full=False):

    print "\n"

    if api.warnings():
        print "Warnings" + api.warnings()

    if api.response_content():
        print "Call Success: %s in length" % len(api.response_content())

    print "Response code: %s" % api.response_code()
    print "Response DOM: %s" % api.response_dom()

    if full:
        print api.response_content()
        print(json.dumps(api.response_dict(), indent=2))
    else:
        dictstr = "%s" % api.response_dict()
        print "Response dictionary: %s..." % dictstr[:150]


def run(opts):
    api = merchandising(debug=opts.debug, appid=opts.appid, config_file=opts.yaml,
                        warnings=True)

    api.execute('getMostWatchedItems', {'maxResults': 3})

    if api.error():
        raise Exception(api.error())

    dump(api)


if __name__ == "__main__":
    (opts, args) = init_options()
    run(opts)
