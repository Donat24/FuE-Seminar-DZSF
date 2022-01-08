from dash import Dash, html, Input, Output, State
import nodes

#scheiß dash
n_clicks = {}

#scheiß dash
def add_callbacks(app):
    app.callback(
        Output("cytoscape", "elements"),
        Input("button-add-node","n_clicks"),
        Input("node-selector","value"),
        Input("button-add-edge","n_clicks"),
        Input("button-rev-edge","n_clicks"),
        State("cytoscape", "selectedNodeData"),
        State("cytoscape", "selectedEdgeData"))(callback)


def callback(btn_add_node,node_type,btn_add_edge,btn_rev_edge,cytoscape_node_list,cytoscape_edge_list):
    
    def check_and_set (name,counter):
        if n_clicks.get(name, 0) != counter:
            n_clicks[name] = counter
            return True
        return False

    if check_and_set("btn_add_node",btn_add_node):
        click_button_add_or_remove_node(btn_add_node,node_type,cytoscape_node_list)
    
    if check_and_set("btn_add_edge",btn_add_edge):
        click_button_add_or_remove_edge(btn_add_edge,cytoscape_node_list,cytoscape_edge_list)

    if check_and_set("btn_rev_edge",btn_rev_edge):
        click_button_rev_edge(btn_add_edge,cytoscape_edge_list)

    return nodes.get_cytoscape_elements_list()

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