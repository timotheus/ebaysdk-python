# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''
import sys

from lxml import etree as ET

def python_2_unicode_compatible(klass):
    """
    A decorator that defines __unicode__ and __str__ methods under Python 2.
    Under Python 3 it does nothing.

    To support Python 2 and 3 with a single code base, define a __str__ method
    returning text and apply this decorator to the class.
    """
    if sys.version_info[0] < 3:
        if '__str__' not in klass.__dict__:
            raise ValueError("@python_2_unicode_compatible cannot be applied "
                             "to %s because it doesn't define __str__()." %
                             klass.__name__)
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass

def get_dom_tree(xml):
    tree = ET.fromstring(xml)
    return tree.getroottree().getroot()

def attribute_check(root):
    attrs = []
    value = None

    if isinstance(root, dict):
        if '#text' in root:
            value = root['#text']
        if '@attrs' in root:
            for ak, av in sorted(root.pop('@attrs').items()):
                attrs.append('%s="%s"' % (ak, av))

    return attrs, value

def smart_encode(value):
    try:
        if sys.version_info[0] < 3:
            return unicode(value).encode('utf-8')
        else:
            return value
            #return str(value)

    except UnicodeDecodeError:
        return value

def to_xml(root):
    return dict2xml(root)

def dict2xml(root):
    '''
    Doctests:
    >>> dict1 = {'Items': {'ItemId': ['1234', '2222']}}
    >>> dict2xml(dict1)
    '<Items><ItemId>1234</ItemId><ItemId>2222</ItemId></Items>'
    >>> dict2 = {
    ...    'searchFilter': {'categoryId': {'#text': 222, '@attrs': {'site': 'US'} }},
    ...    'paginationInput': {
    ...        'pageNumber': '1',
    ...        'pageSize': '25'
    ...    },
    ...    'sortOrder': 'StartTimeNewest'
    ... }
    >>> dict2xml(dict2)
    '<paginationInput><pageNumber>1</pageNumber><pageSize>25</pageSize></paginationInput><searchFilter><categoryId site="US">222</categoryId></searchFilter><sortOrder>StartTimeNewest</sortOrder>'
    >>> dict3 = {
    ...    'parent': {'child': {'#text': 222, '@attrs': {'site': 'US', 'id': 1234}}}
    ... }
    >>> dict2xml(dict3)
    '<parent><child id="1234" site="US">222</child></parent>'
    >>> dict5 = {
    ...    'parent': {'child': {'@attrs': {'site': 'US', 'id': 1234}, }}
    ... }
    >>> dict2xml(dict5)
    '<parent><child id="1234" site="US"></child></parent>'
    >>> dict4 = {
    ...     'searchFilter': {'categoryId': {'#text': 222, '@attrs': {'site': 'US'} }},
    ...     'paginationInput': {
    ...         'pageNumber': '1',
    ...         'pageSize': '25'
    ...     },
    ...     'itemFilter': [
    ...         {'name': 'Condition',
    ...          'value': 'Used'},
    ...          {'name': 'LocatedIn',
    ...          'value': 'GB'},
    ...     ],
    ...     'sortOrder': 'StartTimeNewest'
    ... }
    >>> dict2xml(dict4)
    '<itemFilter><name>Condition</name><value>Used</value></itemFilter><itemFilter><name>LocatedIn</name><value>GB</value></itemFilter><paginationInput><pageNumber>1</pageNumber><pageSize>25</pageSize></paginationInput><searchFilter><categoryId site="US">222</categoryId></searchFilter><sortOrder>StartTimeNewest</sortOrder>'
    >>> dict2xml({})
    ''
    >>> dict2xml('<a>b</a>')
    '<a>b</a>'
    >>> dict2xml(None)
    ''
    >>> common_attrs = {'xmlns:xs': 'http://www.w3.org/2001/XMLSchema', 'xsi:type': 'xs:string'}
    >>> attrdict = { 'attributeAssertion': [
    ...     {'@attrs': {'Name': 'DevId', 'NameFormat': 'String', 'FriendlyName': 'DeveloperID'},
    ...        'urn:AttributeValue': {
    ...            '@attrs': common_attrs,
    ...            '#text': 'mydevid'
    ...        },
    ...    },            
    ...    {'@attrs': {'Name': 'AppId', 'NameFormat': 'String', 'FriendlyName': 'ApplicationID'},
    ...        'urn:AttributeValue': {
    ...            '@attrs': common_attrs,
    ...            '#text': 'myappid',
    ...        },
    ...    },
    ...    {'@attrs': {'Name': 'CertId', 'NameFormat': 'String', 'FriendlyName': 'Certificate'},
    ...        'urn:AttributeValue': {
    ...            '@attrs': common_attrs,
    ...            '#text': 'mycertid',
    ...        },
    ...    },        
    ...    ],
    ... }
    >>> print(dict2xml(attrdict))
    <attributeAssertion FriendlyName="DeveloperID" Name="DevId" NameFormat="String"><urn:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema" xsi:type="xs:string">mydevid</urn:AttributeValue></attributeAssertion><attributeAssertion FriendlyName="ApplicationID" Name="AppId" NameFormat="String"><urn:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema" xsi:type="xs:string">myappid</urn:AttributeValue></attributeAssertion><attributeAssertion FriendlyName="Certificate" Name="CertId" NameFormat="String"><urn:AttributeValue xmlns:xs="http://www.w3.org/2001/XMLSchema" xsi:type="xs:string">mycertid</urn:AttributeValue></attributeAssertion>
    '''

    xml = ''
    if root is None:
        return xml

    if isinstance(root, dict):
        for key in sorted(root.keys()):

            if isinstance(root[key], dict):
                attrs, value = attribute_check(root[key])
                
                if not value:
                    value = dict2xml(root[key])
                elif isinstance(value, dict):
                    value = dict2xml(value)

                attrs_sp = ''
                if len(attrs) > 0:
                    attrs_sp = ' '

                xml = '%(xml)s<%(tag)s%(attrs_sp)s%(attrs)s>%(value)s</%(tag)s>' % \
                    {'tag': key, 'xml': xml, 'attrs': ' '.join(attrs), 
                     'value': smart_encode(value), 'attrs_sp': attrs_sp}                          

            elif isinstance(root[key], list):
                
                for item in root[key]:
                    attrs, value = attribute_check(item)

                    if not value:
                        value = dict2xml(item)
                    elif isinstance(value, dict):
                        value = dict2xml(value)
                    
                    attrs_sp = ''
                    if len(attrs) > 0:
                        attrs_sp = ' '

                    xml = '%(xml)s<%(tag)s%(attrs_sp)s%(attrs)s>%(value)s</%(tag)s>' % \
                        {'xml': xml, 'tag': key, 'attrs': ' '.join(attrs),
                         'value': smart_encode(value), 'attrs_sp': attrs_sp}
 
            else:
                value = root[key]
                xml = '%(xml)s<%(tag)s>%(value)s</%(tag)s>' % \
                    {'xml': xml, 'tag': key, 'value': smart_encode(value)}

    elif isinstance(root, str) or isinstance(root, int) \
        or isinstance(root, unicode) or isinstance(root, long) \
        or isinstance(root, float):
        xml = '%s%s' % (xml, root)
    else:
        raise Exception('Unable to serialize node of type %s (%s)' % \
            (type(root), root))

    return xml

def getValue(response_dict, *args, **kwargs):
    args_a = [w for w in args]
    first = args_a[0]
    args_a.remove(first)

    h = kwargs.get('mydict', {})
    if h:
        h = h.get(first, {})
    else:
        h = response_dict.get(first, {})

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

def getNodeText(node):
    "Returns the node's text string."

    rc = []

    if hasattr(node, 'childNodes'):
        for cn in node.childNodes:
            if cn.nodeType == cn.TEXT_NODE:
                rc.append(cn.data)
            elif cn.nodeType == cn.CDATA_SECTION_NODE:
                rc.append(cn.data)

    return ''.join(rc)

def perftest_dict2xml():
    sample_dict = {
        'searchFilter': {'categoryId': {'#text': 222, '@attrs': {'site': 'US'} }},
        'paginationInput': {
            'pageNumber': '1',
            'pageSize': '25'
        },
        'itemFilter': [
            {'name': 'Condition',
             'value': 'Used'},
            {'name': 'LocatedIn',
             'value': 'GB'},
        ],
        'sortOrder': 'StartTimeNewest'
    }
    
    xml = dict2xml(sample_dict)   

if __name__ == '__main__':

    import timeit    
    print("perftest_dict2xml() %s" % \
        timeit.timeit("perftest_dict2xml()", number=50000,
                      setup="from __main__ import perftest_dict2xml"))

    import doctest
    failure_count, test_count = doctest.testmod()
    sys.exit(failure_count)

