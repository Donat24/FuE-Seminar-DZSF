from os import remove
import uuid
import collections
import math

#Eigene Exception
class BadTreeException(Exception):
    pass

#Referenzen
__elements__ = {}
__children__ = {}
__parents__ = {}

def get_cytoscape_elements_list():
    
    nodes = []
    for element in __elements__.values():
        nodes.append(element.to_cytoscape_dict())
    
    edges=[]
    for key, values in __children__.items():
        for value in values:
            edges.append({"data": {"source": key, "target": value, "type" : "edge"}})
    
    return nodes + edges
  

class Node(object):

    def __init__(self,label="Knoten",description="",position=(0,0)):
        self.id = str(uuid.uuid4())
        self.cytoscape_id = self.id
        self.cytoscape_label = label
        self.cytoscape_descr = description
        self.position = position
        __elements__[self.id] = self
        __children__[self.id] = []
        __parents__[self.id] = []
    
    def to_cytoscape_dict(self):
        return {
            "data" : {
                "id" :              self.cytoscape_id,
                "label" :           self.cytoscape_label,
                "desc" :            self.cytoscape_descr,
                "text":             self.cytoscape_text,
                "type" :            self.__class__.__name__.lower(),
                "isRoot":           self.is_root,
                "isLeave":          self.is_leave,
                "calculation":      self.calculation,
                "properties":       self.properties,
            },

            "position": {
                "x" : self.x,
                "y" : self.y
            }
        }
    
    def add_child(self,node):
        
        child_id = node.id

        #setzt Child Beziehung
        if self.id not in __children__.keys():
            __children__[self.id] = []
        __children__[self.id].append(child_id)

        #setzt Parent Beziehung
        if child_id not in __parents__.keys():
            __parents__[child_id] = []
        __parents__[child_id].append(self.id)
    
    def add_parent(self,node):
        node.add_child(self)
    
    def remove_child(self, node):
        __children__.pop(self.id,[]).remove(node.id)
        __parents__.get(node.id,[]).remove(self.id)
    
    def remove_parent(self, node):
        node.remove_child(self)
    
    def remove(self):
        
        for child in self.children:
            self.remove_child(child)
        
        for parent in self.parents:
            self.remove_parent(parent)

        __elements__.pop(self.id,None)
        __children__.pop(self.id,None)
        __parents__.pop(self.id,None)
    
    @property
    def is_root(self):
        return (len(self.children) > 0) and (len(self.parents) == 0)
    
    @property
    def is_leave(self):
        return (len(self.children) == 0) and (len(self.parents) > 0)

    @property
    def children (self):
        return [__elements__[child_id] for child_id in __children__.get(self.id,[])]
    
    @property
    def parents (self):
        return [__elements__[parent_id] for parent_id in __parents__.get(self.id,[])]
    
    @property
    def cytoscape_text (self):
        return self.cytoscape_descr

    @property
    def position (self):
        return (self.x, self.y)
    
    @position.setter
    def position(self,value):
        self.x = value[0]
        self.y = value[1]

    @property
    def calculation (self):
        raise NotImplementedError
    
    @property
    def properties (self):
        return {}

class AndNode(Node):

    def __init__(self,label="Und-Knoten",description="",position=(0,0)):
        super().__init__(label=label,description=description,position=position)

    @property
    def calculation (self):
        
        if self.is_leave:
            raise BadTreeException("AndNode can't be a leave")
        
        ret = 0
        for child in self.children:
            ret += child.calculation
        return ret

class OrNode(Node):

    def __init__(self, label="Oder-Knoten",description="",position=(0,0)):
        super().__init__(label=label,description=description,position=position)

    @property
    def calculation (self):
        
        if self.is_leave:
            raise BadTreeException("OrNode can't be a leave")
        
        ret = 0
        for child in self.children:
            ret += child.calculation
        return ret

class ValueNode(Node):

    def __init__(self, expected_value = 1, variance = 0,label="Werte-Knoten",description="",position=(0,0)):
        super().__init__(label=label,description=description,position=position)
        self.expected_value = expected_value
        self.variance = variance

    @property
    def calculation (self):
        if len(self.children) > 1:
            raise BadTreeException("ValueNode can only have one children")
        return self.expected_value
    
    @property
    def cytoscape_text (self):
        return f"{self.cytoscape_descr}\nµ={self.expected_value}\nσ²={self.variance}"

    @property
    def properties (self):
        return {
            "expected_value" : self.expected_value,
            "variance": self.variance
        }
    
