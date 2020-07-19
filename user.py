import spotipy
import api_keys
import database_querying as db
from parse_playlist import fetch_playlist
from parse_library import fetch_library
import pandas as pd
scope = "user-library-read"
auth_manager = spotipy.oauth2.SpotifyOAuth(client_id = api_keys.spotify_client_id, client_secret=api_keys.spotify_client_secret,
                                           redirect_uri = api_keys.spotify_redirect_uri, scope=scope, show_dialog=True, username='jeremy_reikes')
audio_features = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                  'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']
class User():
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        self.saved_tracks, self.new_artists  = fetch_library(self.sp)
        self.saved_tracks_df = self.prep_df(self.saved_tracks)
        self.playlists_meta_data = self.sp.current_user_playlists()
        self.playlist_dfs = self.add_playlists()

    def add_playlists(self):
        playlist_ids = []
        for playlist in self.playlists_meta_data['items']:
            playlist_ids.append(playlist['id'])
        playlists = []
        for pid in playlist_ids:
            if db.playlist_exists(pid):
                pass
            else:
                fetch_playlist(pid, allow_every=True)
            playlist = db.get_playlist(pid)
            if playlist:
                playlist_tracks = [db.get_track(tid) for tid in playlist['tids']]
                if not playlist_tracks:
                    continue
                playlist['playlist_tracks'] = playlist_tracks
                playlist['playlist_df'] = self.prep_df(playlist_tracks)
                playlists.append(playlist)
        return playlists

    # def playlists_to_dfs(self):
    #     for playlist in self.playlists:
    #         data = self.prep_df(playlist['playlist_tracks'])

    def convert_duration_to_seconds(self, millis):
        seconds = (millis/1000) % 60
        seconds = round(seconds)
        minutes = millis / (1000*60)
        minutes = round(minutes)
        if seconds // 10 == 0:
            seconds = '0' + str(seconds)
        return str(minutes) + ':' + str(seconds)

    def convert_mode(self, mode):
        if mode == 1:
            return 'Major'
        elif mode == 0:
            return 'Minor'
        else:
            return 'Unknown'

    def id_to_artist_info(self, artist_ids):
        artists_info = []
        for artist_id in artist_ids:
            artist = db.get_artist(artist_id)
            if not artist:
                for new_artist in self.new_artists:
                    if new_artist['_id'] == artist_id:
                        artist = new_artist
            genres = ', '.join(artist['genres'])
            name = artist['name']
            artists_info.append([name, genres])
        return pd.DataFrame(artists_info)

    def prep_df(self, tracks):
        data = pd.DataFrame(tracks)
        data.duration = data.duration.apply(self.convert_duration_to_seconds)
        data = data.reindex(columns = data.columns.tolist() + audio_features)
        data[audio_features] = pd.DataFrame.from_records(data.audio_features)
        data[['artist', 'artist_genres']] = self.id_to_artist_info(list(data['artist_id']))
        data['key'] = data['mode'].apply(self.convert_mode)
        data = data[['name', 'artist', 'duration', 'artist_genres', 'key', 'explicit', 'danceability', 'energy', 'loudness',
                     'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'time_signature']]
        return data

user = User()
user.saved_tracks_df
