import database_querying as dbq

# if song occurs in less than min_occurences playlists, don't consider it.
def weighted_track_frequencies(search_word=None, min_occurences=None):
    frequencies = dbq.get_track_frequencies(search_word)
    to_delete = list()
    for tid in frequencies.keys():
        track = dbq.get_track({'_id': tid})
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
        track_info = dbq.get_track_info(tid)
        top_tracks.append(track_info)
    return top_tracks

# recs = recommend_tracks('workout', 10)
