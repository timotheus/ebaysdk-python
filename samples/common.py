# -*- coding: utf-8 -*-
'''
Copyright 2012-2019 eBay Inc.
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

from ebaysdk.finding import Connection as finding

def get_one_item(opts):
    api = finding(debug=opts.debug, appid=opts.appid,
                  config_file=opts.yaml, warnings=True)

    api_request = {
        'keywords': u'GRAMMY Foundation®',
    }

    response = api.execute('findItemsAdvanced', api_request)
    return response.reply.searchResult.item[0].itemId


def dump(api, full=False):

    print("\n")

    if api.warnings():
        print("Warnings" + api.warnings())

    if api.response.content:
        print("Call Success: %s in length" % len(api.response.content))

    print("Response code: %s" % api.response_code())
    print("Response DOM1: %s" % api.response.dom())  # deprecated
    print("Response ETREE: %s" % api.response.dom())

    if full:
        print(api.response.content)
        print(api.response.json())
        print("Response Reply: %s" % api.response.reply)
    else:
        dictstr = "%s" % api.response.dict()
        print("Response dictionary: %s..." % dictstr[:150])
        replystr = "%s" % api.response.reply
        print("Response Reply: %s" % replystr[:150])
