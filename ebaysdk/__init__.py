import os, sys, re
import string, StringIO, base64
import yaml, pycurl, urllib
from types import DictType, ListType

from xml.dom.minidom import parseString, Node
from BeautifulSoup import BeautifulStoneSoup
from types import DictType 

from ebaysdk.utils import xml2dict, dict2xml, list2xml, make_struct


VERSION = (0, 1, 6)


def get_version():
    version = '%s.%s.%s' % (VERSION[0], VERSION[1], VERSION[2])
    return version

__version__ = get_version()       

def nodeText(node):
    rc = []

    if hasattr(node, 'childNodes'):
        for cn in node.childNodes:
            if cn.nodeType == cn.TEXT_NODE:
                rc.append(cn.data)
            elif cn.nodeType == cn.CDATA_SECTION_NODE:
                rc.append(cn.data)    
        
    return ''.join(rc)

def tag(name, value):
    return "<%s>%s</%s>" % ( name, value, name )

class ebaybase(object):
    
    def __init__(self, debug=False, method='GET', proxy_host=None, timeout=20, proxy_port=80, **kwargs):                
        self.verb       = None
        self.debug      = debug
        self.method     = method
        self.timeout    = timeout
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port 
        self.spooled_calls = [];
        self._reset()
     
    def debug_callback(self, debug_type, debug_message):
        sys.stderr.write('type: ' + str(debug_type) + ' message'+str(debug_message) + "\n")
    
    def v(self, *args, **kwargs):
        
        args_a = [w for w in args]
        first  = args_a[0]
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
        
    def load_yaml(self, config_file):
            
        dirs = [ '.', os.environ.get('HOME'), '/etc' ]

        for mydir in dirs:
            myfile = "%s/%s" % (mydir, config_file)
            
            if os.path.exists( myfile ):
                try:
                    f = open( myfile, "r" ) 
                except IOError, e:
                    print "unable to open file %s" % e

                #print "using file %s" % myfile
                
                yData  = yaml.load( f.read() )
                domain = self.api_config.get('domain', '')
                
                self.api_config_append( yData.get(domain, {}) )
                return
    
    def api_config_append(self, config):
        for c in config:
            self.api_config[c] = config[c] 
        
    def getNodeText(self, nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    def _reset(self):
        self._response_content = None
        self._response_dom     = None
        self._response_obj     = None
        self._response_soup    = None
        self._response_dict    = None
        self._response_error   = None
        
    def do(self, verb, call_data=dict()):
        return self.execute(verb, call_data)
                    
    def execute(self, verb, data):
        self.verb = verb

        if type(data) == DictType:
            self.call_xml = dict2xml(data, roottag='TRASHME')
        elif type(data) == ListType:
            self.call_xml = list2xml(data, roottag='TRASHME')
        else:    
            self.call_xml = data

        self._reset()    
        self._response_content = self._execute_http_request()

        # remove xml namespace
        regex = re.compile('xmlns="[^"]+"')
        self._response_content = regex.sub( '', self._response_content )

    def response_soup(self):
        if not self._response_soup:
            self._response_soup = BeautifulStoneSoup(unicode(self._response_content))
        
        return self._response_soup
        
    def response_obj(self):
        if not self._response_obj:
            self._response_obj = make_struct(self.response_dict())
        
        return self._response_obj
            
    def response_dom(self):
        if not self._response_dom:
            dom = parseString((self._response_content or ("<%sResponse></%sResponse>" % (self.verb, self.verb))) )
            self._response_dom = dom.getElementsByTagName(self.verb+'Response')[0]
        
        return self._response_dom

    def response_dict(self):
        if not self._response_dict:
            mydict = xml2dict().fromstring(self._response_content)
            self._response_dict = mydict.get(self.verb+'Response', mydict)
            
        return self._response_dict
        
    def api_init(self,config_items):
        for config in config_items:
            self.api_config[config[0]] = config[1]
 
    def _execute_http_request(self):
        "performs the http post and returns the XML response body"
        try:
            curl = pycurl.Curl()
            
            if self.proxy_host:
                curl.setopt(pycurl.PROXY, str('%s:%d' % (self.proxy_host, self.proxy_port)))
            else:
                curl.setopt(pycurl.PROXY, '')

            # construct headers
            request_headers = self._build_request_headers()
            curl.setopt( pycurl.HTTPHEADER, [
                str( '%s: %s' % ( k, v ) ) for k, v in request_headers.items()
            ] )

            # construct URL & post data
            request_url = self.api_config.get('domain', None)
            
            if self.api_config.get('uri', None):
                request_url = "%s%s" % ( request_url, self.api_config.get('uri', None) )
            
            if self.api_config.get('https', None):
                request_url = "https://%s" % request_url
            
            if self.method == 'POST':
                request_xml = self._build_request_xml()
                curl.setopt(pycurl.POST, True)
                curl.setopt(pycurl.POSTFIELDS, str(request_xml))
            
            curl.setopt(pycurl.FOLLOWLOCATION, 1)
            curl.setopt(pycurl.URL, str(request_url))
            curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            
            response_header = StringIO.StringIO()
            response_body   = StringIO.StringIO()

            curl.setopt(pycurl.CONNECTTIMEOUT, self.timeout)
            curl.setopt(pycurl.TIMEOUT, self.timeout)

            curl.setopt(pycurl.HEADERFUNCTION, response_header.write)
            curl.setopt(pycurl.WRITEFUNCTION, response_body.write)

            if self.debug:
                sys.stderr.write("CURL Request: %s\n" % request_url)
                curl.setopt(pycurl.VERBOSE, 1)
                curl.setopt(pycurl.DEBUGFUNCTION, self.debug_callback)

            curl.perform()
            
            response_code   = curl.getinfo(pycurl.HTTP_CODE)
            response_status = response_header.getvalue().splitlines()[0]
            response_reason = re.match( r'^HTTP.+? +\d+ +(.*) *$', response_status ).group(1)
            response_data   = response_body.getvalue()
        
            if response_code != 200:
                self._response_error = "Error: %s" % response_reason
                raise Exception('%s' % response_reason)
            else:
                return response_data
            
        except Exception, e:
            self._response_error = "Exception: %s" % e
            raise Exception("%s" % e)
        
    def error(self):
        "builds and returns the api error message"

        str = []

        if self._response_error:
            str.append(self._response_error)

        for e in self.response_dom().getElementsByTagName("Errors"):

            if e.getElementsByTagName('ErrorClassification'):
                str.append('- Class: %s' % nodeText(e.getElementsByTagName('ErrorClassification')[0]))

            if e.getElementsByTagName('SeverityCode'):
                str.append('- Severity: %s' % nodeText(e.getElementsByTagName('SeverityCode')[0]))

            if e.getElementsByTagName('ErrorCode'):
                str.append('- Code: %s' % nodeText(e.getElementsByTagName('ErrorCode')[0]))

            if e.getElementsByTagName('ShortMessage'):
                str.append('- %s ' % nodeText(e.getElementsByTagName('ShortMessage')[0]))

            if e.getElementsByTagName('LongMessage'):
                str.append('- %s ' % nodeText(e.getElementsByTagName('LongMessage')[0]))

        if (len(str) > 0):
            return "%s error:\n%s\n" % (self.verb, "\n".join(str))

        return "\n".join(str)
            
class shopping(ebaybase):
    """
    Shopping backend for ebaysdk.
    http://developer.ebay.com/products/shopping/

    shopping(debug=False, domain='open.api.ebay.com', uri='/shopping', method='POST', https=False, siteid=0, response_encoding='XML', request_encoding='XML', config_file='ebay.yaml')
    
    >>> s = shopping()
    >>> s.execute('FindItemsAdvanced', {'CharityID': 3897})
    >>> print s.response_obj().Ack
    Success
    >>> print s.error()
    <BLANKLINE>
    """
    
    def __init__(self, 
        domain='open.api.ebay.com', 
        uri='/shopping',
        https=False,
        siteid=0,
        response_encoding='XML',
        request_encoding='XML',
        config_file='ebay.yaml',
        **kwargs ):

        ebaybase.__init__(self, method='POST', **kwargs)

        self.api_config = {
            'domain' : domain,
            'uri' : uri,
            'https' : https,
            'siteid' : siteid,
            'response_encoding' : response_encoding,
            'request_encoding' : request_encoding,
        }    

        self.load_yaml(config_file)

    def _build_request_headers(self):
        return {
            "X-EBAY-API-VERSION": self.api_config.get('version', ''),
            "X-EBAY-API-APP-ID": self.api_config.get('appid', ''),
            "X-EBAY-API-SITEID": self.api_config.get('siteid', ''),
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

class html(ebaybase):
    """
    HTML backend for ebaysdk.
    
    (self, debug=False, method='GET', proxy_host=None, timeout=20, proxy_port=80)
    
    >>> h = html()
    >>> h.execute('http://shop.ebay.com/i.html?rt=nc&_nkw=mytouch+slide&_dmpt=PDA_Accessories&_rss=1')
    >>> print h.response_obj().rss.channel.ttl
    60
    >>> title = h.response_dom().getElementsByTagName('title')[0]
    >>> print nodeText( title )
    mytouch slide
    >>> print title.toxml()
    <title><![CDATA[mytouch slide]]></title>
    >>> print h.error()
    None
    """

    def __init__(self, **kwargs):
        ebaybase.__init__(self, method='GET', **kwargs)

    def response_dom(self):
        if not self._response_dom:
            self._response_dom = parseString(self._response_content)

        return self._response_dom

    def response_dict(self):
        if not self._response_dict:
            self._response_dict = xml2dict().fromstring(self._response_content)
            
        return self._response_dict

    def execute(self, url, call_data=dict()):
        "execute(self, url, call_data=dict())"
        
        self.url = url
        self.call_data = call_data
 
        self._reset()    
        self._response_content = self._execute_http_request()

        # remove xml namespace
        regex = re.compile( 'xmlns="[^"]+"' )
        self._response_content = regex.sub( '', self._response_content )

    def _execute_http_request(self):
        "performs the http post and returns the XML response body"
        
        try:
            curl = pycurl.Curl()
            
            if self.proxy_host:
                curl.setopt(pycurl.PROXY, str('%s:%d' % (self.proxy_host, self.proxy_port)))
            else:
                curl.setopt(pycurl.PROXY, '')
            
            request_url = self.url
            if self.call_data and self.method == 'GET':
                request_url = request_url + '?' + urllib.urlencode(self.call_data)

            if self.method == 'POST':
                request_xml = self._build_request_xml()
                curl.setopt(pycurl.POST, True)
                curl.setopt(pycurl.POSTFIELDS, str(request_xml))
            
            curl.setopt(pycurl.FOLLOWLOCATION, 1)
            curl.setopt(pycurl.URL, str(request_url))
            curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            
            response_header = StringIO.StringIO()
            response_body   = StringIO.StringIO()

            curl.setopt(pycurl.CONNECTTIMEOUT, self.timeout)
            curl.setopt(pycurl.TIMEOUT, self.timeout)

            curl.setopt(pycurl.HEADERFUNCTION, response_header.write)
            curl.setopt(pycurl.WRITEFUNCTION, response_body.write)

            if self.debug:
                sys.stderr.write("CURL Request: %s\n" % request_url)
                curl.setopt(pycurl.VERBOSE, 1)
                curl.setopt(pycurl.DEBUGFUNCTION, self.debug_callback)

            curl.perform()
            
            response_code   = curl.getinfo(pycurl.HTTP_CODE)
            response_status = response_header.getvalue().splitlines()[0]
            response_reason = re.match( r'^HTTP.+? +\d+ +(.*) *$', response_status ).group(1)
            response_data   = response_body.getvalue()
        
            if response_code != 200:
                self._response_error = "Error: %s" % response_reason
                raise Exception('%s' % response_reason)
            else:
                return response_data
            
        except Exception, e:
            self._response_error = "Exception: %s" % e
            raise Exception("%s" % e)
        
    def error(self):
         "builds and returns the api error message"     
         return self._response_error
         
class trading(ebaybase):
    """
    Trading backend for the ebaysdk
    http://developer.ebay.com/products/trading/
    
    >>> t = trading()
    >>> t.execute('GetCharities', { 'CharityID': 3897 }) 
    >>> charity_name = ''
    >>> if len( t.response_dom().getElementsByTagName('Name') ) > 0:
    ...   charity_name = nodeText(t.response_dom().getElementsByTagName('Name')[0])
    >>> print charity_name 
    Sunshine Kids Foundation
    >>> print t.error()
    <BLANKLINE>
    """

    def __init__(self, 
        domain=None,
        uri=None,
        https=None,
        siteid=None,
        response_encoding=None,
        request_encoding=None,
        proxy_host=None,
        proxy_port=None,
        username=None,
        password=None,
        token=None,
        appid=None,
        certid=None,
        devid=None,
        version=None,
        config_file='ebay.yaml',
        **kwargs ):
        
        ebaybase.__init__(self, method='POST', **kwargs)

        self.api_config = {
            'domain' : 'api.ebay.com',
            'uri' : '/ws/api.dll',
            'https' : False,
            'siteid' : '0',
            'response_encoding' : 'XML',
            'request_encoding' : 'XML',
            'version' : '648',
        }

        self.load_yaml(config_file)        

        self.api_config['domain']=domain or self.api_config.get('domain')
        self.api_config['uri']=uri or self.api_config.get('uri')
        self.api_config['https']=https or self.api_config.get('https')
        self.api_config['siteid']=siteid or self.api_config.get('siteid')
        self.api_config['response_encoding']=response_encoding or self.api_config.get('response_encoding')
        self.api_config['request_encoding']=request_encoding or self.api_config.get('request_encoding')
        self.api_config['username']=username or self.api_config.get('username')
        self.api_config['password']=password or self.api_config.get('password')
        self.api_config['token']=token or self.api_config.get('token')
        self.api_config['appid']=appid or self.api_config.get('appid')
        self.api_config['certid']=certid or self.api_config.get('certid')
        self.api_config['devid']=devid or self.api_config.get('devid')
        self.api_config['version']=version or self.api_config.get('compatability') or self.api_config.get('version')

    def _build_request_headers(self):
        return {
            "X-EBAY-API-COMPATIBILITY-LEVEL": self.api_config.get('version', ''),
            "X-EBAY-API-DEV-NAME": self.api_config.get('devid', ''),
            "X-EBAY-API-APP-NAME": self.api_config.get('appid',''),
            "X-EBAY-API-CERT-NAME": self.api_config.get('certid',''),
            "X-EBAY-API-SITEID": self.api_config.get('siteid',''),
            "X-EBAY-API-CALL-NAME": self.verb,
            "Content-Type": "text/xml"
        }

    def _build_request_xml(self):
        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<" + self.verb + "Request xmlns=\"urn:ebay:apis:eBLBaseComponents\">"
        xml += "<RequesterCredentials>"
        if self.api_config.get('token', None):
            xml += "<eBayAuthToken>%s</eBayAuthToken>" % self.api_config.get('token')
        else:
            if self.api_config.get('username', None):
                xml += "<Username>%s</Username>" % self.api_config.get('username', '')
            if self.api_config.get('password', None):
                xml += "<Password>%s</Password>" % self.api_config.get('password', '')
                
        xml += "</RequesterCredentials>" 
        xml += self.call_xml
        xml += "</" + self.verb + "Request>"

        return xml
                        
class finding(ebaybase):
    """
    Finding backend for ebaysdk.
    http://developer.ebay.com/products/finding/
    
    >>> f = finding()
    >>> f.execute('findItemsAdvanced', {'keywords': 'shoes'})        
    >>> error = f.error()
    >>> print error
    <BLANKLINE>
    
    >>> if len( error ) <= 0:
    ...   print f.response_obj().itemSearchURL != ''
    ...   items = f.response_obj().searchResult.item    
    ...   print len(items)
    ...   print f.response_obj().ack
    True
    100
    Success
    
    """
    
    def __init__(self, 
        domain='svcs.ebay.com', 
        service='FindingService', 
        uri='/services/search/FindingService/v1',
        https=False,
        siteid='EBAY-US',
        response_encoding='XML',
        request_encoding='XML',
        config_file='ebay.yaml',
        **kwargs ):

        ebaybase.__init__(self, method='POST', **kwargs)

        self.api_config = {
            'domain'  : domain,
            'service' : service,
            'uri'     : uri,
            'https'   : https,
            'siteid'  : siteid,
            'response_encoding' : response_encoding,
            'request_encoding' : request_encoding,
        }    

        self.load_yaml(config_file)

    def _build_request_headers(self):
        return {
            "X-EBAY-SOA-SERVICE-NAME" : self.api_config.get('service',''),
            "X-EBAY-SOA-SERVICE-VERSION" : self.api_config.get('version',''),
            "X-EBAY-SOA-SECURITY-APPNAME"  : self.api_config.get('appid',''),
            "X-EBAY-SOA-GLOBAL-ID"  : self.api_config.get('siteid',''),
            "X-EBAY-SOA-OPERATION-NAME" : self.verb,
            "X-EBAY-SOA-REQUEST-DATA-FORMAT"  : self.api_config.get('request_encoding',''),
            "X-EBAY-SOA-RESPONSE-DATA-FORMAT" : self.api_config.get('response_encoding',''),
            "Content-Type" : "text/xml"
        }

    def _build_request_xml(self):
        xml = "<?xml version='1.0' encoding='utf-8'?>"
        xml += "<" + self.verb + "Request xmlns=\"http://www.ebay.com/marketplace/search/v1/services\">"
        xml += self.call_xml
        xml += "</" + self.verb + "Request>"

        return xml
