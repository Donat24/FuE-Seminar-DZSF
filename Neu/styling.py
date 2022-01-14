
import nodes
import numpy as np


#Funktionen FÜR MAPPER
def text_normal(node):

    #VALUE NODE 
    if isinstance(node,nodes.ValueNode):
        return f"{node.cytoscape_descr}\nµ={node.expected_value}\nσ²={node.variance}"
    
    #RESULT NODE
    elif isinstance(node,nodes.ResultNode):
        #try:
        if node.valide_subtree:
            monte_carlo    = node.monte_carlo()
            expected_value = np.mean(monte_carlo)
            variance       = np.var(monte_carlo)

            return f"-Monte-Carlo-\nµ={expected_value:.2f}\nσ²={variance:.2f}"
        
        return "?"
    
        #except:
        #    return "?"

    
    return node.cytoscape_descr

#Funktionen
def text_result(node):
        
    try:
        
        if node.valide_subtree:
            return f"-Ergebnisse-\nµ={node.calculate_expected_value:.2f}\nσ²={node.calculate_variance:.2f}"
        
        return "?"
    
    except:
        return "?"

#Funktionen
def text_monte_carlo(node):
        
    try:
        
        if node.valide_subtree:
            monte_carlo    = node.monte_carlo()
            expected_value = np.mean(monte_carlo)
            variance       = np.var(monte_carlo)

            return f"-Monte-Carlo-\nµ={expected_value:.2f}\nσ²={variance:.2f}"
        
        return "?"
    
    except:
        return "?"

#MAPPER
nodes.__mapper__ = {
    "text_normal"       : text_normal,
    "text_result"       : text_result,
    "text_monte_carlo"  : text_monte_carlo
}

#STYLESHEETS
cytoscape_normal = [
    {
        'selector': ':selected',
        'style': { 'color': 'CadetBlue', 'background-color': 'CadetBlue' }
    },
    {
        'selector': 'node',             
        'style': { 'content': 'data(text_normal)', 'color': 'grey', 'text-wrap': 'wrap'}
    },
    {
        'selector': '[!valide_node]',             
        'style': {'background-color': 'red', 'text-wrap': 'wrap'}
    },
    {
        'selector': '.resultnode',
        'style': {'content': 'data(text_normal)', "shape":"roundrectangle", "color":'Bisque', 'background-color': 'Bisque', 'text-wrap': 'wrap'}
    },
    {
        'selector': 'edge',
        'style': {'curve-style': 'bezier','source-arrow-shape': 'triangle'}
    },
]

cytoscape_result = [
    {
        'selector': ':selected',
        'style': { 'color': 'CadetBlue', 'background-color': 'CadetBlue' }
    },
    {
        'selector': 'node',
        'style': {'content': 'data(text_result)', "shape":"roundrectangle", "color":'Bisque', 'background-color': 'Bisque', 'text-wrap': 'wrap'}
    },          
    {
        'selector': 'edge',
        'style': {'line-style':'dashed', 'background-color': 'Bisque'}
    },
]

cytoscape_monte_carlo = [
    {
        'selector': ':selected',
        'style': { 'color': 'CadetBlue', 'background-color': 'CadetBlue' }
    },
    {
        'selector': 'node',
        'style': {'content': 'data(text_monte_carlo)', "shape":"roundrectangle", "color":'Bisque', 'background-color': 'Bisque', 'text-wrap': 'wrap'}
    },          
    {
        'selector': 'edge',
        'style': {'line-style':'dashed', 'background-color': 'Bisque'}
    },
]

cytoscape_stylesheet = [cytoscape_normal,cytoscape_result, cytoscape_monte_carlo]