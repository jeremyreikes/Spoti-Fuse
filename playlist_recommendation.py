from pymongo import MongoClient
client = MongoClient(readPreference = 'secondary')
db = client.spotify_db
tracks_db = db.tracks_db
playlists_db = db.playlists_db
import pandas as pd
from collections import Counter

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
def weighted_track_frequency(word, min_occurences=None):
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

# freqs = weighted_track_frequency('love', 5)

# How should I deal with the top values always being 1? Should we always avoid vals of .5, 1, .333, or should
# Option 1:
#   Use a popular filter or term... Only grab songs that are popular based on a certain number of occurences
