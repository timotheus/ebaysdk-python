# -*- coding: utf-8 -*-
'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os
import sys
from optparse import OptionParser

sys.path.insert(0, '%s/../' % os.path.dirname(__file__))

from ebaysdk import finding, html, parallel


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

    p = parallel()
    apis = []

    api1 = finding(parallel=p, debug=opts.debug, appid=opts.appid, config_file=opts.yaml)
    api1.execute('findItemsAdvanced', {'keywords': 'python'})
    apis.append(api1)

    api4 = html(parallel=p)
    api4.execute('http://www.ebay.com/sch/i.html?_nkw=Shirt&_rss=1')
    apis.append(api4)

    api2 = finding(parallel=p, debug=opts.debug, appid=opts.appid, config_file=opts.yaml)
    api2.execute('findItemsAdvanced', {'keywords': 'perl'})
    apis.append(api2)

    api3 = finding(parallel=p, debug=opts.debug, appid=opts.appid, config_file=opts.yaml)
    api3.execute('findItemsAdvanced', {'keywords': 'php'})
    apis.append(api3)

    p.wait()

    if p.error():
        raise Exception(p.error())

    for api in apis:

        print("Call Success: %s in length" % len(api.response_content()))

        print("Response code: %s" % api.response_code())
        print("Response DOM: %s" % api.response_dom())

        dictstr = "%s" % api.response_dict()
        print("Response dictionary: %s...\n" % dictstr[:50])

if __name__ == "__main__":
    (opts, args) = init_options()
    run(opts)
