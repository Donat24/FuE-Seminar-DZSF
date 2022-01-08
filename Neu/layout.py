from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from nodes import get_cytoscape_elements_list



sidebar = html.Div(
    children=[
        
        html.Div(children=[
            html.H2("Editor", className="display-4"),
            html.Hr(),
            html.P(
                "Neue Knoten hinzufügen oder löschen", className="lead"
            )
        ]),

        html.Div(children=[
            html.Div([
                dbc.Label("Knoten-Typ", html_for="dropdown"),
                dcc.Dropdown(
                    id="node-selector",
                    options=[
                        {"label": "Werte-Knoten", "value": "value"},
                        {"label": "Und-Knoten", "value": "and"},
                        {"label": "Oder-Knoten", "value": "or"},
                    ],
                ),
                ],
            className="mb-3",
            ),

            dbc.Button("Knoten + / -",   id="button-add-node", n_clicks=0),
            dbc.Button("Kante + / -",    id="button-add-edge", n_clicks=0),
            dbc.Button("Kante umdrehen", id="button-rev-edge", n_clicks=0),
        ],
        className="d-grid gap-2",)
    ],

    style = {
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "16rem",
        "padding": "2rem 1rem",
        "backgroundColor": "#f8f9fa",
    }
)

content = html.Div(
    
    children=[
        html.H1("TOLLE ÜBERSCHRIGT", className="display-4"),
        html.Hr(),
        cyto.Cytoscape(
            id='cytoscape',
            layout={'name': 'preset'},
            #style={'width': '100%', }#'height': '100%'},
            stylesheet=[
                {
                    'selector': 'node',
                    'style': {'label': 'data(label)'}
                },
                {
                    'selector': 'edge',
                    'style': {'curve-style': 'bezier','source-arrow-shape': 'triangle'}
                },
            ],
            elements = get_cytoscape_elements_list()
        )
    ],

    style = {
        "marginLeft": "18rem",
        "marginRight": "2rem",
        "padding": "2rem 1rem",
    })

def layout():
    return html.Div(children=[
        sidebar, content
    ])