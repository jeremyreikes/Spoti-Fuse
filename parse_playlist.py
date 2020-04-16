from nlp_helpers import lemmatize
import database_querying as db
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import api_keys
client_credentials_manager = SpotifyClientCredentials(client_id=api_keys.spotify_client_id,
                                                      client_secret=api_keys.spotify_client_secret)
from pymongo.errors import BulkWriteError
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
from pymongo import MongoClient
client = MongoClient()
spotify_db = client.spotify_db
tracks_db = spotify_db.tracks_db
playlists_db = spotify_db.playlists_db
artists_db = spotify_db.artists_db
# tracks_db.drop()
# playlists_db.drop()
# artists_db.drop()
tracks_db.find_one({'_id': '3e9HZxeyfWwjeyPAMmWSSQ'})
useless_features = ['type', 'uri', 'track_href', 'analysis_url', 'id']

# before parsing, make sure it's not already in DB
def add_playlist(playlist_id):
    if playlist_id == '' or playlist_id == None:
        return None
    try:
        results = sp.user_playlist(playlist_id = playlist_id, user=None)
        description = results['description']
        name = results['name']
        owner = results['owner']['id']
        total_tracks = results['tracks']['total']
        desc_lemmas, desc_lang = lemmatize(description, return_lang=True)
        name_lemmas, name_lang = lemmatize(name, return_lang=True)
    except:
        print(f'Cannot get playlist {playlist_id}')
        return None

    playlist_tracks = parse_tracks(results, sp)
    playlist_length = len(playlist_tracks)
    if playlist_length > 1000 or playlist_length < 3 or desc_lang != 'en' or name_lang != 'en':
        print(f'Too many/few tracks or not english {playlist_id}')
        return None

    tracks_to_add = list()
    existing_tids = set()
    artists_to_add = set()

    for tid, track in playlist_tracks.items():
        if not db.track_exists(tid):
            try:
                track_data = initialize_track(track, playlist_id)
                artist_id = track_data['artist_id']
                if not db.artist_exists(artist_id):
                    artists_to_add.add(artist_id)
                tracks_to_add.append(track_data)
            except:
                print(f'Error initializing track {tid}')
                continue
        else:
            existing_tids.add(tid)
            tracks_db.update_one({'_id': tid}, {'$push': {'pids': playlist_id}})

    tracks_to_add = add_audio_features(tracks_to_add)
    playlist_to_add = dict(_id=playlist_id, name=name, name_lemmas=name_lemmas, owner=owner,
                           description=description, description_lemmas = desc_lemmas, tids=list())
    artists_to_add = list(artists_to_add)
    artists_to_add = fetch_genres(artists_to_add)
    add_artists(artists_to_add)

    playlist_to_add = add_tracks(tracks_to_add, playlist_to_add)
    playlist_to_add['tids'].extend(list(existing_tids))
    playlists_db.insert_one(playlist_to_add)

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


def fetch_genres(artist_ids):
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


def parse_tracks(results, sp):
    '''Ensures track integrity by removing local and no-id tracks.'''
    clean_tracks = dict()
    tracks = results['tracks']
    for track in tracks['items']:
        clean_tracks = remove_local_tracks(tracks, clean_tracks)
    while tracks['next']:
        tracks = sp.next(tracks)
        clean_tracks = remove_local_tracks(tracks, clean_tracks)
    return clean_tracks

def remove_local_tracks(tracks, clean_tracks):
    for track in tracks['items']:
        try:
            tid = track['track']['id']
            if track['is_local']:
                continue
            clean_tracks[tid] = track
        except:
            print(f'Song ID not present for: {track}')
    return clean_tracks

def add_tracks(tracks_to_add, playlist_to_add):
    if tracks_to_add:
        try:
            tids = [track['_id'] for track in tracks_to_add]
            playlist_to_add['tids'].extend(tids)
            tracks_db.insert_many(tracks_to_add)
        except:
            for track in tracks_to_add:
                try:
                    playlist_to_add['tids'].append(track['_id'])
                    tracks_db.insert_one(track)
                except:
                    print(f'Cannot insert track: {track}')
    return playlist_to_add

def add_artists(artists_to_add):
    if artists_to_add:
        try:
            artists_db.insert_many(artists_to_add)
        except BulkWriteError as bwe:
            for artist in artists_to_add:
                try:
                    artists_db.insert_one(artist)
                except:
                    print(f'cant insert artist {artist}')
