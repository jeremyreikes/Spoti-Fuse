import database_querying as db
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import api_keys
import datetime
import parse_playlist
from collections import OrderedDict

# delete subset when done with testing
def get_valid_tracks(sp, results, subset=None):
    '''Ensures track integrity by removing local and no-id tracks.  Creates dict with valid tracks'''
    valid_tracks = OrderedDict()
    valid_tracks = remove_invalid_tracks(results['items'], valid_tracks)
    if subset:
        return valid_tracks
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

# remove subset
def fetch_library(sp):
    results = sp.current_user_saved_tracks()
    valid_tracks = get_valid_tracks(sp, results, subset=True)

    new_tracks = list() # playlist tracks that don't exist in DB
    indices_to_add_new_tracks = list()
    new_artists = set()
    saved_tracks = list() # playlist tracks that already exist or are initialized without error

    for index, (tid, track) in enumerate(valid_tracks.items()):
        if not db.track_exists(tid):
            try:
                track_data = initialize_track(track)
                artist_id = track_data['artist_id']
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
            saved_tracks.append(track_data)
    new_tracks = parse_playlist.add_audio_features(new_tracks)
    # print(len(new_tracks), ' ', len(indices_to_add_new_tracks), ' ', len(saved_tracks))
    for track, index in zip(new_tracks, indices_to_add_new_tracks):
        saved_tracks[index] = track
    new_artists = parse_playlist.fetch_artist_info(new_artists)
    return saved_tracks, new_artists
