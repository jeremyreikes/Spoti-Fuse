from pymongo import MongoClient
client = MongoClient(readPreference = 'secondary')
db = client.spotify_db
tracks_db = db.tracks_db
playlists_db = db.playlists_db
import pandas as pd
from collections import Counter

# given a tid, returns title and artist
def get_track_info(tid):
    track = tracks_db.find_one({'_id': tid})
    title = track['name']
    artist = artists_db.find_one({'_id': track['artist_id']})
    return (title, artist['name'])

def track_frequency(word):
    frequencies = Counter()
    playlists = playlists_db.find({'name_lemmas': word})
    # get frequency of song in playlist with 'word' in name
    for playlist in playlists:
        tids = playlist['tids']
        for tid in tids:
            frequencies[tid] += 1
    return frequencies

# if song occurs in less than min_occurences playlists, don't consider it.
def weighted_track_frequencies(word, min_occurences=None):
    frequencies = track_frequency(word)
    to_delete = list()
    for tid in frequencies.keys():
        track = tracks_db.find_one({'_id': tid})
        total_occurences = len(track['pids'])
        frequencies[tid] /= total_occurences
        if min_occurences and min_occurences > total_occurences:
            to_delete.append(tid)
    for tid in to_delete:
        del frequencies[tid]
    return frequencies

def recommend_tracks(word, min_occurences=None, num_tracks=20):
    frequencies = weighted_track_frequencies(word, min_occurences=min_occurences)
    tracks = frequencies.most_common(num_tracks)
    tids = [track[0] for track in tracks]
    top_tracks = list()
    for tid in tids:
        track_info = get_track_info(tid)
        top_tracks.append(track_info)
    return top_tracks

# recs = recommend_tracks('workout', 10)