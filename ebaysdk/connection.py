# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

from ebaysdk import log

import re
import json
import time
import uuid

from requests import Request, Session
from requests.adapters import HTTPAdapter

from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError

from ebaysdk import set_stream_logger, UserAgent
from ebaysdk.utils import getNodeText as getNodeTextUtils
from ebaysdk.utils import dict2xml, xml2dict, getValue
from ebaysdk.exception import ConnectionError, ConnectionResponseError

HTTP_SSL = {
    False: 'http',
    True: 'https',
}

class BaseConnection(object):
    """Base Connection Class.

    Doctests:
    >>> d = { 'list': ['a', 'b', 'c']}
    >>> print(dict2xml(d, listnames={'': 'list'}))
    <list>a</list><list>b</list><list>c</list>
    >>> d2 = {'node': {'@attrs': {'a': 'b'}, '#text': 'foo'}}
    >>> print(dict2xml(d2))
    <node a="b">foo</node>
    """

    def __init__(self, debug=False, method='GET',
                 proxy_host=None, timeout=20, proxy_port=80,
                 parallel=None, **kwargs):

        if debug:
            set_stream_logger()

        self.response = None
        self.request = None
        self.verb = None
        self.debug = debug
        self.method = method
        self.timeout = timeout
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

        self.proxies = dict()
        if self.proxy_host:
            proxy = 'http://%s:%s' % (self.proxy_host, self.proxy_port)
            self.proxies = {
                'http': proxy,
                'https': proxy
            }

        self.session = Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))

        self.parallel = parallel

        self._reset()

    def debug_callback(self, debug_type, debug_message):
        log.debug('type: ' + str(debug_type) + ' message' + str(debug_message))

    def v(self, *args, **kwargs):
        return getValue(self.response_dict(), *args, **kwargs)
        
    def getNodeText(self, nodelist):
        return getNodeTextUtils(nodelist)

    def _reset(self):
        self.response = None
        self.request = None
        self.verb = None
        self._request_id = None
        self._time = time.time()
        self._response_content = None
        self._response_dom = None
        self._response_obj = None
        self._response_soup = None
        self._response_dict = None
        self._response_error = None
        self._resp_body_errors = []
        self._resp_body_warnings = []
        self._resp_codes = []

    def do(self, verb, call_data=dict()):
        return self.execute(verb, call_data)

    def execute(self, verb, data=None):
        "Executes the HTTP request."
        log.debug('execute: verb=%s data=%s' % (verb, data))

        self._reset()
        self.build_request(verb, data)
        self.execute_request()        

        if self.response:
            self.process_response()
            self.error_check()

        log.debug('total time=%s' % (time.time() - self._time))
        
        return self

    def build_request(self, verb, data):
 
        self.verb = verb
        self._request_id = uuid.uuid4()

        url = "%s://%s%s" % (
            HTTP_SSL[self.config.get('https', False)],
            self.config.get('domain'),
            self.config.get('uri')
        )

        headers = self.build_request_headers(verb)
        headers.update({'User-Agent': UserAgent, 
                        'X-EBAY-SDK-REQUEST-ID': str(self._request_id)})

        request = Request(self.method, 
            url,
            data=self.build_request_data(verb, data),
            headers=headers,
        )

        self.request = request.prepare()

    def execute_request(self):

        log.debug("REQUEST (%s): %s %s" \
            % (self._request_id, self.request.method, self.request.url))
        log.debug('headers=%s' % self.request.headers)
        log.debug('body=%s' % self.request.body)

        if self.parallel:
            self.parallel._add_request(self)
            return None

        self.response = self.session.send(self.request,
            verify=False,
            proxies=self.proxies,
            timeout=self.timeout,
            allow_redirects=True
        )

        log.debug('RESPONSE (%s):' % self._request_id)
        log.debug('elapsed time=%s' % self.response.elapsed)
        log.debug('status code=%s' % self.response.status_code)
        log.debug('headers=%s' % self.response.headers)
        log.debug('content=%s' % self.response.text)      
    
    def process_response(self):
        """Post processing of the response"""
        
        if self.response.status_code != 200:
            self._response_error = self.response.reason

        # remove xml namespace
        regex = re.compile('xmlns="[^"]+"')
        self._response_content = regex.sub('', self.response.content)

    def error_check(self):
        estr = self.error()

        if estr and self.config.get('errors', True):
            log.error(estr)
            raise ConnectionError(estr)

    def response_codes(self):
        return self._resp_codes

    def response_status(self):
        "Retuns the HTTP response status string."

        return self.response.reason

    def response_code(self):
        "Returns the HTTP response status code."

        return self.response.status_code

    def response_content(self):
        return self._response_content

    def response_soup(self):
        "Returns a BeautifulSoup object of the response."
        try:
            from bs4 import BeautifulStoneSoup
        except ImportError:
            from BeautifulSoup import BeautifulStoneSoup
            log.warn('DeprecationWarning: BeautifulSoup 3 or earlier is deprecated; install bs4 instead\n')

        if not self._response_soup:
            self._response_soup = BeautifulStoneSoup(
                self._response_content.decode('utf-8')
            )

        return self._response_soup

    def response_obj(self):
        return self.response_dict()

    def response_dom(self):
        "Returns the response DOM (xml.dom.minidom)."

        if not self._response_dom:
            dom = None
            content = None

            try:
                if self._response_content:
                    content = self._response_content
                else:
                    content = "<%sResponse></%sResponse>" % (self.verb, self.verb)

                dom = parseString(content)
                self._response_dom = dom.getElementsByTagName(
                    self.verb + 'Response')[0]

            except ExpatError as e:
                raise ConnectionResponseError("Invalid Verb: %s (%s)" % (self.verb, e))
            except IndexError:
                self._response_dom = dom

        return self._response_dom

    def response_dict(self):
        "Returns the response dictionary."

        if not self._response_dict and self._response_content:
            mydict = xml2dict().fromstring(self._response_content)
            self._response_dict = mydict.get(self.verb + 'Response', mydict)

        return self._response_dict

    def response_json(self):
        "Returns the response JSON."

        return json.dumps(self.response_dict())

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

        if self.verb is None:
            return errors

        dom = self.response_dom()
        if dom is None:
            return errors

        return []

    def error(self):
        "Builds and returns the api error message."

        error_array = []
        if self._response_error:
            error_array.append(self._response_error)

        error_array.extend(self._get_resp_body_errors())

        if len(error_array) > 0:
            error_string = "%s: %s" % (self.verb, ", ".join(error_array))

            return error_string

        return None
