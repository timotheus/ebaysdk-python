# -*- coding: utf-8 -*-
'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import json

def dump(api, full=False):

    print("\n")

    if api.warnings():
        print("Warnings" + api.warnings())

    if api.response_content():
        print("Call Success: %s in length" % len(api.response_content()))

    print("Response code: %s" % api.response_code())
    print("Response DOM: %s" % api.response_dom())

    if full:
        print(api.response_content())
        print((json.dumps(api.response_dict(), indent=2)))
    else:
        dictstr = "%s" % api.response_dict()
        print("Response dictionary: %s..." % dictstr[:150])
