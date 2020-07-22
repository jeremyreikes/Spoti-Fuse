import dash
import dash_table
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
from user import User
import pandas as pd

user = User()
playlists = {playlist['name']: playlist['df'] for playlist in user.playlists}
playlists['Liked Songs'] = user.saved_tracks_df

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)
app.layout = html.Div(children=[
    html.H1(children='SpotiFuse', style={'color': '#1DB954'}),
    dcc.Dropdown(
        id='demo-dropdown',
        options=
            # [{'label': playlist['name'], 'value': playlist['df']} for playlist in user.playlists],
            # {'label': 'Liked Songs', 'value': user.saved_tracks_df}
            [{'label': playlist, 'value': playlist} for playlist in playlists],
            value= 'Liked Songs',
            clearable=False
    ),
    dash_table.DataTable(
        id='table',
        data = playlists['Liked Songs'].to_dict('records'),
        columns = [{"name": i, "id": i} for i in playlists['Liked Songs'].columns],
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        row_selectable="multi",
        selected_rows=[],
        # page_action="native",
        style_data={'textAlign': 'left',
                    'maxWidth': '300px',
                    # 'color': '#191414',
                    # 'height': 'auto',
                    # 'overflow': 'ellipsis',
                    'textOverflow': 'ellipsis'
        },
        style_cell_conditional=[
            {'if': {'column_id': 'Name'},
             'width': '100px'},
            {'if': {'column_id': 'Album'},
             'width': '100px'},
        ],
        # style_cell={
        # 'backgroundColor': 'rgb(25, 20, 20)',
        # 'color': 'white'
        # },
        # style_table = {
        #     'color': '#191414'
        # }

    )
])
@app.callback(
    [Output('table', 'data'), Output('table', 'columns')],
    [Input('demo-dropdown', 'value')])
def update_output(playlist_name):
    df = playlists[playlist_name]
    data = df.to_dict('records')
    columns = [{"name": i, "id": i} for i in df.columns]

    return data, columns
if __name__ == '__main__':
    app.run_server(debug=True)
