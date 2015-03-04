
import time
from datetime import datetime, timedelta

from ebaysdk.trading import Connection as Trading
from ebaysdk.poller import parse_args, file_lock
from ebaysdk import log



def sample():
    pass

def main(opts):

    with file_lock("/tmp/.ebaysdk-poller-orders.lock"):
        log.debug("worker")

        to_time = datetime.utcnow()
        from_time = to_time - timedelta(days=1)

        ebay_api = Trading(debug=opts.debug, config_file=opts.yaml, appid=opts.appid,
            certid=opts.certid, devid=opts.devid, siteid=opts.siteid, warnings=False
        )

        resp = ebay_api.execute('GetOrders', {
            'DetailLevel': 'ReturnAll',
            'OrderStatus': 'Completed',
            'Pagination': {
                'EntriesPerPage': 25,
                'PageNumber': 1,
            },
            'ModTimeFrom': from_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
            'ModTimeTo': to_time.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
        })

        #from IPython import embed; embed()

        for order in resp.reply.OrderArray.Order:

            log.debug("ID: %s" % order.OrderID)
            log.debug("Status: %s" % order.OrderStatus)
            log.debug("Seller Email: %s" % order.SellerEmail)
            log.debug("Title: %s" % order.TransactionArray.Transaction.Item.Title)
            log.debug("ItemID: %s" % order.TransactionArray.Transaction.Item.ItemID)
            log.debug("SKU: %s" % order.TransactionArray.Transaction.Variation.SKU)

            if order.ShippingDetails.get('ShipmentTrackingDetails', None):
                log.debug("Tracking: %s" % order.ShippingDetails.ShipmentTrackingDetails.ShipmentTrackingNumber)
                log.debug("Carrier: %s" % order.ShippingDetails.ShipmentTrackingDetails.ShippingCarrierUsed)
                log.debug("Cost: %s" % order.ShippingDetails.ShippingServiceOptions.ShippingServiceCost)
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