# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''
import sys
import lxml
import copy
import datetime

from collections import defaultdict
import json

from ebaysdk.utils import get_dom_tree, python_2_unicode_compatible

@python_2_unicode_compatible
class ResponseDataObject(object):

    def __init__(self, mydict, datetime_nodes):
        self._load_dict(mydict, datetime_nodes)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "%s" % self.__dict__

    def has_key(self, name):
        try:
            getattr(self, name)
            return True
        except AttributeError:
            return False

    def get(self, name, default=None):
        try:
            return getattr(self, name)
        except AttributeError:
            return default

    def _setattr(self, name, value, datetime_nodes):
        if name.lower() in datetime_nodes:
            try:
                ts = "%s %s" % (value.partition('T')[0], value.partition('T')[2].partition('.')[0])
                value = datetime.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                print "Error: %s" % value
                pass

        setattr(self, name, value)

    def _load_dict(self, mydict, datetime_nodes):
        
        for a in mydict.items():

            if isinstance(a[1], dict):
                o = ResponseDataObject(a[1], datetime_nodes)
                setattr(self, a[0], o)

            elif isinstance(a[1], list):
                objs = []
                for i in a[1]:
                    if isinstance(i, str):
                        objs.append(i)
                    else:
                        objs.append(ResponseDataObject(i, datetime_nodes))
                
                setattr(self, a[0], objs)
            else:
                self._setattr(a[0], a[1], datetime_nodes)
                
class Response(object):
    '''
    <?xml version='1.0' encoding='UTF-8'?>
    <findItemsByProductResponse xmlns="http://www.ebay.com/marketplace/search/v1/services">
        <ack>Success</ack>
        <version>1.12.0</version>
        <timestamp>2014-02-07T23:31:13.941Z</timestamp>
        <searchResult count="2">
            <item>
            </item>
        </searchResult>
        <paginationOutput>
            <pageNumber>1</pageNumber>
            <entriesPerPage>2</entriesPerPage>
            <totalPages>90</totalPages>
            <totalEntries>179</totalEntries>
        </paginationOutput>
        <itemSearchURL>http://www.ebay.com/ctg/53039031?_ddo=1&amp;_ipg=2&amp;_pgn=1</itemSearchURL>
    </findItemsByProductResponse>

    Doctests:
    >>> xml = '<?xml version="1.0" encoding="UTF-8"?><findItemsByProductResponse xmlns="http://www.ebay.com/marketplace/search/v1/services"><ack>Success</ack><version>1.12.0</version><timestamp>2014-02-07T23:31:13.941Z</timestamp><searchResult count="1"><item><name>Item Two</name></item></searchResult><paginationOutput><pageNumber>1</pageNumber><entriesPerPage>1</entriesPerPage><totalPages>90</totalPages><totalEntries>179</totalEntries></paginationOutput><itemSearchURL>http://www.ebay.com/ctg/53039031?_ddo=1&amp;_ipg=2&amp;_pgn=1</itemSearchURL></findItemsByProductResponse>'
    >>> o = ResponseDataObject({'content': xml}, [])
    >>> r = Response(o, verb='findItemsByProduct', list_nodes=['finditemsbyproductresponse.searchresult.item', 'finditemsbyproductresponse.paginationoutput.pagenumber'])
    >>> len(r.dom().getchildren()) > 2
    True
    >>> r.reply.searchResult._count == '1'
    True
    >>> r.reply.searchResult
    {'item': [{'name': 'Item Two'}], '_count': '1'}
    >>> len(r.reply.paginationOutput.pageNumber) == 1
    True
    >>> xml = '<?xml version="1.0" encoding="UTF-8"?><findItemsByProductResponse xmlns="http://www.ebay.com/marketplace/search/v1/services"><ack>Success</ack><version>1.12.0</version><timestamp>2014-02-07T23:31:13.941Z</timestamp><searchResult count="2"><item><name>Item Two</name><shipping><c>US</c><c>MX</c></shipping></item><item><name>Item One</name></item></searchResult><paginationOutput><pageNumber>1</pageNumber><entriesPerPage>2</entriesPerPage><totalPages>90</totalPages><totalEntries>179</totalEntries></paginationOutput><itemSearchURL>http://www.ebay.com/ctg/53039031?_ddo=1&amp;_ipg=2&amp;_pgn=1</itemSearchURL></findItemsByProductResponse>'
    >>> o = ResponseDataObject({'content': xml}, [])
    >>> r = Response(o, verb='findItemsByProduct', list_nodes=['searchResult.item'])
    >>> len(r.dom().getchildren()) > 2
    True
    >>> r.json()
    '{"itemSearchURL": "http://www.ebay.com/ctg/53039031?_ddo=1&_ipg=2&_pgn=1", "paginationOutput": {"totalPages": "90", "entriesPerPage": "2", "pageNumber": "1", "totalEntries": "179"}, "ack": "Success", "timestamp": "2014-02-07T23:31:13.941Z", "searchResult": {"item": [{"name": "Item Two", "shipping": {"c": ["US", "MX"]}}, {"name": "Item One"}], "_count": "2"}, "version": "1.12.0"}'
    >>> r.dict() 
    {'itemSearchURL': 'http://www.ebay.com/ctg/53039031?_ddo=1&_ipg=2&_pgn=1', 'paginationOutput': {'totalPages': '90', 'entriesPerPage': '2', 'pageNumber': '1', 'totalEntries': '179'}, 'ack': 'Success', 'timestamp': '2014-02-07T23:31:13.941Z', 'searchResult': {'item': [{'name': 'Item Two', 'shipping': {'c': ['US', 'MX']}}, {'name': 'Item One'}], '_count': '2'}, 'version': '1.12.0'}
    >>> r.reply
    {'itemSearchURL': 'http://www.ebay.com/ctg/53039031?_ddo=1&_ipg=2&_pgn=1', 'paginationOutput': {'totalPages': '90', 'entriesPerPage': '2', 'pageNumber': '1', 'totalEntries': '179'}, 'ack': 'Success', 'timestamp': '2014-02-07T23:31:13.941Z', 'searchResult': {'item': [{'name': 'Item Two', 'shipping': {'c': ['US', 'MX']}}, {'name': 'Item One'}], '_count': '2'}, 'version': '1.12.0'}
    >>> len(r.reply.searchResult.item) == 2
    True
    >>> r.reply.searchResult._count == '2'
    True
    >>> item = r.reply.searchResult.item[0]
    >>> item.name == 'Item Two'
    True
    >>> len(item.shipping.c) == 2
    True
    '''
    
    def __init__(self, obj, verb=None, list_nodes=[], datetime_nodes=[]):
        self._list_nodes=copy.copy(list_nodes)
        self._obj = obj
        
        try:
            self._dom = self._parse_xml(obj.content)
            self._dict = self._etree_to_dict(self._dom)
        
            if verb:
                self._dict = self._dict.get('%sResponse' % verb, self._dict)

            self.reply = ResponseDataObject(self._dict,
                                            datetime_nodes=copy.copy(datetime_nodes))
        except lxml.etree.XMLSyntaxError:
            self.reply = ResponseDataObject({}, [])

    def _get_node_path(self, t):
        i = t
        path = []
        path.insert(0, i.tag)
        while 1:
            try:
                path.insert(0, i.getparent().tag)
                i = i.getparent()
            except AttributeError:
                break

        return '.'.join(path)

    def _etree_to_dict(self, t):
        if type(t) == lxml.etree._Comment:
            return {}

        # remove xmlns from nodes, I find them meaningless
        t.tag = self._get_node_tag(t)

        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(self._etree_to_dict, children):
                for k, v in dc.items():
                    dd[k].append(v)

            d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}    

            # TODO: Optimizations? Forces a node to type list
            parent_path = self._get_node_path(t)
            for k in d[t.tag].keys():
                path = "%s.%s" % (parent_path, k)
                if path.lower() in self._list_nodes:
                    if not isinstance(d[t.tag][k], list):
                        d[t.tag][k] = [ d[t.tag][k] ]

        if t.attrib:
            d[t.tag].update(('_' + k, v) for k, v in t.attrib.items())
        if t.text:
            text = t.text.strip()
            if children or t.attrib:
                if text:
                  d[t.tag]['value'] = text
            else:
                d[t.tag] = text
        return d

    def __getattr__(self, name):
        return getattr(self._obj, name)

    def _parse_xml(self, xml):
        return get_dom_tree(xml)
        
    def _get_node_tag(self, node):
        return node.tag.replace('{' + node.nsmap.get(node.prefix, '') + '}', '')

    def dom(self):
        return self._dom

    def dict(self):
        return self._dict

    def json(self):
        return json.dumps(self.dict())