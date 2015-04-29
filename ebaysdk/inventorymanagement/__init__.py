# -*- coding: utf-8 -*-

'''
Authored by: Michal Hernas
Licensed under CDDL 1.0
'''

import os

from ebaysdk import log
from ebaysdk.connection import BaseConnection
from ebaysdk.exception import RequestPaginationError, PaginationLimit
from ebaysdk.config import Config
from ebaysdk.utils import dict2xml

class Connection(BaseConnection):
    """Connection class for the Inventory Management service

    API documentation:
    http://developer.ebay.com/Devzone/store-pickup/InventoryManagement/index.html

    Supported calls:
    AddInventory
    AddInventoryLocation
    DeleteInventory
    DeleteInventoryLocation
    (all others, see API docs)

    Doctests:
    Create location first
    >>> f = Connection(config_file=os.environ.get('EBAY_YAML'), debug=False)
    >>> retval = f.execute('AddInventoryLocation', {
    ...     'Address1': u'Alexanderplatz 12',
    ...     'Address2': u'Gebaude 6',
    ...     'City': u'Berlin',
    ...     'Country': u'DE',
    ...     'PostalCode': u'13355',
    ...     'Latitude': u'37.374488',
    ...     'Longitude': u'-122.032876',
    ...     'LocationID': u'ebaysdk_test',
    ...     'LocationType': u'STORE',
    ...     'Phone': u'(408)408-4080',
    ...     'URL': u'http://store.com',
    ...     'UTCOffset': u'+02:00',
    ...     'Name': 'Test',
    ...     'Region': 'Berlin',
    ...     'PickupInstructions': 'Pick it up soon',
    ...     'Hours': [{'Day': {'DayOfWeek': 1, 'Interval': {'Open': '08:00:00', 'Close': '10:00:00'}}}]
    ...     })
    >>> error = f.error()
    >>> if not f.error():
    ...   print(f.response.reply.LocationID.lower())
    ebaysdk_test

    And now add item it it
    >>> f = Connection(config_file=os.environ.get('EBAY_YAML'), debug=False)
    >>> retval = f.execute('AddInventory', {"SKU": "SKU_TEST", "Locations": {"Location": [
    ...    {"Availability": "IN_STOCK", "LocationID": "ebaysdk_test", "Quantity": 10}
    ...     ]}})
    >>> error = f.error()
    >>> if not f.error():
    ...   print(f.response.reply.SKU.lower())
    sku_test


    Delete item from all locations
    >>> f = Connection(config_file=os.environ.get('EBAY_YAML'), debug=False)
    >>> retval = f.execute('DeleteInventory', {"SKU": "SKU_TEST", "Confirm": 'true'})
    >>> error = f.error()
    >>> if not f.error():
    ...   print(f.response.reply.SKU.lower())
    sku_test


    Delete location
    >>> f = Connection(config_file=os.environ.get('EBAY_YAML'), debug=False)
    >>> retval = f.execute('DeleteInventoryLocation', {"LocationID": "ebaysdk_test"})
    >>> error = f.error()
    >>> if not f.error():
    ...   print(f.response.reply.LocationID.lower())
    ebaysdk_test

    """

    def __init__(self, **kwargs):
        """Finding class constructor.

        Keyword arguments:
        domain        -- API endpoint (default: svcs.ebay.com)
        config_file   -- YAML defaults (default: ebay.yaml)
        debug         -- debugging enabled (default: False)
        warnings      -- warnings enabled (default: False)
        uri           -- API endpoint uri (default: /services/search/FindingService/v1)
        token         -- eBay application/user token
        version       -- version number (default: 1.0.0)
        https         -- execute of https (default: False)
        proxy_host    -- proxy hostname
        proxy_port    -- proxy port number
        timeout       -- HTTP request timeout (default: 20)
        parallel      -- ebaysdk parallel object
        response_encoding -- API encoding (default: XML)
        request_encoding  -- API encoding (default: XML)
        """

        super(Connection, self).__init__(method='POST', **kwargs)

        self.config=Config(domain=kwargs.get('domain', 'api.ebay.com'),
                           connection_kwargs=kwargs,
                           config_file=kwargs.get('config_file', 'ebay.yaml'))

        # override yaml defaults with args sent to the constructor
        self.config.set('domain', kwargs.get('domain', 'api.ebay.com'))
        self.config.set('uri', '/selling/inventory/v1')
        self.config.set('https', True)
        self.config.set('warnings', True)
        self.config.set('errors', True)
        self.config.set('siteid', None)
        self.config.set('response_encoding', 'XML')
        self.config.set('request_encoding', 'XML')
        self.config.set('proxy_host', None)
        self.config.set('proxy_port', None)
        self.config.set('token', None)
        self.config.set('iaf_token', None)
        self.config.set('appid', None)
        self.config.set('version', '1.0.0')
        self.config.set('service', 'InventoryManagement')
        self.config.set('doc_url', 'http://developer.ebay.com/Devzone/store-pickup/InventoryManagement/index.html')

        self.datetime_nodes = ['starttimefrom', 'timestamp', 'starttime',
                               'endtime']
        self.base_list_nodes = [
        ]

    endpoints = {
        'addinventorylocation': 'locations/delta/add',
        'addinventory': 'inventory/delta/add',
        'deleteinventory': 'inventory/delta/delete',
        'deleteinventorylocation': 'locations/delta/delete',
    }

    def build_request_url(self, verb):
        url = super(Connection, self).build_request_url(verb)
        endpoint = self.endpoints[verb.lower()]
        return "{0}/{1}".format(url, endpoint)

    def build_request_headers(self, verb):
        return {
            "Authorization": "TOKEN {0}".format(self.config.get('token')),
            "Content-Type": "application/xml"
        }

    def build_request_data(self, verb, data, verb_attrs):
        xml = "<?xml version=\"1.0\" encoding=\"utf-8\"?>"
        xml += "<" + verb + "Request>"
        xml += dict2xml(data)
        xml += "</" + verb + "Request>"

        return xml

    def warnings(self):
        warning_string = ""

        if len(self._resp_body_warnings) > 0:
            warning_string = "%s: %s" \
                % (self.verb, ", ".join(self._resp_body_warnings))

        return warning_string


    def _get_resp_body_errors(self):
        """Parses the response content to pull errors.

        Child classes should override this method based on what the errors in the
        XML response body look like. They can choose to look at the 'ack',
        'Errors', 'errorMessage' or whatever other fields the service returns.
        the implementation below is the original code that was part of error()
        """

        if self._resp_body_errors and len(self._resp_body_errors) > 0:
            return self._resp_body_errors

        errors = []
        warnings = []
        resp_codes = []

        if self.verb is None:
            return errors

        dom = self.response.dom()
        if dom is None:
            return errors

        for e in dom.findall('Errors'):
            eSeverity = None
            eClass = None
            eShortMsg = None
            eLongMsg = None
            eCode = None

            try:
                eSeverity = e.findall('SeverityCode')[0].text
            except IndexError:
                pass

            try:
                eClass = e.findall('ErrorClassification')[0].text
            except IndexError:
                pass

            try:
                eCode = e.findall('ErrorCode')[0].text
            except IndexError:
                pass

            try:
                eShortMsg = e.findall('ShortMessage')[0].text
            except IndexError:
                pass

            try:
                eLongMsg = e.findall('LongMessage')[0].text
            except IndexError:
                pass

            try:
                eCode = e.findall('ErrorCode')[0].text
                try:
                    int_code = int(eCode)
                except ValueError:
                    int_code = None

                if int_code and int_code not in resp_codes:
                    resp_codes.append(int_code)

            except IndexError:
                pass

            msg = "Class: %s, Severity: %s, Code: %s, %s%s" \
                % (eClass, eSeverity, eCode, eShortMsg, eLongMsg)

            if eSeverity == 'Warning':
                warnings.append(msg)
            else:
                errors.append(msg)

        self._resp_body_warnings = warnings
        self._resp_body_errors = errors
        self._resp_codes = resp_codes

        if self.config.get('warnings') and len(warnings) > 0:
            log.warn("%s: %s\n\n" % (self.verb, "\n".join(warnings)))

        if self.response.reply.Ack == 'Failure':
            if self.config.get('errors'):
                log.error("%s: %s\n\n" % (self.verb, "\n".join(errors)))

            return errors

        return []