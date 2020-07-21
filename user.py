import spotipy
import api_keys
import database_querying as db
from parse_library import fetch_playlist
import pandas as pd
scope = "user-library-read"
auth_manager = spotipy.oauth2.SpotifyOAuth(client_id = api_keys.spotify_client_id, client_secret=api_keys.spotify_client_secret,
                                           redirect_uri = api_keys.spotify_redirect_uri, scope=scope, show_dialog=True, username='jeremy_reikes')
audio_features = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
                  'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']
class User():
    # subset for testing purposes.  delete from __init__ and parse_library before going live
    def __init__(self, subset=False):
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        self.saved_tracks, self.new_artists  = fetch_playlist(self.sp, subset=subset, library=True)
        self.saved_tracks_df = self.prep_df(self.saved_tracks)
        # self.playlists = self.add_playlists()

    def add_playlists(self):
        playlists_meta_data = self.sp.current_user_playlists()
        playlists = []
        for playlist_meta_data in playlists_meta_data['items']:
            pid = playlist_meta_data['id']
            saved_tracks, new_artists = fetch_playlist(self.sp, playlist_id = pid)
            self.new_artists.extend(new_artists)
            playlist = dict(_id=pid, name=playlist_meta_data['name'])
            if saved_tracks:
                playlist = dict(_id=pid, name=playlist_meta_data['name'])
                playlist['saved_tracks'] = saved_tracks
                playlist['df'] = self.prep_df(saved_tracks)
                playlists.append(playlist)
        return playlists

    def convert_duration_to_seconds(self, millis):
        seconds = (millis/1000) % 60
        seconds = int(seconds)
        minutes = millis / (1000*60)
        minutes = int(minutes)
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
                        break
            genres = ', '.join(artist['genres'])
            name = artist['name']
            artists_info.append([name, genres])
        return pd.DataFrame(artists_info)

    def prep_df(self, tracks):
        data = pd.DataFrame(tracks)
        data.duration = data.duration.apply(self.convert_duration_to_seconds)
        data = data.reindex(columns = data.columns.tolist() + audio_features)
        data[audio_features] = pd.DataFrame.from_records(data.audio_features)
        data[audio_features] = data[audio_features].applymap(lambda x: round(x, 2))
        data[['artist', 'artist genres']] = self.id_to_artist_info(list(data['artist_id']))
        data['key'] = data['mode'].apply(self.convert_mode)
        data['Date Added'] = data['added_at'].apply(lambda x: x[:10])
        data = data[['name', 'artist', 'album_name', 'Date Added', 'duration', 'artist genres', 'key', 'explicit', 'danceability', 'energy', 'loudness',
                     'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'time_signature']]
        data.columns = [name.capitalize() for name in list(data.columns)]
        data = data.rename(columns={'Album_name': 'Album', 'Time_signature': 'Time Signature'})
        return data

# user = User(subset=True)

# user.playlists[0]['df']
# user.saved_tracks_df
# user.new_artists
# tracks = user.sp.current_user_saved_tracks()
# tracks['items'][0]
# playlists = user.sp.current_user_playlists()
# playlists['items'][0]
# playlist = user.sp.playlist('4QSUc9xaEdl5yLnfvfx2Br')
# playlist.keys()
# playlist.keys()
