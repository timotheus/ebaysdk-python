try:
    import xml.etree.ElementTree as ET
except:
    import cElementTree as ET # for 2.4

import re
        
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
        
        d = self.__getitem__(item)
        
        if isinstance(d, dict) and 'value' in d and len(d) == 1:
            return d['value']
        else:
            return d
    
        # if value is the only key in object, you can omit it
            
    def __setattr__(self, item, value):
        self.__setitem__(item, value)

    def getvalue(self, item, value=None):
        return self.get(item, object_dict()).get('value', value)

    def __getstate__(self):
        return self.items()

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
        for (k,v) in node.attrib.items():
            k,v = self._namespace_split(k, object_dict({'value':v}))
            node_tree[k] = v
        #Save childrens
        for child in node.getchildren():
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


class dict2xml:
    xml = ""
    level = 0

    def __init__(self,encoding=None,attributes=False):
        self.xml = ""
        self.level = 0
        self.encoding = encoding
        self.attributes = attributes

    def __del__(self):
        pass

    def setXml(self,Xml):
        self.xml = Xml

    def setLevel(self,Level):
        self.level = Level

    def tostring(self,d):
        return self.dict2xml(d)

    def dict2xml(self,map):
        if type(map) == object_dict or type(map) == dict:
            for key, value in map.items():
                keyo = key
                if self.attributes:
                    # FIXME: This assumes the attributes do not require encoding
                    keyc = re.sub(r' .+$',r'',key)
                else:
                    keyc = key
                if type(value) == object_dict or type(value) == dict:
                    if(len(value) > 0):
                        self.xml += "  "*self.level
                        self.xml += "<%s>\n" % (keyo)
                        self.level += 1
                        self.dict2xml(value)
                        self.level -= 1
                        self.xml += "  "*self.level
                        self.xml += "</%s>\n" % (keyc)
                    else:
                        self.xml += "  "*(self.level)
                        self.xml += "<%s></%s>\n" % (keyo,keyc)
                elif type(value) == list:
                    for v in value:
                        self.dict2xml({key:v})
                else:
                    self.xml += "  "*(self.level)
                    self.xml += "<%s>%s</%s>\n" % (keyo,self.encode(value),keyc)
        else:
            self.xml += "  "*self.level
            self.xml += "<%s>%s</%s>\n" % (keyo,self.encode(value),keyc)
        return self.xml

    def encode(self,str1):
        if type(str1) != str and type(str1) != unicode:
            str1 = str(str1)
        if self.encoding:
            str1 = str1.encode(self.encoding)
        str2 = ''
        for c in str1:
            if c == '&':
                str2 += '&#x26;'
            elif c == '<':
                str2 += '&#x60;'
            elif c == '>':
                str2 += '&#x62;'
            else:
                str2 += c
        return str2

def list_to_xml(name, l, stream):
   for d in l:
      dict_to_xml(d, name, stream)

def dict_to_xml(d, root_node_name, stream):
   """ Transform a dict into a XML, writing to a stream """
   stream.write('\n<' + root_node_name)
   attributes = StringIO() 
   nodes = StringIO()
   for item in d.items():
      key, value = item
      if isinstance(value, dict):
         dict_to_xml(value, key, nodes)
      elif isinstance(value, list):
         list_to_xml(key, value, nodes)
      elif isinstance(value, str) or isinstance(value, unicode):
         attributes.write('\n  %s="%s" ' % (key, value))
      else:
         raise TypeError('sorry, we support only dicts, lists and strings')

   stream.write(attributes.getvalue())
   nodes_str = nodes.getvalue()
   if len(nodes_str) == 0:
      stream.write('/>')
   else:
      stream.write('>')
      stream.write(nodes_str)
      stream.write('\n</%s>' % root_node_name)

def dict_from_xml(xml):
   """ Load a dict from a XML string """

   def list_to_dict(l, ignore_root = True):
      """ Convert our internal format list to a dict. We need this
          because we use a list as a intermediate format during xml load """
      root_dict = {}
      inside_dict = {}
      # index 0: node name
      # index 1: attributes list
      # index 2: children node list
      root_dict[l[0]] = inside_dict
      inside_dict.update(l[1])
      # if it's a node containing lot's of nodes with same name,
      # like <list><item/><item/><item/><item/><item/></list>
      for x in l[2]:
         d = list_to_dict(x, False)
         for k, v in d.iteritems():
            if not inside_dict.has_key(k):
               inside_dict[k] = []

            inside_dict[k].append(v)

      ret = root_dict
      if ignore_root:
          ret = root_dict.values()[0]

      return ret

   class M:
      """ This is our expat event sink """
      def __init__(self):
         self.lists_stack = []
         self.current_list = None
      def start_element(self, name, attrs):
         l = []
         # root node?
         if self.current_list is None:
            self.current_list = [name, attrs, l]
         else:
            self.current_list.append([name, attrs, l])

         self.lists_stack.append(self.current_list)
         self.current_list = l         
         pass

      def end_element(self, name):
         self.current_list = self.lists_stack.pop()
      def char_data(self, data):
         # We don't write char_data to file (beyond \n and spaces).
         # What to do? Raise?
         pass

   p = expat.ParserCreate()
   m = M()

   p.StartElementHandler = m.start_element
   p.EndElementHandler = m.end_element
   p.CharacterDataHandler = m.char_data

   p.Parse(xml)

   d = list_to_dict(m.current_list)

   return d

class ConfigHolder:
    def __init__(self, d=None):
        """
        Init from dict d
        """
        if d is None:
            self.d = {}
        else:
            self.d = d

    def __str__(self):
        return self.d.__str__()

    __repr__ = __str__

    def load_from_xml(self, xml):
        self.d = dict_from_xml(xml)

    def load_from_dict(self, d):
        self.d = d

    def get_must_exist(self, key):
        v = self.get(key)

        if v is None:
            raise KeyError('the required config key "%s" was not found' % key)

        return v

    def __getitem__(self, key):
        """
        Support for config['path/key'] syntax
        """
        return self.get_must_exist(key)

    def get(self, key, default=None):
        """
        Get from config using a filesystem-like syntax

        value = 'start/sub/key' will
        return config_map['start']['sub']['key']
        """
        try:
            d = self.d

            path = key.split('/')
            # handle 'key/subkey[2]/value/'
            if path[-1] == '' :
                path = path[:-1]

            for x in path[:len(path)-1]:
                i = x.find('[')
                if i:
                   if x[-1] != ']':
                      raise Exception('invalid syntax')
                   index = int(x[i+1:-1])

                   d = d[x[:i]][index]
                else:
                   d = d[x]

            return d[path[-1]]

        except:
            return default

