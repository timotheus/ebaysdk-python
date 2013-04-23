# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''
import os
import sys
import re
import traceback
import StringIO
import yaml
import pycurl
import urllib
from types import DictType, ListType

try:
    import simplejson as json
except ImportError:
    import json

from xml.dom.minidom import parseString
from BeautifulSoup import BeautifulStoneSoup

from ebaysdk.utils import xml2dict, dict2xml, list2xml, object_dict


def get_version():
    "Get the version."

    VERSIONFILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "_version.py")
    version = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                        open(VERSIONFILE, "rt").read(), re.M).group(1)

    return version

__version__ = get_version()


def nodeText(node):
    "Returns the node's text string."

    rc = []

    if hasattr(node, 'childNodes'):
        for cn in node.childNodes:
            if cn.nodeType == cn.TEXT_NODE:
                rc.append(cn.data)
            elif cn.nodeType == cn.CDATA_SECTION_NODE:
                rc.append(cn.data)

    return ''.join(rc)


def tag(name, value):
    return "<%s>%s</%s>" % (name, value, name)


class ebaybase(object):
    """Base API class.

    Doctests:
    >>> d = { 'list': ['a', 'b', 'c']}
    >>> print dict2xml(d)
    <list>a</list><list>b</list><list>c</list>
    """

    def __init__(self, debug=False, method='GET',
                 proxy_host=None, timeout=20, proxy_port=80,
                 parallel=None, **kwargs):

        self.verb = None
        self.debug = debug
        self.method = method
        self.timeout = timeout
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.parallel = parallel
        self._reset()

    def debug_callback(self, debug_type, debug_message):
        sys.stderr.write('type: ' + str(debug_type) + ' message'+str(debug_message) + "\n")

    def v(self, *args, **kwargs):

        args_a = [w for w in args]
        first = args_a[0]
        args_a.remove(first)

        h = kwargs.get('mydict', {})
        if h:
            h = h.get(first, {})
        else:
            h = self.response_dict().get(first, {})

        if len(args) == 1:
            try:
                return h.get('value', None)
            except:
                return h

        last = args_a.pop()

        for a in args_a:
            h = h.get(a, {})

        h = h.get(last, {})

        try:
            return h.get('value', None)
        except:
            return h

    def yaml_defaults(self, config_file, domain):
        "Returns a dictionary of YAML defaults."

        # check for absolute path
        if os.path.exists(config_file):
            try:
                f = open(config_file, "r")
            except IOError, e:
                print "unable to open file %s" % e

            yData = yaml.load(f.read())
            return yData.get(domain, {})

        # check other directories
        dirs = ['.', os.environ.get('HOME'), '/etc']
        for mydir in dirs:
            myfile = "%s/%s" % (mydir, config_file)

            if os.path.exists(myfile):
                try:
                    f = open(myfile, "r")
                except IOError, e:
                    print "unable to open file %s" % e

                yData = yaml.load(f.read())
                domain = self.api_config.get('domain', '')

                return yData.get(domain, {})

        return {}

    def set_config(self, cKey, defaultValue):

        if cKey in self._kwargs and self._kwargs[cKey] is not None:
            self.api_config.update({cKey: self._kwargs[cKey]})

        # otherwise, use yaml default and then fall back to
        # the default set in the __init__()
        else:
            if not cKey in self.api_config:
                self.api_config.update({cKey: defaultValue})
            else:
                pass

    def getNodeText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def _reset(self):
        self._response_reason = None
        self._response_status = None
        self._response_code = None
        self._response_content = None
        self._response_dom = None
        self._response_obj = None
        self._response_soup = None
        self._response_dict = None
        self._response_error = None
        self._resp_body_errors = []

    def do(self, verb, call_data=dict()):
        return self.execute(verb, call_data)

    def _to_xml(self, data):
        "Converts a list of dictionary to XML and returns it."

        xml = ''

        if type(data) == DictType:
            xml = dict2xml(data, roottag='TRASHME')
        elif type(data) == ListType:
            xml = list2xml(data, roottag='TRASHME')
        else:
            xml = data

        return xml

    def execute(self, verb, data):
        "Executes the HTTP request."

        self.verb = verb

        self.call_xml = self._to_xml(data)
        self.prepare()

        self._reset()
        self._response_content = self._execute_http_request()

        if self._response_content:
            self.process()

        return self

    def prepare(self):
        "Performs any final changes to the request."
        pass

    def process(self):
        "Performs any final changes to the response."

        # remove xml namespace
        regex = re.compile('xmlns="[^"]+"')
        self._response_content = regex.sub('', self._response_content)

    def response_status(self):
        "Retuns the HTTP response status string."

        return self._response_status

    def response_code(self):
        "Returns the HTTP response status code."

        return self._response_code

    def response_content(self):
        return self._response_content

    def response_soup(self):
        "Returns a BeautifulSoup object of the response."

        if not self._response_soup:
            self._response_soup = BeautifulStoneSoup(unicode(self._response_content, encoding='utf-8'))

        return self._response_soup

    def response_obj(self):
        return self.response_dict()

    def response_dom(self):
        "Returns the response DOM (xml.dom.minidom)."

        if not self._response_dom:
            dom = parseString((self._response_content or ("<%sResponse></%sResponse>" % (self.verb, self.verb))))

            try:
                self._response_dom = dom.getElementsByTagName(self.verb+'Response')[0]
            except IndexError:
                self._response_dom = dom

        return self._response_dom

    def response_dict(self):
        "Returns the response dictionary."

        if not self._response_dict and self._response_content:
            mydict = xml2dict().fromstring(self._response_content)
            self._response_dict = mydict.get(self.verb+'Response', mydict)

        return self._response_dict

    def response_json(self):
        "Returns the response JSON."

        return json.dumps(self.response_dict())

    def _execute_http_request(self):
        "Performs the http request and returns the XML response body."

        try:
            self._curl = pycurl.Curl()

            self._curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            self._curl.setopt(pycurl.SSL_VERIFYHOST, 0)

            if self.proxy_host:
                self._curl.setopt(pycurl.PROXY, str('%s:%d' % (self.proxy_host, self.proxy_port)))
            else:
                self._curl.setopt(pycurl.PROXY, '')

            # construct headers
            request_headers = self._build_request_headers()
            self._curl.setopt(pycurl.HTTPHEADER, [
                str('%s: %s' % (k, v)) for k, v in request_headers.items()
            ])

            # construct URL & post data
            request_url = self.api_config.get('domain', None)

            if self.api_config.get('uri', None):
                request_url = "%s%s" % (request_url, self.api_config.get('uri', None))

            if self.api_config.get('https', None):
                request_url = "https://%s" % request_url

            if self.method == 'POST':
                request_xml = self._build_request_xml()
                self._curl.setopt(pycurl.POST, True)
                self._curl.setopt(pycurl.POSTFIELDS, str(request_xml))

            self._curl.setopt(pycurl.FOLLOWLOCATION, 1)
            self._curl.setopt(pycurl.URL, str(request_url))
            self._curl.setopt(pycurl.SSL_VERIFYPEER, 0)

            self._response_header = StringIO.StringIO()
            self._response_body = StringIO.StringIO()

            self._curl.setopt(pycurl.CONNECTTIMEOUT, self.timeout)
            self._curl.setopt(pycurl.TIMEOUT, self.timeout)

            self._curl.setopt(pycurl.HEADERFUNCTION, self._response_header.write)
            self._curl.setopt(pycurl.WRITEFUNCTION, self._response_body.write)

            if self.debug:
                sys.stderr.write("CURL Request: %s\n" % request_url)
                self._curl.setopt(pycurl.VERBOSE, 1)
                self._curl.setopt(pycurl.DEBUGFUNCTION, self.debug_callback)

            if self.parallel:
                self.parallel._add_request(self)
                return None
            else:
                e = None
                for i in range(3):
                    try:
                        self._curl.perform()
                        return self._process_http_request()
                    except Exception, e:
                        continue
                    break

                raise Exception(e)

        except Exception, e:
            self._response_error = "Exception: %s" % e
            raise Exception("%s" % e)

    def _process_http_request(self):
        """Final processing for the HTTP response.
        Returns the response data.
        """

        self._response_code = self._curl.getinfo(pycurl.HTTP_CODE)

        if self._response_code == 0:
            return None

        self._response_status = self._response_header.getvalue().splitlines()[0]
        self._response_reason = re.match(r'^HTTP.+? +\d+ +(.*) *$', self._response_status).group(1)
        response_data = self._response_body.getvalue()

        self._response_header = None
        self._response_body = None
        self._curl.close()

        if self._response_code != 200:
            self._response_error = "%s" % self._response_reason
            #raise Exception('%s' % self._response_reason)
        else:
            return response_data

    def _get_resp_body_errors(self):
        """Parses the response content to pull errors.

        Child classes should override this method based on what the errors in the
        XML response body look like. They can choose to look at the 'ack',
        'Errors', 'errorMessage' or whatever other fields the service returns.
        the implementation below is the original code that was part of error()
        """

        if self._resp_body_errors and len(self._resp_body_errors) > 0:
            return self._resp_body_errors

        err = []
        if self.verb is None:
            return err
        dom = self.response_dom()
        if dom is None:
            return err

        for e in dom.getElementsByTagName("Errors"):

            if e.getElementsByTagName('ErrorClassification'):
                err.append('Class: %s' % nodeText(e.getElementsByTagName('ErrorClassification')[0]))

            if e.getElementsByTagName('SeverityCode'):
                severity = nodeText(e.getElementsByTagName('SeverityCode')[0])
                err.append('Severity: %s' % severity)

            if e.getElementsByTagName('ErrorCode'):
                err.append('Code: %s' % nodeText(e.getElementsByTagName('ErrorCode')[0]))

            if e.getElementsByTagName('ShortMessage'):
                err.append('%s ' % nodeText(e.getElementsByTagName('ShortMessage')[0]))

            if e.getElementsByTagName('LongMessage'):
                err.append('%s ' % nodeText(e.getElementsByTagName('LongMessage')[0]))

        self._resp_body_errors = err
        return err

    def error(self):
        "Builds and returns the api error message."

        err = []
        if self._response_error:
            err.append(self._response_error)
        err.extend(self._get_resp_body_errors())

        if len(err) > 0:
            return "%s: %s" % (self.verb, ", ".join(err))

        return ""


class shopping(ebaybase):
    """Shopping API class

    API documentation:
    http://developer.ebay.com/products/shopping/

    Supported calls:
    getSingleItem
    getMultipleItems
    (all others, see API docs)

    Doctests:
    >>> s = shopping(config_file=os.environ.get('EBAY_YAML'))
    >>> retval = s.execute('FindPopularItems', {'QueryKeywords': 'Python'})
    >>> print s.response_obj().Ack
    Success
    >>> print s.error()
    <BLANKLINE>
    """

    def __init__(self, **kwargs):
        """Shopping class constructor.

        Keyword arguments:
        domain        -- API endpoint (default: open.api.ebay.com)
        config_file   -- YAML defaults (default: ebay.yaml)
        debug         -- debugging enabled (default: False)
        warnings      -- warnings enabled (default: False)
        uri           -- API endpoint uri (default: /shopping)
        appid         -- eBay application id
        siteid        -- eBay country site id (default: 0 (US))
        compatibility -- version number (default: 799)
        https         -- execute of https (default: True)
        proxy_host    -- proxy hostname
        proxy_port    -- proxy port number
        timeout       -- HTTP request timeout (default: 20)
        parallel      -- ebaysdk parallel object
        response_encoding -- API encoding (default: XML)
        request_encoding  -- API encoding (default: XML)
        """
        ebaybase.__init__(self, method='POST', **kwargs)

        self._kwargs = kwargs

        self.api_config = {
            'domain': kwargs.get('domain', 'open.api.ebay.com'),
            'config_file': kwargs.get('config_file', 'ebay.yaml'),
        }

        # pull stuff in value yaml defaults
        self.api_config.update(
            self.yaml_defaults(self.api_config['config_file'], self.api_config['domain'])
        )

        # override yaml defaults with args sent to the constructor
        self.set_config('uri', '/shopping')
        self.set_config('warnings', True)
        self.set_config('https', False)
        self.set_config('siteid', 0)
        self.set_config('response_encoding', 'XML')
        self.set_config('request_encoding', 'XML')
        self.set_config('proxy_host', None)
        self.set_config('proxy_port', None)
        self.set_config('appid', None)
        self.set_config('version', '799')

        if self.api_config['https'] and self.debug:
            print "HTTPS is not supported on the Shopping API."

    def _build_request_headers(self):
        return {
            "X-EBAY-API-VERSION": self.api_config.get('version', ''),
            "X-EBAY-API-APP-ID":  self.api_config.get('appid', ''),
            "X-EBAY-API-SITEID":  self.api_config.get('siteid', ''),
            "X-EBAY-API-CALL-NAME": self.verb,
            "X-EBAY-API-REQUEST-ENCODING": "XML",
            "Content-Type": "text/xml"
        }

    def _build_request_xml(self):
        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<" + self.verb + "Request xmlns=\"urn:ebay:apis:eBLBaseComponents\">"
        xml += self.call_xml
        xml += "</" + self.verb + "Request>"

        return xml

    def error(self):
        "Builds and returns the api error message."

        err = []
        if self._response_error:
            err.append(self._response_error)

        try:
            if self.response_dict().ack == 'Failure':
                err.append(self.response_dict().errorMessage.error.message)
            elif self.response_dict().ack == 'Warning' and self.api_config.get('warnings'):
                sys.stderr.write(self.response_dict().errorMessage.error.message)

        except AttributeError:
            pass

        if len(err) > 0:
            return "%s: %s" % (self.verb, ", ".join(err))

        return ""


class html(ebaybase):
    """HTML class for traditional calls.

    Doctests:
    >>> h = html()
    >>> retval = h.execute('http://shop.ebay.com/i.html?rt=nc&_nkw=mytouch+slide&_dmpt=PDA_Accessories&_rss=1')
    >>> print h.response_obj().rss.channel.ttl
    60
    >>> title = h.response_dom().getElementsByTagName('title')[0]
    >>> print nodeText( title )
    mytouch slide
    >>> print title.toxml()
    <title><![CDATA[mytouch slide]]></title>
    >>> print h.error()
    None
    >>> h = html(method='POST', debug=False)
    >>> retval = h.execute('http://www.ebay.com/')
    >>> print h.response_content() != ''
    True
    >>> print h.response_code()
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
        ebaybase.__init__(self, method=method, **kwargs)

    def response_dom(self):
        "Returns the HTTP response dom."

        if not self._response_dom:
            self._response_dom = parseString(self._response_content)

        return self._response_dom

    def response_dict(self):
        "Return the HTTP response dictionary."

        if not self._response_dict and self.response_content:
            self._response_dict = xml2dict().fromstring(self._response_content)

        return self._response_dict

    def execute(self, url, call_data=dict()):
        "Excute method for the HTTP request."

        self.url = url
        self.call_data = call_data

        self.prepare()

        self._reset()
        self._response_content = self._execute_http_request()

        if self._response_content:
            self.process()

        return self

    def _execute_http_request(self):
        "Executes and returns the XML response body."

        try:
            self._curl = pycurl.Curl()

            if self.proxy_host:
                self._curl.setopt(pycurl.PROXY, str('%s:%d' % (self.proxy_host, self.proxy_port)))
            else:
                self._curl.setopt(pycurl.PROXY, '')

            request_url = self.url
            if self.call_data and self.method == 'GET':
                request_url = request_url + '?' + urllib.urlencode(self.call_data)

            elif self.method == 'POST':
                request_xml = self._build_request_xml()
                self._curl.setopt(pycurl.POST, True)
                self._curl.setopt(pycurl.POSTFIELDS, str(request_xml))

            self._curl.setopt(pycurl.FOLLOWLOCATION, 1)
            self._curl.setopt(pycurl.URL, str(request_url))
            self._curl.setopt(pycurl.SSL_VERIFYPEER, 0)

            self._response_header = StringIO.StringIO()
            self._response_body = StringIO.StringIO()

            self._curl.setopt(pycurl.CONNECTTIMEOUT, self.timeout)
            self._curl.setopt(pycurl.TIMEOUT, self.timeout)

            self._curl.setopt(pycurl.HEADERFUNCTION, self._response_header.write)
            self._curl.setopt(pycurl.WRITEFUNCTION, self._response_body.write)

            if self.debug:
                sys.stderr.write("CURL Request: %s\n" % request_url)
                self._curl.setopt(pycurl.VERBOSE, 1)
                self._curl.setopt(pycurl.DEBUGFUNCTION, self.debug_callback)

            if self.parallel:
                self.parallel._add_request(self)
                return None
            else:
                self._curl.perform()
                return self._process_http_request()

        except Exception, e:
            self._response_error = "Exception: %s" % e
            raise Exception("%s" % e)

    def error(self):
        "Builds and returns the api error message."

        return self._response_error

    def _build_request_xml(self):
        "Builds and returns the request XML."
        self.call_xml = self._to_xml(self.call_data)

        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += self.call_xml

        return xml


class trading(ebaybase):
    """Trading API class

    API documentation:
    https://www.x.com/developers/ebay/products/trading-api

    Supported calls:
    AddItem
    ReviseItem
    GetUser
    (all others, see API docs)

    Doctests:
    >>> t = trading(config_file=os.environ.get('EBAY_YAML'))
    >>> retval = t.execute('GetCharities', { 'CharityID': 3897 })
    >>> charity_name = ''
    >>> if len( t.response_dom().getElementsByTagName('Name') ) > 0:
    ...   charity_name = nodeText(t.response_dom().getElementsByTagName('Name')[0])
    >>> print charity_name
    Sunshine Kids Foundation
    >>> print t.error()
    <BLANKLINE>
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
        ebaybase.__init__(self, method='POST', **kwargs)

        self._kwargs = kwargs

        self.api_config = {
            'domain': kwargs.get('domain', 'api.ebay.com'),
            'config_file': kwargs.get('config_file', 'ebay.yaml'),
        }

        # pull stuff in value yaml defaults
        self.api_config.update(
            self.yaml_defaults(self.api_config['config_file'], self.api_config['domain'])
        )

        # override yaml defaults with args sent to the constructor
        self.set_config('uri', '/ws/api.dll')
        self.set_config('warnings', True)
        self.set_config('https', True)
        self.set_config('siteid', 0)
        self.set_config('response_encoding', 'XML')
        self.set_config('request_encoding', 'XML')
        self.set_config('proxy_host', None)
        self.set_config('proxy_port', None)
        self.set_config('token', None)
        self.set_config('iaf_token', None)
        self.set_config('appid', None)
        self.set_config('devid', None)
        self.set_config('certid', None)
        self.set_config('version', '648')
        self.set_config('compatibility', '648')

    def _build_request_headers(self):
        "Builds HTTP headers"

        headers = {
            "X-EBAY-API-COMPATIBILITY-LEVEL": self.api_config.get('version', ''),
            "X-EBAY-API-DEV-NAME": self.api_config.get('devid', ''),
            "X-EBAY-API-APP-NAME": self.api_config.get('appid', ''),
            "X-EBAY-API-CERT-NAME": self.api_config.get('certid', ''),
            "X-EBAY-API-SITEID": self.api_config.get('siteid', ''),
            "X-EBAY-API-CALL-NAME": self.verb,
            "Content-Type": "text/xml"
        }
        if self.api_config.get('iaf_token', None):
            headers["X-EBAY-API-IAF-TOKEN"] = self.api_config.get('iaf_token')

        return headers

    def _build_request_xml(self):
        "Builds the XML request"

        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<" + self.verb + "Request xmlns=\"urn:ebay:apis:eBLBaseComponents\">"
        if not self.api_config.get('iaf_token', None):
            xml += "<RequesterCredentials>"
            if self.api_config.get('token', None):
                xml += "<eBayAuthToken>%s</eBayAuthToken>" % self.api_config.get('token')
            elif self.api_config.get('username', None):
                xml += "<Username>%s</Username>" % self.api_config.get('username', '')
                if self.api_config.get('password', None):
                    xml += "<Password>%s</Password>" % self.api_config.get('password', '')
            xml += "</RequesterCredentials>"
        xml += self.call_xml
        xml += "</" + self.verb + "Request>"
        return xml


class finding(ebaybase):
    """Finding API class

    API documentation:
    https://www.x.com/developers/ebay/products/finding-api

    Supported calls:
    findItemsAdvanced
    findItemsByCategory
    (all others, see API docs)

    Doctests:
    >>> f = finding(config_file=os.environ.get('EBAY_YAML'))
    >>> retval = f.execute('findItemsAdvanced', {'keywords': 'shoes'})
    >>> error = f.error()
    >>> print error
    <BLANKLINE>

    >>> if len( error ) <= 0:
    ...   print f.response_obj().itemSearchURL != ''
    ...   items = f.response_obj().searchResult.item
    ...   print len(items)
    ...   print f.response_dict().ack
    True
    100
    Success

    """

    def __init__(self, **kwargs):
        """Finding class constructor.

        Keyword arguments:
        domain        -- API endpoint (default: svcs.ebay.com)
        config_file   -- YAML defaults (default: ebay.yaml)
        debug         -- debugging enabled (default: False)
        warnings      -- warnings enabled (default: False)
        uri           -- API endpoint uri (default: /services/search/FindingService/v1)
        appid         -- eBay application id
        siteid        -- eBay country site id (default: EBAY-US)
        compatibility -- version number (default: 1.0.0)
        https         -- execute of https (default: False)
        proxy_host    -- proxy hostname
        proxy_port    -- proxy port number
        timeout       -- HTTP request timeout (default: 20)
        parallel      -- ebaysdk parallel object
        response_encoding -- API encoding (default: XML)
        request_encoding  -- API encoding (default: XML)
        """
        ebaybase.__init__(self, method='POST', **kwargs)

        self._kwargs = kwargs

        self.api_config = {
            'domain': kwargs.get('domain', 'svcs.ebay.com'),
            'config_file': kwargs.get('config_file', 'ebay.yaml'),
        }

        # pull stuff in value yaml defaults
        self.api_config.update(
            self.yaml_defaults(self.api_config['config_file'],
                               self.api_config['domain'])
        )

        # override yaml defaults with args sent to the constructor
        self.set_config('uri', '/services/search/FindingService/v1')
        self.set_config('https', False)
        self.set_config('warnings', True)
        self.set_config('siteid', 'EBAY-US')
        self.set_config('response_encoding', 'XML')
        self.set_config('request_encoding', 'XML')
        self.set_config('proxy_host', None)
        self.set_config('proxy_port', None)
        self.set_config('token', None)
        self.set_config('iaf_token', None)
        self.set_config('appid', None)
        self.set_config('version', '1.0.0')
        self.set_config('compatibility', '1.0.0')

    def _build_request_headers(self):
        return {
            "X-EBAY-SOA-SERVICE-NAME": self.api_config.get('service', ''),
            "X-EBAY-SOA-SERVICE-VERSION": self.api_config.get('version', ''),
            "X-EBAY-SOA-SECURITY-APPNAME": self.api_config.get('appid', ''),
            "X-EBAY-SOA-GLOBAL-ID": self.api_config.get('siteid', ''),
            "X-EBAY-SOA-OPERATION-NAME": self.verb,
            "X-EBAY-SOA-REQUEST-DATA-FORMAT": self.api_config.get('request_encoding', ''),
            "X-EBAY-SOA-RESPONSE-DATA-FORMAT": self.api_config.get('response_encoding', ''),
            "Content-Type": "text/xml"
        }

    def _build_request_xml(self):
        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<" + self.verb + "Request xmlns=\"http://www.ebay.com/marketplace/search/v1/services\">"
        xml += self.call_xml
        xml += "</" + self.verb + "Request>"

        return xml

    def error(self):
        "Builds and returns the api error message."

        err = []
        if self._response_error:
            err.append(self._response_error)

        try:
            if self.response_dict().ack == 'Failure':
                err.append(self.response_dict().errorMessage.error.message)
            elif self.response_dict().ack == 'Warning' and self.api_config.get('warnings', False):
                sys.stderr.write(self.response_dict().errorMessage.error.message)

        except AttributeError:
            pass

        if len(err) > 0:
            return "%s: %s" % (self.verb, ", ".join(err))

        return ""


class SOAService(ebaybase):
    "SOAP class."

    def __init__(self, app_config=None, site_id='EBAY-US', debug=False):
        self.api_config = {
            'https': False,
            'site_id': site_id,
            'content_type': 'text/xml;charset=UTF-8',
            'request_encoding': 'XML',
            'response_encoding': 'XML',
            'message_protocol': 'SOAP12',
            'soap_env_str': 'http://www.ebay.com/marketplace/fundraising/v1/services',
        }

        ph = None
        pp = 80
        if app_config:
            self.load_from_app_config(app_config)
            ph = self.api_config.get('proxy_host', ph)
            pp = self.api_config.get('proxy_port', pp)

        ebaybase.__init__(
            self,
            debug=debug,
            method='POST',
            proxy_host=ph,
            proxy_port=pp,
        )

    # override this method, to provide setup through a config object, which
    # should provide a get() method for extracting constants we care about
    # this method should then set the .api_config[] dict (e.g. the comment below)
    def load_from_app_config(self, app_config):
        #self.api_config['domain'] = app_config.get('API_SERVICE_DOMAIN')
        #self.api_config['uri'] = app_config.get('API_SERVICE_URI')
        pass

    # Note: this method will always return at least an empty object_dict!
    #   It used to return None in some cases. If you get an empty dict,
    #   you can use the .error() method to look for the cause.
    def response_dict(self):
        if self._response_dict:
            return self._response_dict

        mydict = object_dict()
        try:
            mydict = xml2dict().fromstring(self._response_content)
            verb = self.verb + 'Response'
            self._response_dict = mydict['Envelope']['Body'][verb]

        except Exception, e:
            self._response_dict = mydict
            self._resp_body_errors.append("Error parsing SOAP response: %s" % e)

        return self._response_dict

    def _build_request_headers(self):
        return {
            'Content-Type': self.api_config['content_type'],
            'X-EBAY-SOA-SERVICE-NAME': self.api_config['service'],
            'X-EBAY-SOA-OPERATION-NAME': self.verb,
            'X-EBAY-SOA-GLOBAL-ID': self.api_config['site_id'],
            'X-EBAY-SOA-REQUEST-DATA-FORMAT': self.api_config['request_encoding'],
            'X-EBAY-SOA-RESPONSE-DATA-FORMAT': self.api_config['response_encoding'],
            'X-EBAY-SOA-MESSAGE-PROTOCOL': self.api_config['message_protocol'],
        }

    def _build_request_xml(self):
        xml = '<?xml version="1.0" encoding="utf-8"?>'
        xml += '<soapenv:Envelope'
        xml += ' xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"'
        xml += ' xmlns:ser="%s" >' % self.api_config['soap_env_str']
        xml += '<soapenv:Body>'
        xml += '<ser:%sRequest>' % self.verb
        xml += self.call_xml
        xml += '</ser:%sRequest>' % self.verb
        xml += '</soapenv:Body>'
        xml += '</soapenv:Envelope>'
        return xml

    def execute(self, verb, data):

        self.verb = verb

        self.call_xml = self._to_xml(self.soapify(data))
        self.prepare()

        self._reset()
        self._response_content = self._execute_http_request()

        if self._response_content:
            self.process()

        return self

    def soapify(self, xml):
        xml_type = type(xml)
        if xml_type == dict:
            soap = {}
            for k, v in xml.items():
                soap['ser:%s' % (k)] = self.soapify(v)
        elif xml_type == list:
            soap = []
            for x in xml:
                soap.append(self.soapify(x))
        else:
            soap = xml
        return soap


class parallel(object):
    """
    >>> p = parallel()
    >>> r1 = html(parallel=p)
    >>> retval = r1.execute('http://shop.ebay.com/i.html?rt=nc&_nkw=mytouch+slide&_dmpt=PDA_Accessories&_rss=1')
    >>> r2 = finding(parallel=p, config_file=os.environ.get('EBAY_YAML'))
    >>> retval = r2.execute('findItemsAdvanced', {'keywords': 'shoes'})
    >>> r3 = shopping(parallel=p, config_file=os.environ.get('EBAY_YAML'))
    >>> retval = r3.execute('FindItemsAdvanced', {'CharityID': 3897})
    >>> r4 = trading(parallel=p, config_file=os.environ.get('EBAY_YAML'))
    >>> retval = r4.execute('GetCharities', { 'CharityID': 3897 })
    >>> p.wait()
    >>> print p.error()
    <BLANKLINE>
    >>> print r1.response_obj().rss.channel.ttl
    60
    >>> print r2.response_dict().ack
    Success
    >>> print r3.response_obj().Ack
    Success
    >>> print r4.response_obj().Ack
    Success
    """

    def __init__(self):
        self._requests = []
        self._errors = []

    def _add_request(self, request):
        self._requests.append(request)

    def wait(self, timeout=20):
        "wait for all of the api requests to complete"

        self._errors = []
        try:
            if timeout > 0:
                creqs = self._requests
                for i in range(3):
                    failed_calls = self.execute_multi(creqs, timeout)

                    if failed_calls:
                        creqs = failed_calls
                        continue
                    else:
                        creqs = []

                    break

                for request in creqs:
                    self._errors.append("%s" % self._get_curl_http_error(request._curl))

            self._requests = []
        except Exception, e:
            self._errors.append("Exception: %s" % e)
            traceback.print_exc()
            raise Exception("%s" % e)

    def _get_curl_http_error(self, curl, info=None):
        code = curl.getinfo(pycurl.HTTP_CODE)
        url = curl.getinfo(pycurl.EFFECTIVE_URL)
        if code == 403:
            return 'Server refuses to fullfil the request for: %s' % url
        else:
            if info is None:
                msg = ''
            else:
                msg = ': ' + info

            return '%s : Unable to handle http code %d%s' % (url, code, msg)

    def execute_multi(self, calls, timeout):

        multi = pycurl.CurlMulti()
        for request in calls:
            multi.add_handle(request._curl)

        while True:
            while True:
                ret, num = multi.perform()
                if ret != pycurl.E_CALL_MULTI_PERFORM:
                    break
            if num == 0:
                break
            if multi.select(timeout) < 0:
                raise pycurl.error(pycurl.E_OPERATION_TIMEOUTED)

        failed_calls = []

        for request in calls:
            multi.remove_handle(request._curl)

            request._response_content = request._process_http_request()

            if request.response_code() == 0:
                failed_calls.append(request)
            else:
                if request._response_content:
                    request.process()
                if request._response_error:
                    self._errors.append(request._response_error)

                self._errors.extend(request._get_resp_body_errors())

        multi.close()

        return failed_calls

    def error(self):
        "builds and returns the api error message"

        if len(self._errors) > 0:
            return "parallel error:\n%s\n" % ("\n".join(self._errors))

        return ""
