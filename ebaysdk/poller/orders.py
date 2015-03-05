
import time
from datetime import datetime, timedelta

from ebaysdk.trading import Connection as Trading
from ebaysdk.poller import parse_args, file_lock
from ebaysdk import log



def sample():
    pass

def main(opts):

    with file_lock("/tmp/.ebaysdk-poller-orders.lock"):
        log.debug("Started poller %s" % __file__)

        to_time = datetime.utcnow()
        from_time = to_time - timedelta(days=29)

        ebay_api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
            certid=opts.certid, devid=opts.devid, siteid=opts.siteid, warnings=False
        )

        resp = ebay_api.execute('GetOrders', {
            'DetailLevel': 'ReturnAll',
            'OrderRole': 'Buyer',
            'OrderStatus': 'All',
            'Pagination': {
                'EntriesPerPage': 25,
                'PageNumber': 1,
            },
            'ModTimeFrom': from_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'ModTimeTo': to_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        })


        if resp.reply.OrderArray:
            for order in resp.reply.OrderArray.Order:
                #from IPython import embed; embed()

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
                    log.debug("SKU2: %s" % order.TransactionArray.Transaction.Item.get('SKU', 'None'))

                if order.ShippingDetails.get('ShipmentTrackingDetails', None):
                    log.debug("Tracking: %s" % order.ShippingDetails.ShipmentTrackingDetails.ShipmentTrackingNumber)
                    log.debug("Carrier: %s" % order.ShippingDetails.ShipmentTrackingDetails.ShippingCarrierUsed)
                    log.debug("Cost: %s %s" % (order.ShippingDetails.ShippingServiceOptions.ShippingServiceCost._currencyID, order.ShippingDetails.ShippingServiceOptions.ShippingServiceCost.value))
        else:
            log.debug("no orders to process")


        '''
        - item title .. Title
        - ebay auction Id .. ItemID
        - seller id or alias .. 
        - seller email .. SellerEmail
        - date of auction close
        - ship tracking number
        - cost of auction or transaction .. TransactionPrice
        - shipping cost .. ActualShippingCost
        - SKU .. SKU
        - payment method and date
        '''


if __name__ == '__main__':
    (opts, args) = parse_args("usage: python -u -m ebaysdk.poller.orders [options]")
    main(opts)