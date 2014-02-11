# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''
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
    >>> xml = '<?xml version="1.0" encoding="UTF-8"?><findItemsByProductResponse xmlns="http://www.ebay.com/marketplace/search/v1/services"><ack>Success</ack><version>1.12.0</version><timestamp>2014-02-07T23:31:13.941Z</timestamp><searchResult count="2"><item></item></searchResult><paginationOutput><pageNumber>1</pageNumber><entriesPerPage>2</entriesPerPage><totalPages>90</totalPages><totalEntries>179</totalEntries></paginationOutput><itemSearchURL>http://www.ebay.com/ctg/53039031?_ddo=1&amp;_ipg=2&amp;_pgn=1</itemSearchURL></findItemsByProductResponse>'
    >>> o = ResponseDataObject({'content': xml})
    >>> r = Response(o)
    
    >>> xml

    >>> r.asdict() 

    >>> r.reply

    '''
    rdict = dict()
    rdom = None

    def __init__(self, obj):
        # requests response object
        self.obj = obj
        self.tree = self._parse_xml(obj.content)
        
        res = []
        self.xmltodict(self.tree, res)
        
        mydict = dict()
        self._build_dict(res, mydict)
        self.rdict=mydict

        self.reply = ResponseDataObject(self.asdict())

    def _build_dict(self, ndict, mydict):

        if isinstance(ndict, list):
            for i in ndict:
                self._build_dict(i, mydict)
        elif isinstance(ndict, dict):
            if isinstance(ndict[ndict.keys()[0]], list):
                if isinstance(mydict.get(ndict.keys()[0], {}), dict) \
                    and mydict.has_key(ndict.keys()[0]):
                    mydict[ndict.keys()[0]] = [ mydict[ndict.keys()[0]] ]    
                elif mydict.has_key(ndict.keys()[0]) and isinstance(mydict[ndict.keys()[0]], list):
                    pass
                else:
                    mydict[ndict.keys()[0]] = {}

                for i in ndict[ndict.keys()[0]]:
                    self._build_dict(i, mydict[ndict.keys()[0]])
            else:
                if isinstance(mydict, list):
                    mydict.append(ndict)
                else:
                    mydict.update(ndict)

    def __getattr__(self, name):
        return getattr(self.obj, name)

    def _parse_xml(self, xml):
        return get_dom_tree(xml)
        
    def _get_node_tag(self, node):
        return node.tag.replace('{' + node.nsmap.get(node.prefix, '') + '}', '')

    def xmltodict(self, node, res):
        rep = {}

        if len(node):
            for n in list(node):
                #print self._get_node_tag(node)
                #rep[self._get_node_tag(node)] = []
                rep[self._get_node_tag(node)] = []
                
                self.xmltodict(n, rep[self._get_node_tag(node)])
                    
                if len(n):
                    #print "len=%s" % len(n)
                    value = None
                    if len(n.attrib) > 0:        
                        value = rep[self._get_node_tag(node)]
                        #value = {'value':rep[self._get_node_tag(node)],
                        #         '_attrs': n.attrib}
                    else:
                        value = rep[self._get_node_tag(node)]

                    res.append({self._get_node_tag(n):value})
                else:
                    res.append(rep[ self._get_node_tag(node)][0])
                    #print "else >> %s (%s)"  % (self._get_node_tag(node), rep[ self._get_node_tag(node)][0])
                    #print "res >> %s" % ' '.join(res)                
        else:
            value = None
            if len(node.attrib) > 0:
                value = {'value': node.text, '_attrs': node.attrib}
            else:
                value = node.text

            #print "tag=%s" % self._get_node_tag(node)
            #print "value=%s" % value or ''
            #print "before=" + ' '.join(res)
            res.append({self._get_node_tag(node):value or ''})
            #print "after=" + ' '.join(res)
            
        return

    def orig_xmltodict(self, node, res):
        rep = {}

        if len(node):
            for n in list(node):
                print self._get_node_tag(node)
                rep[self._get_node_tag(node)] = []
                self.xmltodict(n, rep[self._get_node_tag(node)])
                
                if len(n):
                    print "len=%s" % len(n)
                    value = None
                    if len(n.attrib) > 0:        
                        value = {'value':rep[self._get_node_tag(node)],
                                 '_attrs': n.attrib}
                    else:
                        value = rep[self._get_node_tag(node)]

                    res.append({self._get_node_tag(n):value})
                else:
                    res.append(rep[self._get_node_tag(node)][0])
                    print "else >> %s (%s)"  % (self._get_node_tag(node), res)
                    #print "res >> %s" % ' '.join(res)                
        else:
            value = None
            if len(node.attrib) > 0:
                value = {'value': node.text, '_attrs': node.attrib}
            else:
                value = node.text

            res.append({self._get_node_tag(node):value or ''})
        
        return

    def asdict(self):
        return self.rdict