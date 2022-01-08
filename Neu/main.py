import dash
import dash_bootstrap_components as dbc

from layout import layout
from callbacks import add_callbacks
from setup_tree import setup_tree

app = dash.Dash(
    __name__,
)

app.layout = layout
add_callbacks(app)
setup_tree()

if __name__ == '__main__':
    app.run_server(debug=True)