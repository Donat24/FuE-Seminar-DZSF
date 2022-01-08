from dash import dcc
from dash import html
#import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from nodes import get_cytoscape_elements_list



sidebar = html.Div(
    className="columns three",
    children=[

        html.Div(children=[
            
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
                    html.H6("Knoten-Typ"),
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
                
                html.Hr(),
                html.H6("Beschreibung"),
                dcc.Textarea(placeholder="Beschreibung...",style={"width": "100%"}),
                html.H6("Erwartungswert"),
                dcc.Slider(id="update-expected-value", min=0, max=1, value=0, step= 0.001, included=False, updatemode='drag'),
                html.H6("Variance"),
                dcc.Slider(id="update-variance", min=0, max=1, value=0, step= 0.001, included=False, updatemode='drag'),
            ],
            style={
                "margin" : "20px"
            })
        ],
        style={
            "overflow-y" : "scroll"
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
            "position" : "fixed",
            "width"  :"100%",
            "top" : 0,
            "bottom" : 0
        }
    )
