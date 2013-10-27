# -*- coding: utf-8 -*-
'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os
import sys
import datetime
import json
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


def run(opts):
    api = trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                  certid=opts.certid, devid=opts.devid)

    api.execute('GetCharities', {'CharityID': 3897})

    if api.error():
        raise Exception(api.error())

    dump(api)

    print(api.response_dict().Charity.Name)


def feedback(opts):
    api = trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                  certid=opts.certid, devid=opts.devid, warnings=False)

    api.execute('GetFeedback', {'UserID': 'tim0th3us'})

    if api.error():
        raise Exception(api.error())

    dump(api)

    if int(api.response_dict().FeedbackScore) > 50:
        print("Doing good!")
    else:
        print("Sell more, buy more..")


def getTokenStatus(opts):
    api = trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                  certid=opts.certid, devid=opts.devid, warnings=False)

    api.execute('GetTokenStatus')

    if api.error():
        raise Exception(api.error())

    dump(api)


def verifyAddItem(opts):
    """http://www.utilities-online.info/xmltojson/#.UXli2it4avc
    """

    api = trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                  certid=opts.certid, devid=opts.devid, warnings=False)

    myitem = {
        "Item": {
            "Title": "Harry Potter and the Philosopher's Stone",
            "Description": "This is the first book in the Harry Potter series. In excellent condition!",
            "PrimaryCategory": {"CategoryID": "377"},
            "StartPrice": "1.0",
            "CategoryMappingAllowed": "true",
            "Country": "US",
            "ConditionID": "3000",
            "Currency": "USD",
            "DispatchTimeMax": "3",
            "ListingDuration": "Days_7",
            "ListingType": "Chinese",
            "PaymentMethods": "PayPal",
            "PayPalEmailAddress": "tkeefdddder@gmail.com",
            "PictureDetails": {"PictureURL": "http://i1.sandbox.ebayimg.com/03/i/00/30/07/20_1.JPG?set_id=8800005007"},
            "PostalCode": "95125",
            "Quantity": "1",
            "ReturnPolicy": {
                "ReturnsAcceptedOption": "ReturnsAccepted",
                "RefundOption": "MoneyBack",
                "ReturnsWithinOption": "Days_30",
                "Description": "If you are not satisfied, return the book for refund.",
                "ShippingCostPaidByOption": "Buyer"
            },
            "ShippingDetails": {
                "ShippingType": "Flat",
                "ShippingServiceOptions": {
                    "ShippingServicePriority": "1",
                    "ShippingService": "USPSMedia",
                    "ShippingServiceCost": "2.50"
                }
            },
            "Site": "US"
        }
    }

    api.execute('VerifyAddItem', myitem)

    if api.error():
        raise Exception(api.error())

    dump(api)


def verifyAddItemErrorCodes(opts):
    """http://www.utilities-online.info/xmltojson/#.UXli2it4avc
    """

    api = trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                  certid=opts.certid, devid=opts.devid, warnings=False)

    myitem = {
        "Item": {
            "Title": "Harry Potter and the Philosopher's Stone",
            "Description": "This is the first book in the Harry Potter series. In excellent condition!",
            "PrimaryCategory": {"CategoryID": "377aaaaaa"},
            "StartPrice": "1.0",
            "CategoryMappingAllowed": "true",
            "Country": "US",
            "ConditionID": "3000",
            "Currency": "USD",
            "DispatchTimeMax": "3",
            "ListingDuration": "Days_7",
            "ListingType": "Chinese",
            "PaymentMethods": "PayPal",
            "PayPalEmailAddress": "tkeefdddder@gmail.com",
            "PictureDetails": {"PictureURL": "http://i1.sandbox.ebayimg.com/03/i/00/30/07/20_1.JPG?set_id=8800005007"},
            "PostalCode": "95125",
            "Quantity": "1",
            "ReturnPolicy": {
                "ReturnsAcceptedOption": "ReturnsAccepted",
                "RefundOption": "MoneyBack",
                "ReturnsWithinOption": "Days_30",
                "Description": "If you are not satisfied, return the book for refund.",
                "ShippingCostPaidByOption": "Buyer"
            },
            "ShippingDetails": {
                "ShippingType": "Flat",
                "ShippingServiceOptions": {
                    "ShippingServicePriority": "1",
                    "ShippingService": "USPSMedia",
                    "ShippingServiceCost": "2.50"
                }
            },
            "Site": "US"
        }
    }

    api.execute('VerifyAddItem', myitem)

    if api.error():

        # traverse the DOM to look for error codes
        for node in api.response_dom().getElementsByTagName('ErrorCode'):
            print("error code: %s" % ebaysdk.nodeText(node))

        # check for invalid data - error code 37
        if 37 in api.response_codes():
            print("Invalid data in request")

def uploadPicture(opts):

    api = trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                  certid=opts.certid, devid=opts.devid, warnings=True)

    pictureData = {
        "WarningLevel": "High",
        "ExternalPictureURL": "http://developer.ebay.com/DevZone/XML/docs/images/hp_book_image.jpg",
        "PictureName": "WorldLeaders"
    }

    api.execute('UploadSiteHostedPictures', pictureData)

    if api.error():
        raise Exception(api.error())

    dump(api)


def memberMessages(opts):

    api = trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                  certid=opts.certid, devid=opts.devid, warnings=True)

    now = datetime.datetime.now()

    memberData = {
        "WarningLevel": "High",
        "MailMessageType": "All",
        # "MessageStatus": "Unanswered",
        "StartCreationTime": now - datetime.timedelta(days=60),
        "EndCreationTime": now,
        "Pagination": {
            "EntriesPerPage": "5",
            "PageNumber": "1"
        }
    }

    api.execute('GetMemberMessages', memberData)

    dump(api)

    if api.response_dict().MemberMessage:
        for m in api.response_dict().MemberMessage.MemberMessageExchange:
            print("%s: %s" % (m.CreationDate, m.Question.Subject[:50]))

def getUser(opts):

    api = trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                  certid=opts.certid, devid=opts.devid, warnings=True, timeout=20, siteid=101)

    api.execute('GetUser', {'UserID': 'biddergoat'})

    dump(api, full=True)
    

def getOrders(opts):

    api = trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                  certid=opts.certid, devid=opts.devid, warnings=True, timeout=20)

    api.execute('GetOrders', {'NumberOfDays': 30})

    dump(api, full=True)

def categories(opts):

    api = trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
                  certid=opts.certid, devid=opts.devid, warnings=True, timeout=20, siteid=101)

    now = datetime.datetime.now()

    callData = {
        'DetailLevel': 'ReturnAll',
        'CategorySiteID': 101,
        'LevelLimit': 4,
    }

    api.execute('GetCategories', callData)

    dump(api, full=True)

'''
api = trading(domain='api.sandbox.ebay.com')
api.execute('GetCategories', {
    'DetailLevel': 'ReturnAll',
    'CategorySiteID': 101,
    'LevelLimit': 4,
})
'''

if __name__ == "__main__":
    (opts, args) = init_options()

    print("Trading API Samples for version %s" % ebaysdk.get_version())

    run(opts)
    feedback(opts)
    verifyAddItem(opts)
    verifyAddItemErrorCodes(opts)
    uploadPicture(opts)
    memberMessages(opts)
    categories(opts)
    getUser(opts)
    getOrders(opts)
    getTokenStatus(opts)

