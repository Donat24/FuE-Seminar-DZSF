from dash import dcc
from dash import html
#import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from nodes import get_cytoscape_elements_list



sidebar = html.Div(
    className="columns three",
    children=[
        
        html.Div(children=[
            html.H2("Editor"),
            html.Hr(),
        ]),

        html.Div(
            className="row",
            children=[
            html.Div(
                className="div-for-dropdown",
                children=[
                html.Label("Knoten-Typ"),
                dcc.Dropdown(
                    id="node-selector",
                    options=[
                        {"label": "Werte-Knoten", "value": "value"},
                        {"label": "Und-Knoten", "value": "and"},
                        {"label": "Oder-Knoten", "value": "or"},
                    ],
                ),
                ]
            ),

            html.Button("Knoten + / -",   id="button-add-node", n_clicks=0, style={"width" : "100%","margin":"0.75rem"}),
            html.Button("Kante + / -",    id="button-add-edge", n_clicks=0, style={"width" : "100%","margin":"0.75rem"}),
            html.Button("Kante umdrehen", id="button-rev-edge", n_clicks=0, style={"width" : "100%","margin":"0.75rem"}),
        ],
        style={
            "margin" : "20px"
        })
    ]
)

content = html.Div(
    className="columns nine",
    children=[
        html.H2("DB-Risk-Analysis - Monte-Carlo-Simulation"),
        html.Hr(),
        cyto.Cytoscape(
            style = {
                "width" : "100%",
                "height" : "600px"
            } ,
            id='cytoscape',
            layout={'name': 'preset'},
            stylesheet=[
                {
                    'selector': ':selected',
                    'style': { 'color': 'CadetBlue', 'background-color': 'CadetBlue' }
                },
                {
                    'selector': 'label',             
                    'style': { 'content': 'data(text)', 'color': 'grey', 'text-wrap': 'wrap'}
                },          
                {
                    'selector': 'edge',
                    'style': {'curve-style': 'bezier','source-arrow-shape': 'triangle'}
                },
            ],
            elements = get_cytoscape_elements_list()
        ),

    ])

def layout():
    return html.Div(
        className="row",
        children=[
            sidebar, content
        ],
        style={
            "width":"100%",
            "height":"100%"
        }
    )
