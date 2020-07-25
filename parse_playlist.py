from nlp_helpers import lemmatize
import database_querying as db
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import api_keys
import datetime
from collections import OrderedDict
client_credentials_manager = SpotifyClientCredentials(client_id=api_keys.spotify_client_id,
                                                      client_secret=api_keys.spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
useless_features = ['type', 'uri', 'track_href', 'analysis_url', 'id']
max_tracks_per_call = 50



def fetch_playlist(playlist_id, allow_every=False):
    try:
        results = sp.playlist(playlist_id)
    except:
        print(f'Invalid PID: {playlist_id}')
        return False
    description, name, owner = results['description'], results['name'], results['owner']['id']
    total_tracks = results['tracks']['total']
    desc_lemmas, desc_lang = lemmatize(description, return_lang=True)
    name_lemmas, name_lang = lemmatize(name, return_lang=True)
    valid_tracks = get_valid_tracks(sp, results['tracks'])
    playlist_length = len(valid_tracks)
    if not allow_every and (playlist_length > 2000 or playlist_length <= 1 or desc_lang != 'en' or name_lang != 'en'):
        print(f'{playlist_id} rejected.  Invalid # of tracks or non-english.')
        return False

    tracks_to_add = list() # playlist tracks that don't exist in DB
    artists_to_add = set()
    playlist_tids = list() # playlist tracks that already exist or are initialized without error

    for tid, track in valid_tracks.items():
        if not db.track_exists(tid):
            try:
                track_data = initialize_track(track, playlist_id)
                artist_ids = track_data['artist_ids']
                for artist_id in artist_ids:
                    if not db.artist_exists(artist_id):
                        artists_to_add.add(artist_id)
                tracks_to_add.append(track_data)
                playlist_tids.append(tid)
            except:
                print(f'Error initializing track {tid}')
                continue
        else:
            playlist_tids.append(tid)
            db.add_pid_to_track(tid, playlist_id)

    tracks_to_add = add_audio_features(tracks_to_add)
    playlist_to_add = dict(_id=playlist_id, name=name, name_lemmas=name_lemmas, owner=owner, last_updated=datetime.datetime.now(),
                           description=description, description_lemmas = desc_lemmas, tids=playlist_tids)
    artists_to_add = fetch_artist_info(artists_to_add)
    db.insert_artists(artists_to_add)
    db.insert_tracks(tracks_to_add)
    db.insert_playlist(playlist_to_add)
    return True # returns True if it successfully adds playlist to db, False otherwise

def fetch_user_playlist(sp, playlist_id=None, library=False):
    if playlist_id:
        results = sp.playlist(playlist_id)
        valid_tracks = get_valid_tracks(sp, results['tracks'])
    elif library:
        results = sp.current_user_saved_tracks()
        valid_tracks = get_valid_tracks(sp, results)

    new_tracks = list() # playlist tracks that don't exist in DB
    indices_to_add_new_tracks = list()
    new_artists = set()
    saved_tracks = list() # playlist tracks that already exist or are initialized without error

    for index, (tid, track) in enumerate(valid_tracks.items()):
        if not db.track_exists(tid):
            try:
                track_data = initialize_track(track, for_user=True)
                artist_ids = track_data['artist_ids']
                for artist_id in artist_ids:
                    if not db.artist_exists(artist_id):
                        new_artists.add(artist_id)
                new_tracks.append(track_data)
                indices_to_add_new_tracks.append(index)
                saved_tracks.append(0)
            except:
                print(f'Error initializing track {tid}')
                continue
        else:
            track_data = db.get_track(tid)
            track_data['added_at'] = track['added_at']
            saved_tracks.append(track_data)
    new_tracks = add_audio_features(new_tracks)
    for track, index in zip(new_tracks, indices_to_add_new_tracks):
        saved_tracks[index] = track
    new_artists = fetch_artist_info(new_artists)
    return saved_tracks, new_artists

def add_audio_features(tracks_to_add):
    for start in range(0, len(tracks_to_add), max_tracks_per_call):
        curr_ids = [track['_id'] for track in tracks_to_add[start: start + max_tracks_per_call]]
        try:
            audio_features = sp.audio_features(curr_ids)
        except:
            audio_features = list()
            for curr_id in curr_ids:
                try:
                    curr_feature = sp.audio_features(curr_id)
                    audio_features.extend(curr_feature)
                except:
                    audio_features.append({})
        for track, curr_features in zip(tracks_to_add[start: start + max_tracks_per_call], audio_features):
            if curr_features:
                track['analysis_url'] = curr_features['analysis_url']
                track['track_href'] = curr_features['track_href']
                for feature in useless_features:
                    del curr_features[feature]
                track['audio_features'] = curr_features
    return tracks_to_add

def initialize_track(track, playlist_id=None, for_user=False):
    track_data = dict()
    track_info = track['track']
    track_data['name'] = track_info['name']
    track_data['name_lemmas'] = lemmatize(track_data['name'])
    track_data['_id'] = track_info['id']
    track_data['album_name'] = track_info['album']['name']
    track_data['album_id'] = track_info['album']['id']
    track_data['explicit'] = track_info['explicit']
    track_data['duration'] = track_info['duration_ms']
    track_data['artist_ids'] = [artist['id'] for artist in track_info['artists']]
    if for_user:
        track_data['added_at'] = track['added_at']
    else:
        track_data['pids'] = list([playlist_id])
    return track_data

def fetch_artist_info(artist_ids):
    artist_ids = list(artist_ids)
    artist_features = ['_id', 'name', 'genres']
    artists_data = list()
    for start in range(0, len(artist_ids), max_tracks_per_call):
        curr_ids = artist_ids[start: start + max_tracks_per_call]
        try:
            curr_artists = sp.artists(curr_ids)['artists']
        except:
            curr_artists = list()
            for curr_id in curr_ids:
                try:
                    curr_artist = sp.artist(curr_id)
                    curr_artists.append(curr_artist)
                except:
                    curr_artists.append({})
        for curr_id, curr_artist in zip(curr_ids, curr_artists):
            if curr_artist:
                artist_data = dict(_id=curr_artist['id'], name=curr_artist['name'], genres=curr_artist['genres'])
            else:
                artist_data = dict(_id = curr_id, name='', genres=[])
            artists_data.append(artist_data)
    return artists_data


# about .3% of artists are not found by Spotify API on first try.  Retry them here.
def retry_fetch_artist_info(artist_id):
    try:
        artist = sp.artist(artist_id)
    except:
        print(f'Cannot get artist {artist_id}')
        return dict(_id = artist_id)
    artist_data = dict()
    if artist:
        artist_data['_id'] = artist_id
        artist_data['name'] = artist['name']
        artist_data['genres'] = artist['genres']
        return artist_data
    else:
        print(f'Cannot get more info for {artist_id}')
        return dict(_id = artist_id)

# in case there are still unparsed artists
def refetch_unparsed_artists():
    unparsed_artists = db.get_unparsed_artists()
    for artist in unparsed_artists:
        artist_data = retry_fetch_artist_info(artist['_id'])
        db.replace_artist(artist_data)


def get_valid_tracks(sp, tracks):
    '''Ensures track integrity by removing local and no-id tracks.  Creates dict with valid tracks'''
    valid_tracks = OrderedDict()
    valid_tracks = remove_invalid_tracks(tracks, valid_tracks)
    while tracks['next']:
        tracks = sp.next(tracks)
        valid_tracks = remove_invalid_tracks(tracks, valid_tracks)
    return valid_tracks

def is_valid(track):
    ''' Helper for parse_tracks.  Ensures TID present and track not local '''
    try:
        tid = track['track']['id']
        return not track['track']['is_local']
    except:
        return False

def remove_invalid_tracks(tracks, valid_tracks):
    ''' Helper for parse_tracks '''
    for track in tracks['items']:
        if is_valid(track):
            tid = track['track']['id']
            valid_tracks[tid] = track
    return valid_tracks
