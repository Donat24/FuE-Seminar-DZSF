from os import remove
import uuid
import math
import scipy.stats as stats
import numpy as np

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
                "expected_value":   self.calculate_expected_value,
                "variance":         self.calculate_variance,
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
    def no_connections(self):
        return (len(self.children) == 0) and (len(self.parents) == 0)

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
    def calculate_expected_value (self):
        raise NotImplementedError

    @property
    def calculate_variance (self):
        raise NotImplementedError
    
    @property
    def properties (self):
        return {}

class AndNode(Node):

    def __init__(self,label="Und-Knoten",description="",position=(0,0)):
        super().__init__(label=label,description=description,position=position)

    @property
    def calculate_expected_value (self):
        
        if self.is_leave:
            raise BadTreeException("AndNode can't be a leave")
        
        ret = 0
        for child in self.children:
            ret += child.calculate_expected_value
        return ret
    
    @property
    def calculate_variance (self):
        
        if self.is_leave:
            raise BadTreeException("AndNode can't be a leave")
        
        ret = 0
        for child in self.children:
            ret += child.calculate_variance
        return ret

class OrNode(Node):

    def __init__(self, label="Oder-Knoten",description="",position=(0,0)):
        super().__init__(label=label,description=description,position=position)

class ValueNode(Node):

    def __init__(self, expected_value = 1, variance = 0,label="Werte-Knoten",description="",position=(0,0)):
        super().__init__(label=label,description=description,position=position)
        self.expected_value = expected_value
        self.variance = variance

    @property
    def calculate_expected_value (self):
        if len(self.children) > 1:
            raise BadTreeException("ValueNode can only have one children")
        
        if self.is_leave:
            return self.expected_value
        
        else:
            child = self.children[0]
            return self.expected_value * child.calculate_expected_value
    
    @property
    def calculate_variance (self):
        if len(self.children) > 1:
            raise BadTreeException("ValueNode can only have one children")
        
        if self.is_leave:
            return self.variance
        
        else:
            child = self.children[0]
            return self.expected_value * self.expected_value * child.calculate_variance + \
                child.calculate_expected_value * child.calculate_expected_value * self.variance + \
                self.variance * child.calculate_variance
    
    
    @property
    def cytoscape_text (self):
        return f"{self.cytoscape_descr}\nµ={self.expected_value}\nσ²={self.variance}"

    @property
    def properties (self):
        return {
            "expected_value" : self.expected_value,
            "variance": self.variance
        }
    
    #Properties löschen Sample Data
    @property
    def expected_value (self):
        return self.__expected_value__
    
    @expected_value.setter
    def expected_value(self,value):
        self.__expected_value__ = value
        self.__sample_data__ = None
    
    @property
    def variance (self):
        return self.__variance__
    
    @variance.setter
    def variance(self,value):
        self.__variance__ = value
        self.__sample_data__ = None
    
    @property
    def standard_deviation (self):
        return math.sqrt(self.variance)


    def get_sample_data(self,size=1000):
        if self.__sample_data__ is None or len(self.__sample_data__) == size:
            if self.variance == 0:
                self.__sample_data__ = np.full(
                    shape=size,
                    fill_value=self.expected_value
                )
            else:
                lower, upper = 0, 1
                self.__sample_data__ = stats.truncnorm.rvs(
                    (lower - self.expected_value) / self.standard_deviation,
                    (upper - self.expected_value) / self.standard_deviation,
                    size=size
                )
        return self.__sample_data__
