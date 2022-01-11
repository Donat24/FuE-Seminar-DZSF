from dash import Dash, html, Input, Output, State
import plotly.express as px
import nodes
import numpy as np

#scheiß dash
n_clicks = {}

#scheiß dash
def add_callbacks(app):
    app.callback(
        Output("cytoscape", "elements"),

        Input("button-delete-all","n_clicks"),
        Input("button-add-node","n_clicks"),
        Input("node-selector","value"),
        Input("button-add-edge","n_clicks"),
        Input("button-rev-edge","n_clicks"),
        Input("slider-expected-value","value"),
        Input("slider-variance","value"),
        
        State("cytoscape", "selectedNodeData"),
        State("cytoscape", "selectedEdgeData"))(cytoscape_callback)
    
    app.callback(
        Output("button-add-node","children"),
        Input("cytoscape", "selectedNodeData"))(change_btn_add_node_text_callback)

    app.callback(
        Output("button-add-edge","children"),
        Input("cytoscape", "selectedEdgeData"))(change_btn_add_edge_text_callback)
    
    app.callback(
        Output("textarea-description","value"),
        Input("cytoscape", "selectedNodeData"))(change_description_callback)
    
    app.callback(
        Output("slider-expected-value","value"),
        Input("cytoscape", "selectedNodeData"))(change_slider_expected_value_callback)
    
    app.callback(
        Output("slider-variance","value"),
        Input("cytoscape", "selectedNodeData"))(change_slider_variance_callback)
    
    app.callback(
        Output("histogramm-node","figure"),
        Input("cytoscape", "selectedNodeData"),
        Input("slider-expected-value","value"),
        Input("slider-variance","value"))(change_histogramm_node_callback)


def cytoscape_callback(btn_delete_all,btn_add_node,node_type,btn_add_edge,btn_rev_edge,
        slider_expected_value, slider_variance,
        cytoscape_node_list,cytoscape_edge_list):

    def check_and_set (name,counter):
        if n_clicks.get(name, 0) != counter:
            n_clicks[name] = counter
            return True
        return False

    if check_and_set("btn_delete_all",btn_delete_all):
        click_button_delete_all(btn_delete_all)

    if check_and_set("btn_add_node",btn_add_node):
        click_button_add_or_remove_node(btn_add_node,node_type,cytoscape_node_list)
    
    if check_and_set("btn_add_edge",btn_add_edge):
        click_button_add_or_remove_edge(btn_add_edge,cytoscape_node_list,cytoscape_edge_list)

    if check_and_set("btn_rev_edge",btn_rev_edge):
        click_button_rev_edge(btn_add_edge,cytoscape_edge_list)
    
    if check_and_set("slider_expected_value",slider_expected_value) or check_and_set("slider_variance",slider_variance):
        change_expected_value_variance(cytoscape_node_list,slider_expected_value,slider_variance)

    return nodes.get_cytoscape_elements_list()

#Click Events
def click_button_delete_all(n):
    nodes.__elements__= {}
    nodes.__children__= {}
    nodes.__parents__= {}

def click_button_add_or_remove_node(n,node_type,node_list):
    
    #Hinzufügen
    if node_list is None or len(node_list) == 0:
        if node_type is None or node_type == "value":
            node = nodes.ValueNode()
        elif node_type == "and":
            node = nodes.AndNode()
        elif node_type == "or":
            node = nodes.OrNode()

    
    #Löschen
    else:
        for entry in node_list:
            node = nodes.__elements__[entry["id"]]
            node.remove()
            del(node)

def click_button_add_or_remove_edge(n,node_list,edge_list):
    
    #Hinzufügen
    if node_list is not None and len(node_list) == 2:
        parent = nodes.__elements__[node_list[0]["id"]]
        child  = nodes.__elements__[node_list[1]["id"]]
        parent.add_child(child)
    
    #Löschen
    elif edge_list is not None:
        for entry in edge_list:
            parent = nodes.__elements__[entry["source"]]
            child = nodes.__elements__[entry["target"]]
            parent.remove_child(child)

def click_button_rev_edge(n,edge_list):
    if edge_list is not None:
        for entry in edge_list:
            parent = nodes.__elements__[entry["source"]]
            child = nodes.__elements__[entry["target"]]
            parent.remove_child(child)
            child.add_child(parent)

def change_expected_value_variance(node_list, expected_value, variance):
    if node_list is not None and len(node_list) == 1:
        entry = node_list[0]
        node = nodes.__elements__[entry["id"]]
        if isinstance(node,nodes.ValueNode):
            node.expected_value = expected_value
            node.variance = variance

#Ändert UI TEXTE
def change_btn_add_node_text_callback (node_list):
    if node_list is not None and len(node_list) > 0:
        return "Knoten -"
    else:
        return "Knoten +"

def change_btn_add_edge_text_callback(edge_list):
    if edge_list is not None and len(edge_list) > 0:
        return "Kante -"
    else:
        return "Kante +"

#Ändert UI WERTE
def change_description_callback(node_list):
    if node_list is not None and len(node_list) == 1:
        entry = node_list[0]
        node = nodes.__elements__[entry["id"]]
        return node.cytoscape_descr
    
    return ""

def change_slider_expected_value_callback(node_list):
    if node_list is not None and len(node_list) == 1:
        entry = node_list[0]
        node = nodes.__elements__[entry["id"]]
        if isinstance(node,nodes.ValueNode):
            return node.expected_value
    
    return 0

def change_slider_variance_callback(node_list):
    if node_list is not None and len(node_list) == 1:
        entry = node_list[0]
        node = nodes.__elements__[entry["id"]]
        if isinstance(node,nodes.ValueNode):
            return node.variance
    
    return 0

def change_histogramm_node_callback(node_list, slider_expected_value, slider_variance):
    
    data = []

    if node_list is not None and len(node_list) == 1:
        entry = node_list[0]
        node = nodes.__elements__[entry["id"]]
        if isinstance(node,nodes.ValueNode):
            data = node.get_sample_data()
    

    return px.histogram(data, nbins=20, range_x=[0, 1], histnorm="percent")