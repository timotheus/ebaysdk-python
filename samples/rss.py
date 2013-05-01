# -*- coding: utf-8 -*-
'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os
import sys
import smtplib
from optparse import OptionParser

sys.path.insert(0, '%s/../' % os.path.dirname(__file__))

from ebaysdk import html

def init_options():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug",
                      action="store_true", dest="debug", default=False,
                      help="Enabled debugging [default: %default]")

    (opts, args) = parser.parse_args()
    return opts, args


def dump(api, full=False):

    print "\n"

    if api.response_content():
        print "Response Content: %s in length" % len(api.response_content())

    print "Response code: %s" % api.response_code()
    #print "Response soup: %s" % api.response_soup()

    if full:
        print api.response_content()
        #print(json.dumps(api.response_dict(), indent=2))
    else:
        pass
        #dictstr = "%s" % api.response_dict()
        #print "Response dictionary: %s..." % dictstr[:150]

def run404(opts):
    api = html(debug=opts.debug)

    api.execute('http://feeds2.feedburner.com/feedburnerstatus')

    #if api.error():
    #    print Exception(api.error())

    dump(api)

    api.execute('http://feeds2.feedburner.com/feedburnerstatusd')

    if api.error():
        raise Exception(api.error())

    dump(api)
    
if __name__ == "__main__":
    (opts, args) = init_options()
    run404(opts)
