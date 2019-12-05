# -*- coding: utf-8 -*-
'''
Copyright 2012-2019 eBay Inc.
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os
import sys
from optparse import OptionParser
import csv
import json
import requests

sys.path.insert(0, '%s/../' % os.path.dirname(__file__))

from common import dump

import ebaysdk
from ebaysdk.finding import Connection as finding
from ebaysdk.exception import ConnectionError, RequestPaginationError, PaginationLimit


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
    parser.add_option("-s", "--store_name",
                      dest="store_name", default=None,
                      help="Store name")
    parser.add_option("-f", "--file",
                      dest="input_file", default=None,
                      help="Input file containing store names.")
    parser.add_option("-o", "--offset",
                      dest="offset", default=0,
                      help="Input file line offset.")
    parser.add_option("-e", "--line_end",
                      dest="line_end", default=None,
                      help="Input file lines.")
    parser.add_option("-n", "--domain",
                      dest="domain", default='svcs.ebay.com',
                      help="Specifies the eBay domain to use (e.g. svcs.sandbox.ebay.com).")

    (opts, args) = parser.parse_args()
    return opts, args


def run(opts):

        data = None
        if opts.store_name:
            data = get_store_meta(opts.store_name)
            print(data)

        if opts.input_file:
            lines = []
            with open(opts.input_file, newline='') as csvfile:
                for row1 in csv.reader(csvfile, delimiter=',', quotechar='"'):
                    name = row1[1]
                    desc = row1[2].replace('\n', '')
                    logo = row1[3]
                    sub = row1[4]
                    lines.append([name, desc, logo, sub])

                for row in lines[int(opts.offset):(int(opts.offset)+1000)]:
                    print("(%s)" % row)

                    if row[3] == 'http://':
                        row[3] = None

                    if row[0] and row[2] and row[3]:
                        if record_exists(row[0]):
                            print("skipping %s" % row[0])
                            continue

                        try:
                            data = get_store_meta(row[0])
                        except Exception as e:
                            print("Exception %s" % e)

                        if not data:
                            continue

                        data['store_logo'] = row[2]
                        data['store_name'] = row[0]
                        data['store_description'] = row[1]
                        data['subscription_level'] = row[3]

                        req = requests.post(
                            'http://elastic-1-2467465.lvs02.dev.ebayc3.com:9200/stores/storeMeta',
                            data=json.dumps(data, sort_keys=True)
                        )
                        print(req.text)

                    else:
                        pass


def record_exists(store_name):
    query = {
        "query": {
            "match": {
                "store_name": {
                    "query": store_name,
                    "type": "phrase"
                }
            }
        }
    }

    query_req = requests.get('http://elastic-1-2467465.lvs02.dev.ebayc3.com:9200/stores/storeMeta/_search',
                             data=json.dumps(query, sort_keys=True))

    try:
        record_id = query_req.json()['hits']['hits'][0]['_id']
    except Exception as e:
        record_id = None

    return record_id


def get_store_meta(store_name):

    try:
        api = finding(debug=opts.debug, appid=opts.appid,
                      config_file=opts.yaml, domain=opts.domain)

        response = api.execute('findItemsIneBayStores', {
            'storeName': store_name,
            'outputSelector': [
                'CategoryHistogram',
                'AspectHistogram',
                'SellerInfo',
                'StoreInfo',
            ]}
        )

        if response.reply.ack != 'Success':
            return {}

        if int(response.reply.paginationOutput.totalEntries) <= 0:
            return {}

        data = {
            'followers': 0,
            'item_count': response.reply.paginationOutput.totalEntries,
            'seller_name': response.reply.searchResult.item[0].sellerInfo.sellerUserName,
            'store_url': response.reply.searchResult.item[0].storeInfo.storeURL,
            'feedback_score': response.reply.searchResult.item[0].sellerInfo.feedbackScore,
            'positive_feedback_percent': response.reply.searchResult.item[0].sellerInfo.positiveFeedbackPercent,
            'top_rated_seller': response.reply.searchResult.item[0].sellerInfo.topRatedSeller,
            'country_code': response.reply.searchResult.item[0].country,
        }

        agg_data = {
            'cat_asp': {},
            'watch_count': 0,
            'L0': [],
            'L1': [],
        }

        dominate_l0_cat_count = 0
        dominate_l1_cat_count = 0

        for lev0 in response.reply.categoryHistogramContainer.categoryHistogram:
            agg_data['L0'].append({
                'category_id': lev0.categoryId,
                'category_name': lev0.categoryName,
                'item_count': lev0.count
            })

            if int(lev0.count) > dominate_l0_cat_count:
                dominate_l0_cat_count = int(lev0.count)
                agg_data['dominate_l0_category_id'] = lev0.categoryId
                agg_data['dominate_l0_category_name'] = lev0.categoryName

            for lev1 in lev0.childCategoryHistogram:
                agg_data['L1'].append({
                    'category_id': lev1.categoryId,
                    'category_name': lev1.categoryName,
                    'item_count': lev1.count
                })

                if int(lev1.count) > dominate_l1_cat_count:
                    dominate_l1_cat_count = int(lev1.count)
                    agg_data['dominate_l1_category_id'] = lev1.categoryId
                    agg_data['dominate_l1_category_name'] = lev1.categoryName



        for category_node in agg_data['L1']:
            category_id = category_node['category_id']

            category_call = api.execute('findItemsIneBayStores', {
                'storeName': store_name,
                'categoryId': category_id,
                'outputSelector': [
                    'CategoryHistogram',
                    'AspectHistogram',
                    'SellerInfo',
                    'StoreInfo',
                ]}
            )

            if category_call.reply.ack != 'Success':
                return {}

            if int(category_call.reply.paginationOutput.totalEntries) <= 0:
                return {}

            analyze_items(category_call.reply.searchResult.item, category_id, agg_data)

            try:
                while True:
                    category_call2 = api.next_page()
                    analyze_items(category_call2.reply.searchResult.item, category_id, agg_data)

            except PaginationLimit as e:
                pass

        dom_l1_asp = average_asp(
            agg_data['cat_asp'][agg_data['dominate_l1_category_id']]
        )

        for category_node in agg_data['L1']:
            asp = average_asp(agg_data['cat_asp'][category_node['category_id']])
            category_node.update({'asp': asp})

        data.update({
            'L0': agg_data['L0'],
            'L1': agg_data['L1'],
            'watch_count': agg_data['watch_count'],
            'postal_code': agg_data.get('postal_code', None),
            'dominate_category_id': agg_data['dominate_l0_category_id'],
            'dominate_category_name': agg_data['dominate_l0_category_name'],
            'dominate_l1_category_id': agg_data['dominate_l1_category_id'],
            'dominate_l1_category_name': agg_data['dominate_l1_category_name'],
            'dominate_l1_category_asp': dom_l1_asp,
        })

        #from IPython import embed;
        #embed()

        return data

    except ConnectionError as e:
        print(e)


def average_asp(prices):
    total = sum(prices)
    if total > 0:
        return total / len(prices)
    else:
        return 0


def analyze_items(items, category_id, agg_data):

    for item in items:
        if not agg_data['cat_asp'].get(category_id, None):
            agg_data['cat_asp'][category_id] = []

        agg_data['cat_asp'][category_id].append(float(item.sellingStatus.currentPrice.value))
        if getattr(item.listingInfo, 'watchCount', None):
            agg_data['watch_count'] += int(item.listingInfo.watchCount)

        if getattr(item, 'postalCode', None):
            agg_data['postal_code'] = item.postalCode


if __name__ == "__main__":
    print("Finding samples for SDK version %s" % ebaysdk.get_version())
    (opts, args) = init_options()
    run(opts)
