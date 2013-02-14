import os, sys
from optparse import OptionParser

sys.path.insert(0, '%s/../' % os.path.dirname(__file__))

import ebaysdk
from ebaysdk import shopping

usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)

parser.add_option("-d", "--debug",
    			  action="store_true", dest="debug", default=False,
				  help="Enabled debugging [default: %default]")
parser.add_option("-y", "--yaml",#
                  dest="yaml", default='ebay.yaml',
	              help="Specifies the name of the YAML defaults file. [default: %default]")
parser.add_option("-a", "--appid",
	              dest="appid", default=None,
	              help="Specifies the eBay application id to use.")

(opts, args) = parser.parse_args()

api = shopping(debug=opts.debug, appid=opts.appid, config_file=opts.yaml) 
api.execute('FindPopularItems', {'QueryKeywords': 'Python'})

print "Shopping samples for SDK version %s" % ebaysdk.get_version()

if api.error():
	raise Exception(api.error())

if api.response_content():
	print "Call Success: %s in length" % len(api.response_content())

print "Response code: %s" % api.response_code()
print "Response DOM: %s" % api.response_dom()

dictstr = "%s" % api.response_dict()
print "Response dictionary: %s..." % dictstr[:50]

print "Matching Titles:"
for item in api.response_dict().ItemArray.Item:
	print item.Title
