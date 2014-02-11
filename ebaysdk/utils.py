# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

try:
    import xml.etree.ElementTree as ET
except:
    import cElementTree as ET # for 2.4

import re
import sys
from io import BytesIO

def to_xml(data):
    "Converts a list or dictionary to XML and returns it."

    xml = ''

    if type(data) == dict:
        xml = dict2xml(data)
    elif type(data) == list:
        xml = list2xml(data)
    else:
        xml = data

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

class object_dict(dict):
    """object view of dict, you can
    >>> a = object_dict()
    >>> a.fish = 'fish'
    >>> a['fish']
    'fish'
    >>> a['water'] = 'water'
    >>> a.water
    'water'
    >>> a.test = {'value': 1}
    >>> a.test2 = object_dict({'name': 'test2', 'value': 2})
    >>> a.test, a.test2.name, a.test2.value
    (1, 'test2', 2)
    """
    def __init__(self, initd=None):
        if initd is None:
            initd = {}
        dict.__init__(self, initd)

    def __getattr__(self, item):
        try:
            d = self.__getitem__(item)
        except KeyError:
            return None

        if isinstance(d, dict) and 'value' in d and len(d) == 1:
            return d['value']
        else:
            return d

        # if value is the only key in object, you can omit it

    def __setattr__(self, item, value):
        self.__setitem__(item, value)

    def getvalue(self, item, value=None):
        return self.get(item, {}).get('value', value)

    def __getstate__(self):
        return list(self.items())

    def __setstate__(self, items):
        self.update(items)

class xml2dict(object):

    def __init__(self):
        pass

    def _parse_node(self, node):
        node_tree = object_dict()
        # Save attrs and text, hope there will not be a child with same name
        if node.text:
            node_tree.value = node.text
        for (k,v) in list(node.attrib.items()):
            k,v = self._namespace_split(k, object_dict({'value':v}))
            node_tree[k] = v
        #Save childrens
        for child in list(node):
            tag, tree = self._namespace_split(child.tag, self._parse_node(child))
            if  tag not in node_tree: # the first time, so store it in dict
                node_tree[tag] = tree
                continue
            old = node_tree[tag]
            if not isinstance(old, list):
                node_tree.pop(tag)
                node_tree[tag] = [old] # multi times, so change old dict to a list
            node_tree[tag].append(tree) # add the new one

        return node_tree

    def _namespace_split(self, tag, value):
        """
           Split the tag  '{http://cs.sfsu.edu/csc867/myscheduler}patients'
             ns = http://cs.sfsu.edu/csc867/myscheduler
             name = patients
        """
        result = re.compile("\{(.*)\}(.*)").search(tag)
        if result:
            value.namespace, tag = result.groups()

        return (tag,value)

    def parse(self, file):
        """parse a xml file to a dict"""
        f = open(file, 'r')
        return self.fromstring(f.read())

    def fromstring(self, s):
        """parse a string"""
        t = ET.fromstring(s)
        root_tag, root_tree = self._namespace_split(t.tag, self._parse_node(t))
        return object_dict({root_tag: root_tree})


# Basic conversation goal here is converting a dict to an object allowing
# more comfortable access. `Struct()` and `make_struct()` are used to archive
# this goal.
# See http://stackoverflow.com/questions/1305532/convert-python-dict-to-object for the inital Idea
#
# The reasoning for this is the observation that we ferry arround hundreds of dicts via JSON
# and accessing them as `obj['key']` is tiresome after some time. `obj.key` is much nicer.
class Struct(object):
    """Emulate a cross over between a dict() and an object()."""
    def __init__(self, entries, default=None, nodefault=False):
        # ensure all keys are strings and nothing else
        entries = dict([(str(x), y) for x, y in list(entries.items())])
        self.__dict__.update(entries)
        self.__default = default
        self.__nodefault = nodefault

    def __getattr__(self, name):
        """Emulate Object access.

        >>> obj = Struct({'a': 'b'}, default='c')
        >>> obj.a
        'b'
        >>> obj.foobar
        'c'

        `hasattr` results in strange behaviour if you give a default value. This might change in the future.
        >>> hasattr(obj, 'a')
        True
        >>> hasattr(obj, 'foobar')
        True
        """
        if name.startswith('_'):
            # copy expects __deepcopy__, __getnewargs__ to raise AttributeError
            # see http://groups.google.com/group/comp.lang.python/browse_thread/thread/6ac8a11de4e2526f/
            # e76b9fbb1b2ee171?#e76b9fbb1b2ee171
            raise AttributeError("'<Struct>' object has no attribute '%s'" % name)
        if self.__nodefault:
            raise AttributeError("'<Struct>' object has no attribute '%s'" % name)
        return self.__default

    def __getitem__(self, key):
        """Emulate dict like access.

        >>> obj = Struct({'a': 'b'}, default='c')
        >>> obj['a']
        'b'

        While the standard dict access via [key] uses the default given when creating the struct,
        access via get(), results in None for keys not set. This might be considered a bug and
        should change in the future.
        >>> obj['foobar']
        'c'
        >>> obj.get('foobar')
        'c'
        """
        # warnings.warn("dict_accss[foo] on a Struct, use object_access.foo instead",
        #                DeprecationWarning, stacklevel=2)
        if self.__nodefault:
            return self.__dict__[key]
        return self.__dict__.get(key, self.__default)

    def get(self, key, default=None):
        """Emulate dictionary access.

        >>> obj = Struct({'a': 'b'}, default='c')
        >>> obj.get('a')
        'b'
        >>> obj.get('foobar')
        'c'
        """
        if key in self.__dict__:
            return self.__dict__[key]
        if not self.__nodefault:
            return self.__default
        return default

    def __contains__(self, item):
        """Emulate dict 'in' functionality.

        >>> obj = Struct({'a': 'b'}, default='c')
        >>> 'a' in obj
        True
        >>> 'foobar' in obj
        False
        """
        return item in self.__dict__

    def __bool__(self):
        """Returns whether the instance evaluates to False"""
        return bool(list(self.items()))

    def has_key(self, item):
        """Emulate dict.has_key() functionality.

        >>> obj = Struct({'a': 'b'}, default='c')
        >>> obj.has_key('a')
        True
        >>> obj.has_key('foobar')
        False
        """
        return item in self

    def items(self):
        """Emulate dict.items() functionality.

        >>> obj = Struct({'a': 'b'}, default='c')
        >>> obj.items()
        [('a', 'b')]
        """
        return [(k, v) for (k, v) in list(self.__dict__.items()) if not k.startswith('_Struct__')]

    def keys(self):
        """Emulate dict.keys() functionality.

        >>> obj = Struct({'a': 'b'}, default='c')
        >>> obj.keys()
        ['a']
        """
        return [k for (k, _v) in list(self.__dict__.items()) if not k.startswith('_Struct__')]

    def values(self):
        """Emulate dict.values() functionality.

        >>> obj = Struct({'a': 'b'}, default='c')
        >>> obj.values()
        ['b']
        """
        return [v for (k, v) in list(self.__dict__.items()) if not k.startswith('_Struct__')]

    def __repr__(self):
        return "<Struct: %r>" % dict(list(self.items()))

    def as_dict(self):
        """Return a dict representing the content of this struct."""
        return self.__dict__


def make_struct(obj, default=None, nodefault=False):
    """Converts a dict to an object, leaves objects untouched.

    Someting like obj.vars() = dict() - Read Only!

    >>> obj = make_struct(dict(foo='bar'))
    >>> obj.foo
    'bar'

    `make_struct` leaves objects alone.
    >>> class MyObj(object): pass
    >>> data = MyObj()
    >>> data.foo = 'bar'
    >>> obj = make_struct(data)
    >>> obj.foo
    'bar'

    `make_struct` also is idempotent
    >>> obj = make_struct(make_struct(dict(foo='bar')))
    >>> obj.foo
    'bar'

    `make_struct` recursively handles dicts and lists of dicts
    >>> obj = make_struct(dict(foo=dict(bar='baz')))
    >>> obj.foo.bar
    'baz'

    >>> obj = make_struct([dict(foo='baz')])
    >>> obj
    [<Struct: {'foo': 'baz'}>]
    >>> obj[0].foo
    'baz'

    >>> obj = make_struct(dict(foo=dict(bar=dict(baz='end'))))
    >>> obj.foo.bar.baz
    'end'

    >>> obj = make_struct(dict(foo=[dict(bar='baz')]))
    >>> obj.foo[0].bar
    'baz'
    >>> obj.items()
    [('foo', [<Struct: {'bar': 'baz'}>])]
    """
    if type(obj) == type(Struct):
        return obj
    if type(obj) == dict:
        struc = Struct(obj, default, nodefault)
        # handle recursive sub-dicts
        for key, val in list(obj.items()):
            setattr(struc, key, make_struct(val, default, nodefault))
        return struc
    elif type(obj) == list:
        return [make_struct(v, default, nodefault) for v in obj]
    else:
        return obj


# Code is based on http://code.activestate.com/recipes/573463/
def _convert_dict_to_xml_recurse(parent, dictitem, listnames):
    """Helper Function for XML conversion."""
    # we can't convert bare lists
    assert not isinstance(dictitem, list)

    if isinstance(dictitem, dict):
        # special case of attrs and text
        if '@attrs' in dictitem.keys():
            attrs = dictitem.pop('@attrs')
            for key, value in attrs.iteritems():
                parent.set(key, value) # TODO: will fail if attrs is not a dict
        if '#text' in dictitem.keys():
            text = dictitem.pop('#text')
            if sys.version_info[0] < 3:
                parent.text = unicode(text)
            else:
                parent.text = str(text)
        for (tag, child) in sorted(dictitem.items()):
            if isinstance(child, list):
                # iterate through the array and convert
                listparent = ET.Element(tag if tag in listnames.keys() else '')
                parent.append(listparent)
                for listchild in child:
                    item = ET.SubElement(listparent, listnames.get(tag, tag))
                    _convert_dict_to_xml_recurse(item, listchild, listnames)
            else:
                elem = ET.Element(tag)
                parent.append(elem)
                _convert_dict_to_xml_recurse(elem, child, listnames)
    elif not dictitem is None:
        if sys.version_info[0] < 3:
            parent.text = unicode(dictitem)
        else:
            parent.text = str(dictitem)


def dict2et(xmldict, roottag='data', listnames=None):
    """Converts a dict to an ElementTree.

    Converts a dictionary to an XML ElementTree Element::

    >>> data = {"nr": "xq12", "positionen": [{"m": 12}, {"m": 2}]}
    >>> root = dict2et(data)
    >>> ET.tostring(root, encoding="utf-8").replace('<>', '').replace('</>','')
    '<data><nr>xq12</nr><positionen><m>12</m></positionen><positionen><m>2</m></positionen></data>'

    Per default ecerything ins put in an enclosing '<data>' element. Also per default lists are converted
    to collecitons of `<item>` elements. But by provding a mapping between list names and element names,
    you van generate different elements::

    >>> data = {"positionen": [{"m": 12}, {"m": 2}]}
    >>> root = dict2et(data, roottag='xml')
    >>> ET.tostring(root, encoding="utf-8").replace('<>', '').replace('</>','')
    '<xml><positionen><m>12</m></positionen><positionen><m>2</m></positionen></xml>'

    >>> root = dict2et(data, roottag='xml', listnames={'positionen': 'position'})
    >>> ET.tostring(root, encoding="utf-8").replace('<>', '').replace('</>','')
    '<xml><positionen><position><m>12</m></position><position><m>2</m></position></positionen></xml>'

    >>> data = {"kommiauftragsnr":2103839, "anliefertermin":"2009-11-25", "prioritaet": 7,
    ... "ort": u"Hücksenwagen",
    ... "positionen": [{"menge": 12, "artnr": "14640/XL", "posnr": 1},],
    ... "versandeinweisungen": [{"guid": "2103839-XalE", "bezeichner": "avisierung48h",
    ...                          "anweisung": "48h vor Anlieferung unter 0900-LOGISTIK avisieren"},
    ... ]}

    >>> print ET.tostring(dict2et(data, 'kommiauftrag',
    ... listnames={'positionen': 'position', 'versandeinweisungen': 'versandeinweisung'}),
    ... encoding="utf-8").replace('<>', '').replace('</>','')
    ...  # doctest: +SKIP
    '''<kommiauftrag>
    <anliefertermin>2009-11-25</anliefertermin>
    <positionen>
        <position>
            <posnr>1</posnr>
            <menge>12</menge>
            <artnr>14640/XL</artnr>
        </position>
    </positionen>
    <ort>H&#xC3;&#xBC;cksenwagen</ort>
    <versandeinweisungen>
        <versandeinweisung>
            <bezeichner>avisierung48h</bezeichner>
            <anweisung>48h vor Anlieferung unter 0900-LOGISTIK avisieren</anweisung>
            <guid>2103839-XalE</guid>
        </versandeinweisung>
    </versandeinweisungen>
    <prioritaet>7</prioritaet>
    <kommiauftragsnr>2103839</kommiauftragsnr>
    </kommiauftrag>'''
    """

    if not listnames:
        listnames = {}
    root = ET.Element(roottag)
    _convert_dict_to_xml_recurse(root, xmldict, listnames)
    return root


def list2et(xmllist, root, elementname):
    """Converts a list to an ElementTree.

        See also dict2et()
    """

    basexml = dict2et({root: xmllist}, 'xml', listnames={root: elementname})
    return basexml.find(root)


def dict2xml(datadict, roottag='', listnames=None, pretty=False):
    """
    Converts a dictionary to an UTF-8 encoded XML string.
    See also dict2et()
    """
    if isinstance(datadict, dict) and len(datadict):
        root = dict2et(datadict, roottag, listnames)
        xml = to_string(root, pretty=pretty)
        xml = xml.replace('<>', '').replace('</>', '')
        return xml
    else:
        return ''


def list2xml(datalist, roottag, elementname, pretty=False):
    """Converts a list to an UTF-8 encoded XML string.

    See also dict2et()
    """
    root = list2et(datalist, roottag, elementname)
    return to_string(root, pretty=pretty)


def to_string(root, pretty=False):
    """Converts an ElementTree to a string"""

    if pretty:
        indent(root)

    tree = ET.ElementTree(root)
    fileobj = BytesIO()

    # asdf fileobj.write('<?xml version="1.0" encoding="%s"?>' % encoding)

    if pretty:
        fileobj.write('\n')

    tree.write(fileobj, 'utf-8')
    return fileobj.getvalue()


# From http://effbot.org/zone/element-lib.htm
# prettyprint: Prints a tree with each node indented according to its depth. This is
# done by first indenting the tree (see below), and then serializing it as usual.
# indent: Adds whitespace to the tree, so that saving it as usual results in a prettyprinted tree.
# in-place prettyprint formatter

def indent(elem, level=0):
    """XML prettyprint: Prints a tree with each node indented according to its depth."""
    i = "\n" + level * " "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + " "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for child in elem:
            indent(child, level + 1)
        if child:
            if not child.tail or not child.tail.strip():
                child.tail = i
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def test():
    """Simple selftest."""

    data = {"guid": "3104247-7",
            "menge": 7,
            "artnr": "14695",
            "batchnr": "3104247"}
    xmlstr = dict2xml(data, roottag='warenzugang')
    assert xmlstr == ('<warenzugang><artnr>14695</artnr>'
                      '<batchnr>3104247</batchnr><guid>3104247-7</guid><menge>7</menge></warenzugang>')

    data = {"kommiauftragsnr": 2103839,
     "anliefertermin": "2009-11-25",
     "fixtermin": True,
     "prioritaet": 7,
     "info_kunde": "Besuch H. Gerlach",
     "auftragsnr": 1025575,
     "kundenname": "Ute Zweihaus 400424990",
     "kundennr": "21548",
     "name1": "Uwe Zweihaus",
     "name2": "400424990",
     "name3": "",
     "strasse": "Bahnhofstr. 2",
     "land": "DE",
     "plz": "42499",
     "ort": "Hücksenwagen",
     "positionen": [{"menge": 12,
                     "artnr": "14640/XL",
                     "posnr": 1},
                    {"menge": 4,
                     "artnr": "14640/03",
                     "posnr": 2},
                    {"menge": 2,
                     "artnr": "10105",
                     "posnr": 3}],
     "versandeinweisungen": [{"guid": "2103839-XalE",
                              "bezeichner": "avisierung48h",
                              "anweisung": "48h vor Anlieferung unter 0900-LOGISTIK avisieren"},
                             {"guid": "2103839-GuTi",
                              "bezeichner": "abpackern140",
                              "anweisung": "Paletten höchstens auf 140 cm Packen"}]
    }

    xmlstr = dict2xml(data, roottag='kommiauftrag')

    data = {"kommiauftragsnr": 2103839,
     "positionen": [{"menge": 4,
                     "artnr": "14640/XL",
                     "posnr": 1,
                     "nve": "23455326543222553"},
                    {"menge": 8,
                     "artnr": "14640/XL",
                     "posnr": 1,
                     "nve": "43255634634653546"},
                    {"menge": 4,
                     "artnr": "14640/03",
                     "posnr": 2,
                     "nve": "43255634634653546"},
                    {"menge": 2,
                     "artnr": "10105",
                     "posnr": 3,
                     "nve": "23455326543222553"}],
     "nves": [{"nve": "23455326543222553",
               "gewicht": 28256,
               "art": "paket"},
              {"nve": "43255634634653546",
               "gewicht": 28256,
                "art": "paket"}]}

    xmlstr = dict2xml(data, roottag='rueckmeldung')

if __name__ == '__main__':
    import doctest
    import sys
    failure_count, test_count = doctest.testmod()
    d = make_struct({
        'item1': 'string',
        'item2': ['dies', 'ist', 'eine', 'liste'],
        'item3': dict(dies=1, ist=2, ein=3, dict=4),
        'item4': 10,
        'item5': [dict(dict=1, in_einer=2, liste=3)]})
    test()
    sys.exit(failure_count)

