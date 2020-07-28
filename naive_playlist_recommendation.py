import database_querying as db
from collections import defaultdict, Counter
# if song occurs in less than min_occurences playlists, don't consider it.
def weighted_track_frequencies(search_words, min_occurences=None, tid_subset=None):
    word_track_frequencies = db.get_track_frequencies(search_words, tid_subset=tid_subset)
    all_tids = set()
    for tid_counter in word_track_frequencies.values():
        all_tids.update(tid_counter.keys())
    if len(word_track_frequencies) > 1: # make sure every search word has at least value =1 occurence
        for word, tid_counter in word_track_frequencies.items():
            for tid in all_tids:
                word_track_frequencies[word][tid] += 1
    frequency_products = defaultdict(lambda: 1)
    for tid in all_tids:
        total_occurences = len(db.get_track(tid)['pids'])
        if len(word_track_frequencies) > 1:
            total_occurences += 1
        if min_occurences and min_occurences > total_occurences:
            continue
        for word in word_track_frequencies:
            frequency_products[tid] *= word_track_frequencies[word][tid] / total_occurences
    return Counter(frequency_products)

def recommend_tracks(search_words, min_occurences=50, num_tracks=10, tid_subset=None):
    frequencies = weighted_track_frequencies(search_words, min_occurences=min_occurences, tid_subset=tid_subset)
    # tracks = frequencies.most_common(num_tracks)
    # top_tracks = [db.get_track_info(track[0]) for track in tracks]
    # return top_tracks
    return frequencies
