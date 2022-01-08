import dash
import dash_bootstrap_components as dbc

from layout import layout
from callbacks import add_callbacks

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.layout = layout
add_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)