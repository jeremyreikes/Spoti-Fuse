
import spotipy
import api_keys
import os
import database_querying as db
from parse_playlist import fetch_playlist
from parse_library import fetch_library
client_id=api_keys.spotify_client_id
client_secret=api_keys.spotify_client_secret
redirect_uri = api_keys.spotify_redirect_uri
scope = "user-library-read"
auth_manager = spotipy.oauth2.SpotifyOAuth(client_id = client_id, client_secret=client_secret, redirect_uri = redirect_uri,
                                           scope=scope, show_dialog=True, username='jeremy_reikes')

class User():
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        self.playlists_meta_data = self.sp.current_user_playlists()
        self.new_tracks, self.saved_track_ids, self.new_artists  = fetch_library(self.sp)
        self.playlist_ids = self.get_playlist_ids()
        self.playlists = self.add_playlists()

    def get_playlist_ids(self):
        ids = []
        for playlist in self.playlists_meta_data['items']:
            ids.append(playlist['id'])
        return ids

    def add_playlists(self):
        playlists = []
        for pid in self.playlist_ids:
            if db.playlist_exists(pid):
                pass
            else:
                fetch_playlist(pid, allow_every=True)
            playlist = db.get_playlist(pid)
            if playlist:
                playlists.append(playlist)
        return playlists

user = User()
user.new_tracks[0]
db.tracks_db.find_one()
