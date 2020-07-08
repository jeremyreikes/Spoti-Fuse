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

def fetch_playlist(playlist_id):
    if playlist_id == '' or playlist_id == None:
        print(f'Invalid PID: {playlist_id}')
        return False
    try:
        results = sp.user_playlist(playlist_id = playlist_id, user=None)
        description = results['description']
        name = results['name']
        owner = results['owner']['id']
        total_tracks = results['tracks']['total']
        desc_lemmas, desc_lang = lemmatize(description, return_lang=True)
        name_lemmas, name_lang = lemmatize(name, return_lang=True)
    except:
        print(f'Invalid PID: {playlist_id}')
        return False

    valid_tracks = get_valid_tracks(results, sp)
    playlist_length = len(valid_tracks)
    if playlist_length > 2000 or playlist_length <= 1 or desc_lang != 'en' or name_lang != 'en':
        print(f'Too many/few tracks or not english {playlist_id}')
        return False

    tracks_to_add = list() # playlist tracks that don't exist in DB
    artists_to_add = set()
    playlist_tids = list() # playlist tracks that already exist or are initialized without error

    for tid, track in valid_tracks.items():
        if not db.track_exists(tid):
            try:
                track_data = initialize_track(track, playlist_id)
                artist_id = track_data['artist_id']
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

def add_audio_features(tracks_to_add):
    tids = [track['_id'] for track in tracks_to_add]
    for i in range((len(tids) // 50) + 1):
        offset = i*50
        curr_ids = get_curr_ids(tids, offset)
        if len(curr_ids) == 0:
            break
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
        for index, curr_features in enumerate(audio_features):
            if curr_features:
                for feature in useless_features:
                    del curr_features[feature]
                tracks_to_add[offset + index - 1]['audio_features'] = curr_features
    return tracks_to_add

def initialize_track(track, playlist_id):
    track_data = dict()
    track_info = track['track']
    track_data['name'] = track_info['name']
    track_data['name_lemmas'] = lemmatize(track_data['name'])
    track_data['_id'] = track_info['id']
    track_data['explicit'] = track_info['explicit']
    track_data['duration'] = track_info['duration_ms']
    track_data['artist_id'] = track_info['artists'][0]['id']
    track_data['pids'] = list([playlist_id])
    return track_data

def fetch_artist_info(artist_ids):
    artist_ids = list(artist_ids)
    artists_data = list()
    for i in range((len(artist_ids) // 50) + 1):
        offset = i*50
        curr_ids = get_curr_ids(artist_ids, offset)
        if len(curr_ids) == 0: # in case it's a multiple of 50
            break
        try:
            curr_artists = sp.artists(artist_ids)['artists']
        except:
            curr_artists = list()
            for curr_id in curr_ids:
                try:
                    curr_artist = sp.artist(curr_id)
                    curr_artists.append(curr_artist)
                except:
                    curr_artists.append({})
        for index, curr_artist in enumerate(curr_artists):
            artist_data = dict()
            if not curr_artist:
                artist_data['_id'] = curr_ids[index]
            else:
                artist_data['_id'] = curr_ids[index]
                artist_data['name'] = curr_artist['name']
                artist_data['popularity'] = curr_artist['popularity']
                artist_data['genres'] = curr_artist['genres']
            artists_data.append(artist_data)
    return artists_data

def get_curr_ids(tids, offset):
    try:
        curr_ids = tids[offset:offset+50]
    except:
        curr_ids = tids[offset:]
    return list(set(curr_ids))

def get_valid_tracks(results, sp):
    '''Ensures track integrity by removing local and no-id tracks.  Creates dict with valid tracks'''
    valid_tracks = OrderedDict()
    tracks = results['tracks']
    valid_tracks = remove_invalid_tracks(tracks, valid_tracks)
    while tracks['next']:
        tracks = sp.next(tracks)
        valid_tracks = remove_invalid_tracks(tracks, valid_tracks)
    return valid_tracks

def is_valid(track):
    ''' Helper for parse_tracks '''
    try:
        tid = track['track']['id']
        if track['is_local']:
            return False
        return track
    except:
        return False

def remove_invalid_tracks(tracks, valid_tracks):
    ''' Helper for parse_tracks '''
    for track in tracks['items']:
        if is_valid(track):
            tid = track['track']['id']
            valid_tracks[tid] = track
    return valid_tracks
