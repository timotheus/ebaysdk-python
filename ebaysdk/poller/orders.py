# -*- coding: utf-8 -*-

'''
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

from datetime import datetime, timedelta

from ebaysdk.trading import Connection as Trading
from ebaysdk.poller import parse_args, file_lock
from ebaysdk import log


def main(opts):

    with file_lock("/tmp/.ebaysdk-poller-orders.lock"):
        log.debug("Started poller %s" % __file__)

        to_time = datetime.utcnow()# - timedelta(days=80)
        from_time = to_time - timedelta(hours=opts.hours)

        ebay_api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
            certid=opts.certid, devid=opts.devid, siteid=opts.siteid, warnings=False
        )

        ebay_api.build_request('GetOrders', {
            'DetailLevel': 'ReturnAll',
            'OrderRole': 'Buyer',
            'OrderStatus': 'All',
            'Pagination': {
                'EntriesPerPage': 25,
                'PageNumber': 1,
            },
            'ModTimeFrom': from_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'ModTimeTo': to_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        }, None)

        for resp in ebay_api.pages(): 

            if resp.reply.OrderArray:

                for order in resp.reply.OrderArray.Order:

                    data = [
                        ("ID", order.OrderID),
                        ("Status", order.OrderStatus),
                        ("Seller Email", order.SellerEmail),
                        ("Title", order.TransactionArray.Transaction.Item.Title),
                        ("ItemID", order.TransactionArray.Transaction.Item.ItemID),
                        ("QTY", order.TransactionArray.Transaction.QuantityPurchased),
                        ("Payment Method", order.CheckoutStatus.PaymentMethod),
                        ("Payment Date", order.PaidTime),
                        ("Total", (order.Total._currencyID + ' ' + order.Total.value))
                    ]

                    if order.TransactionArray.Transaction.get('Variation', None):
                        data.append(("SKU", order.TransactionArray.Transaction.Variation.SKU)),

                    data.extend([
                        ("Shipped Time", order.ShippedTime),
                        ("Shipping Service", order.ShippingServiceSelected)
                    ])
            
                    if order.ShippingDetails.get('ShipmentTrackingDetails', None):
                        data.extend([
                            ("Min Shipping Days", order.ShippingDetails.ShippingServiceOptions.ShippingTimeMin),
                            ("Max Shipping Days", order.ShippingDetails.ShippingServiceOptions.ShippingTimeMax),
                            ("Tracking", order.ShippingDetails.ShipmentTrackingDetails.ShipmentTrackingNumber),
                            ("Carrier", order.ShippingDetails.ShipmentTrackingDetails.ShippingCarrierUsed),
                            ("Cost", (order.ShippingDetails.ShippingServiceOptions.ShippingServiceCost._currencyID, order.ShippingDetails.ShippingServiceOptions.ShippingServiceCost.value))
                        ])

                    values_array = map((lambda x: "%s=%s" % (x[0], x[1])), data)
                    log.debug(", ".join(values_array))

                    # execute SQL here

            else:
                log.debug("no orders to process")


if __name__ == '__main__':
    (opts, args) = parse_args("usage: python -u -m ebaysdk.poller.orders [options]")
    main(opts)