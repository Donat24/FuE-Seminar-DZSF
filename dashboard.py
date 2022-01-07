#todo: Methode anpassen
    # todo: fehlende Knoten noch hinzufügen zu train_hit_passenger, next_train_incoming
    # da dort mehrere Knoten dieser Art existieren

# todo: Auch Werte von feststehenden Knoten im Backend über Node-Klasse einlesen

# todo: Knoten optisch anpassen für: AND-Knoten und Unfall-Knoten

# todo: Nulldivision in MCS beachten, wenn keine Varianz eingetragen ist

# todo: Auslesen von EW und VAR in backend.Node verbessern (Leerzeichen, kein Leerzeichen) 

# todo: WENN REIHENFOLGE DER NOTEN VERÄNDERT IM DASHBOARD; AUCH BERECHNUNG ANDERS; ANPASSEN!!!!!!

# todo: KNOTEN HINZUFÜGEN UND PARENT VERGEBEN

# todo: neuen Node nur einfügen, wenn die ID, bzw Label noch nicht existiert


# Steps:
#   1) Tree-Lib raussuchen, wo man durch tree iterieren kann
#   2) Berechnungen durch tree ermöglichen
#   3) Einfügen neuer nodes ermöglichen (Unterscheidung zwischen OR, AND und normal-node die man einfügen kann)

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import no_update, callback_context
import dash_cytoscape as cyto
import re
import json
import backend
from treelib import Node, Tree
import uuid

app = dash.Dash(__name__)

#Definition der Nachkommastellen
max_probability = 0.999
amount_decimal_places = len(str(max_probability))
slider_steps = 0.001

nodes = [
    {
        'data': {'id': id, 'label': label},
        'position': {'x': x, 'y': y},
        'locked': locked,
        'selectable': selectable,
        'parent': parent
    }
    for id, label, x, y, locked, selectable, parent in (
        ('root', 'Versagen der Tunnelnotrufeinrichtung bei Inanspruchnahme durch einen Reisenden', 750, 750, True, False, 'root'),
        ('train_stopped_continued', 'Zug hat kurz im Tunnel gehalten und ist weitergefahren. (Reisender im Tunnel) \nµ=0.9997 \nσ²=0', 350, 600, True, False, 'root'),
        ('train_stopped', 'Zug ist im Tunnel liegengeblieben \nµ=0.0003 \nσ²=0', 1150, 600, True, False, 'root'),
        ('and', 'AND', 350, 300, True, False, 'train_stopped_continued'),
        ('old_tunnel_one_rail', 'Altbautunnel eingleisig \nµ=0.199 \nσ²=0', 350, 450, True, False, 'and'),
        ('next_train_incoming', 'Nächster Zug nähert sich', 600, 450, True, True, 'and'),
        ('train_hits_passenger', 'Zug erfasst Reisenden', 100, 450, True, True, 'and'),
        ('_result', 'result', 350, 150, True, False, 'and')
    )
]

edges = edges = [
    {'data': {'source': source, 'target': target}}
    for source, target in (
        ('root', 'train_stopped_continued'),
        ('root', 'train_stopped'),
        ('train_stopped_continued', 'old_tunnel_one_rail'),
        ('old_tunnel_one_rail', 'and'),
        ('next_train_incoming', 'and'),
        ('train_hits_passenger', 'and'),
        ('and', '_result')
    )
]

stylesheet = [
    {
        'selector': 'label',             
        'style': {
            'content': 'data(label)',   
            'color': 'grey',
            'text-wrap': 'wrap'
        }
    },
    {
        'selector': ':selected',
        'style': { 
            'color': 'CadetBlue',
            'background-color': 'CadetBlue'
        }
    },
    {
        'selector': 'edge',
        'style': {
            'curve-style': 'bezier'
        }
    }
]





app.layout = html.Div(children=[
                      html.Div(className='row',  # header
                               children=[
                                  html.Div(className='three columns div-user-controls', # slider and buttons and graph
                                    	    children=[
                                                html.H1('DB-Risk-Analysis - Monte-Carlo-Simulation'),
                                                html.Div(
                                                    className='div-for-slider',
                                                    children=[
                                                        html.H2('Erwartungswert'),
                                                        dcc.Slider(
                                                            id='update-expected-value',
                                                            min=0,
                                                            max=max_probability,
                                                            value=0,
                                                            step=slider_steps,
                                                            included=False,
                                                            updatemode='drag',
                                                        ),                                                   
                                                        html.H2('Varianz'),
                                                        dcc.Slider(
                                                            id='update-variance',
                                                            min=0,
                                                            max=max_probability,
                                                            value=0,
                                                            step=slider_steps,
                                                            included=False,
                                                            updatemode='drag',
                                                        ),   
                                                        html.Button('Run Simulation',
                                                            id='run-sim-button', n_clicks=0),
                                                        html.Div(id='graph-container', style={'display': 'none'}, children= [  
                                                            dcc.Graph(id = 'graph', style={'margin-top': '300px'}, className='div-user-controls',
                                                                    ),
                                                        ]),                                                    
                                                    ],)
                                    ]),  
                                    html.Div(className='nine columns div-for-charts bg-grey',
                                            children=[
                                                html.Div(id="btns", hidden=False, children=[
                                                    html.Button("Add", id="btn_add", n_clicks=0),
                                                    html.Button("Remove", id='btn_remove', n_clicks=0)
                                                ]),

                                                html.Div(id="div_add_nodes", style={'display': 'none'}, children=[
                                                    html.Div(style={'display': 'flex','fonst-size': '35px'}, children=
                                                        [dcc.Dropdown(
                                                            id='dropdown_node_type',
                                                            placeholder="Select type...", 
                                                            style={'width': '337px', 'font-size': '25px','height': '70px'},
                                                            options=[
                                                                {'label': 'AND', 'value': 'AND'},
                                                                {'label': 'OR', 'value': 'OR'},
                                                                {'label': 'Custom', 'value': 'CUSTOM'},
                                                            ]), 
                                                        dcc.Input(id='custom_node_name', style={'display': 'none'})
                                                        ]),
                                                    dcc.Dropdown(
                                                        id='dropdown_edge_to_node',
                                                        placeholder="Edge to node...",
                                                        style={'width': '600px','height': '70px', 'font-size': '25px'},
                                                        ),
                                                    html.Button('Add Node', id="btn_custom", n_clicks=0, style={'width': '337px'})
                                                ]),
                                                cyto.Cytoscape(  
                                                    id='node-callback-event',
                                                     stylesheet=stylesheet,
                                                    #[{
                                                    #     'selector': 'label',             
                                                    #     'style': {
                                                    #         'content': 'data(label)',   
                                                    #         'color': 'grey',
                                                    #         'text-wrap': 'wrap'
                                                    #     }},
                                                    #     {
                                                    #         'selector': ':selected',
                                                    #         'style': { 
                                                    #             'color': 'CadetBlue',
                                                    #             'background-color': 'CadetBlue'
                                                    #         }
                                                    #     }
                                                    # ],
                                                    layout={'name': 'preset', 'directed': 'True'},
                                                    style={'width': '100%', 'height': '3000px', 'display': 'block'},
                                                    elements=nodes+edges
                                                    # [ 
                                                    #     {
                                                    #         'data': {'id': 'root', 'label': 'Versagen der Tunnelnotrufeinrichtung bei Inanspruchnahme durch einen Reisenden'},
                                                    #         'position': {'x': 750, 'y': 750},
                                                    #         'locked': True,
                                                    #         'selectable': False,
                                                    #         'parent': 'root'
                                                    #     },
                                                    #     {
                                                    #         # ES MÜSSEN LEERZEICHEN ZWISCHEN EW UND VAR ENTHALTEN SEIN -- VERBESSERN
                                                    #         'data': {'id': 'train_stopped_continued', 'label': 'Zug hat kurz im Tunnel gehalten und ist weitergefahren. (Reisender im Tunnel) \nµ=0.9997 \nσ²=0'},
                                                    #         'position': {'x': 350, 'y': 600},
                                                    #         'locked': True,
                                                    #         'selectable': False,
                                                    #         'parent': 'root'
                                                    #     },
                                                    #     {
                                                    #         'data': {'id': 'train_stopped', 'label': 'Zug ist im Tunnel liegengeblieben \nµ=0.0003 \nσ²=0'},
                                                    #         'position': {'x': 1150, 'y': 600},
                                                    #         'locked': True,
                                                    #         'selectable': False,
                                                    #         'parent': 'root'
                                                    #     },
                                                    #     {
                                                    #         'data': {'id': 'and', 'label': 'AND'},
                                                    #         'position': {'x': 350, 'y': 300},
                                                    #         'locked': True,
                                                    #         'selectable': False,
                                                    #         'parent': 'train_stopped_continued'
                                                    #     },
                                                    #     {
                                                    #         'data': {'id': 'old_tunnel_one_rail', 'label': 'Altbautunnel eingleisig \nµ=0.199 \nσ²=0'},
                                                    #         'position': {'x': 350, 'y': 450},
                                                    #         'locked': True,
                                                    #         'selectable': False,
                                                    #         'parent': 'and', 
                                                    #     },
                                                    #     {
                                                    #         'data': {'id': 'next_train_incoming', 'label': 'Nächster Zug nähert sich'},
                                                    #         'position': {'x': 600, 'y': 450},
                                                    #         'locked': True,
                                                    #         'parent': 'and'
                                                    #     },
                                                    #     {
                                                    #         'data': {'id': 'train_hits_passenger', 'label': 'Zug erfasst Reisenden'},
                                                    #         'position': {'x': 100, 'y': 450},
                                                    #         'locked': True,
                                                    #         'parent': 'and'

                                                    #     },
                                                    #     {
                                                    #         'data': {'id': '_result', 'label': 'result'},
                                                    #         'position': {'x': 350, 'y': 150},
                                                    #         'selectable': False,
                                                    #         'parent': 'and'
                                                    #     },
                                                    #     {'data': {'source': 'root', 'target': 'train_stopped_continued'}},
                                                    #     {'data': {'source': 'root', 'target': 'train_stopped'}},
                                                    #     {'data': {'source': 'train_stopped_continued', 'target': 'old_tunnel_one_rail'}},
                                                    #     {'data': {'source': 'old_tunnel_one_rail', 'target': 'and'}},
                                                    #     {'data': {'source': 'next_train_incoming', 'target': 'and'}},
                                                    #     {'data': {'source': 'train_hits_passenger', 'target': 'and'}},
                                                    #     {'data': {'source': 'and', 'target': '_result'}},
                                                    # ]
                                                )]
                            ),  # decision tree
                                  ])
                                ])


@app.callback(Output('node-callback-event', 'elements'),
            Output('div_add_nodes', 'style'),
            Output('dropdown_edge_to_node', 'options'),
            Input('update-expected-value', 'value'),
            Input('update-variance', 'value'),
            Input('btn_add', 'n_clicks'),
            Input('dropdown_node_type', 'value'),
            Input('dropdown_edge_to_node', 'value'),
            Input('custom_node_name', 'value'),
            Input('btn_custom', 'n_clicks'),
            Input('btn_remove', 'n_clicks'),
            State('node-callback-event', 'elements'),
            State('node-callback-event', 'selectedNodeData'))
def add_node(valueEW, valueVAR, btn_add, node_type, edge_to_node, node_name, btn_custom, btn_remove, elements, selected):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if selected:
         # Update only the selected element(s)
        ids = [nodeData['id'] for nodeData in selected]
        nodes = ((i,n) for i,n in enumerate(elements) if n['data']['id'] in ids)
        for i, node in nodes:
            label = elements[i]['data']['label']
            label = re.sub('[0-9.,σ²µ=]+','',label).strip()
            label = label + ' ' + '\nµ=' + str(valueEW) + ' ' + '\nσ²=' + str(valueVAR)
            elements[i]['data']['label'] = label
        return elements, no_update, no_update

    elif 'btn_add' in changed_id:
        current_nodes = get_current_nodes(elements)
        current_edges = get_current_edges(elements)

        options = []
        for node in current_nodes:
            options.append({'label': node['data']['label'], 'value': node['data']['id']})

        return no_update, {'display':'block'}, options

    elif 'btn_remove' in changed_id:
        current_nodes = get_current_nodes(elements)
        current_nodes.pop()
        current_edges = get_current_edges(elements)
        return current_nodes+current_edges, no_update, no_update


    elif 'btn_custom' in changed_id:
        
        current_nodes = get_current_nodes(elements)
        current_edges = get_current_edges(elements)
        node_id = str(uuid.uuid4())

        #nur wenn Knoten noch nicht existiert
        #parent setzen (target von edge ist parent)

        if node_type == 'AND' or node_type == 'OR':

            #rnd = random.randrange(10)

            current_nodes.append({'data': {'id':node_id, 'label': node_type}, 'position': {'x': 1150, 'y': 700}, 'locked':False, 'selectable':False, 'parent':edge_to_node})
            current_edges.append({'data': {'source': node_id, 'target': edge_to_node}})
        
        #options noch anpassen und neuen knoten hinzufügen

        elif node_type == 'CUSTOM' and node_name not in current_nodes:
            #noch textbox einfügen und EW und VAR auswählen lassen
            

            current_nodes.append({'data': {'id':node_id, 'label': node_name}, 'position': {'x': 1150, 'y': 700}, 'locked':False, 'selectable':True, 'parent':edge_to_node})
            current_edges.append({'data': {'source': node_id, 'target': edge_to_node}})

        return current_nodes + current_edges, no_update, no_update

    return no_update, no_update, no_update

def get_current_nodes(elements):
    """
    Returns nodes that are present in Cytoscape
    """
    current_nodes = []

    # get current graph nodes
    for ele in elements:
        # if the element is a node
        if 'source' not in ele['data']:
            current_nodes.append(ele)
    
    return current_nodes

def get_current_edges(elements):
    """Returns edges that are present in Cytoscape:
    its source and target nodes are still present in the graph.
    """
    current_edges = []

    # get current graph nodes
    for ele in elements:
        # if the element is a node
        if 'source' in ele['data']:
            current_edges.append(ele)
    
    return current_edges


@app.callback(Output('custom_node_name', 'style'),
            Input('dropdown_node_type', 'value'))
def show_node_name_input(node_type):
    if node_type == 'CUSTOM':
        return {'display':'block','height': '70px', 'font-size': '30px', 'width': '263px'}
    else:
         return {'display':'none'}


@app.callback(Output('update-expected-value', 'value'),
              Output('update-variance', 'value'),
              Input('node-callback-event', 'selectedNodeData'),
              State('node-callback-event', 'elements'),
              State('node-callback-event', 'selectedNodeData'))
def displayTapNodeData(node_clicked, elements, selected):
    if node_clicked:
        ids = [nodeData['id'] for nodeData in selected]
        nodes = ((i,n) for i,n in enumerate(elements) if n['data']['id'] in ids)
        for i, node in nodes:
            label = elements[i]['data']['label']
            if "σ²=" not in label and "µ=" not in label and "AND" not in label and "OR" not in label:
                return (0,0)
            else: return (no_update, no_update)
    else:
        return no_update, no_update

# Möglichkeit 1
# ------------------------------------------
# Ebene - Teilbaum - Nummer in Teilbaum
# Schritt 1: IDs nach Teilbäumen gruppieren ([10, 201, 202, 203, 30, 40], [...])
# Schritt 2: Untermengen entsprechend der Ebenen bilden ([[10], [201,202,203], [30], [40]], [...])
# Schritt 3: Produkt der Untermengen bilden
# Schritt 4: Produkt der Teilbäume bilden

# Möglichkeit 2
# ------------------------------------------
# Berechnung der Wkt. hard-coded

@app.callback(Output("graph", "figure"),
              Output('graph-container', "style"),
              Input('run-sim-button', 'n_clicks'),
              State('node-callback-event', 'elements'))
def displayTapNodeData(clicked, elements):
    if clicked:
        tree = Tree()

        def add_node(id, label, node_type, parent=None):
            node = backend.EventNode(id, label, node_type)
            tree.create_node(tag=id, identifier=id, parent=parent, data=node)
        
        def calculate_and(node):
            and_sub_prob = 1
            for child in tree.children(node.identifier):
                # result ist mit 'and' verbunden - Sonderfall
                if 'result' not in child.data.node_type:
                    if type(child.data.ew) == float: 
                        and_sub_prob *= child.data.ew
            return and_sub_prob


        nodes = []
        for element in get_current_nodes(elements):

            id = element['data']['id']
            label = element['data']['label']
            parent = element['parent']

            if 'and' not in id and 'or' not in id and 'root' not in id:
                node_type = 'custom'
            else:
                node_type = id
                

            #node = backend.EventNode(id, label, type)
            #nodes.append(node)

            if id == 'root':
                add_node(id, label, node_type)
            else:
                add_node(id, label, node_type, parent)

        

        # get info of nodes: 



        # for node in  tree.all_nodes_itr():
        #     print(node.data.type)


        # für jeden Teilbaum bis Blatt erreicht und dann addieren
        
        
        

        for path in tree.paths_to_leaves():
            if "_result" in path:

                prob = 1

                for ele in path:

                    node = tree.get_node(ele)

                    if node.identifier == 'root':
                        prob *= 1

                    if node.is_leaf():
                        print("Crash probability:", prob)
                    
                    if node.data.node_type == 'custom':
                        if type(node.data.ew) == float:
                            prob *= node.data.ew
                    
                    if node.data.node_type == 'and':
                        prob *= calculate_and(node)
                    

        #tree.show(line_type="ascii-em")


        crash_probabilities = backend.run_mcs(nodes)

        return (backend.plot(crash_probabilities), {'display':'block'})

    else: 
        return no_update, no_update



if __name__ == '__main__':
    app.run_server(debug=True)