# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import os

from ebaysdk import log
from ebaysdk.connection import BaseConnection
from ebaysdk.config import Config
from ebaysdk.utils import getNodeText, to_xml

class Connection(BaseConnection):
    """Trading API class

    API documentation:
    https://www.x.com/developers/ebay/products/trading-api

    Supported calls:
    AddItem
    ReviseItem
    GetUser
    (all others, see API docs)

    Doctests:
    >>> t = Connection(config_file=os.environ.get('EBAY_YAML'))
    >>> retval = t.execute('GetCharities', {'CharityID': 3897})
    >>> charity_name = ''
    >>> if len( t.response_dom().getElementsByTagName('Name') ) > 0:
    ...   charity_name = getNodeText(t.response_dom().getElementsByTagName('Name')[0])
    >>> print(charity_name)
    Sunshine Kids Foundation
    >>> print(t.error())
    None
    >>> t2 = Connection(errors=False, debug=False, config_file=os.environ.get('EBAY_YAML'))
    >>> retval2 = t2.execute('VerifyAddItem', {})
    >>> print(t2.response_codes())
    [10009]
    """

    def __init__(self, **kwargs):
        """Trading class constructor.

        Keyword arguments:
        domain        -- API endpoint (default: api.ebay.com)
        config_file   -- YAML defaults (default: ebay.yaml)
        debug         -- debugging enabled (default: False)
        warnings      -- warnings enabled (default: False)
        uri           -- API endpoint uri (default: /ws/api.dll)
        appid         -- eBay application id
        devid         -- eBay developer id
        certid        -- eBay cert id
        token         -- eBay application/user token
        siteid        -- eBay country site id (default: 0 (US))
        compatibility -- version number (default: 648)
        https         -- execute of https (default: True)
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
        self.config.set('uri', '/ws/api.dll')
        self.config.set('warnings', True)
        self.config.set('errors', True)
        self.config.set('https', True)
        self.config.set('siteid', 0)
        self.config.set('response_encoding', 'XML')
        self.config.set('request_encoding', 'XML')
        self.config.set('proxy_host', None)
        self.config.set('proxy_port', None)
        self.config.set('token', None)
        self.config.set('iaf_token', None)
        self.config.set('appid', None)
        self.config.set('devid', None)
        self.config.set('certid', None)
        self.config.set('version', '837')
        self.config.set('compatibility', '837')

    def build_request_headers(self, verb):
        headers = {
            "X-EBAY-API-COMPATIBILITY-LEVEL": self.config.get('version', ''),
            "X-EBAY-API-DEV-NAME": self.config.get('devid', ''),
            "X-EBAY-API-APP-NAME": self.config.get('appid', ''),
            "X-EBAY-API-CERT-NAME": self.config.get('certid', ''),
            "X-EBAY-API-SITEID": self.config.get('siteid', ''),
            "X-EBAY-API-CALL-NAME": self.verb,
            "Content-Type": "text/xml"
        }
        if self.config.get('iaf_token', None):
            headers["X-EBAY-API-IAF-TOKEN"] = self.config.get('iaf_token')

        return headers

    def build_request_data(self, verb, data):
        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<" + self.verb + "Request xmlns=\"urn:ebay:apis:eBLBaseComponents\">"
        if not self.config.get('iaf_token', None):
            xml += "<RequesterCredentials>"
            if self.config.get('token', None):
                xml += "<eBayAuthToken>%s</eBayAuthToken>" % self.config.get('token')
            elif self.config.get('username', None):
                xml += "<Username>%s</Username>" % self.config.get('username', '')
                if self.config.get('password', None):
                    xml += "<Password>%s</Password>" % self.config.get('password', '')
            xml += "</RequesterCredentials>"
        xml += to_xml(data) or ''
        xml += "</" + self.verb + "Request>"
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

        dom = self.response_dom()
        if dom is None:
            return errors

        for e in dom.getElementsByTagName("Errors"):
            eSeverity = None
            eClass = None
            eShortMsg = None
            eLongMsg = None
            eCode = None

            if e.getElementsByTagName('SeverityCode'):
                eSeverity = getNodeText(e.getElementsByTagName('SeverityCode')[0])

            if e.getElementsByTagName('ErrorClassification'):
                eClass = getNodeText(e.getElementsByTagName('ErrorClassification')[0])

            if e.getElementsByTagName('ErrorCode'):
                eCode = getNodeText(e.getElementsByTagName('ErrorCode')[0])
                if int(eCode) not in resp_codes:
                    resp_codes.append(int(eCode))

            if e.getElementsByTagName('ShortMessage'):
                eShortMsg = getNodeText(e.getElementsByTagName('ShortMessage')[0])

            if e.getElementsByTagName('LongMessage'):
                eLongMsg = getNodeText(e.getElementsByTagName('LongMessage')[0])

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

        if self.response_dict().Ack == 'Failure':
            if self.config.get('errors'):
                log.error("%s: %s\n\n" % (self.verb, "\n".join(errors)))
            
            return errors

        return []
