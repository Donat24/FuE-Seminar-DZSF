from ast import And
from os import remove
import uuid
import math
import scipy.stats as stats
import numpy as np

#Eigene Exception
class BadTreeException(Exception):
    def __init__(self, message=None, node=None, *args: object) -> None:
        super().__init__(message,*args)
        self.node = node

#Referenzen
__elements__ = {}
__children__ = {}
__parents__ = {}

#Fügt Elemente dem Cytoscope-Dict hinzu
__mapper__= {}

def get_cytoscape_elements_list():
    
    nodes = []
    for element in __elements__.values():
        nodes.append(element.to_cytoscape_dict(__mapper__))
    
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
        self.classes = [self.__class__.__name__.lower()]

        __elements__[self.id] = self
        __children__[self.id] = []
        __parents__[self.id] = []
    
    def to_cytoscape_dict(self,data_mapper={}):
        
        #Standard Object
        cytoscape_obj = {
            "data" : {
                "id" :              self.cytoscape_id,
                "text":             self.cytoscape_text,
                "isRoot":           self.is_root,
                "isLeave":          self.is_leave,
                "no_connections":   self.no_connections,
                "valide_node":      self.valide_node,
                "valide_subtree":   self.valide_subtree,
            },

            "classes" : " ".join(cls for cls in self.classes),

            "position": {
                "x" : self.x,
                "y" : self.y
            }
        }

        #Überschreibt Werte
        for mapping,mapped_function in data_mapper.items():
            
            mapper_result = mapped_function(self)
            if mapper_result is not None:
                cytoscape_obj["data"][mapping] = mapper_result
        
        return cytoscape_obj
    
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
        __children__.get(self.id,[]).remove(node.id)
        __parents__.get (node.id,[]).remove(self.id)
    
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
    def cytoscape_text(self):
        return self.cytoscape_descr

    @property
    def valide_node(self):
        raise NotImplementedError
    
    @property
    def valide_subtree(self):
        return self.valide_node and all([child.valide_subtree for child in self.children])

    @property
    def children (self):
        return [__elements__[child_id] for child_id in __children__.get(self.id,[])]
    
    @property
    def parents (self):
        return [__elements__[parent_id] for parent_id in __parents__.get(self.id,[])]

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
    
    def monte_carlo (self,size):
        raise NotImplementedError

class AndNode(Node):

    def __init__(self,label="Und-Knoten",description="",position=(0,0)):
        super().__init__(label=label,description=description,position=position)

    @property
    def valide_node(self):
        
        if self.is_leave or self.no_connections:
            return False

        return True

    @property
    def calculate_expected_value (self):
        
        if not self.valide_node:
            raise BadTreeException("AndNode need at least one child",node=self)
        
        expected_value = self.children[0].calculate_expected_value

        for child in self.children[1:]:
            expected_value *= child.expected_value
        
        return expected_value
    
    @property
    def calculate_variance (self):
        
        if not self.valide_node:
            raise BadTreeException("AndNode need at least one child",node=self)
        
        variance = self.children[0].calculate_variance
        expected_value = self.children[0].calculate_expected_value
        
        for child in self.children[1:]:
            #update variance
            variance = expected_value * expected_value * child.calculate_variance + \
                child.calculate_expected_value * child.calculate_expected_value * variance + \
                variance * child.calculate_variance
            
            #update expected_value
            expected_value *= child.calculate_expected_value
        
        return variance
    
    def monte_carlo(self, size=1000):
        
        if not self.valide_node:
            raise BadTreeException("AndNode need at least one child",node=self)
        
        monte_carlo = self.children[0].monte_carlo(size)
        
        for child in self.children[1:]:
            monte_carlo *= child.monte_carlo(size)
        
        return monte_carlo

class OrNode(Node):

    def __init__(self, label="Oder-Knoten",description="",position=(0,0)):
        super().__init__(label=label,description=description,position=position)

class ResultNode(Node):

    def __init__(self, label="Result-Knoten",description="",position=(0,0)):
        super().__init__(label=label,description=description,position=position)
    
    @property
    def valide_node(self):
        return len(self.children) == 1

    @property
    def calculate_expected_value (self):
        if not self.valide_node:
            raise BadTreeException("ResultNode needs one child")

        child = self.children[0]
        return child.calculate_expected_value

    @property
    def calculate_variance (self):
        if not self.valide_node:
            raise BadTreeException("ResultNode needs one child")

        child = self.children[0]
        return child.calculate_variance
    
    def monte_carlo (self,size=1000):
        if not self.valide_node:
            raise BadTreeException("ResultNode needs one child")

        child = self.children[0]
        return child.monte_carlo(size)



class ValueNode(Node):

    def __init__(self, expected_value = 1, variance = 0,label="Werte-Knoten",description="",position=(0,0)):
        super().__init__(label=label,description=description,position=position)
        self.expected_value = expected_value
        self.variance = variance
    
    @property
    def valide_node(self):
        return len(self.children) <= 1

    @property
    def calculate_expected_value (self):
        if not self.valide_node:
            raise BadTreeException("ValueNode can only have one children")
        
        if self.is_leave or self.no_connections:
            return self.expected_value
        
        child = self.children[0]
        return self.expected_value * child.calculate_expected_value
    
    @property
    def calculate_variance (self):
        if not self.valide_node:
            raise BadTreeException("ValueNode can only have one children")
        
        if self.is_leave or self.no_connections:
            return self.variance
        
        child = self.children[0]
        return self.expected_value * self.expected_value * child.calculate_variance + \
            child.calculate_expected_value * child.calculate_expected_value * self.variance + \
            self.variance * child.calculate_variance
    
    def monte_carlo(self, size=1000):
        if not self.valide_node:
            raise BadTreeException("ValueNode can only have one children")
        
        if self.is_leave or self.no_connections:
            return self.get_sample_data(size)
        
        child = self.children[0] 
        return child.monte_carlo(size) * self.get_sample_data(size)


    def get_sample_data(self,size=1000):
        if self.__sample_data__ is None or len(self.__sample_data__) != size:
            
            if self.variance == 0:
                self.__sample_data__ = np.full(
                    shape=size,
                    fill_value=self.expected_value,
                    dtype=np.float64
                )
            
            else:
                lower, upper = 0, 1
                self.__sample_data__ = stats.truncnorm.rvs(
                    (lower - self.expected_value) / self.standard_deviation,
                    (upper - self.expected_value) / self.standard_deviation,
                    loc=self.expected_value,
                    scale = self.standard_deviation,
                    size=size
                )
        
        return self.__sample_data__
    
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