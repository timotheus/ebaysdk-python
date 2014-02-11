# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

try:
    from lxml import etree as ET
    print("running with lxml.etree")
except ImportError:    
    try:
        # Python 2.5
        import xml.etree.cElementTree as ET
        print("running with cElementTree on Python 2.5+")
    except ImportError:
    
        try:
            # Python 2.5
            import xml.etree.ElementTree as ET
            print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as ET
                print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as ET
                    print("running with ElementTree")
                except ImportError:
                    print("Failed to import ElementTree from any known place")

def to_xml(data):
    "Converts a list or dictionary to XML and returns it."

    if isinstance(data, str):
        return data
    else:
        return dicttoxml(data)

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
            for ak, av in root.pop('@attrs').iteritems():
                attrs.append('%s="%s"' % (ak, av))

    return attrs, value

def dicttoxml(root):
    '''
    Doctests:
    >>> dict1 = {'Items': [{'ItemId': 1234}, {'ItemId': 2222}]}
    >>> dicttoxml(dict1)
    '<Items><ItemId>1234</ItemId><ItemId>2222</ItemId></Items>'
    >>> dict2 = {
    ...    'searchFilter': {'categoryId': {'#text': 222, '@attrs': {'site': 'US'} }},
    ...    'paginationInput': [
    ...        {'pageNumber': '1'},
    ...        {'pageSize': '25'}
    ...    ],
    ...    'sortOrder': 'StartTimeNewest'
    ... }
    >>> dicttoxml(dict2)
    '<paginationInput><pageNumber>1</pageNumber><pageSize>25</pageSize></paginationInput><sortOrder>StartTimeNewest</sortOrder><searchFilter><categoryId site="US">222</categoryId></searchFilter>'
    >>> dict3 = {
    ...    'parent': {'child': {'#text': 222, '@attrs': {'site': 'US', 'id': 1234}}}
    ... }
    >>> dicttoxml(dict3)
    '<parent><child site="US" id="1234">222</child></parent>'
    '''

    xml = ''
    if isinstance(root, dict):
        for key in root.keys():

            if isinstance(root[key], dict):
                attrs, value = attribute_check(root[key])
                
                if not value:
                    value = dicttoxml(root[key])

                attrs_sp = ''
                if len(attrs) > 0:
                    attrs_sp = ' '

                xml = '%(xml)s<%(tag)s%(attrs_sp)s%(attrs)s>%(value)s</%(tag)s>' % \
                    {'tag': key, 'xml': xml, 'attrs': ' '.join(attrs), 
                     'value': value, 'attrs_sp': attrs_sp}                          

            elif isinstance(root[key], list):
                xml = '%s<%s>' % (xml, key)

                for item in root[key]:
                    attrs, value = attribute_check(item)

                    if not value:
                        value = dicttoxml(item)

                    xml = '%s%s' % (xml, value)

                xml = '%s</%s>' % (xml, key)

            else:
                value = root[key]
                xml = '%(xml)s<%(tag)s>%(value)s</%(tag)s>' % \
                    {'xml': xml, 'tag': key, 'value': value}

    else:
        raise Exception('Unable to serialize node of type %s (%s)' % (type(root), root))

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

if __name__ == '__main__':
    import doctest
    import sys
    failure_count, test_count = doctest.testmod()
    sys.exit(failure_count)

