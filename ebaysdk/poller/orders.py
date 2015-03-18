# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

from datetime import datetime, timedelta

from ebaysdk.trading import Connection as Trading
from ebaysdk.poller import parse_args, file_lock
from ebaysdk import log


def sample():
    pass

def main(opts):

    with file_lock("/tmp/.ebaysdk-poller-orders.lock"):
        log.debug("Started poller %s" % __file__)

        to_time = datetime.utcnow() - timedelta(days=29)
        from_time = to_time - timedelta(hours=opts.hours)

        ebay_api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
            certid=opts.certid, devid=opts.devid, siteid=opts.siteid, warnings=False
        )

        ebay_api.build_request('GetOrders', {
            'DetailLevel': 'ReturnAll',
            'OrderRole': 'Buyer',
            'OrderStatus': 'All',
            'Pagination': {
                'EntriesPerPage': 2,
                'PageNumber': 1,
            },
            'ModTimeFrom': from_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'ModTimeTo': to_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        }, None)

        for resp in ebay_api.pages(): 

            if resp.reply.OrderArray:

                for order in resp.reply.OrderArray.Order:

                    log.debug("ID: %s" % order.OrderID)
                    log.debug("Status: %s" % order.OrderStatus)
                    log.debug("Seller Email: %s" % order.SellerEmail)
                    log.debug("Title: %s" % order.TransactionArray.Transaction.Item.Title)
                    log.debug("ItemID: %s" % order.TransactionArray.Transaction.Item.ItemID)
                    log.debug("QTY: %s" % order.TransactionArray.Transaction.QuantityPurchased)
                    log.debug("Payment Method: %s" % order.CheckoutStatus.PaymentMethod)
                    log.debug("Payment Date: %s" % order.PaidTime)
                    log.debug("Total: %s %s" % (order.Total._currencyID, order.Total.value))

                    if order.TransactionArray.Transaction.get('Variation', None):
                        log.debug("SKU: %s" % order.TransactionArray.Transaction.Variation.SKU)

                    log.debug("Shipped Time: %s" % order.ShippedTime)
                    log.debug("Shipping Service: %s" % order.ShippingServiceSelected)
            
                    if order.ShippingDetails.get('ShipmentTrackingDetails', None):
                        log.debug("Min Shipping Days: %s" % order.ShippingDetails.ShippingServiceOptions.ShippingTimeMin)
                        log.debug("Max Shipping Days: %s" % order.ShippingDetails.ShippingServiceOptions.ShippingTimeMax)
                        log.debug("Tracking: %s" % order.ShippingDetails.ShipmentTrackingDetails.ShipmentTrackingNumber)
                        log.debug("Carrier: %s" % order.ShippingDetails.ShipmentTrackingDetails.ShippingCarrierUsed)
                        log.debug("Cost: %s %s" % (order.ShippingDetails.ShippingServiceOptions.ShippingServiceCost._currencyID, order.ShippingDetails.ShippingServiceOptions.ShippingServiceCost.value))
            
                    # execute SQL here

            else:
                log.debug("no orders to process")


if __name__ == '__main__':
    (opts, args) = parse_args("usage: python -u -m ebaysdk.poller.orders [options]")
    main(opts)