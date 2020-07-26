import dash
import dash_table
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
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
    dcc.Dropdown(
        id='demo-dropdown',
        options=
            [{'label': playlist, 'value': playlist} for playlist in playlists],
        value= 'Liked Songs',
        clearable=False
    ),
    dcc.Input(
        id = 'search_term_input',
        type='text',
        placeholder='Enter A Search Term'
    ),
    html.Button('Search', id='search-term-button', n_clicks=0),
    dash_table.DataTable(
        id='table',
        data = playlists['Liked Songs'].to_dict('records'),
        columns = [{"name": i, "id": i} for i in playlists['Liked Songs'].columns],
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
    html.Div(id='output'),
    html.Button('Add Playlist', id='add_playlist', n_clicks=0),
    html.Div(id='filler')
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

#
# @app.callback(
#     # [Output('table', 'data'), Output('table', 'columns')],
#     Output('demo-dropdown', 'value'),
#     [Input('search-term-button', 'n_clicks')],
#     [State('search_term_input', 'value'),
#      State('table', 'derived_virtual_indices'),
#      State('demo-dropdown', 'value')]
# )
# def add_search_word_score(n_clicks, search_words, derived_virtual_indices, df_name):
#     if n_clicks >= 1 and search_words:
#         scores = []
#         track_ids = list(playlists[df_name].loc[derived_virtual_indices, '_id'])
#         recs = recommend_tracks(search_words, min_occurences=1, tid_subset=track_ids)
#         for track_id in track_ids:
#             if track_id in recs:
#                 scores.append(recs[track_id])
#             else:
#                 scores.append(0)
#         playlists[df_name].insert(7, 'Search Score', scores, True)
#         # data = playlists[df_name]['Search Score'].to_dict('records')
#         # columns = [{"name": i, "id": i} for i in playlists[df_name].columns]
#         # return data, columns
#     # else:
#         # return playlists['Liked Songs'].to_dict('records'), [{"name": i, "id": i} for i in playlists['Liked Songs'].columns]
#     # data = playlists[df_name]['Search Score'].to_dict('records')
#     # columns = [{"name": i, "id": i} for i in playlists[df_name].columns]
#     # return df_name#, columns
#     return df_name


if __name__ == '__main__':
    app.run_server(debug=True)
