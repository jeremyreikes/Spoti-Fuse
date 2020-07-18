import database_querying as db
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import api_keys
import datetime
import parse_playlist
from collections import OrderedDict

def get_valid_tracks(sp, results):
    '''Ensures track integrity by removing local and no-id tracks.  Creates dict with valid tracks'''
    valid_tracks = OrderedDict()
    valid_tracks = remove_invalid_tracks(results['items'], valid_tracks)
    while results['next']:
        results = sp.next(results)
        valid_tracks = remove_invalid_tracks(results['items'], valid_tracks)
    return valid_tracks

def is_valid(track):
    ''' Helper for parse_tracks '''
    try:
        tid = track['track']['id']
        return not track['track']['is_local']
    except:
        return False

def remove_invalid_tracks(tracks, valid_tracks):
    ''' Helper for parse_tracks '''
    for track in tracks:
        if is_valid(track):
            tid = track['track']['id']
            valid_tracks[tid] = track
    return valid_tracks

def initialize_track(track):
    track_data = dict()
    track_info = track['track']
    track_data['name'] = track_info['name']
    track_data['name_lemmas'] = parse_playlist.lemmatize(track_data['name'])
    track_data['_id'] = track_info['id']
    track_data['explicit'] = track_info['explicit']
    track_data['duration'] = track_info['duration_ms']
    track_data['artist_id'] = track_info['artists'][0]['id']
    return track_data

def fetch_library(sp):
    results = sp.current_user_saved_tracks()
    valid_tracks = get_valid_tracks(sp, results)

    new_tracks = list() # playlist tracks that don't exist in DB
    new_artists = set()
    library_tids = list() # playlist tracks that already exist or are initialized without error

    for tid, track in valid_tracks.items():
        if not db.track_exists(tid):
            try:
                track_data = initialize_track(track)
                artist_id = track_data['artist_id']
                if not db.artist_exists(artist_id):
                    new_artists.add(artist_id)
                new_tracks.append(track_data)
                library_tids.append(tid)
            except:
                print(f'Error initializing track {tid}')
                continue
        else:
            library_tids.append(tid)
    new_tracks = parse_playlist.add_audio_features(new_tracks)
    new_artists = parse_playlist.fetch_artist_info(new_artists)

    return new_tracks, library_tids, new_artists
