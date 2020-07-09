import database_querying as db
from collections import defaultdict, Counter
# if song occurs in less than min_occurences playlists, don't consider it.
def weighted_track_frequencies(search_words, min_occurences=None):
    word_track_frequencies = db.get_track_frequencies(search_words)
    frequency_products = defaultdict(lambda: 1)
    # need a new dict to combine them
    for word, tid_counter in word_track_frequencies.items():
        for tid in tid_counter:
            total_occurences = len(db.get_track(tid)['pids'])
            if len(word_track_frequencies) > 1:
                total_occurences += 1 # add 1 so denominator isn't above 1
            frequency_products[tid] *= word_track_frequencies[word][tid] / total_occurences
    return Counter(frequency_products)

def recommend_tracks(search_words, min_occurences=50, num_tracks=10):
    frequencies = weighted_track_frequencies(search_words, min_occurences=min_occurences)
    tracks = frequencies.most_common(num_tracks)
    tids = [track[0] for track in tracks]
    top_tracks = list()
    for tid in tids:
        track_info = db.get_track_info(tid)
        top_tracks.append(track_info)
    return top_tracks

recs = recommend_tracks('summer dance')
recs
#
# import tensorflow as tf
