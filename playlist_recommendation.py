from pymongo import MongoClient
client = MongoClient(readPreference = 'secondary')
db = client.spotify_db
tracks_db = db.tracks_db
playlists_db = db.playlists_db
import pandas as pd
from collections import Counter


def get_playlist_word_frequencies(tid, target_word=None):
    word_counts = Counter()
    playlist_ids = get_track_playlists(tid)
    total_occurences = len(playlist_ids)
    for playlist_id in playlist_ids:
        lemmas = get_playlist_lemmas(playlist_id)
        for lemma in lemmas:
            word_counts[lemma] += 1
    for word in word_counts:
        word_counts[word] /= total_occurences
    if target_word:
        return word_counts.get(target_word, 0)
    return word_counts

def get_frequencies_for_word(word):
    all_tids = list()
    playlist_occurences = Counter()
    playlists = playlists_db.find({'lemmas': word})
    for playlist in playlists:
        tids = set(playlist['tids'])
        for tid in tids:
            playlist_occurences[tid] += 1
        all_tids.extend(tids)
    all_tids = list(set(all_tids))

    total_word_playlists = playlists.count()
    all_playlist_frequencies = dict()
    word_playlist_frequencies = dict()
    track_occurences = dict()

    for track in tracks_db.find({'_id': {'$in': all_tids}}, {'_id': 1, 'playlists': 1}):
        tid = track['_id']
        total_track_playlists = len(track['playlists'])

        if total_track_playlists > 10:
            all_playlist_frequencies[tid] = playlist_occurences[tid] / total_track_playlists
        word_playlist_frequencies[tid] = playlist_occurences[tid] / total_word_playlists

    return word_playlist_frequencies, all_playlist_frequencies

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
