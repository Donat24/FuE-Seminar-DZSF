from os import remove
import uuid
import collections
import math

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

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.cytoscape_id = self.id
        self.cytoscape_label = "Knoten"
        __elements__[self.id] = self
        __children__[self.id] = []
        __parents__[self.id] = []
    
    def to_cytoscape_dict(self):
        return {
            "data" : {
                "id" :              self.cytoscape_id,
                "label" :           self.cytoscape_label,
                "type" :            self.__class__.__name__.lower(),
                "isRoot":           self.is_root,
                "isLeave":          self.is_leave,
                "expected_value":   self.expected_value
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
        parent_id = node.id

        #setzt Parent Beziehung
        if self.id not in __parents__.keys():
            __parents__[self.id] = []
        __parents__[self.id].append(parent_id)

        #setzt Child Beziehung
        if parent_id not in __children__.keys():
            __children__[parent_id] = []
        __children__[parent_id].append(self.id)
    
    def remove_child(self, node):
        __children__.pop(self.id,[]).remove(node.id)
        __parents__.get(node.id,[]).remove(self.id)
    
    def remove_parent(self, node):
        __parents__.get(self.id,[]).remove(node.id)
        __children__.pop(node.id,[]).remove(self.id)
    
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
    def expected_value (self):
        raise NotImplementedError

class AndNode(Node):

    def __init__(self):
        super().__init__()
        self.cytoscape_label = "Und-Knoten"

    @property
    def expected_value (self):
        
        if len(self.children) == 0 and len(self.parents) > 0:
            raise ValueError("AndNode can't be a leave")
        
        ret = 0
        for child in self.children:
            ret += child.expected_value
        return ret

class OrNode(Node):

    def __init__(self):
        super().__init__()
        self.cytoscape_label = "Oder-Knoten"

    @property
    def expected_value (self):
        
        if len(self.children) == 0 and len(self.parents) > 0:
            raise ValueError("OrNode can't be a leave")
        
        ret = 0
        for child in self.children:
            ret += child.expected_value
        return ret

class ValueNode(Node):

    def __init__(self):
        super().__init__()
        self.cytoscape_label = "Werte-Knoten"
        self.__expected_value__ = 13
    
    def add_child(self, node):
        raise ValueError("ValueNode must be a leave")

    @property
    def expected_value (self):
        return self.__expected_value__
    
