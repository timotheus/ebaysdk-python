# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''
from collections import defaultdict
import json

from ebaysdk.utils import get_dom_tree

class ResponseDataObject(object):

    def __init__(self, mydict={}):
        self._load_dict(mydict)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return str(self.__dict__)

    def _load_dict(self, mydict):
        
        for a in mydict.items():

            if isinstance(a[1], dict):
                o = ResponseDataObject(a[1])
                setattr(self, a[0], o)

            elif isinstance(a[1], list):
                objs = []
                for i in a[1]:
                    if isinstance(i, str):
                        objs.append(i)
                    else:
                        objs.append(ResponseDataObject(i))
                
                setattr(self, a[0], objs)
            else:
                setattr(self, a[0], a[1])

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
    >>> o = ResponseDataObject({'content': xml})
    >>> r = Response(o, verb='findItemsByProduct', listnodes=['searchResult.item', 'findItemsByProductResponse.paginationOutput.pageNumber'])
    >>> len(r.dom().getchildren()) > 2
    True
    >>> r.reply.searchResult._count == '1'
    True
    >>> r.reply.searchResult
    {'item': [{'name': 'Item Two'}], '_count': '1'}
    >>> len(r.reply.paginationOutput.pageNumber) == 1
    True
    >>> xml = '<?xml version="1.0" encoding="UTF-8"?><findItemsByProductResponse xmlns="http://www.ebay.com/marketplace/search/v1/services"><ack>Success</ack><version>1.12.0</version><timestamp>2014-02-07T23:31:13.941Z</timestamp><searchResult count="2"><item><name>Item Two</name><shipping><c>US</c><c>MX</c></shipping></item><item><name>Item One</name></item></searchResult><paginationOutput><pageNumber>1</pageNumber><entriesPerPage>2</entriesPerPage><totalPages>90</totalPages><totalEntries>179</totalEntries></paginationOutput><itemSearchURL>http://www.ebay.com/ctg/53039031?_ddo=1&amp;_ipg=2&amp;_pgn=1</itemSearchURL></findItemsByProductResponse>'
    >>> o = ResponseDataObject({'content': xml})
    >>> r = Response(o, verb='findItemsByProduct', listnodes=['searchResult.item'])
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
    
    def __init__(self, obj, verb=None, listnodes=[]):
        self._listnodes=listnodes
        self._add_prefix(self._listnodes, verb)

        self._obj = obj
        self._dom = self._parse_xml(obj.content)
        self._dict = self._etree_to_dict(self._dom)
        
        if verb:
            self._dict = self._dict.get('%sResponse' % verb, self._dict)

        self.reply = ResponseDataObject(self._dict)

    def _add_prefix(self, nodes, verb):
        if verb:
            for i, v in enumerate(nodes):
                if not nodes[i].startswith(verb):
                    nodes[i] = "%sResponse.%s" % (verb, nodes[i])

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
        # remove xmlns from nodes, I find them meaningless
        t.tag = self._get_node_tag(t)

        d = {t.tag: {} if t.attrib else None}
        children = list(t)
        if children:
            dd = defaultdict(list)
            for dc in map(self._etree_to_dict, children):
                for k, v in dc.iteritems():
                    dd[k].append(v)

            d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}    

            # TODO: Optimizations? Forces a node to type list
            parent_path = self._get_node_path(t)
            for k in d[t.tag].keys():
                path = "%s.%s" % (parent_path, k)
                if path in self._listnodes:
                    if not isinstance(d[t.tag][k], list):
                        d[t.tag][k] = [ d[t.tag][k] ]

        if t.attrib:
            d[t.tag].update(('_' + k, v) for k, v in t.attrib.iteritems())
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