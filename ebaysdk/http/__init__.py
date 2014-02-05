# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import uuid
import time

from xml.parsers.expat import ExpatError
from xml.dom.minidom import parseString
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode 

from requests import Request

from ebaysdk import log, UserAgent
from ebaysdk.connection import BaseConnection
from ebaysdk.exception import ConnectionResponseError
from ebaysdk.config import Config
from ebaysdk.utils import getNodeText, xml2dict

class Connection(BaseConnection):
    """HTML class for traditional calls.

    Doctests:
    >>> h = Connection()
    >>> retval = h.execute('http://shop.ebay.com/i.html?rt=nc&_nkw=mytouch+slide&_dmpt=PDA_Accessories&_rss=1')
    >>> print(h.response_obj().rss.channel.ttl)
    60
    >>> title = h.response_dom().getElementsByTagName('title')[0]
    >>> print(getNodeText(title))
    mytouch slide
    >>> print(title.toxml())
    <title><![CDATA[mytouch slide]]></title>
    >>> print(h.error())
    None
    >>> h = Connection(method='POST', debug=False)
    >>> retval = h.execute('http://www.ebay.com/')
    >>> print(h.response_content() != '')
    True
    >>> print(h.response_code())
    200
    """

    def __init__(self, method='GET', **kwargs):
        """HTML class constructor.

        Keyword arguments:
        debug         -- debugging enabled (default: False)
        method        -- GET/POST/PUT (default: GET)
        proxy_host    -- proxy hostname
        proxy_port    -- proxy port number
        timeout       -- HTTP request timeout (default: 20)
        parallel      -- ebaysdk parallel object
        """

        super(Connection, self).__init__(method=method, **kwargs)

        self.config=Config(domain=None,
                           connection_kwargs=kwargs,
                           config_file=kwargs.get('config_file', 'ebay.yaml'))

        
    def response_dom(self):
        "Returns the HTTP response dom."

        try:
            if not self._response_dom:
                self._response_dom = parseString(self._response_content)

            return self._response_dom
        except ExpatError:
            raise ConnectionResponseError('response is not well-formed')

    def response_dict(self):
        "Return the HTTP response dictionary."

        try:
            if not self._response_dict and self.response_content:
                self._response_dict = xml2dict().fromstring(self._response_content)

            return self._response_dict
        except ExpatError:
            raise ConnectionResponseError('response is not well-formed')

    def execute(self, url, data=None, headers=dict(), method=None):
        "Executes the HTTP request."
        log.debug('execute: url=%s data=%s' % (url, data))
        
        if method:
            self.method=method

        self._reset()
        self.build_request(url, data, headers)
        self.execute_request()

        if self.parallel:
            self.parallel._add_request(self)
            return None        
        
        self.process_response()
        self.error_check()

        log.debug('total time=%s' % (time.time() - self._time))
        
        return self

    def build_request(self, url, data, headers):
 
        self._request_id = uuid.uuid4()

        headers.update({'User-Agent': UserAgent, 
                        'X-EBAY-SDK-REQUEST-ID': str(self._request_id)})

        kw = dict()
        if self.method == 'POST':
            kw['data'] = data
        else:
            kw['params'] = data

        request = Request(self.method, 
            url,
            headers=headers,
            **kw
        )

        self.request = request.prepare()

    def warnings(self):
        return ''


