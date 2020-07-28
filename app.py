import dash
import dash_table
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
from user import User
import pandas as pd
import pickle
from naive_playlist_recommendation import recommend_tracks

user = User()
# # Uncomment to pick new users
# pickle.dump(user, open('user.p', 'wb'))
# user = pickle.load(open('user.p', 'rb'))
playlists = {playlist['name']: playlist['df'] for playlist in user.playlists}
playlists['Liked Songs'] = user.saved_tracks_df

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(children=[
    html.H1(children='SpotiFuse', style={'color': '#1DB954'}),
    dcc.Store(
        id = 'df-memory',
        data= playlists['Liked Songs'].to_dict('records')
    ),
    dcc.Dropdown(
        id='demo-dropdown',
        options=
            [{'label': playlist, 'value': playlist} for playlist in playlists],
        # value= 'Liked Songs',
        clearable=False
    ),
    dcc.Input(
        id = 'search_term_input',
        type='text',
        placeholder='Enter A Search Term'
    ),
    html.Button('Search', id='search-term-button'),
    dash_table.DataTable(
        id='table',
        # data = playlists['Liked Songs'].to_dict('records'),
        # columns = [{"name": i, "id": i} for i in playlists['Liked Songs'].columns],
        derived_virtual_indices = [],
        hidden_columns=['_id', 'Pids'],
        filter_action="native",
        page_size=500,
        sort_action="native",
        sort_mode="multi",
        style_as_list_view=True,
        css=[{"selector": ".show-hide", "rule": "display: none"}],
        style_cell={'textAlign': 'left',
                    'maxWidth': '250px',
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
    ),
    dcc.Input(id='playlist_name_input', type='text', placeholder='Enter a playlist name'),
    html.Button('Add Playlist', id='add_playlist'),
    html.Div(id='playlist-addition-message'),
    html.Div(id='filler')
])

# @app.callback(
#     Output('df-memory', 'data'),
#     [Input('demo-dropdown', 'value')]
# )
# def switch_table(playlist_name):
#     if playlist_name is None:
#         raise PreventUpdate
#     else:
#         playlist = playlists[playlist_name]
#         data = playlist.to_dict('records')
#         return data

@app.callback(
    [Output('table', 'data'), Output('table', 'columns')],
    [Input('df-memory', 'data')]
)
def update_table(data):
    if data is None:
        raise PreventUpdate
    else:
        columns = [{"name": i, "id": i} for i in data[0].keys()]
        return data, columns

@app.callback(
    [Output('playlist_name_input', 'value'),
     Output('playlist-addition-message', 'children'),
     Output('demo-dropdown', 'options'),
     Output('demo-dropdown', 'value')],
    [Input('add_playlist', 'n_clicks')],
    [State('playlist_name_input', 'value'),
     State('table', 'derived_virtual_indices'),
     State('demo-dropdown', 'value'),
     State('demo-dropdown', 'options')])
def add_playlist(n_clicks, playlist_name, derived_virtual_indices, df_name, options):
    if n_clicks is None:
        raise PreventUpdate
    elif not playlist_name:
        return None, "Please enter a name for your playlist.", options, df_name
    elif not df_name:
        return None, "Please select a playlist.", options, df_name
    else:
        user_id = user.sp.me()['id']
        playlist = user.sp.user_playlist_create(user_id, playlist_name)
        rows = playlists[df_name].loc[derived_virtual_indices]
        tids = rows['_id'].tolist()
        user.sp.user_playlist_add_tracks(user_id, playlist['id'], tids)
        playlists[playlist_name] = rows
        options.append({'label': playlist_name, 'value': playlist_name})
        return None, f"\"{playlist_name}\" Added!", options, playlist_name

@app.callback(
    Output('df-memory', 'data'),
    [Input('search-term-button', 'n_clicks'),
     Input('demo-dropdown', 'value')],
    [State('search_term_input', 'value'),
     State('table', 'derived_virtual_indices'),
     State('df-memory', 'data')]
)
def change_or_modify_table(search_n_clicks, dropdown_playlist_name, search_words, derived_virtual_indices, data):
    ctx = dash.callback_context
    print(ctx.triggered)
    triggered = ctx.triggered[0]['prop_id'].split('.')[0]
    if 'demo-dropdown' == triggered:
        playlist_name = ctx.triggered[0]['value']
        playlist = playlists[dropdown_playlist_name]
        data = playlist.to_dict('records')
        return data
    elif 'search-term-button' == triggered and search_words:
        scores = []
        temp_df = pd.DataFrame.from_records(data)
        track_ids = temp_df.loc[derived_virtual_indices, '_id'].tolist()
        recs = recommend_tracks(search_words, min_occurences=1, tid_subset=track_ids)
        for track_id in track_ids:
            if track_id in recs:
                scores.append(recs[track_id])
            else:
                scores.append(0)
        if 'Search Score' in temp_df.columns:
            temp_df['Search Score'] = scores
        else:
            temp_df.insert(7, 'Search Score', scores, True)
        return temp_df.to_dict('records')
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)
