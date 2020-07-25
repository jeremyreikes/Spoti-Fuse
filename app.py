import dash
import dash_table
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_html_components as html
from user import User
import pandas as pd

user = User()
playlists = {playlist['name']: playlist['df'] for playlist in user.playlists}
playlists['Liked Songs'] = user.saved_tracks_df
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(children=[
    html.H1(children='SpotiFuse', style={'color': '#1DB954'}),
    dcc.Dropdown(
        id='demo-dropdown',
        options=
            [{'label': playlist, 'value': playlist} for playlist in playlists],
        value= 'Liked Songs',
        clearable=False
    ),
    dash_table.DataTable(
        id='table',
        data = playlists['Liked Songs'].to_dict('records'),
        columns = [{"name": i, "id": i} for i in playlists['Liked Songs'].columns],
        derived_virtual_indices = [],
        hidden_columns=['_id'],
        filter_action="native",
        page_size=500,
        sort_action="native",
        sort_mode="multi",
        css=[{"selector": ".show-hide", "rule": "display: none"}],
        # page_action="native",
        style_header= {

        },
        style_cell={'textAlign': 'left',
                    'maxWidth': '250px',
                    # 'color': '#191414',
                    # 'height': 'auto',
                    # 'overflow': 'ellipsis',
                    'textOverflow': 'ellipsis'
        },
        style_cell_conditional=[
            {'if': {'column_id': 'Name'},
             'maxWidth': '240px'},
            {'if': {'column_id': 'Artist'},
             'maxWidth': '150px'},
            {'if': {'column_id': 'Genres'},
             'maxWidth': '130px'},
            {'if': {'column_id': 'Album'},
             'maxWidth': '150px'},
            {'if': {'column_id': 'Date added'},
             'minWidth': '100px'},
            {'if': {'column_id': 'Duration'},
             'minWidth': '75px'},
            {'if': {'column_id': 'Explicit'},
             'minWidth': '80px'}
        ]

        # style_cell_conditional=[
        #     {'if': {'column_id': 'Name'},
        #      'width': '100px'},
        #     {'if': {'column_id': 'Album'},
        #      'width': '100px'},
        # ],
        # style_cell={
        # 'backgroundColor': 'rgb(25, 20, 20)',
        # 'color': 'white'
        # },
        # style_table = {
        #     'color': '#191414'
        # }

    ),
    dcc.Input(id='playlist_name_input', type='text', placeholder='Enter a playlist name'),
    html.Div(id='output'),
    html.Button('Add Playlist', id='add_playlist', n_clicks=0),
])

@app.callback(
    [Output('table', 'data'), Output('table', 'columns')],
    [Input('demo-dropdown', 'value')])
def update_df(playlist_name):
    df = playlists[playlist_name]
    data = df.to_dict('records')
    columns = [{"name": i, "id": i} for i in df.columns]
    return data, columns


# want button push to trigger a input field
@app.callback(
    [Output('playlist_name_input', 'value'),
     Output('output', 'children'),
     Output('demo-dropdown', 'options'),
     Output('demo-dropdown', 'value')],
    [Input('add_playlist', 'n_clicks')],
    [State('playlist_name_input', 'value'),
     State('table', 'derived_virtual_indices'),
     State('demo-dropdown', 'value')])
def add_playlist(n_clicks, playlist_name, derived_virtual_indices, df_name):
    options = [{'label': playlist, 'value': playlist} for playlist in playlists]
    if n_clicks >= 1 and playlist_name:
        user_id = user.sp.me()['id']
        playlist = user.sp.user_playlist_create(user_id, playlist_name)
        rows = playlists[df_name].loc[derived_virtual_indices]
        tids = list(rows['_id'])
        user.sp.user_playlist_add_tracks(user_id, playlist['id'], tids)
        playlists[playlist_name] = rows
        options.append({'label': playlist_name, 'value': playlist_name})
        return "", f"{playlist_name} Added!", options, playlist_name
    elif n_clicks >= 1 and not playlist_name:
        return "", "Please Enter a Playlist Name", options, df_name
    else:
        return "", None, options, df_name

if __name__ == '__main__':
    app.run_server(debug=True)
