
'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os, sys
from optparse import OptionParser

sys.path.insert(0, '%s/../' % os.path.dirname(__file__))

import ebaysdk
from ebaysdk import trading

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
    parser.add_option("-p", "--devid",
                      dest="devid", default=None,
                      help="Specifies the eBay developer id to use.")
    parser.add_option("-c", "--certid",
                      dest="certid", default=None,
                      help="Specifies the eBay cert id to use.")

    (opts, args) = parser.parse_args()
    return opts, args

def run(opts):
    api = trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                  certid=opts.certid, devid=opts.devid)

    api.execute('GetCharities', {'CharityID': 3897})

    # checkfor errors
    if api.error():
        raise Exception(api.error())

    print "Trading samples for SDK version %s" % ebaysdk.get_version()

    if api.response_content():
        print "Call Success: %s in length" % len(api.response_content())

    print "Response code: %s" % api.response_code()
    print "Response DOM: %s" % api.response_dom()

    dictstr = "%s" % api.response_dict()
    print "Response dictionary: %s..." % dictstr[:150]

    print api.response_dict().Charity.Name
    print api.response_content()

if __name__ == "__main__":
    (opts, args) = init_options()
    run(opts)
