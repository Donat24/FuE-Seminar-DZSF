from dash import dcc
from dash import html
import styling
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
            
            html.Button("Alles Löschen",   id="button-delete-all", n_clicks=0, style={"width" : "100%","margin":"0.75rem"}),
            html.Button("Ansicht",    id="button-toggle-view", n_clicks=0, style={"width" : "100%","margin":"0.75rem"}),
            html.Hr(),
            
            html.Div(
                className="div-for-dropdown",
                children=[
                html.H6("Knoten-Typ"),
                dcc.Dropdown(
                    id="node-selector",
                    options=[
                        {"label": "Werte-Knoten",   "value": "value"},
                        {"label": "Und-Knoten",     "value": "and"},
                        {"label": "Oder-Knoten",    "value": "or"},
                        {"label": "Result-Knoten",  "value": "result"},
                    ],
                ),
                ]
            ),

            html.Button("Knoten +",   id="button-add-node", n_clicks=0, style={"width" : "100%","margin":"0.75rem"}),
            html.Button("Kante +",    id="button-add-edge", n_clicks=0, style={"width" : "100%","margin":"0.75rem"}),
            html.Button("Kante umdrehen", id="button-rev-edge", n_clicks=0, style={"width" : "100%","margin":"0.75rem"}),
            
            html.Hr(),
            html.H6("Beschreibung"),
            dcc.Textarea(id="textarea-description", placeholder="Beschreibung...",style={"width": "100%"}),
            html.H6("Histogramm"),
            dcc.Graph(id="histogramm-node"),
            html.H6("Erwartungswert"),
            dcc.Slider(id="slider-expected-value", min=0, max=1, value=0, step= 0.001, included=True, updatemode='drag'),
            html.H6("Variance"),
            dcc.Slider(id="slider-variance", min=0, max=1, value=0, step= 0.001, included=True, updatemode='drag'),

            html.Hr(),
            html.H6("Monte-Carlo"),
            dcc.Graph(id="histogramm-monte-carlo"),

        ],
        style={
            "margin" : "20px"
        })
    ],

    style={
            "position":"fixed",
            "overflow-y" : "scroll",
            "top" : 0,
            "bottom" : 0

    }
)

content = html.Div(
    className="columns nine offset-by-three",
    children=[
        html.H2("DB-Risk-Analysis - Monte-Carlo-Simulation"),
        html.Hr(),
        cyto.Cytoscape(
            style = {
                "position": "absolute",
                "width": "100%",
                "height": "100%",
                "z-index": 999
            } ,
            id='cytoscape',
            layout={'name': 'preset'},
            stylesheet=styling.cytoscape_normal,
            elements = get_cytoscape_elements_list()
        ),
    ],
    style={
        "position":"fixed",
        "overflow-y" : "scroll",
        "top" : 0,
        "bottom" : 0

    })

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